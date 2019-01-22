"""
Module contianing all transaction types
"""

from Jumpscale import j

from clients.blockchain.rivine.types.signatures import Ed25519PublicKey
from clients.blockchain.rivine.types.unlockconditions import SingleSignatureFulfillment, UnlockHashCondition,\
 LockTimeCondition, AtomicSwapCondition, AtomicSwapFulfillment, MultiSignatureCondition, FulfillmentFactory, UnlockCondtionFactory, MultiSignatureFulfillment
from clients.blockchain.rivine.encoding import binary

from clients.blockchain.rivine.utils import hash #DONT WE HAVE THIS AS JUMPSCALE PRIMITIVE?
from types.unlockhash import UnlockHash
from clients.blockchain.rivine.secrets import token_bytes
from clients.blockchain.rivine.const import HASTINGS_TFT_VALUE

from clients.blockchain.tfchain.encoding import binary as tfbinary
from clients.blockchain.tfchain.types import network as tftnet
from clients.blockchain.tfchain.types import signatures as tftsig
from clients.blockchain.tfchain import const as tfconst

from enum import Enum
import base64
import json

LEGACY_TRANSACTION_VERSION = 0
DEFAULT_TRANSACTION_VERSION = 1
MINTERDEFINITION_TRANSACTION_VERSION = 128
COINCREATION_TRANSACTION_VERSION = 129
BOT_REGISTRATION_TRANSACTION_VERSION = 144
BOT_RECORD_UPDATE_TRANSACTION_VERSION = 145
BOT_NAME_TRANSFER_TRANSACTION_VERSION = 146
HASHTYPE_COINOUTPUT_ID = 'coinoutputid'
DEFAULT_MINERFEE = 100000000

class TransactionFactory(j.application.JSBaseClass):
    """
    A transaction factory class
    """

    @staticmethod
    def create_transaction(version):
        """
        Creates and return a transaction of the speicfied verion

        @param version: Version of the transaction
        """
        if version == 1:
            return TransactionV1()


    @staticmethod
    def from_json(txn_json):
        """
        Creates a new transaction object from a json formated string

        @param txn_json: JSON string, representing a transaction
        """
        txn_dict = json.loads(txn_json)
        return TransactionFactory.from_dict(txn_dict)


    @staticmethod
    def from_dict(txn_dict):
        """
        Creates a new transaction object from a raw (JSON-decoded) dict.

        @param from_dict: dictionary, representing a raw transaction, as decoded from a JSON object.
        """
        if 'version' not in txn_dict:
            return None
 
        if txn_dict['version'] == DEFAULT_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in Default Transaction (v{})".format(DEFAULT_TRANSACTION_VERSION))
            txn = TransactionV1()
            txn_data = txn_dict['data']
            if 'coininputs' in txn_data:
                for ci_info in (txn_data['coininputs'] or []):
                    ci = CoinInput.from_dict(ci_info)
                    txn._coin_inputs.append(ci)
            if 'coinoutputs' in txn_data:
                for co_info in (txn_data['coinoutputs'] or []):
                    co = CoinOutput.from_dict(co_info)
                    txn._coin_outputs.append(co)
            if 'minerfees' in txn_data:
                for minerfee in (txn_data['minerfees'] or []) :
                    txn.add_minerfee(int(minerfee))
            if 'arbitrarydata' in txn_data:
                txn._data = base64.b64decode(txn_data['arbitrarydata'])
            return txn

        if txn_dict['version'] == LEGACY_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in Legacy Transaction (v{})".format(LEGACY_TRANSACTION_VERSION))
            txn = TransactionV1() # parse as v1 transaction, converting the coin inputs and outputs
            txn_data = txn_dict['data']
            if 'coininputs' in txn_data:
                for legacy_ci_info in (txn_data['coininputs'] or []):
                    unlocker = legacy_ci_info.get('unlocker', {})
                    ci_info = {
                        'parentid': legacy_ci_info.get('parentid', ''),
                        'fulfillment': {
                            'type': 1, # TODO: support legacy atomic swap fulfillments
                            'data': {
                                'publickey': unlocker.get('condition', {}).get('publickey'),
                                'signature': unlocker.get('fulfillment', {}).get('signature'),
                            }
                        }
                    }
                    ci = CoinInput.from_dict(ci_info)
                    txn._coin_inputs.append(ci)
            if 'coinoutputs' in txn_data:
                for legacy_co_info in (txn_data['coinoutputs'] or []):
                    co_info = {
                        'value': legacy_co_info.get('value', '0'),
                        'condition': {
                            'type': 1, # TODO: support legacy atomic swap conditions
                            'data': {
                                'unlockhash': legacy_co_info.get('unlockhash', ''),
                            }
                        }
                    }
                    co = CoinOutput.from_dict(co_info)
                    txn._coin_outputs.append(co)
            if 'minerfees' in txn_data:
                for minerfee in (txn_data['minerfees'] or []) :
                    txn.add_minerfee(int(minerfee))
            if 'arbitrarydata' in txn_data:
                txn._data.value = base64.b64decode(txn_data['arbitrarydata'])
            if 'arbitrarydatatype' in txn_data:
                txn._data.type = int(txn_data['arbitrarydatatype'])
            return txn
              
        if txn_dict['version'] == MINTERDEFINITION_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in MinterDefinition Transaction")
            txn = TransactionV128()
            txn_data = txn_dict['data']
            if 'nonce' in txn_data:
                txn._nonce = base64.b64decode(txn_data['nonce'])
            if 'mintcondition' in txn_data:
                txn._mint_condition = UnlockCondtionFactory.from_dict(txn_data['mintcondition'])
            if 'mintfulfillment' in txn_data:
                txn._mint_fulfillment = FulfillmentFactory.from_dict(txn_data['mintfulfillment'])
            if 'minerfees' in txn_data:
                for minerfee in txn_data['minerfees']:
                    txn.add_minerfee(int(minerfee))
            if 'arbitrarydata' in txn_data:
                txn._data.value = base64.b64decode(txn_data['arbitrarydata'])
            if 'arbitrarydatatype' in txn_data:
                txn._data.type = int(txn_data['arbitrarydatatype'])
            return txn
   
        if txn_dict['version'] == COINCREATION_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in CoinCreation Transaction")
            txn = TransactionV129()
            txn_data = txn_dict['data']
            if 'nonce' in txn_data:
                txn._nonce = base64.b64decode(txn_data['nonce'])
            if 'mintfulfillment' in txn_data:
                txn._mint_fulfillment = FulfillmentFactory.from_dict(txn_data['mintfulfillment'])
            if 'coinoutputs' in txn_data:
                for co_info in txn_data['coinoutputs']:
                    co = CoinOutput.from_dict(co_info)
                    txn._coin_outputs.append(co)
            if 'minerfees' in txn_data:
                for minerfee in txn_data['minerfees']:
                    txn.add_minerfee(int(minerfee))
            if 'arbitrarydata' in txn_data:
                txn._data.value = base64.b64decode(txn_data['arbitrarydata'])
            if 'arbitrarydatatype' in txn_data:
                txn._data.type = int(txn_data['arbitrarydatatype'])
            return txn

        if txn_dict['version'] == BOT_REGISTRATION_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in BotRegistration Transaction")
            txn = TransactionV144()
            txn.from_dict(txn_dict['data'])
            return txn

        if txn_dict['version'] == BOT_RECORD_UPDATE_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in BotRecordUpdate Transaction")
            txn = TransactionV145()
            txn.from_dict(txn_dict['data'])
            return txn

        if txn_dict['version'] == BOT_NAME_TRANSFER_TRANSACTION_VERSION:
            if 'data' not in txn_dict:
                raise ValueError("no data object found in BotNameTransfer Transaction")
            txn = TransactionV146()
            txn.from_dict(txn_dict['data'])
            return txn

