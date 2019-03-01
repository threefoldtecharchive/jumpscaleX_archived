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
        self._grid_broker_pub_key = None
        self._grid_broker_addr = ''  # TODO: hardcode tfchain address of the grid broker
        self._notary_client = j.clients.gedis.configure('tfnotary', host='notary.grid.tf', port=8888)
        # self._notary_client = NotaryMock()
        # this all key management needs to be improved
        keypair = self._wallet.key_pair_get(self._wallet.address)
        self._signing_key = nacl.signing.SigningKey(keypair.private_key.to_seed())
        self._private_key = self._signing_key.to_curve25519_private_key()

    @property
    def grid_broker_pub_key(self):
        if self._grid_broker_pub_key is None:
            record = self._wallet.client.threebot.record_get('tf3bot.zaibon')
            encoded_key = record.public_key.unlockhash
            self._grid_broker_pub_key = nacl.public.PublicKey(
                str(encoded_key.hash),
                encoder=nacl.encoding.HexEncoder)
        return self._grid_broker_pub_key

    def new(self):
        return _RESERVATION_SCHEMA.new()

    def send(self, reservation):
        reservation.created = j.data.time.epoch
        blob = reservation._data

        # TODO: this api does not yet exists
        # encrypted = j.data.nacl.encrypt(blob, self.grid_broker_pub_key)
        # I'm doing it manually here for now, will have to update this once nacl module has be
        # proper API
        encrypted = nacl.public.Box(self._private_key, self.grid_broker_pub_key)
        signature = self._signing_key.sign(encrypted, nacl.encoding.RawEncoder)

        key = self._notary_client.register(encrypted, signature, reservation.bot_id)
        tx = self._wallet.coins_send(self._grid_broker_addr, reservation_amount(reservation), data=key)
        return tx.id


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
