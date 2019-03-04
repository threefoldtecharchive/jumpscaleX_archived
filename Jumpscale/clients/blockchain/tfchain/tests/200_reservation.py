import pytest
from unittest.mock import MagicMock
import nacl
from Jumpscale import j


def patch_reservation(tfchain_reserv):
    tfchain_reserv._notary_client = MagicMock()
    pk = nacl.public.PrivateKey.generate()
    tfchain_reserv._grid_broker_pub_key = pk.public_key
    tfchain_reserv._wallet.coin_send = MagicMock()


@pytest.fixture
def reservation():
    # create a tfchain client for devnet
    c = j.clients.tfchain.new("mydevclient", network_type="DEV")
    w = c.wallets.mywallet  # is the implicit form of `c.wallets.new("mywallet")`
    reservation = w.reservation
    patch_reservation(reservation)
    return reservation


def test_validate_reservation(reservation):
    r = reservation.new()

    with pytest.raises(ValueError):
        reservation._validate_reservation(r)

    r.bot_id = "1"
    r.size = 1
    r.duration = 20
    r.email = 'user@mail.com'

    reservation._validate_reservation(r)


def test_send_reservation(reservation):
    r = reservation.new()
    r.bot_id = "1"
    r.size = 1
    r.duration = 20
    r.email = 'user@mail.com'

    h = reservation.send(r)

    reservation._wallet.coin_send.assert_called()
    reservation._notary_client.register.assert_called()