class TransactionV1:
    """
    A Transaction is an atomic component of a block. Transactions can contain
	inputs and outputs and even arbitrar data. They can also contain signatures to prove that a given party has
	approved the transaction, or at least a particular subset of it.

	Transactions can depend on other previous transactions in the same block,
	but transactions cannot spend outputs that they create or otherwise beself-dependent.
    """
    def __init__(self):
        """
        Initializes a new tansaction
        """
        self._coin_inputs = []
        self._blockstakes_inputs = []
        self._coin_outputs = []
        self._blockstakes_outputs = []
        self._minerfees = []
        self._data = ArbitraryData()
        self._version = bytearray([1])
        self._id = None

    @property
    def version(self):
        return 1

    @property
    def id(self):
        """
        Gets transaction id
        """
        return self._id

    @id.setter
    def id(self, txn_id):
        """
        Sets transaction id
        """
        self._id = txn_id

    @property
    def coin_inputs(self):
        """
        Retrieves coins inputs
        """
        return self._coin_inputs or []

    @property
    def coin_outputs(self):
        """
        Retrieves coins outputs
        """
        return self._coin_outputs or []

    @property
    def data(self):
        """
        Gets the arbitrary data of the transaction
        """
        return self._data.value

    @property
    def data_type(self):
        """
        Gets the optional type of the arbitrary data of the transaction
        """
        return self._data.type


    @property
    def json(self):
        """
        Returns a json version of the TransactionV1 object
        """
        result = {
            'version': self.version,
            'data': {
                'coininputs': [input.json for input in self._coin_inputs],
                'coinoutputs': [output.json for output in self._coin_outputs],
                'minerfees': [str(fee) for fee in self._minerfees]
            }
        }
        if self._data.value:
            result['data']['arbitrarydata'] = base64.b64encode(self._data.value).decode('utf-8')
        if self._data.type != 0:
            result['data']['arbitrarydatatype'] = self._data.type 
        return result


    def set_data(self, data, data_type=0):
        """
        Set data of the transaction
        """
        self._data.value = data
        self._data.type = data_type


    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))


    def add_atomicswap_input(self, parent_id, pub_key, secret=None):
        """
        Adds a new atomicswap input to the transaction
        An atomicswap input can be for refund or redeem purposes, if for refund no secret is needed, but if for redeem then
        a secret needs tp be provided
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = AtomicSwapFulfillment(pub_key=key, secret=secret)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))


    def add_multisig_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))



    def add_coin_output(self, value, recipient, locktime=None):
        """
        Add a new coin output to the transaction

        @param value: Amout of coins
        @param recipient: The recipient address
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._coin_outputs.append(CoinOutput(value=value, condition=condition))



    def add_atomicswap_output(self, value, recipient, locktime, refund_address, hashed_secret):
        """
        Add a new atomicswap output to the transaction
        """
        condition = AtomicSwapCondition(sender=refund_address, reciever=recipient,
                                        hashed_secret=hashed_secret, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coin_outputs.append(coin_output)
        return coin_output


    def add_multisig_output(self, value, unlockhashes, min_nr_sig, locktime=None):
        """
        Add a new MultiSignature output to the transaction

        @param value: Value of the output in hastings
        @param unlockhashes: List of all unlock hashes which are authorised to spend this output by signing off
        @param min_nr_sig: Defines the amount of signatures required in order to spend this output
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes,
                                            min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coin_outputs.append(coin_output)
        return coin_output


    def add_minerfee(self, minerfee):
        """
        Adds a minerfee to the transaction
        """
        self._minerfees.append(minerfee)


    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []

        buffer = bytearray()
        # encode the transaction version
        buffer.extend(self._version)
        # encode the input index
        buffer.extend(binary.encode(input_index))

        # encode extra objects if exists
        for extra_object in extra_objects:
            buffer.extend(binary.encode(extra_object))

        # encode the number of coins inputs
        buffer.extend(binary.encode(len(self._coin_inputs)))

        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(binary.encode(coin_input.parent_id, type_='hex'))

        # encode coin outputs
        buffer.extend(binary.encode(self._coin_outputs, type_='slice'))

        # encode the number of blockstakes
        buffer.extend(binary.encode(len(self._blockstakes_inputs)))
        # encode blockstack inputs parent_ids
        for bs_input in self._blockstakes_inputs:
            buffer.extend(binary.encode(bs_input.parent_id, type_='hex'))

        # encode blockstake outputs
        buffer.extend(binary.encode(self._blockstakes_outputs, type_='slice'))

        # encode miner fees
        buffer.extend(binary.encode(len(self._minerfees)))
        for miner_fee in self._minerfees:
            buffer.extend(binary.encode(miner_fee, type_='currency'))

        # encode custom data
        buffer.extend(binary.encode(self._data))

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)


class TransactionV128:
    """
    Minter definition transaction class. This transaction type
    allows the current coin creators to redefine who has the ability to create coins.
    """
    def __init__(self):
        self._mint_fulfillment = None
        self._mint_condition = None
        self._minerfees = []
        self._data = ArbitraryData()
        self._version = bytearray([128])
        self._id = None
        self._nonce = token_bytes(nbytes=8)
        self._specifier = bytearray(b'minter defin tx\0')

    @property
    def version(self):
        return 128

    @property
    def id(self):
        """
        Get transaction id
        """
        return self._id
    @id.setter
    def id(self, txn_id):
        """
        Set transaction id
        """
        self._id = txn_id

    @property
    def coin_inputs(self):
        """
        Retrieves the coin inputs
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return []

    @property
    def coin_outputs(self):
        """
        Retrieves the coin outputs
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return []

    @property
    def data(self):
        """
        Retrieves the data
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return self._data.value


    @property
    def data_type(self):
        """
        Retrieves the data type
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return self._data.type


    @property
    def mint_condition(self):
        """
        Retrieve the new mint condition which will be set
        """
        return self._mint_condition


    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        return self._mint_fulfillment


    @property
    def json(self):
        """
        Returns a json representation of the transaction
        """
        result = {
                'version': binary.decode(self._version, type_=int),
                'data': {
                    'nonce': base64.b64encode(self._nonce).decode('utf-8'),
                    'mintfulfillment': self._mint_fulfillment.json if self._mint_fulfillment else '{}',
                    'mintcondition': self._mint_condition.json if self._mint_condition else '{}',
                    'minerfees': [str(fee) for fee in self._minerfees]
                }
        }
        if self._data.value:
            result['data']['arbitrarydata'] = base64.b64encode(self._data.value).decode('utf-8')
        if self._data.type != 0:
            result['data']['arbitrarydatatype'] = self._data.type 
        return result

    
    def set_data(self, data, data_type=0):
        """
        Set data of the transaction
        """
        self._data.value = data
        self._data.type = data_type


    def set_singlesig_mint_condition(self, minter_address, locktime=None):
        """
        Set the mint condition to a singlesig condition.
         @param minter_address: The address of the singlesig condition to set as new mint condition
        """
        unlockhash = UnlockHash.from_string(minter_address)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._mint_condition = condition


    def set_multisig_mint_condition(self, unlockhashes, min_nr_sig, locktime=None):
        """
        Set the mint condition to a multisig condition
         @param unlockhashes: The unlockhashes which can sign the multisig condition
        @param min_nr_sig: The minimum amount of signatures in order to fulfill the condition
        @param locktime: An optional time until which the condition cannot be fulfilled
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes, min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._mint_condition = condition

    def set_condition(self, condition):
        """
        Set a new premade minter condition
        """
        self._mint_condition = condition

    def add_minerfee(self, minerfee):
        """
        Adds a minerfee to the transaction
        """
        self._minerfees.append(minerfee)


    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode transaction version
        buffer.extend(self._version)
        # encode the specifier
        buffer.extend(self._specifier)
        # encode nonce
        buffer.extend(self._nonce)
         # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(binary.encode(extra_object))
         # encode new mintcondition
        buffer.extend(binary.encode(self._mint_condition))
        # minerfee length
        buffer.extend(binary.encode(len(self._minerfees)))
        # actual minerfees
        for miner_fee in self._minerfees:
            buffer.extend(binary.encode(miner_fee, type_='currency'))
        # arb data
        buffer.extend(binary.encode(self._data))

        return hash(data=buffer)


class TransactionV129:
    """
    Coin creation transaction class. This transaction type allows the current
    coin creators to create new coins and spend them.
    """
    def __init__(self):
        self._mint_fulfillment = None
        self._nonce = token_bytes(nbytes=8)
        self._version = bytearray([129])
        self._id = None
        self._minerfees = []
        self._data = ArbitraryData()
        self._coin_outputs = []
        self._specifier = bytearray(b'coin mint tx')
        self._specifier.extend([0,0,0,0])

    @property
    def version(self):
        return 129

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id

    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id


    @property
    def coin_inputs(self):
        """
        Retrieves the coin inputs
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return []


    @property
    def coin_outputs(self):
        """
        Retrieves the coin outputs
        """
        return self._coin_outputs or []

    @property
    def data(self):
        """
        Retrieves the data
        """
        return self._data.value

    @property
    def data_type(self):
        """
        Retrieves the data type
        """
        return self._data.type

    @property
    def mint_fulfillment(self):
        """
        Retrieve the current mint fulfillment
        """
        return self._mint_fulfillment

    @property
    def json(self):
        """
        Returns a json version of the TransactionV129 object
        """
        result = {
            'version': binary.decode(self._version, type_=int),
            'data': {
                'nonce': base64.b64encode(self._nonce).decode('utf-8'),
                'mintfulfillment': self._mint_fulfillment.json if self._mint_fulfillment else '{}',
                'coinoutputs': [output.json for output in self._coin_outputs],
                'minerfees': [str(fee) for fee in self._minerfees]
            }
        }
        if self._data.value:
            result['data']['arbitrarydata'] = base64.b64encode(self._data.value).decode('utf-8')
        if self._data.type != 0:
            result['data']['arbitrarydatatype'] = self._data.type 
        return result

    
    def set_data(self, data, data_type=0):
        """
        Set data of the transaction
        """
        self._data.value = data
        self._data.type = data_type


    def add_coin_output(self, value, recipient, locktime=None):
        """
        Add a new coin output to the transaction

        @param value: Amount of coins
        @param recipient: The recipient address
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        self._coin_outputs.append(CoinOutput(value=value, condition=condition))

    def add_multisig_output(self, value, unlockhashes, min_nr_sig, locktime=None):
        """
        Add a new MultiSignature output to the transaction

        @param value: Value of the output in hastings
        @param unlockhashes: List of all unlockhashes which are authorised to spend this input
        @param min_nr_sig: The amount of signatures required to spend this output
        @param locktime: If provided then a locktimecondition will be created for this output
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes, min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        coin_output = CoinOutput(value=value, condition=condition)
        self._coin_outputs.append(coin_output)

    def add_output(self, value, condition):
        """
        Add a new output from a premade condition
        """
        self._coin_outputs.append(CoinOutput(value=value, condition=condition))

    def add_minerfee(self, minerfee):
        """
        Adds a miner fee to the transaction
        """
        self._minerfees.append(minerfee)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: ignored
        """
        if extra_objects is None:
            extra_objects = []

        buffer = bytearray()
        # encode the transaction version
        buffer.extend(self._version)
        # specifier
        buffer.extend(self._specifier)
        # nonce
        buffer.extend(self._nonce)

        # arbitrary objects if any
        for extra_object in extra_objects:
            buffer.extend(binary.encode(extra_object))

        # new coin outputs
        buffer.extend(binary.encode(self._coin_outputs, type_='slice'))

        # miner fees
        buffer.extend(binary.encode(len(self._minerfees)))
        for miner_fee in self._minerfees:
            buffer.extend(binary.encode(miner_fee, type_='currency'))

        # finally custom data
        buffer.extend(binary.encode(self._data))

        return hash(data=buffer)

class TransactionV144:
    """
    Bot Registration transaction class. This transaction type allows a
    new 3Bot to be registered.
    """
    def __init__(self):
        self._specifier = bytearray(b'bot register tx\0')
        self._id = None
        self._addresses = []
        self._names = []
        self._number_of_months = 0
        self._transaction_fee = None
        self._coin_inputs = []
        self._refund_coin_output = None
        self._identification = TfchainPublicKeySignaturePair(None, None)
    
    @property
    def version(self):
        return BOT_REGISTRATION_TRANSACTION_VERSION

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id
    
    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id
    
    @property
    def identification(self):
        """
        Get the 3Bot identification of this transaction.
        """
        return self._identification

    @property
    def required_bot_fees(self):
        # a static registration fee has to be paid
        fees = tfconst.BOT_REGISTRATION_FEE_MULTIPLIER * HASTINGS_TFT_VALUE
        # the amount of desired months also has to be paid
        fees += _compute_monthly_bot_fees(self._number_of_months)
        # if more than one name is defined it also has to be paid
        lnames = len(self._names)
        if lnames > 1:
            fees += HASTINGS_TFT_VALUE * (lnames-1) * tfconst.BOT_FEE_PER_ADDITIONAL_NAME_MULTIPLIER
        # no fee has to be paid for the used network addresses during registration
        # return the total fees
        return fees

    @property
    def coin_inputs(self):
        """
        Retrieves coin inputs
        """
        return self._coin_inputs

    @property
    def coin_outputs(self):
        """
        Retrieves coin inputs
        """
        # TODO: support 3Bot Fee Payout as well
        if self._refund_coin_output:
            return [self._refund_coin_output]
        return []

    @property
    def data(self):
        """
        Retrieves the data
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return bytearray()

    @property
    def json(self):
        """
        Returns a json version of the TransactionV144 object
        """
        result = {
            'version': self.version,
            'data': {
                'nrofmonths': self._number_of_months,
                'txfee': str(self._transaction_fee),
                'coininputs': [ci.json for ci in self._coin_inputs],
                'identification': self._identification.json,
            }
        }
        if self._addresses:
            result['data']['addresses'] = [addr.json for addr in self._addresses]
        if self._names:
            result['data']['names'] = self._names.copy()
        if self._refund_coin_output:
            result['data']['refundcoinoutput'] = self._refund_coin_output.json
        return result
    
    def from_dict(self, data):
        """
        Populates this TransactionV144 object from a data (JSON-decoded) dictionary
        """
        if 'nrofmonths' in data:
            self._number_of_months = data['nrofmonths']
        else:
            self._number_of_months = 0
        if 'txfee' in data:
            self._transaction_fee = int(data['txfee'])
        else:
            self._transaction_fee = None
        if 'coininputs' in data:
            for ci_info in data['coininputs']:
                ci = CoinInput.from_dict(ci_info)
                self._coin_inputs.append(ci)
        else:
            self._coin_inputs = []
        if 'identification' in data:
            self._identification = TfchainPublicKeySignaturePair.from_dict(data['identification'])
        else:
            self._identification = TfchainPublicKeySignaturePair(None, None)
        if 'addresses' in data:
            for addr_str in data['addresses']:
                addr = tftnet.NetworkAddress.from_string(addr_str)
                self._addresses.append(addr)
        else:
            self._addresses = []
        if 'names' in data:
            self._names = data['names'].copy()
        else:
            self._names = []
        if 'refundcoinoutput' in data:
            co = CoinOutput.from_dict(data['refundcoinoutput'])
            self._refund_coin_output = co
        else:
            self._refund_coin_output = None

    def add_address(self, addr_str):
        addr = tftnet.NetworkAddress.from_string(addr_str)
        self._addresses.append(addr)
    
    def add_name(self, name):
        self._names.append(name)

    def set_transaction_fee(self, txfee):
        self._transaction_fee = txfee

    def set_number_of_months(self, n):
        if n < 1 or n > 24:
            ValueError("number of months for a 3Bot Registration Transaction has to be in the inclusive range [1,24]")
        self._number_of_months = n

    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))
    
    def add_multisig_coin_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))

    def set_refund_coin_output(self, value, recipient):
        """
        Set a coin output as refund coin output of this tx

        @param value: Amout of coins
        @param recipient: The recipient address
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        self._refund_coin_output = CoinOutput(value=value, condition=condition)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode the transaction version
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self.version))
        # encode the specifier
        buffer.extend(self._specifier)

        # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(tfbinary.BinaryEncoder.encode(extra_object))

        # encode addresses
        buffer.extend(tfbinary.BinaryEncoder.encode(self._addresses, type_='slice'))
        # encode names
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names, type_='slice'))
        # encode number of months
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._number_of_months, _kind='int8'))

        # encode the number of coins inputs
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(len(self._coin_inputs), _kind='int'))
        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(tfbinary.BinaryEncoder.encode(coin_input.parent_id, type_='hex'))

        # encode transaction fee
        buffer.extend(binary.encode(self._transaction_fee, type_='currency'))
        # encode refund coin output
        if self._refund_coin_output:
            buffer.extend([1])
            buffer.extend(binary.encode(self._refund_coin_output))
        else:
            buffer.extend([0])
        # encode public key
        buffer.extend(tfbinary.BinaryEncoder.encode(self._identification.public_key))

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)

