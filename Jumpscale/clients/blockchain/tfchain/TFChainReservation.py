from Jumpscale import j
import nacl

_RESERVATION_SCHEMA = j.data.schema.get("""
@url = tfchain.reservation
type = "S3,VM" (E)
duration = (I)
size = (I)
email = (email)
bot_id = (S)
created = (I)
""")

_GRID_BROKER_PUB_KEY = "..."


class TFChainReservation():
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
            self._notary_client_ = j.clients.gedis.configure('tfnotary', host='notary.grid.tf', port=8888)
        return self._notary_client_

    @property
    def _grid_broker_pub_key(self):
        if self._grid_broker_pub_key_ is None:
            record = self._wallet.client.threebot.record_get('tf3bot.zaibon')
            encoded_key = record.public_key.unlockhash
            self._grid_broker_pub_key_ = nacl.public.PublicKey(
                str(encoded_key.hash),
                encoder=nacl.encoding.HexEncoder)
        return self._grid_broker_pub_key_

    def new(self):
        return _RESERVATION_SCHEMA.new()

    def send(self, reservation):
        reservation.created = j.data.time.epoch

        self._validate_reservation(reservation)
        # get binary representation
        b = encode_reservation(reservation)

        # TODO: this api does not yet exists
        # encrypted = j.data.nacl.encrypt(blob, self.grid_broker_pub_key)
        # I'm doing it manually here for now, will have to update this once nacl module be proper API
        box = nacl.public.Box(self._private_key, self._grid_broker_pub_key)
        encrypted = box.encrypt(b)
        signature = self._signing_key.sign(encrypted, nacl.encoding.RawEncoder)

        key = self._notary_client.register(encrypted, signature, reservation.bot_id)
        tx = self._wallet.coins_send(self._grid_broker_addr, reservation_amount(reservation), data=key)
        return tx.id

    def _validate_reservation(self, reservation):
        # for field in ['type', 'reservation', 'size', 'email', 'bot_id']:
        for field in ['size', 'email', 'bot_id', 'duration']:
            if not getattr(reservation, field):
                raise ValueError("field '%s' cannot be empty" % field)

        # validate bot id exists
        self._wallet.client.threebot.record_get(reservation.bot_id)

        if reservation.duration <= 0:
            raise ValueError("reservation duration must be greated then 0")

        if reservation.size < 0 or reservation > 2:
            raise ValueError('reservation size can only be 1 or 2')


def encode_reservation(reservation):
    return reservation._data


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
