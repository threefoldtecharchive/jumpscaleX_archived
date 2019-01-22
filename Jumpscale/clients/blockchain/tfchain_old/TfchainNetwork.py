"""
Tfchain Network
"""

from enum import Enum, auto

"""
standard and testnet are official tfchain networks,
use devnet for everything else
"""
class TfchainNetwork(str, Enum):
    STANDARD = 'standard'
    TESTNET = 'testnet'
    DEVNET = 'devnet'

    """
    returns the official explorers for the networks that have them
    """
    def official_explorers(self):
        if self is TfchainNetwork.STANDARD:
            return [
                'https://explorer.threefoldtoken.com',
                'https://explorer2.threefoldtoken.com',
                'https://explorer3.threefoldtoken.com',
                'https://explorer4.threefoldtoken.com',
            ]
        if self is TfchainNetwork.TESTNET:
            return [
                'https://explorer.testnet.threefoldtoken.com',
                'https://explorer2.testnet.threefoldtoken.com',
            ]
        return []
    