class TransactionV145:
    """
    Bot Record Update transaction class. This transaction type allows
    an existing 3Bot to be updated.
    """
    def __init__(self):
        self._specifier = bytearray(b'bot recupdate tx')
        self._id = None
        self._botid = None
        self._addresses_to_add = []
        self._addresses_to_remove = []
        self._names_to_add = []
        self._names_to_remove = []
        self._number_of_months = 0
        self._transaction_fee = None
        self._coin_inputs = []
        self._refund_coin_output = None
        self._signature = ''
        self._publickey = None
    
    @property
    def version(self):
        return BOT_RECORD_UPDATE_TRANSACTION_VERSION

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id
    
    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id

    @property
    def required_bot_fees(self):
        fees = 0
        # all additional months have to be paid
        if self._number_of_months > 0:
            fees += _compute_monthly_bot_fees(self._number_of_months)
        # a Tx that modifies the network address info of a 3bot record also has to be paid
        if self._addresses_to_add or self._addresses_to_remove:
            fees += tfconst.BOT_FEE_FOR_NETWORK_ADDRESS_INFO_CHANGE_MULTIPLIER * HASTINGS_TFT_VALUE
        # each additional name has to be paid as well
	    # (regardless of the fact that the 3bot has a name or not)
        lnames = len(self._names_to_add)
        if lnames > 0:
            fees += HASTINGS_TFT_VALUE * lnames * tfconst.BOT_FEE_PER_ADDITIONAL_NAME_MULTIPLIER
        # return the total fees
        return fees

    @property
    def coin_inputs(self):
        """
        Retrieves coin inputs
        """
        return self._coin_inputs

    @property
    def coin_outputs(self):
        """
        Retrieves coin inputs
        """
        # TODO: support 3Bot Fee Payout as well
        if self._refund_coin_output:
            return [self._refund_coin_output]
        return []

    @property
    def data(self):
        """
        Retrieves the data
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return bytearray()

    @property
    def json(self):
        """
        Returns a json version of the TransactionV144 object
        """
        result = {
            'version': self.version,
            'data': {
                'id': self._botid,
                'nrofmonths': self._number_of_months,
                'txfee': str(self._transaction_fee),
                'coininputs': [ci.json for ci in self._coin_inputs],
                'signature': self._signature,
            }
        }
        addr_dic = {}
        if self._addresses_to_add:
            addr_dic['add'] = [addr.json for addr in self._addresses_to_add]
        if self._addresses_to_remove:
            addr_dic['remove'] = [addr.json for addr in self._addresses_to_remove]
        if len(addr_dic) > 0:
            result['data']['addresses'] = addr_dic
        name_dic = {}
        if self._names_to_add:
            name_dic['add'] = self._names_to_add.copy()
        if self._names_to_remove:
            name_dic['remove'] = self._names_to_remove.copy()
        if len(name_dic) > 0:
            result['data']['names'] = name_dic
        if self._refund_coin_output:
            result['data']['refundcoinoutput'] = self._refund_coin_output.json
        return result
    
    def from_dict(self, data):
        """
        Populates this TransactionV145 object from a data (JSON-decoded) dictionary
        """
        if 'id' in data:
            self._botid = data['id']
        else:
            self._botid = 0 # 0 is an invalid botID, the identifiers start at 1
        if 'nrofmonths' in data:
            self._number_of_months = data['nrofmonths']
        else:
            self._number_of_months = 0
        if 'txfee' in data:
            self._transaction_fee = int(data['txfee'])
        else:
            self._transaction_fee = None
        if 'coininputs' in data:
            for ci_info in data['coininputs']:
                ci = CoinInput.from_dict(ci_info)
                self._coin_inputs.append(ci)
        else:
            self._coin_inputs = []
        if 'signature' in data:
            self._signature = data['signature']
        else:
            self._signature = ''
        self._addresses_to_add = []
        self._addresses_to_remove = []
        if 'addresses' in data:
            if 'add' in data['addresses']:
                for addr_str in data['addresses']['add']:
                    addr = tftnet.NetworkAddress.from_string(addr_str)
                    self._addresses_to_add.append(addr)
            if 'remove' in data['addresses']:
                for addr_str in data['addresses']['remove']:
                    addr = tftnet.NetworkAddress.from_string(addr_str)
                    self._addresses_to_remove.append(addr)
        self._names_to_add = []
        self._names_to_remove = []
        if 'names' in data:
            if 'add' in data['names']:
                self._names_to_add = data['names']['add'].copy()
            if 'remove' in data['names']:
                self._names_to_remove = data['names']['remove'].copy()
        if 'refundcoinoutput' in data:
            co = CoinOutput.from_dict(data['refundcoinoutput'])
            self._refund_coin_output = co
        else:
            self._refund_coin_output = None

    def add_address_to_add(self, addr_str):
        addr = tftnet.NetworkAddress.from_string(addr_str)
        self._addresses_to_add.append(addr)

    def add_address_to_remove(self, addr_str):
        addr = tftnet.NetworkAddress.from_string(addr_str)
        self._addresses_to_remove.append(addr)
    
    def add_name_to_add(self, name):
        self._names_to_add.append(name)
    
    def add_name_to_remove(self, name):
        self._names_to_remove.append(name)

    def set_transaction_fee(self, txfee):
        self._transaction_fee = txfee

    def set_number_of_months(self, n):
        if n < 1 or n > 24:
            ValueError("number of months for a 3Bot Registration Transaction has to be in the inclusive range [1,24]")
        self._number_of_months = n
    
    def set_bot_id(self, identifier):
        self._botid = identifier
    
    def get_bot_id(self):
        return self._botid
    
    def set_signature(self, signature):
        self._signature = signature

    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))
    
    def add_multisig_coin_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))

    def set_refund_coin_output(self, value, recipient):
        """
        Set a coin output as refund coin output of this tx

        @param value: Amout of coins
        @param recipient: The recipient address
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        self._refund_coin_output = CoinOutput(value=value, condition=condition)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode the transaction version
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self.version))
        # encode the specifier
        buffer.extend(self._specifier)
        # encode the bot identifier
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._botid, _kind='uint32'))

        # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(tfbinary.BinaryEncoder.encode(extra_object))

        # encode addresses
        buffer.extend(tfbinary.BinaryEncoder.encode(self._addresses_to_add, type_='slice'))
        buffer.extend(tfbinary.BinaryEncoder.encode(self._addresses_to_remove, type_='slice'))
        # encode names
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names_to_add, type_='slice'))
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names_to_remove, type_='slice'))
        # encode number of months
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._number_of_months, _kind='int8'))

        # encode the number of coins inputs
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(len(self._coin_inputs), _kind='int'))
        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(tfbinary.BinaryEncoder.encode(coin_input.parent_id, type_='hex'))

        # encode transaction fee
        buffer.extend(binary.encode(self._transaction_fee, type_='currency'))
        # encode refund coin output
        if self._refund_coin_output:
            buffer.extend([1])
            buffer.extend(binary.encode(self._refund_coin_output))
        else:
            buffer.extend([0])

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)

