from Jumpscale import j

import re
import requests

from clients.blockchain.tfchain.TfchainNetwork import TfchainNetwork
from clients.blockchain.tfchain.errors import NoExplorerNetworkAddresses
from clients.blockchain.tfchain.types import signatures as tftsig
from clients.blockchain.tfchain.types import threebot as tftbot
from clients.blockchain.rivine.errors import RESTAPIError
from clients.blockchain.rivine.types import transaction
from clients.blockchain.rivine import RivineWallet

class TfchainThreeBotClient():
    """
    Client used to get, create and update records.
    This client provides all you need in order to use the Threebot support in TFChain.
    """

    __bot_name_pattern = re.compile(r"^[A-Za-z]{1}[A-Za-z\-0-9]{3,61}[A-Za-z0-9]{1}(\.[A-Za-z]{1}[A-Za-z\-0-9]{3,55}[A-Za-z0-9]{1})*$")
    
    @staticmethod
    def get_record(identifier, network=TfchainNetwork.STANDARD, explorers=None):
        """
        Get a 3Bot record registered on a TFchain network

        @param identifier: unique 3Bot id, public key or name to search a 3Bot record for, in string format
        @param network: optional network, STANDARD by default, TESTNET is another valid choice, for DEVNET use the network_addresses param instead
        @param explorers: explorer network addresses from which to get the 3bot record (only required for DEVNET, optional for other networks)
        """
        if not explorers:
            explorers = network.official_explorers()
            if not explorers:
                raise NoExplorerNetworkAddresses("network {} has no official explorer networks and none were specified by callee".format(network.name.lower()))

        msg = 'Failed to retrieve 3Bot record.'
        result = None
        response = None
        endpoint = "explorer/3bot"
        if isinstance(identifier, str) and TfchainThreeBotClient.__bot_name_pattern.match(identifier):
            endpoint = "explorer/whois/3bot"
        for address in explorers:
            url = '{}/{}/{}'.format(address.strip('/'), endpoint, identifier)
            headers = {'user-agent': 'Rivine-Agent'}
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                continue
            if response.status_code == 200:
                result = response.json()
                break

        if result is None:
            if response:
                raise RESTAPIError('{} {}'.format(msg, response.text.strip('\n')))
            else:
                raise RESTAPIError('error while fetching 3bot record from {} for {}: {}'.format(explorers, identifier, msg))
        return tftbot.ThreeBotRecord.from_dict(result.get('record', {}))
    
    # TODO: it might be useful to also allow the usage of spendable keys not related to the given wallet, currently this is not Possible

    @staticmethod
    def create_record(wallet, months=1, names=None, addresses=None, public_key=None):
        # create the tx and fill the easiest properties already
        tx = transaction.TransactionV144()
        tx.set_number_of_months(months)

        # add names and/or addresses
        if names:
            for name in names:
                tx.add_name(name)
        if addresses:
            for addr in addresses:
                tx.add_address(addr)

        # add coin inputs for miner fees (implicitly computed) and required bot fees
        input_results, used_addresses, minerfee, remainder = wallet._get_inputs(amount=tx.required_bot_fees)
        tx.set_transaction_fee(minerfee)
        for input_result in input_results:
            tx.add_coin_input(**input_result)
        for txn_input in tx.coin_inputs:
            if used_addresses[txn_input.parent_id] not in wallet._keys:
                raise RivineWallet.NonExistingOutputError('Trying to spend unexisting output')
        # optionally add the remainder as a refund coin output
        if remainder > 0:
            # TODO: are we sure refunding to first address is always desired?
            tx.set_refund_coin_output(value=remainder, recipient=wallet.addresses[0])

        # set the public key (used to sign using the wallet)
        if not public_key:
            key = wallet.generate_key()
            public_key = key.public_key
        pk = tftsig.SiaPublicKey(tftsig.SiaPublicKeySpecifier.ED25519, public_key)
        tx.identification.public_key = pk

        # sign and commit the Tx, return the tx ID afterwards
        wallet.sign_transaction(transaction=tx, commit=True)
        return tx
    
    @staticmethod
    def update_record(wallet, identifier, months=0, names_to_add=None, names_to_remove=None, addresses_to_add=None, addresses_to_remove=None):
        # create the tx and fill user-defined properties in
        tx = transaction.TransactionV145()
        tx.set_bot_id(identifier)
        tx.set_number_of_months(months)
        if names_to_add:
            for name in names_to_add:
                tx.add_name_to_add(name)
        if names_to_remove:
            for name in names_to_remove:
                tx.add_name_to_remove(name)
        if addresses_to_add:
            for addr in addresses_to_add:
                tx.add_address_to_add(addr)
        if addresses_to_remove:
            for addr in addresses_to_remove:
                tx.add_address_to_remove(addr)
        
        # add coin inputs for miner fees (implicitly computed) and required bot fees
        input_results, used_addresses, minerfee, remainder = wallet._get_inputs(amount=tx.required_bot_fees)
        tx.set_transaction_fee(minerfee)
        for input_result in input_results:
            tx.add_coin_input(**input_result)
        for txn_input in tx.coin_inputs:
            if used_addresses[txn_input.parent_id] not in wallet._keys:
                raise RivineWallet.NonExistingOutputError('Trying to spend unexisting output')
        # optionally add the remainder as a refund coin output
        if remainder > 0:
            # TODO: are we sure refunding to first address is always desired?
            tx.set_refund_coin_output(value=remainder, recipient=wallet.addresses[0])
        
        # sign and commit the Tx, return the tx ID afterwards
        wallet.sign_transaction(transaction=tx, commit=True)
        return tx

    @staticmethod
    def create_name_transfer(wallet, sender_identifier, receiver_identifier, names):
        # create the tx and fill user-defined properties in
        tx = transaction.TransactionV146()
        tx.set_sender_bot_id(sender_identifier)
        tx.set_receiver_bot_id(receiver_identifier)
        for name in names:
            tx.add_name(name)

        # add coin inputs for miner fees (implicitly computed) and required bot fees
        input_results, used_addresses, minerfee, remainder = wallet._get_inputs(amount=tx.required_bot_fees)
        tx.set_transaction_fee(minerfee)
        for input_result in input_results:
            tx.add_coin_input(**input_result)
        for txn_input in tx.coin_inputs:
            if used_addresses[txn_input.parent_id] not in wallet._keys:
                raise RivineWallet.NonExistingOutputError('Trying to spend unexisting output')
        # optionally add the remainder as a refund coin output
        if remainder > 0:
            # TODO: are we sure refunding to first address is always desired?
            tx.set_refund_coin_output(value=remainder, recipient=wallet.addresses[0])

        # sign and commit the Tx, return the tx ID afterwards
        wallet.sign_transaction(transaction=tx, commit=True)
        return tx
