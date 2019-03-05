import nacl
from Jumpscale import j

from . import schemas


class TFChainCapacity():
    """
    TFChainReservation contains all TF grid reservation logic.
    """

    def __init__(self, wallet):
        self._wallet = wallet
        self._notary_client_ = None
        self._grid_broker_pub_key_ = None
        self._grid_broker_addr = ''  # TODO: hardcode tfchain address of the grid broker
        # this all key management needs to be improved
        keypair = self._wallet.key_pair_get(self._wallet.address)
        self._signing_key = nacl.signing.SigningKey(keypair.private_key.to_seed())
        self._private_key = self._signing_key.to_curve25519_private_key()

    @property
    def _notary_client(self):
        if self._notary_client_ is None:
            c = j.clients.gedis.configure('tfnotary', host='notary.grid.tf', port=6830)
            self._notary_client_ = c.cmds.notary_actor
        return self._notary_client_

    @property
    def _grid_broker_pub_key(self):
        if self._grid_broker_pub_key_ is None:
            record = self._wallet.client.threebot.record_get('tf3bot.zaibon')
            encoded_key = record.public_key.hash
            vk = nacl.signing.VerifyKey(
                str(encoded_key),
                encoder=nacl.encoding.HexEncoder)
            self._grid_broker_pub_key_ = vk.to_curve25519_public_key()
        return self._grid_broker_pub_key_

    def reserve_s3(self, size, email, threebot_id, duration=None):
        reservation = j.data.schema.get(url='tfchain.reservation.s3').new(data={
            'size': size,
            'email': email,
            'created': j.data.time.epoch
        })
        return self._process_reservation(reservation, threebot_id)

    def reserve_zos_vm(self, size, email, threebot_id, duration=None):
        reservation = j.data.schema.get(url='tfchain.reservation.zos_vm').new(data={
            'size': size,
            'email': email,
            'created': j.data.time.epoch
        })
        return self._process_reservation(reservation, threebot_id)

    def _process_reservation(self, reservation, threebot_id):
        _validate_reservation(reservation)

        # validate bot id exists
        self._wallet.client.threebot.record_get(threebot_id)

        # get binary representation
        b = encode_reservation(reservation)

        # TODO: this api does not yet exists
        # encrypted = j.data.nacl.encrypt(blob, self.grid_broker_pub_key)
        # I'm doing it manually here for now, will have to update this once nacl module be proper API
        box = nacl.public.Box(self._private_key, self._grid_broker_pub_key)
        encrypted = box.encrypt(b)
        signature = self._signing_key.sign(encrypted, nacl.encoding.RawEncoder)
        key = self._notary_client.register(threebot_id, encrypted, signature)
        tx = self._wallet.coins_send(self._grid_broker_addr, reservation_amount(reservation), data=key)
        return tx.id


def _validate_reservation(reservation):
    for field in ['size', 'email']:
        if not getattr(reservation, field):
            raise ValueError("field '%s' cannot be empty" % field)

    if reservation.size < 0 or reservation.size > 2:
        raise ValueError('reservation size can only be 1 or 2')


def encode_reservation(reservation):
    return reservation._msgpack


def reservation_amount(reservation):
    amounts = {
        's3': {
            1: 10,
            2: 40,
        },
        'vm': {
            1: 1,
            2: 4,
        }
    }
    return amounts[reservation.type][reservation.size]