class TransactionV146:
    """
    Bot Name Transfer transaction class. This transaction type allows
    the transfer of one or multiple (bot) names between two existing 3 bots.
    """
    def __init__(self):
        self._specifier = bytearray(b'bot nametrans tx')
        self._id = None

        self._sender_botid = None
        self._sender_signature = ''
        self._receiver_botid = None
        self._receiver_signature = ''
        self._names = []

        self._transaction_fee = None
        self._coin_inputs = []
        self._refund_coin_output = None

        self._sender_publickey = None
        self._receiver_publickey = None

    @property
    def version(self):
        return BOT_NAME_TRANSFER_TRANSACTION_VERSION

    @property
    def id(self):
        """
        Get the transaction id
        """
        return self._id
    
    @id.setter
    def id(self, tx_id):
        """
        Set the transaction id
        """
        self._id = tx_id

    @property
    def required_bot_fees(self):
        return HASTINGS_TFT_VALUE * len(self._names) * tfconst.BOT_FEE_PER_ADDITIONAL_NAME_MULTIPLIER

    @property
    def coin_inputs(self):
        """
        Retrieves coin inputs
        """
        return self._coin_inputs

    @property
    def coin_outputs(self):
        """
        Retrieves coin inputs
        """
        # TODO: support 3Bot Fee Payout as well
        if self._refund_coin_output:
            return [self._refund_coin_output]
        return []

    @property
    def data(self):
        """
        Retrieves the data
        """
        # TODO: make this static of some Base (Abstract) Tx class
        return bytearray()

    @property
    def json(self):
        """
        Returns a json version of the TransactionV144 object
        """
        result = {
            'version': self.version,
            'data': {
                'sender': {
                    'id': self._sender_botid,
                    'signature': self._sender_signature
                },
                'receiver': {
                    'id': self._receiver_botid,
                    'signature': self._receiver_signature
                },
                'names': self._names.copy(),
                'txfee': str(self._transaction_fee),
                'coininputs': [ci.json for ci in self._coin_inputs]
            }
        }
        if self._refund_coin_output:
            result['data']['refundcoinoutput'] = self._refund_coin_output.json
        return result
    
    def from_dict(self, data):
        """
        Populates this TransactionV146 object from a data (JSON-decoded) dictionary
        """
        sender_data = data.get('sender', {})
        self._sender_botid = sender_data.get('id', 0)
        self._sender_signature = sender_data.get('signature', '')
        receiver_data = data.get('receiver', {})
        self._receiver_botid = receiver_data.get('id', 0)
        self._receiver_signature = receiver_data.get('signature', '')
        if 'txfee' in data:
            self._transaction_fee = int(data['txfee'])
        else:
            self._transaction_fee = None
        if 'coininputs' in data:
            for ci_info in data['coininputs']:
                ci = CoinInput.from_dict(ci_info)
                self._coin_inputs.append(ci)
        else:
            self._coin_inputs = []
        self._names = []
        if 'names' in data:
            self._names = data['names'].copy()
        if 'refundcoinoutput' in data:
            co = CoinOutput.from_dict(data['refundcoinoutput'])
            self._refund_coin_output = co
        else:
            self._refund_coin_output = None

    def add_name(self, name):
        self._names.append(name)

    def set_transaction_fee(self, txfee):
        self._transaction_fee = txfee

    def set_sender_bot_id(self, identifier):
        self._sender_botid = identifier

    def get_sender_bot_id(self):
        return self._sender_botid
    
    def set_sender_signature(self, signature):
        self._sender_signature = signature

    def set_receiver_bot_id(self, identifier):
        self._receiver_botid = identifier

    def get_receiver_bot_id(self):
        return self._receiver_botid
    
    def set_receiver_signature(self, signature):
        self._receiver_signature = signature

    def add_coin_input(self, parent_id, pub_key):
        """
        Adds a new input to the transaction
        """
        key = Ed25519PublicKey(pub_key=pub_key)
        fulfillment = SingleSignatureFulfillment(pub_key=key)
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))
    
    def add_multisig_coin_input(self, parent_id):
        """
        Adds a new coin input with an empty MultiSignatureFulfillment
        """
        fulfillment = MultiSignatureFulfillment()
        self._coin_inputs.append(CoinInput(parent_id=parent_id, fulfillment=fulfillment))

    def set_refund_coin_output(self, value, recipient):
        """
        Set a coin output as refund coin output of this tx

        @param value: Amout of coins
        @param recipient: The recipient address
        """
        unlockhash = UnlockHash.from_string(recipient)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        self._refund_coin_output = CoinOutput(value=value, condition=condition)

    def get_input_signature_hash(self, input_index, extra_objects=None):
        """
        Builds a signature hash for an input

        @param input_index: Index of the input we will get signature hash for
        """
        if extra_objects is None:
            extra_objects = []
        buffer = bytearray()
        # encode the transaction version
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self.version))
        # encode the specifier
        buffer.extend(self._specifier)
        # encode the bot identifiers
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._sender_botid, _kind='uint32'))
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(self._receiver_botid, _kind='uint32'))

        # extra objects if any
        for extra_object in extra_objects:
            buffer.extend(tfbinary.BinaryEncoder.encode(extra_object))

        # encode names
        buffer.extend(tfbinary.BinaryEncoder.encode(self._names, type_='slice'))

        # encode the number of coins inputs
        buffer.extend(tfbinary.IntegerBinaryEncoder.encode(len(self._coin_inputs), _kind='int'))
        # encode inputs parent_ids
        for coin_input in self._coin_inputs:
            buffer.extend(tfbinary.BinaryEncoder.encode(coin_input.parent_id, type_='hex'))

        # encode transaction fee
        buffer.extend(binary.encode(self._transaction_fee, type_='currency'))
        # encode refund coin output
        if self._refund_coin_output:
            buffer.extend([1])
            buffer.extend(binary.encode(self._refund_coin_output))
        else:
            buffer.extend([0])

        # now we need to return the hash value of the binary array
        # return bytes(buffer)
        return hash(data=buffer)

