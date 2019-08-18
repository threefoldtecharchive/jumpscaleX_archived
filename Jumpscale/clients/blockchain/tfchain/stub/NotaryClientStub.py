from Jumpscale import j
from io import BytesIO


class Hash:
    def __init__(self, h):
        self.hash = h


class NotaryClientStub:
    def __init__(self, tfclient):
        self._tfclient = tfclient
        self._store = {}

    def register(self, threebot_id, reservation, signature):
        record = self._tfclient.threebot.record_get(threebot_id)
        threebot_id = record.identifier

        if not isinstance(threebot_id, int):
            raise j.exceptions.Value("threebot_id must be an int. The unique identifier of the theebot, not its same")
        if threebot_id <= 0:
            raise j.exceptions.Value("threebot_id cannot be negative")

        buff = BytesIO()
        bi = threebot_id.to_bytes(64, byteorder="big")
        buff.write(bi)

        if isinstance(reservation, str):
            reservation = reservation.encode("utf-8")
        buff.write(reservation)
        h = j.data.hash.blake2_string(buff.getvalue(), 32)

        self._store[h] = reservation

        return Hash(h)

    def get(self, hash):
        return self._store[hash]
