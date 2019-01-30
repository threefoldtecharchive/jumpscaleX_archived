"""
Define Exceptions

PUT ALL ERRORS IN THIS ONE FILE
"""

class InvalidPublicKeySpecifier(Exception):
    """
    InvalidPublicKeySpecifier error
    """

class UnknownTransansactionVersion(Exception):
    """
    UnknownTransansactionVersion error
    """

class ExplorerNoContent(Exception):
    """
    ExplorerNoContent error
    """

class InsufficientFunds(Exception):
    """
    InsufficientFunds error
    """