def _compute_monthly_bot_fees(months):
    """
    computes the total monthly fees required for the given months,
    using the given oneCoin value as the currency's unit value.
    """
    multiplier = months * tfconst.BOT_MONTHLY_FEE_MULTIPLIER
    fees = HASTINGS_TFT_VALUE * multiplier
    if months < 12:
        return fees
    if months < 24:
        return int(fees * 0.7)
    return int(fees * 0.5)

class TfchainPublicKeySignaturePair:
    """
    TfchainPublicKeySignaturePair class
    """
    def __init__(self, public_key, signature):
        self._public_key = public_key
        self._signature = signature
    
    @classmethod
    def from_dict(cls, pair_info):
        """
        Creates a new TfchainPublicKeySignaturePair from dict
        
        @param pair_info: JSON dict representing a TfchainPublicKeySignaturePair
        """
        if 'publickey' in pair_info and 'signature' in pair_info:
            return cls(
                public_key = tftsig.SiaPublicKey.from_string(pair_info['publickey']),
                signature = pair_info['signature'],
            )
    
    @property
    def public_key(self):
        return self._public_key
    @public_key.setter
    def public_key(self, key):
        self._public_key = key
    
    @property
    def signature(self):
        return self._signature
    @signature.setter
    def signature(self, sig):
        self._signature = sig

    @property
    def json(self):
        """
        Returns a json encoded version of the TfchainPublicKeySignaturePair
        """
        return {
            'publickey': self._public_key.json,
            'signature': self._signature
        }

