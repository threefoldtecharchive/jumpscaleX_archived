from Jumpscale import j

import re

from Jumpscale.clients.blockchain.tfchain.types.ConditionTypes import ConditionBaseClass
from Jumpscale.clients.blockchain.tfchain.types.CryptoTypes import PublicKey
from Jumpscale.clients.blockchain.tfchain.types.PrimitiveTypes import Hash
from Jumpscale.clients.blockchain.tfchain.types.ThreeBot import BotName
from Jumpscale.clients.blockchain.tfchain.TFChainClient import ThreeBotRecord


class TFChainExplorerGetClientStub(j.application.JSBaseClass):
    def __init__(self):
        self._blocks = {}
        self._hashes = {}
        self._threebot_records = {}
        self._mint_conditions = {}
        self._chain_info = None
        self._posted_transactions = {}

    @property
    def chain_info(self):
        if not self._chain_info:
            raise Exception("chain info not set in stub client")
        return self._chain_info

    @chain_info.setter
    def chain_info(self, value):
        assert isinstance(value, str) and len(value) > 2
        self._chain_info = value

    def posted_transaction_get(self, transactionid):
        """
        Get a posted transaction using our random generated transaction ID.
        """
        if isinstance(transactionid, Hash):
            transactionid = str(transactionid)
        else:
            assert isinstance(transactionid, str)
        return self._posted_transactions[transactionid]

    def explorer_get(self, endpoint):
        """
        Get explorer data from the stub client for the specified endpoint.
        """
        hash_template = re.compile(r"^.*/explorer/hashes/(.+)$")
        match = hash_template.match(endpoint)
        if match:
            return self.hash_get(match.group(1))
        hash_template = re.compile(r"^.*/explorer/blocks/(\d+)$")
        match = hash_template.match(endpoint)
        if match:
            return self.block_get(int(match.group(1)))
        threebot_template = re.compile(r"^.*/explorer/3bot/(.+)$")
        match = threebot_template.match(endpoint)
        if match:
            return self._record_as_json_resp(
                self.threebot_record_get(match.group(1), endpoint="/explorer/3bot/{}".format(match.group(1)))
            )
        threebot_whois_template = re.compile(r"^.*/explorer/whois/3bot/(.+)$")
        match = threebot_whois_template.match(endpoint)
        if match:
            return self._record_as_json_resp(
                self.threebot_record_get(match.group(1), endpoint="/explorer/whois/3bot/{}".format(match.group(1)))
            )
        mint_condition_at_template = re.compile(r"^.*/explorer/mintcondition/(\d+)$")
        match = mint_condition_at_template.match(endpoint)
        if match:
            return self.mint_condition_get(
                height=int(match.group(1)), endpoint="/explorer/mintcondition/" + match.group(1)
            )
        mint_condition_latest_template = re.compile(r"^.*/explorer/mintcondition$")
        match = mint_condition_latest_template.match(endpoint)
        if match:
            return self.mint_condition_get(height=None, endpoint="/explorer/mintcondition")
        info_template = re.compile(r"^.*/explorer$")
        if info_template.match(endpoint):
            return self.chain_info
        raise Exception("invalid endpoint {}".format(endpoint))

    def explorer_post(self, endpoint, data):
        """
        Put explorer data onto the stub client for the specified endpoint.
        """
        hash_template = re.compile(r"^.*/transactionpool/transactions$")
        match = hash_template.match(endpoint)
        if match:
            transactionid = str(Hash(value=j.data.idgenerator.generateXByteID(Hash.SIZE)))
            transaction = j.clients.tfchain.types.transactions.from_json(data)
            # ensure all coin outputs and block stake outputs have identifiers set
            for idx, co in enumerate(transaction.coin_outputs):
                co.id = transaction.coin_outputid_new(idx)
            for idx, bso in enumerate(transaction.blockstake_outputs):
                bso.id = transaction.blockstake_outputid_new(idx)
            self._posted_transactions[transactionid] = transaction
            return '{"transactionid":"%s"}' % (str(transactionid))
        raise Exception("invalid endpoint {}".format(endpoint))

    def block_get(self, height):
        """
        The explorer block response at the given height.
        """
        assert isinstance(height, int)
        if not height in self._blocks:
            raise j.clients.tfchain.errors.ExplorerNoContent(
                "no content found for block {}".format(height), endpoint="/explorer/blocks/{}".format(height)
            )
        return self._blocks[height]

    def block_add(self, height, resp, force=False):
        """
        Add a block response to the stub explorer at the given height.
        """
        assert isinstance(height, int)
        assert isinstance(resp, str)
        if not force and height in self._blocks:
            raise j.exceptions.NotFound("{} already exists in explorer blocks".format(height))
        self._blocks[height] = resp

    def hash_get(self, hash):
        """
        The explorer hash response at the given hash.
        """
        assert isinstance(hash, str)
        if not hash in self._hashes:
            raise j.clients.tfchain.errors.ExplorerNoContent(
                "no content found for hash {}".format(hash), endpoint="/explorer/hashes/{}".format(str(hash))
            )
        return self._hashes[hash]

    def hash_add(self, hash, resp, force=False):
        """
        Add a hash response to the stub explorer at the given hash.
        """
        assert isinstance(hash, str)
        assert isinstance(resp, str)
        if not force and hash in self._hashes:
            raise j.exceptions.NotFound("{} already exists in explorer hashes".format(hash))
        self._hashes[hash] = resp

    def threebot_record_add(self, record, force=False):
        """
        Add a block response to the stub explorer at the given height.
        """
        assert isinstance(record, ThreeBotRecord)
        if not force and record.identifier in self._threebot_records:
            raise j.exceptions.NotFound("3Bot {} already exists in explorer threebot records".format(record.identifier))
        self._threebot_records[record.identifier] = record

    def threebot_record_get(self, identifier, endpoint):
        """
        Add a block response to the stub explorer at the given height.
        """
        assert isinstance(identifier, str)
        if identifier.isdigit():
            try:
                return self._threebot_records[int(identifier)]
            except KeyError as exc:
                raise j.clients.tfchain.errors.ExplorerNoContent(
                    "no 3Bot record could be found for identifier {}".format(identifier), endpoint=endpoint
                ) from exc
        if BotName.REGEXP.match(identifier) is not None:
            for record in self._threebot_records.values():
                for name in record.names:
                    if name.value == identifier:
                        return record
            raise j.clients.tfchain.errors.ExplorerNoContent(
                "no content found for 3Bot identifier {}".format(identifier), endpoint=endpoint
            )
        # must be a public key
        pk = PublicKey.from_json(identifier)
        for record in self._threebot_records.values():
            if record.public_key.unlockhash == pk.unlockhash:
                return record
        raise j.clients.tfchain.errors.ExplorerNoContent(
            "no content found for 3Bot identifier {}".format(identifier), endpoint=endpoint
        )

    def mint_condition_add(self, condition, height, force=False):
        if not (isinstance(height, int) and not isinstance(height, bool)):
            raise j.exceptions.Value(
                "height has to be None or an int: {} is an invalid height type".format(type(height))
            )
        if height < 0:
            raise j.exceptions.Value("height cannot be negative")
        if height in self._mint_conditions and not force:
            raise j.exceptions.NotFound(
                "{} already exists in explorer mint conditions on height {}".format(str(condition.unlockhash), height)
            )
        if not isinstance(condition, ConditionBaseClass):
            raise j.exceptions.Value(
                "condition is expected to be a subtype of ConditionBaseClass: {} is an invalid type".format(
                    type(condition)
                )
            )
        self._mint_conditions[height] = condition

    def mint_condition_get(self, height, endpoint):
        # ensure there is a mint condition
        if len(self._mint_conditions) == 0:
            raise j.clients.tfchain.errors.ExplorerServerError("no mint conditions defined", endpoint=endpoint)

        # define the desired condition
        if height is None:
            heights = list(self._mint_conditions.keys())
            heights.sort(reverse=True)
            condition = self._mint_conditions[heights[0]]
        elif isinstance(height, int) and not isinstance(height, bool):
            if height < 0:
                raise j.exceptions.Value("height cannot be negative")
            heights = list(self._mint_conditions.keys())
            heights.sort()
            condition_height = heights[0]
            for current_height in heights[1:]:
                if current_height <= height:
                    condition_height = current_height
                if current_height >= height:
                    break
            condition = self._mint_conditions[condition_height]
        else:
            raise j.exceptions.Value(
                "height has to be None or an int: {} is an invalid height type".format(type(height))
            )

        # return it as a JSON string
        return j.data.serializers.json.dumps({"mintcondition": condition.json()})

    def _record_as_json_resp(self, record):
        return j.data.serializers.json.dumps(
            {
                "record": {
                    "id": record.identifier,
                    "names": [name.json() for name in record.names],
                    "addresses": [address.json() for address in record.addresses],
                    "publickey": record.public_key.json(),
                    "expiration": record.expiration,
                }
            }
        )
