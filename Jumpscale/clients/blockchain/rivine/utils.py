"""
Modules for common utilites
"""
import re
import time
import string
import json
import requests
from random import choice
from pyblake2 import blake2b
from requests.auth import HTTPBasicAuth

from Jumpscale import j
from clients.blockchain.rivine import secrets
from clients.blockchain.rivine.encoding import binary
from clients.blockchain.rivine.errors import RESTAPIError, BackendError
from clients.blockchain.rivine.const import \
    HASH_SIZE, MINER_PAYOUT_MATURITY_WINDOW, TIMELOCK_CONDITION_HEIGHT_LIMIT, NIL_UNLOCK_HASH

DURATION_REGX_PATTERN = '^(?P<hours>\d*)h(?P<minutes>\d*)m(?P<seconds>\d*)s$'
DURATION_TEMPLATE = 'XXhXXmXXs'

logger = j.logger.get(__name__)

def hash(data, encoding_type=None):
    """
    Hashes the input binary data using the blake2b algorithm

    @param data: Input data to be hashed
    @param encoding_type: Type of the data to guide the binary encoding before hashing
    @returns: Hashed value of the input data
    """
    binary_data = binary.encode(data, type_=encoding_type)
    return blake2b(binary_data, digest_size=HASH_SIZE).digest()


def locktime_from_duration(duration):
    """
    Parses a duration string and return a locktime timestamp

    @param duration: A string represent a duration if the format of XXhXXmXXs and return a timestamp
    @returns: number of seconds represented by the duration string
    """
    if not duration:
        raise ValueError("Duration needs to be in the format {}".format(DURATION_TEMPLATE))
    match = re.search(DURATION_REGX_PATTERN, duration)
    if not match:
        raise ValueError("Duration needs to be in the format {}".format(DURATION_TEMPLATE))
    values = match.groupdict()
    result = 0
    if values['hours']:
        result += int(values['hours']) * 60 * 60
    if values['minutes']:
        result += int(values['minutes']) * 60
    if values['seconds']:
        result += int(values['seconds'])

    return int(result)


def get_secret(size):
    """
    Generate a random secert token

    @param size: The size of the secret token
    """
    # alphapet = string.ascii_letters + string.digits
    # result = []
    # for _ in range(size):
    #     result.append(choice(alphapet))
    # return ''.join(result)
    return secrets.token_bytes(nbytes=size)


