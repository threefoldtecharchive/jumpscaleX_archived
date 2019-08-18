import decimal
import nacl
import time

from datetime import date
from Jumpscale import j

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

        raise j.exceptions.NotFound(
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

    def _notary_data_get(self, hash_key):
        data = self._notary_client.get(hash_key)
        sk = self._threebot_singing_key(data.threebot_id)
        pk = _signing_key_to_private_key(sk)
        box = nacl.public.Box(pk, self._grid_broker_pub_key)
        data_dict = j.data.serializers.msgpack.loads(box.decrypt(data.content))

        return data.threebot_id, data_dict

    def reservations_transactions_list(self):
        """
        list ids of all transactions that happened due to a reservation
        """
        if not self._wallet.reservations_transactions:
            transactions = list()
            for transaction in self._wallet.transactions:
                if not transaction.data:
                    continue
                try:
                    _, data_dict = self._notary_data_get(transaction.data.value.decode())
                    if data_dict.get("type") in ["vm", "reverse_proxy", "namespace", "s3"]:
                        transactions.append(transaction.id)
                except UnicodeDecodeError:
                    self._wallet._log_warning("failed to decode tx %s" % transaction.id)
                    continue
                except Exception as e:
                    if "reservation not found" not in str(e):
                        raise e
            self._wallet.reservations_transactions = transactions
            self._wallet.save()
        return self._wallet.reservations_transactions

    def reservation_extend(self, transaction_id, email, duration=1, source=None, refund=None):
        """
        extend the expiry of an existing reservation

        :param transaction_id: id of the transaction that was created for the reservation you want to extend
        :type transaction_id: string
        :param email: email address on which to send the result of the extension
        :type email: string
        :param duration: number of months to extend the expiry by
        :type duration: int
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional

        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple

        """
        transaction = self._wallet.client.transaction_get(transaction_id)
        try:
            threebot_id, reservation = self._notary_data_get(transaction.data.value.decode())
            if reservation.get("type") not in ["vm", "reverse_proxy", "namespace", "s3"]:
                raise j.exceptions.Value("Invalid reservation transaction")
        except Exception as e:
            if "reservation not found" in str(e):
                raise j.exceptions.Value("Invalid reservation transaction")
            raise e

        templates = {
            "vm": "tfchain.reservation.zos_vm",
            "s3": "tfchain.reservation.s3",
            "namespace": "tfchain.reservation.zdb_namespace",
            "reverse_proxy": "tfchain.reservation.reverse_proxy",
        }
        reservation["duration"] = duration
        reservation = j.data.schema.get_from_url(url=templates[reservation["type"]]).new(data=reservation)

        amount = reservation_amount(reservation)
        extension = j.data.schema.get_from_url(url="tfchain.reservation.extend").new(
            data={"duration": duration, "transaction_id": transaction.id, "email": email}
        )

        signature = self._sign_reservation(threebot_id, extension)
        response = self._notary_client.register(threebot_id, signature.message, signature.signature)
        return self._wallet.coins_send(self._grid_broker_addr, amount, data=response.hash, source=source, refund=refund)

    def reserve_s3(self, email, threebot_id, location, size=1, duration=1, source=None, refund=None):
        """
        reserve an S3 archive

        :param email: email address on which to send the connection information
        :type email: string
        :param threebot_id: name or address of your threebot
        :type threebot_id: string
        :param size: size of the archive to reserve, defaults to 1
                    possible value:
                    - 1 => 500 GiB of storage
                    - 2 => 1000 GiB of storage
        :type size: int, optional
        :param duration: number of months the reservation should be valid for
        :type duration: int
        :param location: farm name where to deploy the archive
                         based on the size requests, a certain number of different node will be use to provide the required
                         0-db namespaces
        :type location: string
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional
        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple
        """

        reservation = j.data.schema.get_from_url(url="tfchain.reservation.s3").new(
            data={
                "size": size,
                "email": email,
                "created": j.data.time.epoch,
                "type": "s3",
                "location": location,
                "duration": duration,
            }
        )
        _validate_reservation_s3(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def reserve_zos_vm(
        self, email, threebot_id, location, size=1, duration=1, organization="", source=None, refund=None
    ):
        """
        reserve an virtual 0-OS

        :param email: email address on which to send the connection information
        :type email: string
        :param threebot_id: name or address of your threebot
        :type threebot_id: string
        :param location: node id or farm name where to deploy the virtual 0-OS
                        if location is a node id, the node is used
                        if location is a farm id, a node is automatically chosen in the farm and used.
        :type location: string
        :param size: size of the archive to reserve, defaults to 1
                    possible value:
                    - 1 => 1 CPU 2 GiB of memory  10 GiB of storage
                    - 2 => 2 CPU 4 GiB of memory  40 GiB of storage
        :type size: int, optional
        :param duration: number of months the reservation should be valid for
        :type duration: int
        :param organization: organization for the deployed zos vm. If left empty, anyone can send commands to your zos vm.
        :type organization: string
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional
        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple
        """
        reservation = j.data.schema.get_from_url(url="tfchain.reservation.zos_vm").new(
            datadict={
                "size": size,
                "email": email,
                "created": j.data.time.epoch,
                "type": "vm",
                "location": location,
                "duration": duration,
                "organization": organization,
            }
        )
        _validate_reservation_vm(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def reserve_zdb_namespace(
        self,
        email,
        threebot_id,
        location,
        size=1,
        duration=1,
        disk_type="ssd",
        mode="seq",
        password=None,
        source=None,
        refund=None,
    ):
        """
        reserve an 0-DB namespace

        :param email: email address on which to send the connection information
        :type email: string
        :param threebot_id: name or address of your threebot
        :type threebot_id: string
        :param size: size of the namespace in GB, defaults to 1
        :type size: int, optional
        :param duration: number of months the reservation should be valid for
        :type duration: int
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
        reservation = j.data.schema.get_from_url(url="tfchain.reservation.zdb_namespace").new(
            data={
                "type": "namespace",
                "size": size,
                "email": email,
                "created": j.data.time.epoch,
                "location": location,
                "disk_type": disk_type,
                "mode": mode,
                "password": password,
                "duration": duration,
            }
        )
        _validate_reservation_namespace(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def reserve_reverse_proxy(self, email, threebot_id, domain, backend_urls, duration=1, source=None, refund=None):
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
        :param duration: number of months the reservation should be valid for
        :type duration: int
        :param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        :type source: string, optional
        :param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        :type refund: string, optional
        :return: a tuple containing the transaction and the submission status as a boolean
        :rtype: tuple
        """
        reservation = j.data.schema.get_from_url(url="tfchain.reservation.reverse_proxy").new(
            data={
                "type": "reverse_proxy",
                "email": email,
                "created": j.data.time.epoch,
                # 'location': location,
                "domain": domain,
                "backend_urls": backend_urls,
                "duration": duration,
            }
        )
        _validate_reverse_proxy(reservation)
        return self._process_reservation(reservation, threebot_id, source=source, refund=refund)

    def _process_reservation(self, reservation, threebot_id, source=None, refund=None):
        _validate_reservation_base(reservation)
        amount = reservation_amount(reservation)

        # validate bot id exists
        bot = self._wallet.client.threebot.record_get(threebot_id)
        reservation_expiry = j.clients.tfchain.time.extend(time.time(), reservation.duration)
        if date.fromtimestamp(reservation_expiry) > date.fromtimestamp(bot.expiration):
            raise j.exceptions.Value("Capacity expiration time exceeds threebot's expiration")

        signature = self._sign_reservation(threebot_id, reservation)
        response = self._notary_client.register(threebot_id, signature.message, signature.signature)
        transaction_result = self._wallet.coins_send(
            self._grid_broker_addr, amount, data=response.hash, source=source, refund=refund
        )
        self._wallet.reservations_transactions.append(transaction_result.transaction.id)
        self._wallet.save()
        return transaction_result

    def _sign_reservation(self, threebot_id, reservation):
        # get binary representation
        b = encode_reservation(reservation)

        # TODO: this api does not yet exists
        # encrypted = j.data.nacl.encrypt(blob, self.grid_broker_pub_key)
        # I'm doing it manually here for now, will have to update this once nacl module be proper API

        sk = self._threebot_singing_key(threebot_id)
        pk = _signing_key_to_private_key(sk)
        box = nacl.public.Box(pk, self._grid_broker_pub_key)
        encrypted = bytes(box.encrypt(b))
        return sk.sign(encrypted, nacl.encoding.RawEncoder)


def _validate_reservation_base(reservation):
    for field in ["email"]:
        if not getattr(reservation, field):
            raise j.exceptions.Value("field '%s' cannot be empty" % field)

    if reservation.duration < 1:
        raise j.exceptions.Value("reservation duration has to be 1 month or more")


def _validate_reservation_s3(reservation):
    for field in ["size"]:
        if not getattr(reservation, field):
            raise j.exceptions.Value("field '%s' cannot be empty" % field)

    if reservation.size < 0 or reservation.size > 2:
        raise j.exceptions.Value("reservation size can only be 1 or 2")

    if not _validate_location(reservation.location):
        raise j.exceptions.Value("location '%s' is not valid" % reservation.location)


def _validate_reservation_vm(reservation):
    for field in ["size"]:
        if not getattr(reservation, field):
            raise j.exceptions.Value("field '%s' cannot be empty" % field)

    if reservation.size < 0 or reservation.size > 2:
        raise j.exceptions.Value("reservation size can only be 1 or 2")

    if not _validate_location(reservation.location):
        raise j.exceptions.Value("location '%s' is not valid" % reservation.location)


def _validate_reservation_namespace(reservation):
    for field in ["size"]:
        if not getattr(reservation, field):
            raise j.exceptions.Value("field '%s' cannot be empty" % field)

    if not reservation.mode or reservation.mode not in ["seq", "user", "direct"]:
        raise j.exceptions.Value("mode can only be 'seq', 'user' or 'direct'")
    if not reservation.disk_type or reservation.disk_type not in ["hdd", "ssd"]:
        raise j.exceptions.Value("disk_type can only be 'ssd' or 'hdd'")

    if not _validate_location(reservation.location):
        raise j.exceptions.Value("location '%s' is not valid" % reservation.location)


def _validate_reverse_proxy(reservation):
    for field in ["domain", "backend_urls"]:
        if not getattr(reservation, field):
            raise j.exceptions.Value("field '%s' cannot be empty" % field)


def encode_reservation(reservation):
    return reservation._msgpack


def _signing_key_to_private_key(sk):
    if not isinstance(sk, nacl.signing.SigningKey):
        raise j.exceptions.Value("sk must be of type nacl.signing.SigningKey")
    return sk.to_curve25519_private_key()


def reservation_amount(reservation):
    # https://github.com/threefoldfoundation/info_grid/tree/development/docs/capacity_reservation#amount-of-tft-for-each-type-of-reservation
    if reservation.type == "s3":
        price = s3_price(reservation.size)
    elif reservation.type == "vm":
        price = vm_price(reservation.size)
    elif reservation.type == "namespace":
        price = namespace_price(reservation.size)
    elif reservation.type == "reverse_proxy":
        price = proxy_price()
    else:
        raise j.exceptions.Value("unsupported reservation type")

    return price * reservation.duration


def s3_price(size):
    if size == 1:
        return decimal.Decimal("41.65")
    elif size == 2:
        return decimal.Decimal("83.3")
    else:
        raise j.exceptions.Value("size for s3 can only be 1 or 2")


def vm_price(size):
    if size == 1:
        return decimal.Decimal("41.65")
    elif size == 2:
        return decimal.Decimal("83.3")
    else:
        raise j.exceptions.Value("size for vm can only be 1 or 2")


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