def sign_bot_transaction(transaction, public_key, secret_key):
    """
    Sign the pair using the secret key and fulfillment
    """
    sig_ctx = {
        'input_idx': 0,
        'transaction': transaction,
        'secret_key': secret_key
    }
    fulfillment = SingleSignatureFulfillment(pub_key=public_key)
    fulfillment.sign(sig_ctx=sig_ctx)
    return fulfillment._signature.hex()

class CoinInput:
    """
    CoinIput class
    """
    def __init__(self, parent_id, fulfillment):
        """
        Initializes a new coin input object
        """
        self._parent_id = parent_id
        self._fulfillment = fulfillment


    @classmethod
    def from_dict(cls, ci_info):
        """
        Creates a new CoinInput from dict

        @param ci_info: JSON dict representing a coin input
        """
        if 'fulfillment' in ci_info:
            f = FulfillmentFactory.from_dict(ci_info['fulfillment'])
            if 'parentid' in ci_info:
                return cls(parent_id=ci_info['parentid'],
                           fulfillment=f)

    @property
    def parent_id(self):
        return self._parent_id


    @property
    def json(self):
        """
        Returns a json encoded version of the Coininput
        """
        return {
            'parentid': self._parent_id,
            'fulfillment': self._fulfillment.json
        }


    def sign(self, input_idx, transaction, secret_key):
        """
        Sign the input using the secret key
        """
        sig_ctx = {
            'input_idx': input_idx,
            'transaction': transaction,
            'secret_key': secret_key
        }
        self._fulfillment.sign(sig_ctx=sig_ctx)