def get_current_chain_height(rivine_explorer_addresses):
    """
    Retrieves the current chain height

    @param rivine_explorer_addresses: List of explorer nodes addresses to connect to.
    """
    msg = 'Failed to get current chain height.'
    result = None
    response = None
    for rivine_explorer_address in rivine_explorer_addresses:
        url = '{}/explorer'.format(rivine_explorer_address.strip('/'))
        headers = {'user-agent': 'Rivine-Agent'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.ConnectionError as ex:
            logger.warn(msg)
            continue
        if response.status_code != 200:
            logger.warn('{} {}'.format(msg, response.text))
        else:
            result = response.json().get('height', None)
            break

    if result is not None:
        result = int(result)
    else:
        if response:
            raise RESTAPIError('{} {}'.format(msg, response.text))
        else:
            raise RESTAPIError(msg)
    return result


def check_address(rivine_explorer_addresses, address, min_height=0, log_errors=True):
    """
    Check if an address is valid and return its details

    @param rivine_explorer_addresses: List of explorer nodes addresses to connect to.
    @param address: Address to check
    @param log_errors: If False, no logging will be executed

    @raises: @RESTAPIError if failed to check address
    """
    msg = 'Failed to retrieve address information.'
    result = None
    response = None
    min_height = max(0, int(min_height))
    for rivine_explorer_address in rivine_explorer_addresses:
        url = '{}/explorer/hashes/{}?minheight={}'.format(rivine_explorer_address.strip('/'), address, min_height)
        headers = {'user-agent': 'Rivine-Agent'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.ConnectionError as ex:
            if log_errors:
                logger.warn(msg)
            continue
        if response.status_code != 200:
            if log_errors:
                logger.warn('{} {}'.format(msg, response.text.strip('\n')))
        else:
            result = response.json()
            break

    if result is None:
        if response:
            raise RESTAPIError('{} {}'.format(msg, response.text.strip('\n')))
        else:
            raise RESTAPIError(msg)
    return result


def get_unconfirmed_transactions(rivine_explorer_addresses, format_inputs=False):
    """
    Retrieves the unconfirmed transaction from a remote node that runs the Transaction pool module

    @param rivine_explorer_addresses: List of explorer nodes addresses to connect to.
    @param format_inputs: If True, the output will be formated to get a list of the inputs parent ids

    # example output
            {'transactions': [{'version': 1,
       'data': {'coininputs': [{'parentid': '7616c88f452d6b22a3683bcbdfdf6ee3c32b63a810a8ac0d46a7403a33d4c06f',
          'fulfillment': {'type': 1,
           'data': {'publickey': 'ed25519:9413b12a6158f52fad6c39cc164054a9e7fbe5378892311f498eae56f80c068a',
            'signature': '34cee9bbc380deba2f52ccb20c2a47d4f6001fe66cfe7079d6b71367ea14544e89e69657201d0cc7b7b901324e64a7f4dce6ac6177536726cee576a0b74a8700'}}}],
        'coinoutputs': [{'value': '2000000000',
          'condition': {'type': 1,
           'data': {'unlockhash': '0112a7c1813746c5f6d5d496441d7a6a226984a3cc318021ee82b5695e4470f160c6ca61f66df2'}}},
         {'value': '3600000000',
          'condition': {'type': 1,
           'data': {'unlockhash': '012bdb563a4b3b630ddf32f1fde8d97466376a67c0bc9a278c2fa8c8bd760d4dcb4b9564cdea6f'}}}],
        'minerfees': ['100000000']}}]}
    """
    msg = 'Failed to retrieve unconfirmed transactions.'
    result = []
    response = None
    for rivine_explorer_address in rivine_explorer_addresses:
        url = "{}/transactionpool/transactions".format(rivine_explorer_address.strip('/'))
        headers = {'user-agent': 'Rivine-Agent'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.ConnectionError as ex:
            logger.warn(msg)
            continue
        if response.status_code != 200:
            logger.warn('{} {}'.format(msg, response.text))
        else:
            transactions = response.json().get('transactions', None)
            if transactions is None:
                transactions = []
            if format_inputs:
                for txn in transactions:
                    result.extend([coininput['parentid'] for coininput in txn['data']['coininputs']])
            else:
                result = transactions
            return result

    if response:
        raise RESTAPIError('{} {}'.format(msg, response.text))
    else:
        raise RESTAPIError(msg)


def get_current_minter_definition(rivine_explorer_addresses, explorer_password):
    """
    Retrieve the current minter definition from the chain
    """
    msg = 'Failed to retrieve current mint condition'
    response = None
    mint_condition = None
    for rivine_explorer_address in rivine_explorer_addresses:
        url = '{}/explorer/mintcondition'.format(rivine_explorer_address.strip('/'))
        headers = {'user-agent': 'Rivine-Agent'}
        auth = HTTPBasicAuth('', explorer_password)
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except request.exceptions.ConnectionError as ex:
            logger.warn(msg)
            continue
        if response.status_code != 200:
            logger.warn('{} {}'.format(msg, response.text))
        else:
            mint_condition = response.json()['mintcondition']
            break
    return mint_condition



def commit_transaction(rivine_explorer_addresses, rivine_explorer_api_password, transaction):
    """
    Commits a singed transaction to the chain

    @param rivine_explorer_addresses: List of explorer nodes addresses to connect to.
    @param transaction: Transaction object to be committed
    """
    data = transaction.json
    res = None
    msg = 'Failed to commit transaction to chain network.'
    for rivine_explorer_address in rivine_explorer_addresses:
        url = '{}/transactionpool/transactions'.format(rivine_explorer_address.strip('/'))
        headers = {'user-agent': 'Rivine-Agent'}
        auth = HTTPBasicAuth('', rivine_explorer_api_password)
        try:
            res = requests.post(url, headers=headers, auth=auth, json=data, timeout=30)
        except requests.exceptions.ConnectionError as ex:
            logger.warn(msg)
            logger.debug('error with tx: {}'.format(str(data)))
            continue
        if res.status_code != 200:
            msg = 'Failed to commit transaction to chain network.{}'.format(res.text)
            logger.warn('{} {}'.format(msg, res.text))
            logger.debug('error with tx: {}'.format(str(data)))
        else:
            transaction.id = res.json()['transactionid']
            logger.info('Transaction committed successfully')
            return transaction.id
    if res:
        raise BackendError('{} {}'.format(msg, res.text))
    else:
        raise BackendError(msg)


def remove_spent_inputs(unspent_coin_outputs, transactions):
    """
    Remvoes the already spent outputs

    @param transactions: Details about the transactions
    """
    for txn_info in transactions:
        # cointinputs can exist in the dict but have the value None
        coininputs = txn_info.get('rawtransaction', {}).get('data', {}).get('coininputs', [])
        for coin_input in coininputs:
            parentid = coin_input.get('parentid')
            if parentid in unspent_coin_outputs:
                logger.debug('Found a spent address {}'.format(parentid))
                del unspent_coin_outputs[parentid]


def find_subset_sum(values, target):
    """
    Find a subset of the values that sums to the target number
    This implements a dynamic programming approach to the subset sum problem
    Implementation is taken from: https://github.com/saltycrane/subset-sum/blob/master/subsetsum/stackoverflow.py

    @param values: List of integers
    @param target: The sum that we need to find a subset to equal to it.
    """
    def g(v, w, S, memo):
        subset = []
        id_subset = []
        for i, (x, y) in enumerate(zip(v, w)):
            # Check if there is still a solution if we include v[i]
            if f(v, i + 1, S - x, memo) > 0:
                subset.append(x)
                id_subset.append(y)
                S -= x
        return subset, id_subset


    def f(v, i, S, memo):
        if i >= len(v):
            return 1 if S == 0 else 0
        if (i, S) not in memo:    # <-- Check if value has not been calculated.
            count = f(v, i + 1, S, memo)
            count += f(v, i + 1, S - v[i], memo)
            memo[(i, S)] = count  # <-- Memoize calculated result.
        return memo[(i, S)]       # <-- Return memoized value.

    memo = dict()
    result, _ = g(values, values, target, memo)
    return result
