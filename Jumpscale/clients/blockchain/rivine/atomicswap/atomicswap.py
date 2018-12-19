"""
This module add the support of atomicswaps to the rivine light weight client
"""
import time
import hashlib
from Jumpscale import j
from JumpscaleLib.clients.blockchain.rivine import utils
from JumpscaleLib.clients.blockchain.rivine.encoding import binary
from JumpscaleLib.clients.blockchain.rivine.errors import InvalidAtomicswapContract, AtomicSwapError
from JumpscaleLib.clients.blockchain.rivine.types.unlockconditions import ATOMICSWAP_CONDITION_TYPE, UnlockCondtionFactory, AtomicSwapCondition
from JumpscaleLib.clients.blockchain.rivine.const import HASTINGS_TFT_VALUE, ATOMICSWAP_SECRET_SIZE, MINIMUM_TRANSACTION_FEE
from JumpscaleLib.clients.blockchain.rivine.types.transaction import TransactionFactory, DEFAULT_TRANSACTION_VERSION, HASHTYPE_COINOUTPUT_ID

logger = j.logger.get(__name__)

class AtomicSwapManager:
    """
    A manager class to expose high level APIs for atomicswap operations
    """

    def __init__(self, wallet):
        """
        Initializes a new AtomicSwapManager instance

        @param wallet: An instance of RivineWallet that will be used to create tansactions
        """
        self._wallet = wallet


    def _create_atomicswap_contract(self, receiver, amount, hashed_secret, duration, refund_address):
        """
        Create an atomic swap contract
        """
        contract = {
            'amount': amount
        }
        if refund_address is None:
            refund_address = self._wallet.generate_address()
        # convert amount to hastings
        actuall_amount = int(amount * HASTINGS_TFT_VALUE)
        if type(duration) == int:
            locktime = duration
        else:
            locktime = int(time.time()) + utils.locktime_from_duration(duration=duration)
        input_results, used_addresses, minerfee, remainder = self._wallet._get_inputs(amount=actuall_amount)
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)
        for input_result in input_results:
            transaction.add_coin_input(**input_result)

        if hashed_secret is None:
            # generate a secret
            secret = utils.get_secret(size=ATOMICSWAP_SECRET_SIZE)
            # hash the secret
            hashed_secret = hashlib.sha256(secret).digest().hex()
            contract['secret'] = secret.hex()
        else:
            secret = None
        contract['hashed_secret'] = hashed_secret

        ats_coin_output = transaction.add_atomicswap_output(value=actuall_amount,recipient=receiver,
                                         locktime=locktime, refund_address=refund_address,
                                         hashed_secret=hashed_secret)

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            address = self._wallet.generate_address()
            transaction.add_coin_output(value=remainder, recipient=address)

        # add minerfee to the transaction
        transaction.add_minerfee(minerfee)

        # sign the transaction
        self._wallet._sign_transaction(transaction)

        # commit transaction
        txn_id = self._wallet._commit_transaction(transaction)
        contract['transaction_id'] = txn_id

        # retrieve the info from the transaction
        ats_output_id = None
        txn_info = self._wallet._check_address(txn_id)
        coinoutputs = txn_info.get("transaction", {}).get('rawtransaction', {}).get('data', {}).get('coinoutputs', [])
        if coinoutputs:
            for index, coin_output in enumerate(coinoutputs):
                if coin_output == ats_coin_output.json:
                    ats_output_id = txn_info['transaction']['coinoutputids'][index]

        contract['output_id'] = ats_output_id

        return contract



    def participate(self, initiator_address, amount, hashed_secret, duration='24h0m0s', refund_address=None):
        """
        Create an atomic swap contract as participant

        @param initiator_address: Address of the initiator (unlockhash) to send the money to.
        @param amount: The mount of TF tokens to use for the atomicswap contract
        @oaran hashed_secret: Hash of the secret that was created during the initiate process
        @param duration: The duration of the atomic swap contract, the amount of time the initiator has to collect (default 24h0m0s)
        @param refund_address: Address to receive the funds back if transaction is not compeleted (AUTO selected from the wallet if not provided)
        """
        return self._create_atomicswap_contract(receiver=initiator_address,
                                                amount=amount,
                                                hashed_secret=hashed_secret,
                                                duration=duration,
                                                refund_address=refund_address)


    def initiate(self, participant_address, amount, duration='48h0m0s', refund_address=None):
        """
        Create an atomic swap contract as initiator

        @param participant_address: Address of the participant (unlockhash) to send the money to.
        @param amount: The mount of TF tokens to use for the atomicswap contract
        @param duration: The duration of the atomic swap contract, the amount of time the participator has to collect (default 48h0m0s)
        @param refund_address: Address to receive the funds back if transaction is not compeleted (AUTO selected from the wallet if not provided)
        """

        return self._create_atomicswap_contract(receiver=participant_address,
                                                amount=amount,
                                                hashed_secret=None,
                                                duration=duration,
                                                refund_address=refund_address)


    def validate(self, transaction_id, amount=None, hashed_secret=None, receiver_address=None, time_left=None):
        """
        Validates that the given output id exist in the consensus as an unspent output

        @param transaction_id: Transaction id from from initiate or participate contract to validate
        @param amount: Amount to validaate against the output information
        @param hashed_secret: Validate the secret of the found atomic swap contract condition by comparing its hashed version with this secret hash
        @param receiver_address: Validate the given receiver's address (unlockhash) to the one found in the atomic swap contract condition
        @param time_left: Minimum time left for the contract, if the contract locktime is expired in less than this value the contract will be considered invalid
        """
        return self._validate(transaction_id=transaction_id,
                             amount=amount,
                             hashed_secret=hashed_secret,
                             receiver_address=receiver_address,
                             time_left=time_left)[0]


    def _validate(self, transaction_id, amount=None, hashed_secret=None, receiver_address=None, time_left=None):
        """
        An internal function that does all the validation the public validate method does, but return more info
        """
        output_id, output_result = self._get_output_info_from_id(transaction_id=transaction_id)
        if output_result:
            if amount and int(output_result['value']) != amount * HASTINGS_TFT_VALUE:
                raise InvalidAtomicswapContract("Contract amount does not match the provided amount value")
            if output_result['condition']['type'] != binary.decode(ATOMICSWAP_CONDITION_TYPE, type_=int):
                raise InvalidAtomicswapContract("Condition type is not correct")
            if receiver_address and output_result['condition']['data']['receiver'] != receiver_address:
                raise InvalidAtomicswapContract("Receiver address does not match the provided address")
            if hashed_secret and output_result['condition']['data']['hashedsecret'] != hashed_secret:
                raise InvalidAtomicswapContract("Hashed secret does not match the provided hashed secret")
            if time_left and abs(output_result['condition']['data']['timelock'] - time.time()) < time_left:
                raise InvalidAtomicswapContract("Contract will expired in less than the minimum time specified")
        else:
            raise InvalidAtomicswapContract("Could not validate atomicswap contract for transaction {}".format(transaction_id))
        return True, output_result, output_id


    def _get_output_info_from_id(self, transaction_id):
        """
        Retrieves information about an atomicswap output from a given id
        """

        txn_info = self._wallet._check_address(transaction_id)['transaction']
        for idx, coin_output in enumerate(txn_info['rawtransaction']['data']['coinoutputs']):
            condition = UnlockCondtionFactory.from_dict(coin_output['condition'])
            if isinstance(condition, AtomicSwapCondition):
                return txn_info['coinoutputids'][idx], coin_output

        return None, None


    def _spend_atomicswap_contract(self, transaction_id, secret=None):
        """
        Spends an atomicswap contract
        Can be used by both refund and redeem operations
        """
        _, output_info, output_id = self._validate(transaction_id=transaction_id)
        if secret is None:
            # spending the output as refund
            # fetch the sender address from the output_info
            address = output_info['condition']['data']['sender']
        else:
            # spend the output as redeem
            address = output_info['condition']['data']['receiver']
        if address not in self._wallet._keys:
            raise AtomicSwapError('Address found in the output does not belong to the current wallet')
        key = self._wallet._keys[address]
        value = int(output_info['value'])
        if value <= MINIMUM_TRANSACTION_FEE:
            raise AtomicSwapError("Value of the atomicswap contract is less than or equal to the minimum transaction fee.")
        # create a new transaction
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)
        transaction.add_atomicswap_input(parent_id=output_id, pub_key=key.public_key,
                                        secret=secret)
        txn_value = value - MINIMUM_TRANSACTION_FEE
        transaction.add_coin_output(value=txn_value, recipient=address)
        transaction.add_minerfee(minerfee=MINIMUM_TRANSACTION_FEE)

        # sign the transaction input
        input_idx = 0
        transaction.coin_inputs[input_idx].sign(input_idx=input_idx,
                                                 transaction=transaction,
                                                 secret_key=key.secret_key
                                                 )

        # commit transaction
        txn_id = self._wallet._commit_transaction(transaction)
        return txn_id



    def refund(self, transaction_id):
        """
        Spends an atomicswap contract

        @param transaction_id: Transaction id from the atomicswap contract
        """
        txn_id = self._spend_atomicswap_contract(transaction_id=transaction_id)
        logger.info("Refund executed successfully. Transaction ID: {}".format(txn_id))
        return txn_id



    def redeem(self, transaction_id, secret):
        """
        Complete the atomicswap contract by spending a the output as the receiver of the atomicswap

        @param transaction_id: Transaction ID of the transaction to redeemed
        @param secret: Atomicswap secert
        """
        txn_id = self._spend_atomicswap_contract(transaction_id=transaction_id, secret=secret)
        logger.info("Redeem executed successfully. Transaction ID: {}".format(txn_id))
        return txn_id
