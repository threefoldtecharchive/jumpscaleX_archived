import nacl
from Jumpscale import j
import decimal

from . import schemas


class TFChainCapacity:
    """
    TFChainReservation contains all TF grid reservation logic.
    """

    def __init__(self, wallet):
        self._wallet = wallet
        self._notary_client_ = None
        self._grid_broker_pub_key_ = None
        self._grid_broker_addr = None

    @property
    def _notary_client(self):
        """
        lazy loading of the notary client
        """

        if self._notary_client_ is None:
            c = j.clients.gedis.new("tfnotary", host="notary.grid.tf", port=5000)
            self._notary_client_ = c.actors.notary_actor
        return self._notary_client_

    def _threebot_singing_key(self, threebot_id):
        """
        reteive the singing key used to register the threebot
        identify by `threebot_id`

        :param threebot_id: name or address or identifier or the threebot
        :type threebot_id: string
        :raises KeyError: raises if no matching key has been found
        :return: signing key used to register the threebot
        :rtype: nacl.signing.SigningKey
        """

        record = self._wallet.client.threebot.record_get(threebot_id)
        for addr in self._wallet.addresses:
            keypair = self._wallet.key_pair_get(addr)
            if record.public_key.hash == keypair.public_key.hash:
                return nacl.signing.SigningKey(keypair.private_key.to_seed())

        raise KeyError(
            "could not found the private used to create the threebot %s. Please generate more addresses" % threebot_id
        )

    @property
    def _grid_broker_pub_key(self):
        """
        retrieve the public key of the grid broker to encrypt the reservation
        """

        if self._grid_broker_pub_key_ is None:
            record = self._wallet.client.threebot.record_get("development.broker")
            encoded_key = record.public_key.hash
            self._grid_broker_addr = record.public_key.unlockhash
            vk = nacl.signing.VerifyKey(str(encoded_key), encoder=nacl.encoding.HexEncoder)
            self._grid_broker_pub_key_ = vk.to_curve25519_public_key()
        return self._grid_broker_pub_key_

    def reserve_s3(self, email, threebot_id, location, size=1, source=None, refund=None):
        """
        reserve an S3 archive

        :param email: email address on which to send the connection information
        :type email: string
        :param threebot_id: name or address of your threebot
        :type threebot_id: string
        :param size: size of the archive to reserve, defaults to 1
                    possible value:
                    - 1 => 50GiB of storage
                    - 2 => 100GiB of storage
        :type size: int, optional
        :param location: node id or farm name where to deploy the virtual 0-OS
                        if location is a node id, the node is used
                        if location is a farm id, a node is automatically chosen in the farm and used.
        :type location: string
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional
        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple
        """

        reservation = j.data.schema.get_from_url_latest(url="tfchain.reservation.s3").new(
            data={"size": size, "email": email, "created": j.data.time.epoch, "type": "s3", "location": location}
        )
        _validate_reservation_s3(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def reserve_zos_vm(self, email, threebot_id, location, size=1, source=None, refund=None):
        """
        reserve an virtual 0-OS

        :param email: email address on which to send the connection information
        :type email: string
        :param threebot_id: name or address of your threebot
        :type threebot_id: string
        :param size: size of the archive to reserve, defaults to 1
                    possible value:
                    - 1 => 1 CPU 2 GiB of memory  10 GiB of storage
                    - 2 => 2 CPU 4 GiB of memory  40 GiB of storage
        :type size: int, optional
        :param location: node id or farm name where to deploy the virtual 0-OS
                        if location is a node id, the node is used
                        if location is a farm id, a node is automatically chosen in the farm and used.
        :type location: string
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional
        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple
        """
        reservation = j.data.schema.get_from_url_latest(url="tfchain.reservation.zos_vm").new(
            data={"size": size, "email": email, "created": j.data.time.epoch, "type": "vm", "location": location}
        )
        _validate_reservation_vm(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def reserve_zdb_namespace(
        self, email, threebot_id, location, size=1, disk_type="ssd", mode="seq", password=None, source=None, refund=None
    ):
        """
        reserve an 0-DB namespace

        :param email: email address on which to send the connection information
        :type email: string
        :param threebot_id: name or address of your threebot
        :type threebot_id: string
        :param size: size of the namespace in GB, defaults to 1
        :type size: int, optional
        :param disk_type: type of disk used for the 0-db
                          can be or 'ssd' or 'hdd'
        :type disk_type: string
        :param mode: 0-db mode, for more detail see: https://github.com/threefoldtech/0-db#running-modes
                     valid values are: 'seq' or 'user'
        :type mode: string
        :param password: is specified, the namespace will required authentication using the password
        :type password: string
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional
        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple
        """
        reservation = j.data.schema.get_from_url_latest(url="tfchain.reservation.zdb_namespace").new(
            data={
                "type": "namespace",
                "size": size,
                "email": email,
                "created": j.data.time.epoch,
                "location": location,
                "disk_type": disk_type,
                "mode": mode,
                "password": password,
            }
        )
        _validate_reservation_namespace(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def reserve_reverse_proxy(self, email, threebot_id, domain, backend_urls, source=None, refund=None):
        """
        reserve a HTTP reverse proxy


        :param email: email address on which to send the connection information
        :type email: string
        :param threebot_id: name or address of your threebot
        :type threebot_id: string
        :param domain: the domain name you want to proxy from
        :type domain: string
        :param backend_urls: List of http url of your backend
                             the proxy will forward incoming requests on domain and forward it
                             to the backend. If multiple url are specified, round robin is used.
                             Format of the url should be a full url with port.
                             example: http://10.244.1.10:8080
        :type backend_urls: list
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional
        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple
        """
        reservation = j.data.schema.get_from_url_latest(url="tfchain.reservation.reverse_proxy").new(
            data={
                "type": "reverse_proxy",
                "email": email,
                "created": j.data.time.epoch,
                # 'location': location,
                "domain": domain,
                "backend_urls": backend_urls,
            }
        )
        _validate_reverse_proxy(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def _process_reservation(self, reservation, threebot_id, source=None, refund=None):
        _validate_reservation_base(reservation)
        amount = reservation_amount(reservation)

        # validate bot id exists
        self._wallet.client.threebot.record_get(threebot_id)

        # get binary representation
        b = encode_reservation(reservation)

        # TODO: this api does not yet exists
        # encrypted = j.data.nacl.encrypt(blob, self.grid_broker_pub_key)
        # I'm doing it manually here for now, will have to update this once nacl module be proper API

        sk = self._threebot_singing_key(threebot_id)
        pk = _signing_key_to_private_key(sk)
        box = nacl.public.Box(pk, self._grid_broker_pub_key)
        encrypted = bytes(box.encrypt(b))
        signature = sk.sign(encrypted, nacl.encoding.RawEncoder)
        response = self._notary_client.register(threebot_id, signature.message, signature.signature)
        return self._wallet.coins_send(self._grid_broker_addr, amount, data=response.hash, source=source, refund=refund)


def _validate_reservation_base(reservation):
    for field in ["email"]:
        if not getattr(reservation, field):
            raise ValueError("field '%s' cannot be empty" % field)


def _validate_reservation_s3(reservation):
    for field in ["size"]:
        if not getattr(reservation, field):
            raise ValueError("field '%s' cannot be empty" % field)

    if reservation.size < 0 or reservation.size > 2:
        raise ValueError("reservation size can only be 1 or 2")

    if not _validate_location(reservation.location):
        raise ValueError("location '%s' is not valid" % reservation.location)


def _validate_reservation_vm(reservation):
    for field in ["size"]:
        if not getattr(reservation, field):
            raise ValueError("field '%s' cannot be empty" % field)

    if reservation.size < 0 or reservation.size > 2:
        raise ValueError("reservation size can only be 1 or 2")

    if not _validate_location(reservation.location):
        raise ValueError("location '%s' is not valid" % reservation.location)


def _validate_reservation_namespace(reservation):
    for field in ["size"]:
        if not getattr(reservation, field):
            raise ValueError("field '%s' cannot be empty" % field)

    if not reservation.mode or reservation.mode not in ["seq", "user", "direct"]:
        raise ValueError("mode can only be 'seq', 'user' or 'direct'")
    if not reservation.disk_type or reservation.disk_type not in ["hdd", "ssd"]:
        raise ValueError("disk_type can only be 'ssd' or 'hdd'")

    if not _validate_location(reservation.location):
        raise ValueError("location '%s' is not valid" % reservation.location)


def _validate_reverse_proxy(reservation):
    for field in ["domain", "backend_urls"]:
        if not getattr(reservation, field):
            raise ValueError("field '%s' cannot be empty" % field)


def encode_reservation(reservation):
    return reservation._msgpack


def _signing_key_to_private_key(sk):
    if not isinstance(sk, nacl.signing.SigningKey):
        raise TypeError("sk must be of type nacl.signing.SigningKey")
    return sk.to_curve25519_private_key()


def reservation_amount(reservation):
    # https://github.com/threefoldfoundation/info_grid/tree/development/docs/capacity_reservation#amount-of-tft-for-each-type-of-reservation
    if reservation.type == "s3":
        return s3_price(reservation.size)
    elif reservation.type == "vm":
        return vm_price(reservation.size)
    elif reservation.type == "namespace":
        return namespace_price(reservation.size)
    elif reservation.type == "reverse_proxy":
        return proxy_price()
    else:
        raise ValueError("unsupported reservation type")


def s3_price(size):
    if size == 1:
        return decimal.Decimal("41.65")
    elif size == 2:
        return decimal.Decimal("83.3")
    else:
        raise ValueError("size for s3 can only be 1 or 2")


def vm_price(size):
    if size == 1:
        return decimal.Decimal("41.65")
    elif size == 2:
        return decimal.Decimal("83.3")
    else:
        raise ValueError("size for vm can only be 1 or 2")


def namespace_price(size):
    return size * decimal.Decimal("0.0833")


def proxy_price():
    return 10


def _validate_location(location):
    cl = j.clients.threefold_directory.get()
    farm_exists = False
    node_exists = False
    try:
        cl.api.GetFarmer(location)
        farm_exists = True
    except:
        farm_exists = False

    if farm_exists:
        return True

    try:
        cl.api.GetCapacity(location)
        node_exists = True
    except:
        node_exists = False

    return node_exists
