"""
TODO: remove/deprecate this file ASAP
      it is copied from utils.py and put here to avoid cyclic dependencies,
      but really, this can be cleaner and simpler
"""

import time
import json
from Jumpscale import j
from clients.blockchain.rivine.types.transaction import TransactionFactory
from clients.blockchain.rivine.const import \
    MINER_PAYOUT_MATURITY_WINDOW, TIMELOCK_CONDITION_HEIGHT_LIMIT, NIL_UNLOCK_HASH

logger = j.logger.get(__name__)

# TODO: simplify this function a lot or eliminate it,
#       the logic chain in this function is really convoluted...
def get_unlockhash_from_output(output, address, current_height):
    """
    Retrieves unlockhash from coin output. This should handle different types of output conditions and transaction formats

    @param current_height: The current chain height
    """
    result = {
        'locked': [],
        'unlocked': []
    }
    # support both v0 and v1 tnx format
    if 'unlockhash' in output:
        # v0 transaction format
        result['unlocked'].append(output['unlockhash'])
    elif 'condition' in output:
        # v1 transaction format
        # check condition type
        if not output['condition']:
            result['unlocked'].append(NIL_UNLOCK_HASH)
        elif output['condition'].get('type') == 1:
            # unlockhash condition type
            result['unlocked'].append(output['condition']['data']['unlockhash'])
        elif output['condition'].get('type') == 3:
            # timelock condition, right now we only support timelock condition with internal unlockhash condition, and multisig condition
            locktime = output['condition']['data']['locktime']
            if locktime < TIMELOCK_CONDITION_HEIGHT_LIMIT:
                if not output['condition']['data']['condition']:
                    if current_height > locktime:
                        result['unlocked'].append(NIL_UNLOCK_HASH)
                    else:
                        result['locked'].append(NIL_UNLOCK_HASH)
                elif output['condition']['data']['condition']['type'] == 1:
                    # locktime should be checked against the current chain height
                    if current_height > locktime:
                        result['unlocked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                elif output['condition']['data']['condition']['type'] == 4:
                    # locktime should be checked against the current chain height
                    if current_height > locktime:
                        result['unlocked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))
            else:
                # locktime represent timestamp
                current_time = time.time()
                if not output['condition']['data']['condition']:
                    if current_time > locktime:
                        result['unlocked'].append(NIL_UNLOCK_HASH)
                    else:
                        result['locked'].append(NIL_UNLOCK_HASH)
                elif output['condition']['data']['condition']['type'] == 1:
                    # locktime should be checked against the current time
                    if current_time > locktime:
                        result['unlocked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].append(output['condition']['data']['condition']['data'].get('unlockhash'))
                elif output['condition']['data']['condition']['type'] == 4:
                    # locktime should be checked against the current time
                    if current_time > locktime:
                        result['unlocked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))
                    else:
                        logger.warn("Found transaction output for address {} but it cannot be unlocked yet".format(address))
                        result['locked'].extend(output['condition']['data']['condition']['data'].get('unlockhashes'))
        elif output['condition'].get('type') == 4:
            result['unlocked'].extend(output['condition']['data']['unlockhashes'])

    return result


def collect_miner_fees(address, blocks, height):
    """
    Scan the bocks for miner fees and Collects the miner fees But only that have matured already

    @param address: address to collect miner fees for
    @param blocks: Blocks from an address
    @param height: The current chain height
    """
    result = {}
    if blocks is None:
        blocks = {}
    for block_info in blocks:
        if block_info.get('height', None) and block_info['height'] + MINER_PAYOUT_MATURITY_WINDOW >= height:
            logger.info('Ignoring miner payout that has not matured yet')
            continue
        # mineroutputs can exist in the dictionary but with value None
        mineroutputs = block_info.get('rawblock', {}).get('minerpayouts', [])
        if mineroutputs:
            for index, minerpayout in enumerate(mineroutputs):
                if minerpayout.get('unlockhash') == address:
                    logger.info('Found miner output with value {}'.format(minerpayout.get('value')))
                    result[block_info['minerpayoutids'][index]] = {
                        'value': minerpayout['value'],
                        'condition':{
                            'data': {
                                'unlockhash': address
                            }
                        }
                    }
    return result


def collect_transaction_outputs(current_height, address, transactions, unconfirmed_txs=None):
    """
    Collects transactions outputs

    @param current_height: The current chain height
    @param address: address to collect transactions outputs
    @param transactions: Details about the transactions
    @param unconfirmed_txs: List of unconfirmed transactions
    """
    result = {
        'locked': {},
        'unlocked': {},
        'multisig_unlocked': {},
        'multisig_locked': {},
        'unconfirmed_locked': {},
        'unconfirmed_unlocked': {},
        'unconfirmed_multisig_unlocked': {},
        'unconfirmed_multisig_locked': {}
    }
    if unconfirmed_txs is None:
        unconfirmed_txs = []
    for txn_info in transactions:
        rawtxn = txn_info.get('rawtransaction', {})
        version = rawtxn.get('version', 1)
        coinoutputs = []
        unlockhashes = txn_info.get('coinoutputunlockhashes', [])
        if version >= 144 and version <= 146: # TODO: Remove HACK as it is only here until we fixed 3Bot transactions!!
            txn = TransactionFactory.from_json(json.dumps(rawtxn))
            payout_output = {
                'value': txn.required_bot_fees,
                'unlockhash': unlockhashes[0] # TODO: remove this dirty HACK, for now it will work as it mimics v0 Txn outputs
            }
            # 3Bot fee payout is not supported for now,
            # only the refund output
            coinoutputs = [payout_output]
            refundco = rawtxn.get('data', {}).get('refundcoinoutput', None)
            if refundco:
                coinoutputs.append(refundco)
        else:
            coinoutputs = rawtxn.get('data', {}).get('coinoutputs', [])
        if coinoutputs:
            for index, utxo in enumerate(coinoutputs):
                condition_ulh = get_unlockhash_from_output(output=utxo, address=address, current_height=current_height)

                if address in condition_ulh['locked'] or address in condition_ulh['unlocked']:
                    logger.debug('Found transaction output for address {}'.format(address))
                    if txn_info['coinoutputids'][index] in unconfirmed_txs:
                        logger.warn("Transaction output is part of an unconfirmed tansaction. Ignoring it...")
                        continue
                    if address in condition_ulh['locked']:
                        result['locked'][txn_info['coinoutputids'][index]] = utxo
                    else:
                        result['unlocked'][txn_info['coinoutputids'][index]] = utxo
        if not address.startswith('03'):
            # Next part collects multisig outputs, lets ignore that if we don't
            # have a multisig address
            continue
        if unlockhashes:
            for idx, uh in enumerate(unlockhashes):
                if uh == address:
                    output = coinoutputs[idx]
                    condition_ulh = get_unlockhash_from_output(output=output,
                                                                address=address,
                                                                current_height=current_height)
                    if condition_ulh['unlocked']:
                        result['multisig_unlocked'][txn_info['coinoutputids'][idx]] = output
                    if condition_ulh['locked']:
                        result['multisig_locked'][txn_info['coinoutputids'][idx]] = output
    # Add unconfirmed outputs
    for txn_info in unconfirmed_txs:
        rawtxn = txn_info.get('rawtransaction', {})
        version = rawtxn.get('version', 1)
        coinoutputs = []
        unlockhashes = txn_info.get('coinoutputunlockhashes', [])
        if version >= 144 and version <= 146: # TODO: Remove HACK as it is only here until we fixed 3Bot transactions!!
            txn = TransactionFactory.from_json(json.dumps(rawtxn))
            payout_output = {
                'value': txn.required_bot_fees,
                'unlockhash': unlockhashes[0] # TODO: remove this dirty HACK, for now it will work as it mimics v0 Txn outputs
            }
            # 3Bot fee payout is not supported for now,
            # only the refund output
            coinoutputs = [payout_output]
            refundco = rawtxn.get('data', {}).get('refundcoinoutput', None)
            if refundco:
                coinoutputs.append(refundco)
        else:
            coinoutputs = rawtxn.get('data', {}).get('coinoutputs', [])
        if coinoutputs:
            for index, utxo in enumerate(coinoutputs):
                condition_ulh = get_unlockhash_from_output(output=utxo, address=address, current_height=current_height)
                if address in condition_ulh['locked'] or address in condition_ulh['unlocked']:
                    if address in condition_ulh['locked']:
                        result['unconfirmed_locked'][txn_info['coinoutputids'][index]] = utxo
                    else:
                        result['unconfirmed_unlocked'][txn_info['coinoutputids'][index]] = utxo
        if not address.startswith('03'):
            # Next part collects multisig outputs, lets ignore that if we don't
            # have a multisig address
            continue
        if unlockhashes:
            for idx, uh in enumerate(unlockhashes):
                if uh == address:
                    output = coinoutputs[idx]
                    condition_ulh = get_unlockhash_from_output(output=output,
                                                                address=address,
                                                                current_height=current_height)
                    if condition_ulh['unlocked']:
                        result['unconfirmed_multisig_unlocked'][txn_info['coinoutputids'][idx]] = output
                    if condition_ulh['locked']:
                        result['unconfirmed_multisig_locked'][txn_info['coinoutputids'][idx]] = output

    return result