class CoinOutput:
    """
    CoinOutput calss
    """
    def __init__(self, value, condition):
        """
        Initializes a new coinoutput
        """
        self._value = value
        self._condition = condition


    @classmethod
    def from_dict(cls, co_info):
        """
        Creates a new CoinOutput from dict

        @param co_info: JSON dict representing a coin output
        """
        if 'condition' in co_info:
            condition = UnlockCondtionFactory.from_dict(co_info['condition'])
            if 'value' in co_info:
                return cls(value=int(co_info['value']),
                           condition=condition)


    @property
    def binary(self):
        """
        Returns a binary encoded version of the CoinOutput
        """
        result = bytearray()
        result.extend(binary.encode(self._value, type_='currency'))
        result.extend(binary.encode(self._condition))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the CointOutput
        """
        result = {
            'value': str(self._value),
            'condition': {},
        }
        if self._condition:
            result['condition'] = self._condition.json
        return result


class ArbitraryData:
    def __init__(self):
        self._value = bytearray()
        self._type = 0

    def __str__(self):
        if self._type == 1:
            return self._value.decode('utf-8')
        return self._value.hex()
    def __repr__(self):
        return str(self)
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, data):
        if isinstance(data, bytearray):
            self._value = data
            return
        if not data:
            self._value = bytearray()
        elif isinstance(data, bytes):
            self._value = bytearray(data)
        elif isinstance(data, str):
            self._value = data.encode('utf-8')
        else:
            raise ValueError("value of unsupported type {} cannot be used as arbitrary data".format(type(data)))
    
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, i):
        if not isinstance(i, int):
            raise ValueError("value of unsupported type {} cannot be used as the integral type of arbitrary data".format(type(i)))
        if i < 0 or i > 255:
            raise ValueError("invalid arbitrary data type {}, it has to be in the inclusive range [0,255]".format(i))
        self._type = i

    
    @property
    def binary(self):
        length = len(self._value)
        output = bytearray(binary.encode(length))
        output[3] = self._type # type in using byte 3 of the 8-byte length of arbitrary data in Sia-encoding
        output.extend(self._value) # append arbitrary data and return the total array
        return output
    

class CoinOutputSummary:
    def __init__(self):
        self._amount = 0
        self._locked = 0
        self._unlockhash = ''
        self._addresses = []
        self._signatures_required = 0
        self._raw_condition = {}

    def __repr__(self):
        output = '{} : {}'.format(self._unlockhash, self._amount)
        if self._locked:
            output += ' ({})'.format(self._locked)
        return output

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__


    @classmethod
    def from_raw_coin_output(cls, unlockhash, raw_coin_output):
        cos = cls()
        # set the unlockhash as-is
        cos._unlockhash = unlockhash
        # get the amount
        cos._amount = int(raw_coin_output.get('value', 0))
        # assign the raw condition
        cos._raw_condition = raw_coin_output.get('condition', {})
        # populate the rest of the properties using the condition
        cos._populate_from_condition(cos._raw_condition)
        # return the populated cos
        return cos

    def _populate_from_condition(self, condition):
        condition_type = condition.get('type', 0)
        if not condition or condition_type == 0:
            self._addresses.append('0'*78) # free-for-all wallet
            self._signatures_required = 1
            return
    
        # interpret the condition data based on its type
        condition_data = condition.get('data', {})

        if condition_type == 1:
            # v1 condition: unlockhash condition
            self._populate_from_condition_v1(condition_data)
        elif condition_type == 3:
            # v3 condition: time lock condition
            self._populate_from_condition_v3(condition_data)
        elif condition_type == 4:
            # v4 condition: multi-signature condition
            self._populate_from_condition_v4(condition_data)
        # unknown conditions are ignored, and some other ones are ignored
        # on purpose (e.g. v2 atomic swap conditions)

    def _populate_from_condition_v1(self, data):
        uh = data.get('unlockhash', '')
        if not uh:
            raise ValueError("invalid raw UnlockHash condition: no unlockhash property found")
        self._addresses.append(uh)
        self._signatures_required = 1
    
    def _populate_from_condition_v3(self, data):
        # define the locked value
        lt = data.get('locktime', 0)
        if not lt:
            raise ValueError("invalid raw TimeLock condition: no locktime property found")
        self._locked = lt
        # populate further using the inner condition
        condition = data.get('condition', {})
        self._populate_from_condition(condition)

    def _populate_from_condition_v4(self, data):
        # populate the addresses
        uhs = data.get('unlockhashes', '')
        if not uhs:
            raise ValueError("invalid raw MultiSignature condition: no unlockhashes property found")
        self._addresses = uhs.copy()
        msc = data.get('minimumsignaturecount', 0)
        if msc < 2:
            raise ValueError("invalid raw MultiSignature condition: {} is an invalid minimum signature count".format(msc))
        self._signatures_required = msc


    @property
    def amount(self):
        """
        Returns the amounts of coins that are send in the form of this CoinOutput.
        """
        return self._amount

    @property
    def locked(self):
        """
        Locked is 0 if no lock is coupled to this CoinOutput.
        Otherwise it represents either a block height or a UNIX epoch timestamp (in seconds)
        on which the CoinOutput unlocks, and thus becomes available for spending.
        The lock value represents a block height if it is less than 500.000.000,
        otherwise it represents a UNIX epoch timestamp.
        """
        return self._locked

    @property
    def unlockhash(self):
        """
        The unlockhash of the condition of this coin output.
        """
        return self._unlockhash

    @property
    def addresses(self):
        """
        Returns the addresses to which this CoinOutput is sent,
        for SingleSignature CoinOutputs this is always a single address,
        for MultiSignature CoinOutputs these will be at least 2 addresses.

        If no addresses are listed, this coin output is not a regular coin output,
        and instead might for example be part of an atomic swap contract.
        """
        return self._addresses

    @property
    def signatures_required(self):
        """
        Returns the amount of signatures required,
        for SingleSignature CoinOutputs this value will always be be 1,
        for MultiSignature CoinOutputs this value will always be greater than 2.

        If 0 is returned, this coin output is not a regular coin output,
        and instead might for example be part of an atomic swap contract.
        """
        return self._signatures_required

    @property
    def raw_condition(self):
        """
        Returns the condition of this CoinOutput,
        as a decoded dictionary, as regisered on the chain.
        """
        return self._raw_condition


class CoinInputSummary:
    def __init__(self, id, amount, address, raw_fulfillment):
        self._id = id
        self._amount = amount
        self._address = address
        self._raw_fulfillment = raw_fulfillment

    def __repr__(self):
        return '({}) {} : {}'.format(self._id, self._address, self._amount)


    @property
    def identifier(self):
        """
        The (parent) identifier of this spent coin output (coin input).
        """
        return self._id

    @property
    def amount(self):
        """
        The amount of coins spend using this fulfilled coin input.
        """
        return self._amount

    @property
    def address(self):
        """
        The address (unlockhash) that spent this coin input.
        """
        return self._address

    @property
    def raw_fulfillment(self):
        """
        The raw fulfillment (JSON-decoded dict), as recored on the chain.
        """
        return self._raw_fulfillment


class TransactionSummary:
    def __init__(self):
        self._id = '',
        self._block_height = 0
        self._confirmed = False
        self._coin_inputs = []
        self._coin_outputs = []
        self._data = ''
        self._data_type = 0


    def __repr__(self):
        output = ''
        if self._confirmed:
            output = 'Transaction {} at block height {}'.format(self._id, self._block_height)
        else:
            output = 'Unconfirmed ransaction {}'.format(self._id)
        if self._coin_inputs or self._coin_outputs or self._data:
            output += ':\n'
        else:
            output += '\n'
        if self._coin_inputs:
            output += '\t- Coin Inputs:\n\t\t- '
            output += '\n\t\t- '.join([str(ci) for ci in self._coin_inputs]) + '\n'
        if self._coin_outputs:
            output += '\t- Coin Outputs:\n\t\t- '
            output += '\n\t\t- '.join([str(co) for co in self._coin_outputs]) + '\n'
        if self._data:
            output += '\t- Data ({}): {}'.format(self._data_type, self._data)
        return output


    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other.__dict__


    @classmethod
    def from_explorer_transaction(cls, explorer_transaction):
        # create a transaction summary
        ts = cls()

        rawtx = explorer_transaction.get('rawtransaction', {})
        rawtxdata = rawtx.get('data', {})
        # collect the optional data as well
        if 'arbitrarydata' in rawtxdata:
            ad = ArbitraryData()
            ad.value = base64.b64decode(rawtxdata['arbitrarydata'])
            if 'arbitrarydatatype' in rawtxdata:
                ad.type = int(rawtxdata['arbitrarydatatype'])
            ts._data = str(ad)
            ts._data_type = ad.type

        # copy the block height, (tx) id and confirmation state as-is
        ts._id = explorer_transaction.get('id', '')
        ts._block_height = explorer_transaction.get('height', 0)
        ts._confirmed = not explorer_transaction.get('unconfirmed', False)

        # first parse the raw transaction
        tx = TransactionFactory.from_dict(rawtx)
        if not tx:
            raise ValueError("invalid transaction {} cannot be decoded".format(rawtx))

        # fetch all parent identifiers from the coin inputs,
        # and pair them to the unlockhash and amount
        # collect the from_addresses as-is
        cis = rawtxdata.get('coininputs', []) or []
        cois = explorer_transaction.get('coininputoutputs', []) or []
        if len(cois) is not len(cis):
            raise ValueError("explorer transaction does not contain (all) coin input unlock hashes")
        index = 0
        for ci in cis:
            coi = cois[index]
            index += 1
            ts._coin_inputs.append(CoinInputSummary(
                ci.get('parentid', ''),
                int(coi.get('value', '0')),
                coi.get('unlockhash', ''),
                ci.get('fulfillment', {}),
            ))

        # fetch and summarize all listed coin outputs
        couhs = explorer_transaction.get('coinoutputunlockhashes', []) or []
        if len(couhs) is not len(tx.coin_outputs):
            raise ValueError("explorer transaction does not contain (all) coin output unlock hashes")
        index = 0
        for coin_output in tx.coin_outputs:
            couh = couhs[index]
            index += 1
            coin_output_dict = {}
            if coin_output:
                coin_output_dict = coin_output.json
            cos = CoinOutputSummary.from_raw_coin_output(couh, coin_output_dict)
            ts._coin_outputs.append(cos)

        # return the created transaction summary
        return ts


    @property
    def id(self):
        """
        Returns the identifier of this transaction, in
        string hex-encoded format.
        """
        return self._id

    @property
    def confirmed(self):
        """
        Returns True if this transaction was confirmed,
        meaning it was part of a registered block on the chain,
        and False otherwise.
        """
        return self._confirmed

    @property
    def coin_inputs(self):
        """
        Returns an array of identifiers,
        each identifier pointing to a coin output that was used as input
        to fund all coin outputs of this transaction.

        Can be empty in case this transaction has no coin inputs defined.
        """
        return self._coin_inputs
    
    @property
    def coin_outputs(self):
        """
        Returns an array of CoinOutputs, in summarized format.

        Can be empty in case this transaction has no coin outputs defined.
        """
        return self._coin_outputs

    @property
    def data(self):
        """
        Returns the (optional) data of this Transaction,
        only defined if there is arbitrary data attached to this Transaction.
        """
        return self._data

    @property
    def data_type(self):
        """
        The optional (arbitrary) data type that was attached to the data in this transaction.
        """
        return self._data_type


class FlatMoneyTransaction:
    """
    FlatMoneyTransaction is the representation of a partial regular chain transaction,
    with the focus on a single receiving (coin output) address. Meaning that a regular
    Transaction that defines multiple coin outputs, will result in a list of FlatMoneyTransactions.
    """
    
    @staticmethod
    def create_list(explorer_transaction):
        """
        Create a list of flat transactions,
        using the data from the given explorer transaction as input.
        """
        # check if the transaction has coin outputs,
        # if not this static method will return an empty list
        rawtxdata = explorer_transaction.get('rawtransaction', {}).get('data', {})
        cos = rawtxdata.get('coinoutputs', []) or []
        if not cos:
            return []
        couhs = explorer_transaction.get('coinoutputunlockhashes', []) or []
        if len(couhs) is not len(cos):
            raise ValueError("explorer transaction does not contain (all) coin output unlock hashes")

        # collect the optional data as well
        data = ''
        data_type = 0
        if 'arbitrarydata' in rawtxdata:
            ad = ArbitraryData()
            ad.value = base64.b64decode(rawtxdata['arbitrarydata'])
            if 'arbitrarydatatype' in rawtxdata:
                ad.type = int(rawtxdata['arbitrarydatatype'])
            data = str(ad)
            data_type = ad.type

        # copy the block height, (tx) id and confirmation state as-is
        block_height = explorer_transaction.get('height', 0)
        transaction_id = explorer_transaction.get('id', '')
        confirmed = not explorer_transaction.get('unconfirmed', False)

        # collect the from_addresses as-is
        from_addresses = set()
        for ci in explorer_transaction.get('coininputoutputs', []):
            if 'unlockhash' in ci:
                from_addresses.add(ci['unlockhash'])
        
        # collect the amounts per unlockhash
        to_addresses = {}
        coi = 0
        for co in cos:
            uh = couhs[coi]
            coi += 1
            to_addresses[uh] = to_addresses.get(uh, 0) + int(co.get('value', '0'))

        # create a flat transaction per to_address mapping
        txs = []
        for uh, amount in to_addresses.items():
            tx = FlatMoneyTransaction()
            tx._block_height = block_height
            tx._transaction_id = transaction_id
            tx._confirmed = confirmed
            tx._from_addresses = list(from_addresses)
            tx._to_address = uh
            tx._amount = amount
            tx._data = data
            tx._data_type = data_type
            txs.append(tx)

        # return a list of flat transactions
        return txs


    def __init__(self):
        self._block_height = 0
        self._transaction_id = ''
        self._confirmed = False
        self._from_addresses = []
        self._to_address = ''
        self._amount = 0
        self._data = ''
        self._data_type = 0


    def __repr__(self):
        output = ''
        if self._confirmed:
            output += str(self._block_height) + ' - '
        else:
            output += 'unconfirmed - '
        output += self._transaction_id + ' :\n\t'
        if len(self._from_addresses) > 1:
            output += ' & '.join(self._from_addresses)
        elif len(self._from_addresses) == 1:
            output += self._from_addresses[0]
        else:
            output += '?'
        output += ' -> ' + self._to_address
        output += ' : ' + str(self._amount)
        if self._data:
            output += '\n\tdata ({}): {}'.format(self._data_type, self._data)
        return output


    @property
    def block_height(self):
        """
        The height of the block this transaction was registered upon.
        Using the height one can look up the block this FlatMoneyTransaction was registered with.
        """
        return self._block_height
    
    @property
    def id(self):
        """
        The identifier of the transaction as registered on the chain.
        Using the identifier you can look up a more detailed version of the Transaction if desired.
        """
        return self._transaction_id
    
    @property
    def confirmed(self):
        """
        True if the transaction was already created as part of a block on the chain,
        False if the transaction is still waiting in the transaction pool to be registered on the chain.
        """
        return self._confirmed
    
    @property
    def from_addresses(self):
        """
        The addresses that funded the inputs used for the sent amount.
        """
        return self._from_addresses
    
    @property
    def to_address(self):
        """
        The address to which the amount of coins were sent.
        """
        return self._to_address
    
    @property
    def amount(self):
        """
        The amount of coins that were sent with this transaction.
        """
        return self._amount
    
    @property
    def data(self):
        """
        The optional (arbitrary) data that was attached with this transaction.
        """
        return self._data

    @property
    def data_type(self):
        """
        The optional (arbitrary) data type that was attached to the data in this transaction.
        """
        return self._data_type
