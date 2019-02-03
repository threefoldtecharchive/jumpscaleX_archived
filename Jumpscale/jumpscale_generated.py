
# from Jumpscale.core.JSBase import JSBase
import os
import sys
from Jumpscale import j


if "/sandbox/lib/jumpscale" not in sys.path:
    sys.path.append("/sandbox/lib/jumpscale")

class JSGroup():
    pass



class group_clients(JSGroup):
    def __init__(self):
        
        self._gedis = None
        self._multicast = None
        self._gedis_backend = None
        self._syncthing = None
        self._postgres = None
        self._s3 = None
        self._zhub = None
        self._portal = None
        self._ovh = None
        self._oauth = None
        self._redis_config = None
        self._logger = None
        self._telegram_bot = None
        self._mongoengine = None
        self._mongodb = None
        self._currencylayer = None
        self._tarantool = None
        self._zos = None
        self._redis = None
        self._credis_core = None
        self._email = None
        self._sendgrid = None
        self._openvcloud = None
        self._intercom = None
        self.__template = None
        self._itsyouonline = None
        self._grafana = None
        self._zstor = None
        self._zerostor = None
        self._sqlalchemy = None
        self._virtualbox = None
        self._influxdb = None
        self._btc_electrum = None
        self._tfchain = None
        self._tfchain_old = None
        self._sshagent = None
        self._ssh = None
        self._racktivity = None
        self._gitea = None
        self._github = None
        self._google_compute = None
        self._http = None
        self._peewee = None
        self._rogerthat = None
        self._mysql = None
        self._zboot = None
        self._webgateway = None
        self._etcd = None
        self._zhubdirect = None
        self._threefold_directory = None
        self._kraken = None
        self._btc_alpha = None
        self._trello = None
        self._sshkey = None
        self._zerotier = None
        self._kubernetes = None
        self._coredns = None
        self._ipmi = None
        self._graphite = None
        self._zdb = None
        self._git = None
        self._traefik = None
        self._packetnet = None

    
    @property
    def gedis(self):
        if self._gedis is None:
            from DigitalMe.clients.gedis.GedisClientFactory import GedisClientFactory
            self._gedis =  GedisClientFactory()
            # print("load:%sgedis")
            if hasattr(self._gedis,"_init"):
                self._gedis._init()
                # print("init:%sgedis")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._gedis,"_init2"):
                self._gedis._init2()
                # print("init2:%sgedis")
        return self._gedis
    @property
    def multicast(self):
        if self._multicast is None:
            from DigitalMe.clients.multicast.MulticastFactory import MulticastFactory
            self._multicast =  MulticastFactory()
            # print("load:%smulticast")
            if hasattr(self._multicast,"_init"):
                self._multicast._init()
                # print("init:%smulticast")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._multicast,"_init2"):
                self._multicast._init2()
                # print("init2:%smulticast")
        return self._multicast
    @property
    def gedis_backend(self):
        if self._gedis_backend is None:
            from DigitalMe.clients.gedis_backends.GedisBackendClientFactory import GedisBackendClientFactory
            self._gedis_backend =  GedisBackendClientFactory()
            # print("load:%sgedis_backend")
            if hasattr(self._gedis_backend,"_init"):
                self._gedis_backend._init()
                # print("init:%sgedis_backend")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._gedis_backend,"_init2"):
                self._gedis_backend._init2()
                # print("init2:%sgedis_backend")
        return self._gedis_backend
    @property
    def syncthing(self):
        if self._syncthing is None:
            from Jumpscale.clients.syncthing.SyncthingFactory import SyncthingFactory
            self._syncthing =  SyncthingFactory()
            # print("load:%ssyncthing")
            if hasattr(self._syncthing,"_init"):
                self._syncthing._init()
                # print("init:%ssyncthing")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._syncthing,"_init2"):
                self._syncthing._init2()
                # print("init2:%ssyncthing")
        return self._syncthing
    @property
    def postgres(self):
        if self._postgres is None:
            from Jumpscale.clients.postgresql.PostgresqlFactory import PostgresqlFactory
            self._postgres =  PostgresqlFactory()
            # print("load:%spostgres")
            if hasattr(self._postgres,"_init"):
                self._postgres._init()
                # print("init:%spostgres")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._postgres,"_init2"):
                self._postgres._init2()
                # print("init2:%spostgres")
        return self._postgres
    @property
    def s3(self):
        if self._s3 is None:
            from Jumpscale.clients.s3.S3Factory import S3Factory
            self._s3 =  S3Factory()
            # print("load:%ss3")
            if hasattr(self._s3,"_init"):
                self._s3._init()
                # print("init:%ss3")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._s3,"_init2"):
                self._s3._init2()
                # print("init2:%ss3")
        return self._s3
    @property
    def zhub(self):
        if self._zhub is None:
            from Jumpscale.clients.zero_hub.ZeroHubFactory import ZeroHubFactory
            self._zhub =  ZeroHubFactory()
            # print("load:%szhub")
            if hasattr(self._zhub,"_init"):
                self._zhub._init()
                # print("init:%szhub")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zhub,"_init2"):
                self._zhub._init2()
                # print("init2:%szhub")
        return self._zhub
    @property
    def portal(self):
        if self._portal is None:
            from Jumpscale.clients.portal.PortalClientFactory import PortalClientFactory
            self._portal =  PortalClientFactory()
            # print("load:%sportal")
            if hasattr(self._portal,"_init"):
                self._portal._init()
                # print("init:%sportal")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._portal,"_init2"):
                self._portal._init2()
                # print("init2:%sportal")
        return self._portal
    @property
    def ovh(self):
        if self._ovh is None:
            from Jumpscale.clients.ovh.OVHFactory import OVHFactory
            self._ovh =  OVHFactory()
            # print("load:%sovh")
            if hasattr(self._ovh,"_init"):
                self._ovh._init()
                # print("init:%sovh")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ovh,"_init2"):
                self._ovh._init2()
                # print("init2:%sovh")
        return self._ovh
    @property
    def oauth(self):
        if self._oauth is None:
            from Jumpscale.clients.oauth.OauthFactory import OauthFactory
            self._oauth =  OauthFactory()
            # print("load:%soauth")
            if hasattr(self._oauth,"_init"):
                self._oauth._init()
                # print("init:%soauth")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._oauth,"_init2"):
                self._oauth._init2()
                # print("init2:%soauth")
        return self._oauth
    @property
    def redis_config(self):
        if self._redis_config is None:
            from Jumpscale.clients.redisconfig.RedisConfigFactory import RedisConfigFactory
            self._redis_config =  RedisConfigFactory()
            # print("load:%sredis_config")
            if hasattr(self._redis_config,"_init"):
                self._redis_config._init()
                # print("init:%sredis_config")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._redis_config,"_init2"):
                self._redis_config._init2()
                # print("init2:%sredis_config")
        return self._redis_config
    @property
    def logger(self):
        if self._logger is None:
            from Jumpscale.clients.logger.LoggerFactory import LoggerFactory
            self._logger =  LoggerFactory()
            # print("load:%slogger")
            if hasattr(self._logger,"_init"):
                self._log__init()
                # print("init:%slogger")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._logger,"_init2"):
                self._log__init2()
                # print("init2:%slogger")
        return self._logger
    @property
    def telegram_bot(self):
        if self._telegram_bot is None:
            from Jumpscale.clients.telegram_bot.TelegramBotFactory import TelegramBotFactory
            self._telegram_bot =  TelegramBotFactory()
            # print("load:%stelegram_bot")
            if hasattr(self._telegram_bot,"_init"):
                self._telegram_bot._init()
                # print("init:%stelegram_bot")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._telegram_bot,"_init2"):
                self._telegram_bot._init2()
                # print("init2:%stelegram_bot")
        return self._telegram_bot
    @property
    def mongoengine(self):
        if self._mongoengine is None:
            from Jumpscale.clients.mongodbclient.MongoEngineFactory import MongoEngineFactory
            self._mongoengine =  MongoEngineFactory()
            # print("load:%smongoengine")
            if hasattr(self._mongoengine,"_init"):
                self._mongoengine._init()
                # print("init:%smongoengine")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._mongoengine,"_init2"):
                self._mongoengine._init2()
                # print("init2:%smongoengine")
        return self._mongoengine
    @property
    def mongodb(self):
        if self._mongodb is None:
            from Jumpscale.clients.mongodbclient.MongoFactory import MongoFactory
            self._mongodb =  MongoFactory()
            # print("load:%smongodb")
            if hasattr(self._mongodb,"_init"):
                self._mongodb._init()
                # print("init:%smongodb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._mongodb,"_init2"):
                self._mongodb._init2()
                # print("init2:%smongodb")
        return self._mongodb
    @property
    def currencylayer(self):
        if self._currencylayer is None:
            from Jumpscale.clients.currencylayer.CurrencyLayer import CurrencyLayerSingleton
            self._currencylayer =  CurrencyLayerSingleton()
            # print("load:%scurrencylayer")
            if hasattr(self._currencylayer,"_init"):
                self._currencylayer._init()
                # print("init:%scurrencylayer")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._currencylayer,"_init2"):
                self._currencylayer._init2()
                # print("init2:%scurrencylayer")
        return self._currencylayer
    @property
    def tarantool(self):
        if self._tarantool is None:
            from Jumpscale.clients.tarantool.TarantoolFactory import TarantoolFactory
            self._tarantool =  TarantoolFactory()
            # print("load:%starantool")
            if hasattr(self._tarantool,"_init"):
                self._tarantool._init()
                # print("init:%starantool")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tarantool,"_init2"):
                self._tarantool._init2()
                # print("init2:%starantool")
        return self._tarantool
    @property
    def zos(self):
        if self._zos is None:
            from Jumpscale.clients.zero_os_protocol.ZeroOSFactory import ZeroOSFactory
            self._zos =  ZeroOSFactory()
            # print("load:%szos")
            if hasattr(self._zos,"_init"):
                self._zos._init()
                # print("init:%szos")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zos,"_init2"):
                self._zos._init2()
                # print("init2:%szos")
        return self._zos
    @property
    def redis(self):
        if self._redis is None:
            from Jumpscale.clients.redis.RedisFactory import RedisFactory
            self._redis =  RedisFactory()
            # print("load:%sredis")
            if hasattr(self._redis,"_init"):
                self._redis._init()
                # print("init:%sredis")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._redis,"_init2"):
                self._redis._init2()
                # print("init2:%sredis")
        return self._redis
    @property
    def credis_core(self):
        if self._credis_core is None:
            from Jumpscale.clients.redis.RedisCoreClient import RedisCoreClient
            self._credis_core =  RedisCoreClient()
            # print("load:%scredis_core")
            if hasattr(self._credis_core,"_init"):
                self._credis_core._init()
                # print("init:%scredis_core")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._credis_core,"_init2"):
                self._credis_core._init2()
                # print("init2:%scredis_core")
        return self._credis_core
    @property
    def email(self):
        if self._email is None:
            from Jumpscale.clients.mail.EmailFactory import EmailFactory
            self._email =  EmailFactory()
            # print("load:%semail")
            if hasattr(self._email,"_init"):
                self._email._init()
                # print("init:%semail")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._email,"_init2"):
                self._email._init2()
                # print("init2:%semail")
        return self._email
    @property
    def sendgrid(self):
        if self._sendgrid is None:
            from Jumpscale.clients.mail.sendgrid.SendGridClient import SendGridClient
            self._sendgrid =  SendGridClient()
            # print("load:%ssendgrid")
            if hasattr(self._sendgrid,"_init"):
                self._sendgrid._init()
                # print("init:%ssendgrid")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sendgrid,"_init2"):
                self._sendgrid._init2()
                # print("init2:%ssendgrid")
        return self._sendgrid
    @property
    def openvcloud(self):
        if self._openvcloud is None:
            from Jumpscale.clients.openvcloud.OVCFactory import OVCClientFactory
            self._openvcloud =  OVCClientFactory()
            # print("load:%sopenvcloud")
            if hasattr(self._openvcloud,"_init"):
                self._openvcloud._init()
                # print("init:%sopenvcloud")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._openvcloud,"_init2"):
                self._openvcloud._init2()
                # print("init2:%sopenvcloud")
        return self._openvcloud
    @property
    def intercom(self):
        if self._intercom is None:
            from Jumpscale.clients.intercom.IntercomFactory import Intercom
            self._intercom =  Intercom()
            # print("load:%sintercom")
            if hasattr(self._intercom,"_init"):
                self._intercom._init()
                # print("init:%sintercom")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._intercom,"_init2"):
                self._intercom._init2()
                # print("init2:%sintercom")
        return self._intercom
    @property
    def _template(self):
        if self.__template is None:
            from Jumpscale.clients.TEMPLATE.TemplateGrafanaFactory import GrafanaFactory
            self.__template =  GrafanaFactory()
            # print("load:%s_template")
            if hasattr(self.__template,"_init"):
                self.__template._init()
                # print("init:%s_template")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self.__template,"_init2"):
                self.__template._init2()
                # print("init2:%s_template")
        return self.__template
    @property
    def itsyouonline(self):
        if self._itsyouonline is None:
            from Jumpscale.clients.itsyouonline.IYOFactory import IYOFactory
            self._itsyouonline =  IYOFactory()
            # print("load:%sitsyouonline")
            if hasattr(self._itsyouonline,"_init"):
                self._itsyouonline._init()
                # print("init:%sitsyouonline")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._itsyouonline,"_init2"):
                self._itsyouonline._init2()
                # print("init2:%sitsyouonline")
        return self._itsyouonline
    @property
    def grafana(self):
        if self._grafana is None:
            from Jumpscale.clients.grafana.GrafanaFactory import GrafanaFactory
            self._grafana =  GrafanaFactory()
            # print("load:%sgrafana")
            if hasattr(self._grafana,"_init"):
                self._grafana._init()
                # print("init:%sgrafana")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._grafana,"_init2"):
                self._grafana._init2()
                # print("init2:%sgrafana")
        return self._grafana
    @property
    def zstor(self):
        if self._zstor is None:
            from Jumpscale.clients.zero_stor.ZeroStorFactory import ZeroStorFactory
            self._zstor =  ZeroStorFactory()
            # print("load:%szstor")
            if hasattr(self._zstor,"_init"):
                self._zstor._init()
                # print("init:%szstor")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zstor,"_init2"):
                self._zstor._init2()
                # print("init2:%szstor")
        return self._zstor
    @property
    def zerostor(self):
        if self._zerostor is None:
            from Jumpscale.clients.zero_stor.ZeroStorFactoryDeprecated import ZeroStorFactoryDeprecated
            self._zerostor =  ZeroStorFactoryDeprecated()
            # print("load:%szerostor")
            if hasattr(self._zerostor,"_init"):
                self._zerostor._init()
                # print("init:%szerostor")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zerostor,"_init2"):
                self._zerostor._init2()
                # print("init2:%szerostor")
        return self._zerostor
    @property
    def sqlalchemy(self):
        if self._sqlalchemy is None:
            from Jumpscale.clients.sqlalchemy.SQLAlchemyFactory import SQLAlchemyFactory
            self._sqlalchemy =  SQLAlchemyFactory()
            # print("load:%ssqlalchemy")
            if hasattr(self._sqlalchemy,"_init"):
                self._sqlalchemy._init()
                # print("init:%ssqlalchemy")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sqlalchemy,"_init2"):
                self._sqlalchemy._init2()
                # print("init2:%ssqlalchemy")
        return self._sqlalchemy
    @property
    def virtualbox(self):
        if self._virtualbox is None:
            from Jumpscale.clients.virtualbox.VirtualboxFactory import VirtualboxFactory
            self._virtualbox =  VirtualboxFactory()
            # print("load:%svirtualbox")
            if hasattr(self._virtualbox,"_init"):
                self._virtualbox._init()
                # print("init:%svirtualbox")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._virtualbox,"_init2"):
                self._virtualbox._init2()
                # print("init2:%svirtualbox")
        return self._virtualbox
    @property
    def influxdb(self):
        if self._influxdb is None:
            from Jumpscale.clients.influxdb.InfluxdbFactory import InfluxdbFactory
            self._influxdb =  InfluxdbFactory()
            # print("load:%sinfluxdb")
            if hasattr(self._influxdb,"_init"):
                self._influxdb._init()
                # print("init:%sinfluxdb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._influxdb,"_init2"):
                self._influxdb._init2()
                # print("init2:%sinfluxdb")
        return self._influxdb
    @property
    def btc_electrum(self):
        if self._btc_electrum is None:
            from Jumpscale.clients.blockchain.electrum.ElectrumClientFactory import ElectrumClientFactory
            self._btc_electrum =  ElectrumClientFactory()
            # print("load:%sbtc_electrum")
            if hasattr(self._btc_electrum,"_init"):
                self._btc_electrum._init()
                # print("init:%sbtc_electrum")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._btc_electrum,"_init2"):
                self._btc_electrum._init2()
                # print("init2:%sbtc_electrum")
        return self._btc_electrum
    @property
    def tfchain(self):
        if self._tfchain is None:
            from Jumpscale.clients.blockchain.tfchain.TFChainClientFactory import TFChainClientFactory
            self._tfchain =  TFChainClientFactory()
            # print("load:%stfchain")
            if hasattr(self._tfchain,"_init"):
                self._tfchain._init()
                # print("init:%stfchain")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tfchain,"_init2"):
                self._tfchain._init2()
                # print("init2:%stfchain")
        return self._tfchain
    @property
    def tfchain_old(self):
        if self._tfchain_old is None:
            from Jumpscale.clients.blockchain.tfchain_old.TfchainClientFactory import TfchainClientFactory
            self._tfchain_old =  TfchainClientFactory()
            # print("load:%stfchain_old")
            if hasattr(self._tfchain_old,"_init"):
                self._tfchain_old._init()
                # print("init:%stfchain_old")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tfchain_old,"_init2"):
                self._tfchain_old._init2()
                # print("init2:%stfchain_old")
        return self._tfchain_old
    @property
    def sshagent(self):
        if self._sshagent is None:
            from Jumpscale.clients.sshagent.SSHAgent import SSHAgent
            self._sshagent =  SSHAgent()
            # print("load:%ssshagent")
            if hasattr(self._sshagent,"_init"):
                self._sshagent._init()
                # print("init:%ssshagent")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sshagent,"_init2"):
                self._sshagent._init2()
                # print("init2:%ssshagent")
        return self._sshagent
    @property
    def ssh(self):
        if self._ssh is None:
            from Jumpscale.clients.ssh.SSHClientFactory import SSHClientFactory
            self._ssh =  SSHClientFactory()
            # print("load:%sssh")
            if hasattr(self._ssh,"_init"):
                self._ssh._init()
                # print("init:%sssh")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ssh,"_init2"):
                self._ssh._init2()
                # print("init2:%sssh")
        return self._ssh
    @property
    def racktivity(self):
        if self._racktivity is None:
            from Jumpscale.clients.racktivity.RacktivityFactory import RacktivityFactory
            self._racktivity =  RacktivityFactory()
            # print("load:%sracktivity")
            if hasattr(self._racktivity,"_init"):
                self._racktivity._init()
                # print("init:%sracktivity")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._racktivity,"_init2"):
                self._racktivity._init2()
                # print("init2:%sracktivity")
        return self._racktivity
    @property
    def gitea(self):
        if self._gitea is None:
            from Jumpscale.clients.gitea.GiteaFactory import GiteaFactory
            self._gitea =  GiteaFactory()
            # print("load:%sgitea")
            if hasattr(self._gitea,"_init"):
                self._gitea._init()
                # print("init:%sgitea")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._gitea,"_init2"):
                self._gitea._init2()
                # print("init2:%sgitea")
        return self._gitea
    @property
    def github(self):
        if self._github is None:
            from Jumpscale.clients.github.GitHubFactory import GitHubFactory
            self._github =  GitHubFactory()
            # print("load:%sgithub")
            if hasattr(self._github,"_init"):
                self._github._init()
                # print("init:%sgithub")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._github,"_init2"):
                self._github._init2()
                # print("init2:%sgithub")
        return self._github
    @property
    def google_compute(self):
        if self._google_compute is None:
            from Jumpscale.clients.google_compute.GoogleComputeFactory import GoogleComputeFactory
            self._google_compute =  GoogleComputeFactory()
            # print("load:%sgoogle_compute")
            if hasattr(self._google_compute,"_init"):
                self._google_compute._init()
                # print("init:%sgoogle_compute")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._google_compute,"_init2"):
                self._google_compute._init2()
                # print("init2:%sgoogle_compute")
        return self._google_compute
    @property
    def http(self):
        if self._http is None:
            from Jumpscale.clients.http.HttpClient import HttpClient
            self._http =  HttpClient()
            # print("load:%shttp")
            if hasattr(self._http,"_init"):
                self._http._init()
                # print("init:%shttp")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._http,"_init2"):
                self._http._init2()
                # print("init2:%shttp")
        return self._http
    @property
    def peewee(self):
        if self._peewee is None:
            from Jumpscale.clients.peewee.PeeweeFactory import PeeweeFactory
            self._peewee =  PeeweeFactory()
            # print("load:%speewee")
            if hasattr(self._peewee,"_init"):
                self._peewee._init()
                # print("init:%speewee")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._peewee,"_init2"):
                self._peewee._init2()
                # print("init2:%speewee")
        return self._peewee
    @property
    def rogerthat(self):
        if self._rogerthat is None:
            from Jumpscale.clients.rogerthat.RogerthatFactory import RogerthatFactory
            self._rogerthat =  RogerthatFactory()
            # print("load:%srogerthat")
            if hasattr(self._rogerthat,"_init"):
                self._rogerthat._init()
                # print("init:%srogerthat")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._rogerthat,"_init2"):
                self._rogerthat._init2()
                # print("init2:%srogerthat")
        return self._rogerthat
    @property
    def mysql(self):
        if self._mysql is None:
            from Jumpscale.clients.mysql.MySQLFactory import MySQLFactory
            self._mysql =  MySQLFactory()
            # print("load:%smysql")
            if hasattr(self._mysql,"_init"):
                self._mysql._init()
                # print("init:%smysql")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._mysql,"_init2"):
                self._mysql._init2()
                # print("init2:%smysql")
        return self._mysql
    @property
    def zboot(self):
        if self._zboot is None:
            from Jumpscale.clients.zero_boot.ZerobootFactory import ZerobootFactory
            self._zboot =  ZerobootFactory()
            # print("load:%szboot")
            if hasattr(self._zboot,"_init"):
                self._zboot._init()
                # print("init:%szboot")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zboot,"_init2"):
                self._zboot._init2()
                # print("init2:%szboot")
        return self._zboot
    @property
    def webgateway(self):
        if self._webgateway is None:
            from Jumpscale.clients.webgateway.WebGatewayFactory import WebGatewayFactory
            self._webgateway =  WebGatewayFactory()
            # print("load:%swebgateway")
            if hasattr(self._webgateway,"_init"):
                self._webgateway._init()
                # print("init:%swebgateway")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._webgateway,"_init2"):
                self._webgateway._init2()
                # print("init2:%swebgateway")
        return self._webgateway
    @property
    def etcd(self):
        if self._etcd is None:
            from Jumpscale.clients.etcd.EtcdFactory import EtcdFactory
            self._etcd =  EtcdFactory()
            # print("load:%setcd")
            if hasattr(self._etcd,"_init"):
                self._etcd._init()
                # print("init:%setcd")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._etcd,"_init2"):
                self._etcd._init2()
                # print("init2:%setcd")
        return self._etcd
    @property
    def zhubdirect(self):
        if self._zhubdirect is None:
            from Jumpscale.clients.zero_hub_direct.HubDirectFactory import HubDirectFactory
            self._zhubdirect =  HubDirectFactory()
            # print("load:%szhubdirect")
            if hasattr(self._zhubdirect,"_init"):
                self._zhubdirect._init()
                # print("init:%szhubdirect")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zhubdirect,"_init2"):
                self._zhubdirect._init2()
                # print("init2:%szhubdirect")
        return self._zhubdirect
    @property
    def threefold_directory(self):
        if self._threefold_directory is None:
            from Jumpscale.clients.threefold_directory.GridCapacityFactory import GridCapacityFactory
            self._threefold_directory =  GridCapacityFactory()
            # print("load:%sthreefold_directory")
            if hasattr(self._threefold_directory,"_init"):
                self._threefold_directory._init()
                # print("init:%sthreefold_directory")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._threefold_directory,"_init2"):
                self._threefold_directory._init2()
                # print("init2:%sthreefold_directory")
        return self._threefold_directory
    @property
    def kraken(self):
        if self._kraken is None:
            from Jumpscale.clients.kraken.KrakenFactory import KrakenFactory
            self._kraken =  KrakenFactory()
            # print("load:%skraken")
            if hasattr(self._kraken,"_init"):
                self._kraken._init()
                # print("init:%skraken")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._kraken,"_init2"):
                self._kraken._init2()
                # print("init2:%skraken")
        return self._kraken
    @property
    def btc_alpha(self):
        if self._btc_alpha is None:
            from Jumpscale.clients.btc_alpha.BTCFactory import GitHubFactory
            self._btc_alpha =  GitHubFactory()
            # print("load:%sbtc_alpha")
            if hasattr(self._btc_alpha,"_init"):
                self._btc_alpha._init()
                # print("init:%sbtc_alpha")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._btc_alpha,"_init2"):
                self._btc_alpha._init2()
                # print("init2:%sbtc_alpha")
        return self._btc_alpha
    @property
    def trello(self):
        if self._trello is None:
            from Jumpscale.clients.trello.TrelloFactory import Trello
            self._trello =  Trello()
            # print("load:%strello")
            if hasattr(self._trello,"_init"):
                self._trello._init()
                # print("init:%strello")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._trello,"_init2"):
                self._trello._init2()
                # print("init2:%strello")
        return self._trello
    @property
    def sshkey(self):
        if self._sshkey is None:
            from Jumpscale.clients.sshkey.SSHKeys import SSHKeys
            self._sshkey =  SSHKeys()
            # print("load:%ssshkey")
            if hasattr(self._sshkey,"_init"):
                self._sshkey._init()
                # print("init:%ssshkey")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sshkey,"_init2"):
                self._sshkey._init2()
                # print("init2:%ssshkey")
        return self._sshkey
    @property
    def zerotier(self):
        if self._zerotier is None:
            from Jumpscale.clients.zerotier.ZerotierFactory import ZerotierFactory
            self._zerotier =  ZerotierFactory()
            # print("load:%szerotier")
            if hasattr(self._zerotier,"_init"):
                self._zerotier._init()
                # print("init:%szerotier")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zerotier,"_init2"):
                self._zerotier._init2()
                # print("init2:%szerotier")
        return self._zerotier
    @property
    def kubernetes(self):
        if self._kubernetes is None:
            from Jumpscale.clients.kubernetes.KubernetesFactory import KubernetesFactory
            self._kubernetes =  KubernetesFactory()
            # print("load:%skubernetes")
            if hasattr(self._kubernetes,"_init"):
                self._kubernetes._init()
                # print("init:%skubernetes")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._kubernetes,"_init2"):
                self._kubernetes._init2()
                # print("init2:%skubernetes")
        return self._kubernetes
    @property
    def coredns(self):
        if self._coredns is None:
            from Jumpscale.clients.coredns.CoreDNSFactory import CoreDNSFactory
            self._coredns =  CoreDNSFactory()
            # print("load:%scoredns")
            if hasattr(self._coredns,"_init"):
                self._coredns._init()
                # print("init:%scoredns")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._coredns,"_init2"):
                self._coredns._init2()
                # print("init2:%scoredns")
        return self._coredns
    @property
    def ipmi(self):
        if self._ipmi is None:
            from Jumpscale.clients.ipmi.IpmiFactory import IpmiFactory
            self._ipmi =  IpmiFactory()
            # print("load:%sipmi")
            if hasattr(self._ipmi,"_init"):
                self._ipmi._init()
                # print("init:%sipmi")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ipmi,"_init2"):
                self._ipmi._init2()
                # print("init2:%sipmi")
        return self._ipmi
    @property
    def graphite(self):
        if self._graphite is None:
            from Jumpscale.clients.graphite.GraphiteFactory import GraphiteFactory
            self._graphite =  GraphiteFactory()
            # print("load:%sgraphite")
            if hasattr(self._graphite,"_init"):
                self._graphite._init()
                # print("init:%sgraphite")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._graphite,"_init2"):
                self._graphite._init2()
                # print("init2:%sgraphite")
        return self._graphite
    @property
    def zdb(self):
        if self._zdb is None:
            from Jumpscale.clients.zdb.ZDBFactory import ZDBFactory
            self._zdb =  ZDBFactory()
            # print("load:%szdb")
            if hasattr(self._zdb,"_init"):
                self._zdb._init()
                # print("init:%szdb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zdb,"_init2"):
                self._zdb._init2()
                # print("init2:%szdb")
        return self._zdb
    @property
    def git(self):
        if self._git is None:
            from Jumpscale.clients.git.GitFactory import GitFactory
            self._git =  GitFactory()
            # print("load:%sgit")
            if hasattr(self._git,"_init"):
                self._git._init()
                # print("init:%sgit")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._git,"_init2"):
                self._git._init2()
                # print("init2:%sgit")
        return self._git
    @property
    def traefik(self):
        if self._traefik is None:
            from Jumpscale.clients.traefik.TraefikFactory import TraefikFactory
            self._traefik =  TraefikFactory()
            # print("load:%straefik")
            if hasattr(self._traefik,"_init"):
                self._traefik._init()
                # print("init:%straefik")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._traefik,"_init2"):
                self._traefik._init2()
                # print("init2:%straefik")
        return self._traefik
    @property
    def packetnet(self):
        if self._packetnet is None:
            from Jumpscale.clients.packetnet.PacketNetFactory import PacketNetFactory
            self._packetnet =  PacketNetFactory()
            # print("load:%spacketnet")
            if hasattr(self._packetnet,"_init"):
                self._packetnet._init()
                # print("init:%spacketnet")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._packetnet,"_init2"):
                self._packetnet._init2()
                # print("init2:%spacketnet")
        return self._packetnet

j.clients = group_clients()
j.core._groups["clients"] = j.clients


class group_world(JSGroup):
    def __init__(self):
        
        self._system = None
        self._hypervisor = None

    
    @property
    def system(self):
        if self._system is None:
            from DigitalMe.tools.kosmos.WorldSystem import WorldSystem
            self._system =  WorldSystem()
            # print("load:%ssystem")
            if hasattr(self._system,"_init"):
                self._system._init()
                # print("init:%ssystem")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._system,"_init2"):
                self._system._init2()
                # print("init2:%ssystem")
        return self._system
    @property
    def hypervisor(self):
        if self._hypervisor is None:
            from DigitalMe.tools.kosmos.world_example.HyperVisorCoordinator.CoordinatorHypervisor import CoordinatorHypervisor
            self._hypervisor =  CoordinatorHypervisor()
            # print("load:%shypervisor")
            if hasattr(self._hypervisor,"_init"):
                self._hypervisor._init()
                # print("init:%shypervisor")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._hypervisor,"_init2"):
                self._hypervisor._init2()
                # print("init2:%shypervisor")
        return self._hypervisor

j.world = group_world()
j.core._groups["world"] = j.world


class group_tools(JSGroup):
    def __init__(self):
        
        self._kosmos = None
        self._tfbot = None
        self._sandboxer = None
        self._fixer = None
        self._logger = None
        self._legal_contracts = None
        self._imagelib = None
        self._markdowndocs = None
        self._jinja2 = None
        self._performancetrace = None
        self._code = None
        self._codeloader = None
        self._offliner = None
        self._rexplorer = None
        self._path = None
        self._aggregator = None
        self._realityprocess = None
        self._timer = None
        self._cython = None
        self._formatters = None
        self._capacity = None
        self._team_manager = None
        self._memusagetest = None
        self._objectinspector = None
        self._dnstools = None
        self._tmux = None
        self._dash = None
        self._executor = None
        self._executorLocal = None
        self._storybot = None
        self._syncer = None
        self._code = None
        self._reportlab = None
        self._notapplicableyet = None
        self._typechecker = None
        self._console = None
        self._expect = None
        self._bash = None
        self._flist = None
        self._tarfile = None
        self._zipfile = None
        self._numtools = None
        self._issuemanager = None
        self._email = None

    
    @property
    def kosmos(self):
        if self._kosmos is None:
            from DigitalMe.tools.kosmos.kosmos_OLD.Kosmos import Kosmos
            self._kosmos =  Kosmos()
            # print("load:%skosmos")
            if hasattr(self._kosmos,"_init"):
                self._kosmos._init()
                # print("init:%skosmos")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._kosmos,"_init2"):
                self._kosmos._init2()
                # print("init2:%skosmos")
        return self._kosmos
    @property
    def tfbot(self):
        if self._tfbot is None:
            from DigitalMe.tools.tfbot.TFBotFactory import TFBotFactory
            self._tfbot =  TFBotFactory()
            # print("load:%stfbot")
            if hasattr(self._tfbot,"_init"):
                self._tfbot._init()
                # print("init:%stfbot")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tfbot,"_init2"):
                self._tfbot._init2()
                # print("init2:%stfbot")
        return self._tfbot
    @property
    def sandboxer(self):
        if self._sandboxer is None:
            from Jumpscale.tools.sandboxer.Sandboxer import Sandboxer
            self._sandboxer =  Sandboxer()
            # print("load:%ssandboxer")
            if hasattr(self._sandboxer,"_init"):
                self._sandboxer._init()
                # print("init:%ssandboxer")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sandboxer,"_init2"):
                self._sandboxer._init2()
                # print("init2:%ssandboxer")
        return self._sandboxer
    @property
    def fixer(self):
        if self._fixer is None:
            from Jumpscale.tools.fixer.Fixer import Fixer
            self._fixer =  Fixer()
            # print("load:%sfixer")
            if hasattr(self._fixer,"_init"):
                self._fixer._init()
                # print("init:%sfixer")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._fixer,"_init2"):
                self._fixer._init2()
                # print("init2:%sfixer")
        return self._fixer
    @property
    def logger(self):
        if self._logger is None:
            from Jumpscale.tools.logger.LoggerFactory import LoggerFactory
            self._logger =  LoggerFactory()
            # print("load:%slogger")
            if hasattr(self._logger,"_init"):
                self._log__init()
                # print("init:%slogger")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._logger,"_init2"):
                self._log__init2()
                # print("init2:%slogger")
        return self._logger
    @property
    def legal_contracts(self):
        if self._legal_contracts is None:
            from Jumpscale.tools.legal_contracts.LegalContractsFactory import LegalContractsFactory
            self._legal_contracts =  LegalContractsFactory()
            # print("load:%slegal_contracts")
            if hasattr(self._legal_contracts,"_init"):
                self._legal_contracts._init()
                # print("init:%slegal_contracts")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._legal_contracts,"_init2"):
                self._legal_contracts._init2()
                # print("init2:%slegal_contracts")
        return self._legal_contracts
    @property
    def imagelib(self):
        if self._imagelib is None:
            from Jumpscale.tools.imagelib.ImageLib import ImageLib
            self._imagelib =  ImageLib()
            # print("load:%simagelib")
            if hasattr(self._imagelib,"_init"):
                self._imagelib._init()
                # print("init:%simagelib")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._imagelib,"_init2"):
                self._imagelib._init2()
                # print("init2:%simagelib")
        return self._imagelib
    @property
    def markdowndocs(self):
        if self._markdowndocs is None:
            from Jumpscale.tools.markdowndocs.MarkDownDocs import MarkDownDocs
            self._markdowndocs =  MarkDownDocs()
            # print("load:%smarkdowndocs")
            if hasattr(self._markdowndocs,"_init"):
                self._markdowndocs._init()
                # print("init:%smarkdowndocs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._markdowndocs,"_init2"):
                self._markdowndocs._init2()
                # print("init2:%smarkdowndocs")
        return self._markdowndocs
    @property
    def jinja2(self):
        if self._jinja2 is None:
            from Jumpscale.tools.jinja2.Jinja2 import Jinja2
            self._jinja2 =  Jinja2()
            # print("load:%sjinja2")
            if hasattr(self._jinja2,"_init"):
                self._jinja2._init()
                # print("init:%sjinja2")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._jinja2,"_init2"):
                self._jinja2._init2()
                # print("init2:%sjinja2")
        return self._jinja2
    @property
    def performancetrace(self):
        if self._performancetrace is None:
            from Jumpscale.tools.performancetrace.PerformanceTrace import PerformanceTraceFactory
            self._performancetrace =  PerformanceTraceFactory()
            # print("load:%sperformancetrace")
            if hasattr(self._performancetrace,"_init"):
                self._performancetrace._init()
                # print("init:%sperformancetrace")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._performancetrace,"_init2"):
                self._performancetrace._init2()
                # print("init2:%sperformancetrace")
        return self._performancetrace
    @property
    def code(self):
        if self._code is None:
            from Jumpscale.tools.codeloader.CodeTools import CodeTools
            self._code =  CodeTools()
            # print("load:%scode")
            if hasattr(self._code,"_init"):
                self._code._init()
                # print("init:%scode")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._code,"_init2"):
                self._code._init2()
                # print("init2:%scode")
        return self._code
    @property
    def codeloader(self):
        if self._codeloader is None:
            from Jumpscale.tools.codeloader.CodeLoader import CodeLoader
            self._codeloader =  CodeLoader()
            # print("load:%scodeloader")
            if hasattr(self._codeloader,"_init"):
                self._codeloader._init()
                # print("init:%scodeloader")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._codeloader,"_init2"):
                self._codeloader._init2()
                # print("init2:%scodeloader")
        return self._codeloader
    @property
    def offliner(self):
        if self._offliner is None:
            from Jumpscale.tools.offliner.Offliner import Offliner
            self._offliner =  Offliner()
            # print("load:%soffliner")
            if hasattr(self._offliner,"_init"):
                self._offliner._init()
                # print("init:%soffliner")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._offliner,"_init2"):
                self._offliner._init2()
                # print("init2:%soffliner")
        return self._offliner
    @property
    def rexplorer(self):
        if self._rexplorer is None:
            from Jumpscale.tools.offliner.Rexplorer import Rexplorer
            self._rexplorer =  Rexplorer()
            # print("load:%srexplorer")
            if hasattr(self._rexplorer,"_init"):
                self._rexplorer._init()
                # print("init:%srexplorer")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._rexplorer,"_init2"):
                self._rexplorer._init2()
                # print("init2:%srexplorer")
        return self._rexplorer
    @property
    def path(self):
        if self._path is None:
            from Jumpscale.tools.path.PathFactory import PathFactory
            self._path =  PathFactory()
            # print("load:%spath")
            if hasattr(self._path,"_init"):
                self._path._init()
                # print("init:%spath")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._path,"_init2"):
                self._path._init2()
                # print("init2:%spath")
        return self._path
    @property
    def aggregator(self):
        if self._aggregator is None:
            from Jumpscale.tools.aggregator.Aggregator import Aggregator
            self._aggregator =  Aggregator()
            # print("load:%saggregator")
            if hasattr(self._aggregator,"_init"):
                self._aggregator._init()
                # print("init:%saggregator")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._aggregator,"_init2"):
                self._aggregator._init2()
                # print("init2:%saggregator")
        return self._aggregator
    @property
    def realityprocess(self):
        if self._realityprocess is None:
            from Jumpscale.tools.aggregator.RealityProcess import RealitProcess
            self._realityprocess =  RealitProcess()
            # print("load:%srealityprocess")
            if hasattr(self._realityprocess,"_init"):
                self._realityprocess._init()
                # print("init:%srealityprocess")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._realityprocess,"_init2"):
                self._realityprocess._init2()
                # print("init2:%srealityprocess")
        return self._realityprocess
    @property
    def timer(self):
        if self._timer is None:
            from Jumpscale.tools.timer.Timer import TIMER
            self._timer =  TIMER()
            # print("load:%stimer")
            if hasattr(self._timer,"_init"):
                self._timer._init()
                # print("init:%stimer")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._timer,"_init2"):
                self._timer._init2()
                # print("init2:%stimer")
        return self._timer
    @property
    def cython(self):
        if self._cython is None:
            from Jumpscale.tools.cython.CythonFactory import CythonFactory
            self._cython =  CythonFactory()
            # print("load:%scython")
            if hasattr(self._cython,"_init"):
                self._cython._init()
                # print("init:%scython")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._cython,"_init2"):
                self._cython._init2()
                # print("init2:%scython")
        return self._cython
    @property
    def formatters(self):
        if self._formatters is None:
            from Jumpscale.tools.formatters.FormattersFactory import FormattersFactory
            self._formatters =  FormattersFactory()
            # print("load:%sformatters")
            if hasattr(self._formatters,"_init"):
                self._formatters._init()
                # print("init:%sformatters")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._formatters,"_init2"):
                self._formatters._init2()
                # print("init2:%sformatters")
        return self._formatters
    @property
    def capacity(self):
        if self._capacity is None:
            from Jumpscale.tools.capacity.Factory import Factory
            self._capacity =  Factory()
            # print("load:%scapacity")
            if hasattr(self._capacity,"_init"):
                self._capacity._init()
                # print("init:%scapacity")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._capacity,"_init2"):
                self._capacity._init2()
                # print("init2:%scapacity")
        return self._capacity
    @property
    def team_manager(self):
        if self._team_manager is None:
            from Jumpscale.tools.teammgr.Teammgr import Teammgr
            self._team_manager =  Teammgr()
            # print("load:%steam_manager")
            if hasattr(self._team_manager,"_init"):
                self._team_manager._init()
                # print("init:%steam_manager")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._team_manager,"_init2"):
                self._team_manager._init2()
                # print("init2:%steam_manager")
        return self._team_manager
    @property
    def memusagetest(self):
        if self._memusagetest is None:
            from Jumpscale.tools.memusagetest.MemUsageTest import MemUsageTest
            self._memusagetest =  MemUsageTest()
            # print("load:%smemusagetest")
            if hasattr(self._memusagetest,"_init"):
                self._memusagetest._init()
                # print("init:%smemusagetest")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._memusagetest,"_init2"):
                self._memusagetest._init2()
                # print("init2:%smemusagetest")
        return self._memusagetest
    @property
    def objectinspector(self):
        if self._objectinspector is None:
            from Jumpscale.tools.objectinspector.ObjectInspector import ObjectInspector
            self._objectinspector =  ObjectInspector()
            # print("load:%sobjectinspector")
            if hasattr(self._objectinspector,"_init"):
                self._objectinspector._init()
                # print("init:%sobjectinspector")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._objectinspector,"_init2"):
                self._objectinspector._init2()
                # print("init2:%sobjectinspector")
        return self._objectinspector
    @property
    def dnstools(self):
        if self._dnstools is None:
            from Jumpscale.tools.dnstools.DNSTools import DNSTools
            self._dnstools =  DNSTools()
            # print("load:%sdnstools")
            if hasattr(self._dnstools,"_init"):
                self._dnstools._init()
                # print("init:%sdnstools")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._dnstools,"_init2"):
                self._dnstools._init2()
                # print("init2:%sdnstools")
        return self._dnstools
    @property
    def tmux(self):
        if self._tmux is None:
            from Jumpscale.tools.tmux.Tmux import Tmux
            self._tmux =  Tmux()
            # print("load:%stmux")
            if hasattr(self._tmux,"_init"):
                self._tmux._init()
                # print("init:%stmux")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tmux,"_init2"):
                self._tmux._init2()
                # print("init2:%stmux")
        return self._tmux
    @property
    def dash(self):
        if self._dash is None:
            from Jumpscale.tools.dash.DASH import DASH
            self._dash =  DASH()
            # print("load:%sdash")
            if hasattr(self._dash,"_init"):
                self._dash._init()
                # print("init:%sdash")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._dash,"_init2"):
                self._dash._init2()
                # print("init2:%sdash")
        return self._dash
    @property
    def executor(self):
        if self._executor is None:
            from Jumpscale.tools.executor.ExecutorFactory import ExecutorFactory
            self._executor =  ExecutorFactory()
            # print("load:%sexecutor")
            if hasattr(self._executor,"_init"):
                self._executor._init()
                # print("init:%sexecutor")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._executor,"_init2"):
                self._executor._init2()
                # print("init2:%sexecutor")
        return self._executor
    @property
    def executorLocal(self):
        if self._executorLocal is None:
            from Jumpscale.tools.executor.ExecutorLocal import ExecutorLocal
            self._executorLocal =  ExecutorLocal()
            # print("load:%sexecutorLocal")
            if hasattr(self._executorLocal,"_init"):
                self._executorLocal._init()
                # print("init:%sexecutorLocal")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._executorLocal,"_init2"):
                self._executorLocal._init2()
                # print("init2:%sexecutorLocal")
        return self._executorLocal
    @property
    def storybot(self):
        if self._storybot is None:
            from Jumpscale.tools.storybot.StoryBotFactory import StoryBotFactory
            self._storybot =  StoryBotFactory()
            # print("load:%sstorybot")
            if hasattr(self._storybot,"_init"):
                self._storybot._init()
                # print("init:%sstorybot")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._storybot,"_init2"):
                self._storybot._init2()
                # print("init2:%sstorybot")
        return self._storybot
    @property
    def syncer(self):
        if self._syncer is None:
            from Jumpscale.tools.syncer.SyncerFactory import SyncerFactory
            self._syncer =  SyncerFactory()
            # print("load:%ssyncer")
            if hasattr(self._syncer,"_init"):
                self._syncer._init()
                # print("init:%ssyncer")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._syncer,"_init2"):
                self._syncer._init2()
                # print("init2:%ssyncer")
        return self._syncer
    @property
    def code(self):
        if self._code is None:
            from Jumpscale.tools.codetools.CodeTools import CodeTools
            self._code =  CodeTools()
            # print("load:%scode")
            if hasattr(self._code,"_init"):
                self._code._init()
                # print("init:%scode")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._code,"_init2"):
                self._code._init2()
                # print("init2:%scode")
        return self._code
    @property
    def reportlab(self):
        if self._reportlab is None:
            from Jumpscale.tools.reportlab.ReportlabFactory import ReportlabFactory
            self._reportlab =  ReportlabFactory()
            # print("load:%sreportlab")
            if hasattr(self._reportlab,"_init"):
                self._reportlab._init()
                # print("init:%sreportlab")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._reportlab,"_init2"):
                self._reportlab._init2()
                # print("init2:%sreportlab")
        return self._reportlab
    @property
    def notapplicableyet(self):
        if self._notapplicableyet is None:
            from Jumpscale.tools.builder.Builder import Builder
            self._notapplicableyet =  Builder()
            # print("load:%snotapplicableyet")
            if hasattr(self._notapplicableyet,"_init"):
                self._notapplicableyet._init()
                # print("init:%snotapplicableyet")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._notapplicableyet,"_init2"):
                self._notapplicableyet._init2()
                # print("init2:%snotapplicableyet")
        return self._notapplicableyet
    @property
    def typechecker(self):
        if self._typechecker is None:
            from Jumpscale.tools.typechecker.TypeChecker import TypeCheckerFactory
            self._typechecker =  TypeCheckerFactory()
            # print("load:%stypechecker")
            if hasattr(self._typechecker,"_init"):
                self._typechecker._init()
                # print("init:%stypechecker")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._typechecker,"_init2"):
                self._typechecker._init2()
                # print("init2:%stypechecker")
        return self._typechecker
    @property
    def console(self):
        if self._console is None:
            from Jumpscale.tools.console.Console import Console
            self._console =  Console()
            # print("load:%sconsole")
            if hasattr(self._console,"_init"):
                self._console._init()
                # print("init:%sconsole")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._console,"_init2"):
                self._console._init2()
                # print("init2:%sconsole")
        return self._console
    @property
    def expect(self):
        if self._expect is None:
            from Jumpscale.tools.expect.Expect import ExpectTool
            self._expect =  ExpectTool()
            # print("load:%sexpect")
            if hasattr(self._expect,"_init"):
                self._expect._init()
                # print("init:%sexpect")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._expect,"_init2"):
                self._expect._init2()
                # print("init2:%sexpect")
        return self._expect
    @property
    def bash(self):
        if self._bash is None:
            from Jumpscale.sal.bash.BashFactory import BashFactory
            self._bash =  BashFactory()
            # print("load:%sbash")
            if hasattr(self._bash,"_init"):
                self._bash._init()
                # print("init:%sbash")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._bash,"_init2"):
                self._bash._init2()
                # print("init2:%sbash")
        return self._bash
    @property
    def flist(self):
        if self._flist is None:
            from Jumpscale.data.flist.FListFactory import FListFactory
            self._flist =  FListFactory()
            # print("load:%sflist")
            if hasattr(self._flist,"_init"):
                self._flist._init()
                # print("init:%sflist")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._flist,"_init2"):
                self._flist._init2()
                # print("init2:%sflist")
        return self._flist
    @property
    def tarfile(self):
        if self._tarfile is None:
            from Jumpscale.data.tarfile.TarFile import TarFileFactory
            self._tarfile =  TarFileFactory()
            # print("load:%starfile")
            if hasattr(self._tarfile,"_init"):
                self._tarfile._init()
                # print("init:%starfile")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tarfile,"_init2"):
                self._tarfile._init2()
                # print("init2:%starfile")
        return self._tarfile
    @property
    def zipfile(self):
        if self._zipfile is None:
            from Jumpscale.data.zip.ZipFile import ZipFileFactory
            self._zipfile =  ZipFileFactory()
            # print("load:%szipfile")
            if hasattr(self._zipfile,"_init"):
                self._zipfile._init()
                # print("init:%szipfile")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zipfile,"_init2"):
                self._zipfile._init2()
                # print("init2:%szipfile")
        return self._zipfile
    @property
    def numtools(self):
        if self._numtools is None:
            from Jumpscale.data.numtools.NumTools import NumTools
            self._numtools =  NumTools()
            # print("load:%snumtools")
            if hasattr(self._numtools,"_init"):
                self._numtools._init()
                # print("init:%snumtools")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._numtools,"_init2"):
                self._numtools._init2()
                # print("init2:%snumtools")
        return self._numtools
    @property
    def issuemanager(self):
        if self._issuemanager is None:
            from Jumpscale.data.issuemanager.IssueManager import IssueManager
            self._issuemanager =  IssueManager()
            # print("load:%sissuemanager")
            if hasattr(self._issuemanager,"_init"):
                self._issuemanager._init()
                # print("init:%sissuemanager")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._issuemanager,"_init2"):
                self._issuemanager._init2()
                # print("init2:%sissuemanager")
        return self._issuemanager
    @property
    def email(self):
        if self._email is None:
            from Jumpscale.data.email.Email import EmailTool
            self._email =  EmailTool()
            # print("load:%semail")
            if hasattr(self._email,"_init"):
                self._email._init()
                # print("init:%semail")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._email,"_init2"):
                self._email._init2()
                # print("init2:%semail")
        return self._email

j.tools = group_tools()
j.core._groups["tools"] = j.tools


class group_kosmos(JSGroup):
    def __init__(self):
        
        self._zos = None

    
    @property
    def zos(self):
        if self._zos is None:
            from DigitalMe.kosmos.zos.ZOSFactory import ZOSCmdFactory
            self._zos =  ZOSCmdFactory()
            # print("load:%szos")
            if hasattr(self._zos,"_init"):
                self._zos._init()
                # print("init:%szos")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zos,"_init2"):
                self._zos._init2()
                # print("init2:%szos")
        return self._zos

j.kosmos = group_kosmos()
j.core._groups["kosmos"] = j.kosmos


class group_data(JSGroup):
    def __init__(self):
        
        self._nltk = None
        self._encryption = None
        self._cachelru = None
        self._inifile = None
        self._types = None
        self._randomnames = None
        self._worksheets = None
        self._treemanager = None
        self._hash = None
        self._indexfile = None
        self._markdown = None
        self._latex = None
        self._capnp = None
        self._html = None
        self._docs = None
        self._regex = None
        self._time = None
        self._timeinterval = None
        self._schema = None
        self._serializers = None
        self._rivine = None
        self._nacl = None
        self._bcdb = None
        self._dict_editor = None
        self._idgenerator = None

    
    @property
    def nltk(self):
        if self._nltk is None:
            from DigitalMe.data.nltk.NLTK import NLTKFactory
            self._nltk =  NLTKFactory()
            # print("load:%snltk")
            if hasattr(self._nltk,"_init"):
                self._nltk._init()
                # print("init:%snltk")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._nltk,"_init2"):
                self._nltk._init2()
                # print("init2:%snltk")
        return self._nltk
    @property
    def encryption(self):
        if self._encryption is None:
            from Jumpscale.data.encryption.EncryptionFactory import EncryptionFactory
            self._encryption =  EncryptionFactory()
            # print("load:%sencryption")
            if hasattr(self._encryption,"_init"):
                self._encryption._init()
                # print("init:%sencryption")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._encryption,"_init2"):
                self._encryption._init2()
                # print("init2:%sencryption")
        return self._encryption
    @property
    def cachelru(self):
        if self._cachelru is None:
            from Jumpscale.data.cachelru.LRUCacheFactory import LRUCacheFactory
            self._cachelru =  LRUCacheFactory()
            # print("load:%scachelru")
            if hasattr(self._cachelru,"_init"):
                self._cachelru._init()
                # print("init:%scachelru")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._cachelru,"_init2"):
                self._cachelru._init2()
                # print("init2:%scachelru")
        return self._cachelru
    @property
    def inifile(self):
        if self._inifile is None:
            from Jumpscale.data.inifile.IniFile import InifileTool
            self._inifile =  InifileTool()
            # print("load:%sinifile")
            if hasattr(self._inifile,"_init"):
                self._inifile._init()
                # print("init:%sinifile")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._inifile,"_init2"):
                self._inifile._init2()
                # print("init2:%sinifile")
        return self._inifile
    @property
    def types(self):
        if self._types is None:
            from Jumpscale.data.types.Types import Types
            self._types =  Types()
            # print("load:%stypes")
            if hasattr(self._types,"_init"):
                self._types._init()
                # print("init:%stypes")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._types,"_init2"):
                self._types._init2()
                # print("init2:%stypes")
        return self._types
    @property
    def randomnames(self):
        if self._randomnames is None:
            from Jumpscale.data.random_names.RandomNames import RandomNames
            self._randomnames =  RandomNames()
            # print("load:%srandomnames")
            if hasattr(self._randomnames,"_init"):
                self._randomnames._init()
                # print("init:%srandomnames")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._randomnames,"_init2"):
                self._randomnames._init2()
                # print("init2:%srandomnames")
        return self._randomnames
    @property
    def worksheets(self):
        if self._worksheets is None:
            from Jumpscale.data.worksheets.Sheets import Sheets
            self._worksheets =  Sheets()
            # print("load:%sworksheets")
            if hasattr(self._worksheets,"_init"):
                self._worksheets._init()
                # print("init:%sworksheets")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._worksheets,"_init2"):
                self._worksheets._init2()
                # print("init2:%sworksheets")
        return self._worksheets
    @property
    def treemanager(self):
        if self._treemanager is None:
            from Jumpscale.data.treemanager.Treemanager import TreemanagerFactory
            self._treemanager =  TreemanagerFactory()
            # print("load:%streemanager")
            if hasattr(self._treemanager,"_init"):
                self._treemanager._init()
                # print("init:%streemanager")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._treemanager,"_init2"):
                self._treemanager._init2()
                # print("init2:%streemanager")
        return self._treemanager
    @property
    def hash(self):
        if self._hash is None:
            from Jumpscale.data.hash.HashTool import HashTool
            self._hash =  HashTool()
            # print("load:%shash")
            if hasattr(self._hash,"_init"):
                self._hash._init()
                # print("init:%shash")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._hash,"_init2"):
                self._hash._init2()
                # print("init2:%shash")
        return self._hash
    @property
    def indexfile(self):
        if self._indexfile is None:
            from Jumpscale.data.indexFile.IndexFiles import IndexDB
            self._indexfile =  IndexDB()
            # print("load:%sindexfile")
            if hasattr(self._indexfile,"_init"):
                self._indexfile._init()
                # print("init:%sindexfile")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._indexfile,"_init2"):
                self._indexfile._init2()
                # print("init2:%sindexfile")
        return self._indexfile
    @property
    def markdown(self):
        if self._markdown is None:
            from Jumpscale.data.markdown.MarkdownFactory import MarkdownFactory
            self._markdown =  MarkdownFactory()
            # print("load:%smarkdown")
            if hasattr(self._markdown,"_init"):
                self._markdown._init()
                # print("init:%smarkdown")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._markdown,"_init2"):
                self._markdown._init2()
                # print("init2:%smarkdown")
        return self._markdown
    @property
    def latex(self):
        if self._latex is None:
            from Jumpscale.data.latex.Latex import Latex
            self._latex =  Latex()
            # print("load:%slatex")
            if hasattr(self._latex,"_init"):
                self._latex._init()
                # print("init:%slatex")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._latex,"_init2"):
                self._latex._init2()
                # print("init2:%slatex")
        return self._latex
    @property
    def capnp(self):
        if self._capnp is None:
            from Jumpscale.data.capnp.Capnp import Capnp
            self._capnp =  Capnp()
            # print("load:%scapnp")
            if hasattr(self._capnp,"_init"):
                self._capnp._init()
                # print("init:%scapnp")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._capnp,"_init2"):
                self._capnp._init2()
                # print("init2:%scapnp")
        return self._capnp
    @property
    def html(self):
        if self._html is None:
            from Jumpscale.data.html.HTMLFactory import HTMLFactory
            self._html =  HTMLFactory()
            # print("load:%shtml")
            if hasattr(self._html,"_init"):
                self._html._init()
                # print("init:%shtml")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._html,"_init2"):
                self._html._init2()
                # print("init2:%shtml")
        return self._html
    @property
    def docs(self):
        if self._docs is None:
            from Jumpscale.data.docs.DocsFactory import DocsFactory
            self._docs =  DocsFactory()
            # print("load:%sdocs")
            if hasattr(self._docs,"_init"):
                self._docs._init()
                # print("init:%sdocs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._docs,"_init2"):
                self._docs._init2()
                # print("init2:%sdocs")
        return self._docs
    @property
    def regex(self):
        if self._regex is None:
            from Jumpscale.data.regex.RegexTools import RegexTools
            self._regex =  RegexTools()
            # print("load:%sregex")
            if hasattr(self._regex,"_init"):
                self._regex._init()
                # print("init:%sregex")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._regex,"_init2"):
                self._regex._init2()
                # print("init2:%sregex")
        return self._regex
    @property
    def time(self):
        if self._time is None:
            from Jumpscale.data.time.Time import Time_
            self._time =  Time_()
            # print("load:%stime")
            if hasattr(self._time,"_init"):
                self._time._init()
                # print("init:%stime")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._time,"_init2"):
                self._time._init2()
                # print("init2:%stime")
        return self._time
    @property
    def timeinterval(self):
        if self._timeinterval is None:
            from Jumpscale.data.time.TimeInterval import TimeInterval
            self._timeinterval =  TimeInterval()
            # print("load:%stimeinterval")
            if hasattr(self._timeinterval,"_init"):
                self._timeinterval._init()
                # print("init:%stimeinterval")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._timeinterval,"_init2"):
                self._timeinterval._init2()
                # print("init2:%stimeinterval")
        return self._timeinterval
    @property
    def schema(self):
        if self._schema is None:
            from Jumpscale.data.schema.SchemaFactory import SchemaFactory
            self._schema =  SchemaFactory()
            # print("load:%sschema")
            if hasattr(self._schema,"_init"):
                self._schema._init()
                # print("init:%sschema")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._schema,"_init2"):
                self._schema._init2()
                # print("init2:%sschema")
        return self._schema
    @property
    def serializers(self):
        if self._serializers is None:
            from Jumpscale.data.serializers.SerializersFactory import SerializersFactory
            self._serializers =  SerializersFactory()
            # print("load:%sserializers")
            if hasattr(self._serializers,"_init"):
                self._serializers._init()
                # print("init:%sserializers")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._serializers,"_init2"):
                self._serializers._init2()
                # print("init2:%sserializers")
        return self._serializers
    @property
    def rivine(self):
        if self._rivine is None:
            from Jumpscale.data.rivine.RivineDataFactory import RivineDataFactory
            self._rivine =  RivineDataFactory()
            # print("load:%srivine")
            if hasattr(self._rivine,"_init"):
                self._rivine._init()
                # print("init:%srivine")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._rivine,"_init2"):
                self._rivine._init2()
                # print("init2:%srivine")
        return self._rivine
    @property
    def nacl(self):
        if self._nacl is None:
            from Jumpscale.data.nacl.NACLFactory import NACLFactory
            self._nacl =  NACLFactory()
            # print("load:%snacl")
            if hasattr(self._nacl,"_init"):
                self._nacl._init()
                # print("init:%snacl")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._nacl,"_init2"):
                self._nacl._init2()
                # print("init2:%snacl")
        return self._nacl
    @property
    def bcdb(self):
        if self._bcdb is None:
            from Jumpscale.data.bcdb.BCDBFactory import BCDBFactory
            self._bcdb =  BCDBFactory()
            # print("load:%sbcdb")
            if hasattr(self._bcdb,"_init"):
                self._bcdb._init()
                # print("init:%sbcdb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._bcdb,"_init2"):
                self._bcdb._init2()
                # print("init2:%sbcdb")
        return self._bcdb
    @property
    def dict_editor(self):
        if self._dict_editor is None:
            from Jumpscale.data.dicteditor.DictEditor import DictEditorFactory
            self._dict_editor =  DictEditorFactory()
            # print("load:%sdict_editor")
            if hasattr(self._dict_editor,"_init"):
                self._dict_editor._init()
                # print("init:%sdict_editor")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._dict_editor,"_init2"):
                self._dict_editor._init2()
                # print("init2:%sdict_editor")
        return self._dict_editor
    @property
    def idgenerator(self):
        if self._idgenerator is None:
            from Jumpscale.data.idgenerator.IDGenerator import IDGenerator
            self._idgenerator =  IDGenerator()
            # print("load:%sidgenerator")
            if hasattr(self._idgenerator,"_init"):
                self._idgenerator._init()
                # print("init:%sidgenerator")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._idgenerator,"_init2"):
                self._idgenerator._init2()
                # print("init2:%sidgenerator")
        return self._idgenerator

j.data = group_data()
j.core._groups["data"] = j.data


class group_servers(JSGroup):
    def __init__(self):
        
        self._gedis = None
        self._digitalme = None
        self._myjobs = None
        self._raftserver = None
        self._dns = None
        self._errbot = None
        self._openresty = None
        self._redis_logger = None
        self._web = None
        self._etcd = None
        self._capacity = None
        self._zdb = None
        self._jsrun = None

    
    @property
    def gedis(self):
        if self._gedis is None:
            from DigitalMe.servers.gedis.GedisFactory import GedisFactory
            self._gedis =  GedisFactory()
            # print("load:%sgedis")
            if hasattr(self._gedis,"_init"):
                self._gedis._init()
                # print("init:%sgedis")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._gedis,"_init2"):
                self._gedis._init2()
                # print("init2:%sgedis")
        return self._gedis
    @property
    def digitalme(self):
        if self._digitalme is None:
            from DigitalMe.servers.digitalme.DigitalMe import DigitalMe
            self._digitalme =  DigitalMe()
            # print("load:%sdigitalme")
            if hasattr(self._digitalme,"_init"):
                self._digitalme._init()
                # print("init:%sdigitalme")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._digitalme,"_init2"):
                self._digitalme._init2()
                # print("init2:%sdigitalme")
        return self._digitalme
    @property
    def myjobs(self):
        if self._myjobs is None:
            from DigitalMe.servers.myjobs.MyJobs import MyJobs
            self._myjobs =  MyJobs()
            # print("load:%smyjobs")
            if hasattr(self._myjobs,"_init"):
                self._myjobs._init()
                # print("init:%smyjobs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._myjobs,"_init2"):
                self._myjobs._init2()
                # print("init2:%smyjobs")
        return self._myjobs
    @property
    def raftserver(self):
        if self._raftserver is None:
            from DigitalMe.servers.raft.RaftServerFactory import RaftServerFactory
            self._raftserver =  RaftServerFactory()
            # print("load:%sraftserver")
            if hasattr(self._raftserver,"_init"):
                self._raftserver._init()
                # print("init:%sraftserver")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._raftserver,"_init2"):
                self._raftserver._init2()
                # print("init2:%sraftserver")
        return self._raftserver
    @property
    def dns(self):
        if self._dns is None:
            from DigitalMe.servers.dns.DNSServerFactory import DNSServerFactory
            self._dns =  DNSServerFactory()
            # print("load:%sdns")
            if hasattr(self._dns,"_init"):
                self._dns._init()
                # print("init:%sdns")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._dns,"_init2"):
                self._dns._init2()
                # print("init2:%sdns")
        return self._dns
    @property
    def errbot(self):
        if self._errbot is None:
            from Jumpscale.servers.errbot.ErrBotFactory import ErrBotFactory
            self._errbot =  ErrBotFactory()
            # print("load:%serrbot")
            if hasattr(self._errbot,"_init"):
                self._errbot._init()
                # print("init:%serrbot")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._errbot,"_init2"):
                self._errbot._init2()
                # print("init2:%serrbot")
        return self._errbot
    @property
    def openresty(self):
        if self._openresty is None:
            from Jumpscale.servers.openresty.OpenRestyFactory import OpenRestyFactory
            self._openresty =  OpenRestyFactory()
            # print("load:%sopenresty")
            if hasattr(self._openresty,"_init"):
                self._openresty._init()
                # print("init:%sopenresty")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._openresty,"_init2"):
                self._openresty._init2()
                # print("init2:%sopenresty")
        return self._openresty
    @property
    def redis_logger(self):
        if self._redis_logger is None:
            from Jumpscale.servers.redis.RedisServer import RedisLoggingServer
            self._redis_logger =  RedisLoggingServer()
            # print("load:%sredis_logger")
            if hasattr(self._redis_logger,"_init"):
                self._redis_logger._init()
                # print("init:%sredis_logger")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._redis_logger,"_init2"):
                self._redis_logger._init2()
                # print("init2:%sredis_logger")
        return self._redis_logger
    @property
    def web(self):
        if self._web is None:
            from Jumpscale.servers.webserver.JSWebServers import JSWebServers
            self._web =  JSWebServers()
            # print("load:%sweb")
            if hasattr(self._web,"_init"):
                self._web._init()
                # print("init:%sweb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._web,"_init2"):
                self._web._init2()
                # print("init2:%sweb")
        return self._web
    @property
    def etcd(self):
        if self._etcd is None:
            from Jumpscale.servers.etcd.EtcdServer import EtcdServer
            self._etcd =  EtcdServer()
            # print("load:%setcd")
            if hasattr(self._etcd,"_init"):
                self._etcd._init()
                # print("init:%setcd")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._etcd,"_init2"):
                self._etcd._init2()
                # print("init2:%setcd")
        return self._etcd
    @property
    def capacity(self):
        if self._capacity is None:
            from Jumpscale.servers.grid_capacity.CapacityFactory import CapacityFactory
            self._capacity =  CapacityFactory()
            # print("load:%scapacity")
            if hasattr(self._capacity,"_init"):
                self._capacity._init()
                # print("init:%scapacity")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._capacity,"_init2"):
                self._capacity._init2()
                # print("init2:%scapacity")
        return self._capacity
    @property
    def zdb(self):
        if self._zdb is None:
            from Jumpscale.servers.zdb.ZDBServer import ZDBServer
            self._zdb =  ZDBServer()
            # print("load:%szdb")
            if hasattr(self._zdb,"_init"):
                self._zdb._init()
                # print("init:%szdb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zdb,"_init2"):
                self._zdb._init2()
                # print("init2:%szdb")
        return self._zdb
    @property
    def jsrun(self):
        if self._jsrun is None:
            from Jumpscale.servers.jsrun.JSRun import JSRun
            self._jsrun =  JSRun()
            # print("load:%sjsrun")
            if hasattr(self._jsrun,"_init"):
                self._jsrun._init()
                # print("init:%sjsrun")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._jsrun,"_init2"):
                self._jsrun._init2()
                # print("init2:%sjsrun")
        return self._jsrun

j.servers = group_servers()
j.core._groups["servers"] = j.servers


class group_sal(JSGroup):
    def __init__(self):
        
        self._coredns = None
        self._docker = None
        self._qemu_img = None
        self._btrfs = None
        self._nettools = None
        self._ssl = None
        self._disklayout = None
        self._nic = None
        self._nfs = None
        self._sshd = None
        self._hostsfile = None
        self._rsync = None
        self._unix = None
        self._tls = None
        self._samba = None
        self._nginx = None
        self._netconfig = None
        self._kvm = None
        self._windows = None
        self._ufw = None
        self._bind = None
        self._fswalker = None
        self._fs = None
        self._ubuntu = None
        self._openvswitch = None
        self._dnsmasq = None
        self._process = None

    
    @property
    def coredns(self):
        if self._coredns is None:
            from Jumpscale.clients.coredns.alternative.CoreDnsFactory import CoreDnsFactory
            self._coredns =  CoreDnsFactory()
            # print("load:%scoredns")
            if hasattr(self._coredns,"_init"):
                self._coredns._init()
                # print("init:%scoredns")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._coredns,"_init2"):
                self._coredns._init2()
                # print("init2:%scoredns")
        return self._coredns
    @property
    def docker(self):
        if self._docker is None:
            from Jumpscale.tools.docker.Docker import Docker
            self._docker =  Docker()
            # print("load:%sdocker")
            if hasattr(self._docker,"_init"):
                self._docker._init()
                # print("init:%sdocker")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._docker,"_init2"):
                self._docker._init2()
                # print("init2:%sdocker")
        return self._docker
    @property
    def qemu_img(self):
        if self._qemu_img is None:
            from Jumpscale.sal.qemu_img.Qemu_img import QemuImg
            self._qemu_img =  QemuImg()
            # print("load:%sqemu_img")
            if hasattr(self._qemu_img,"_init"):
                self._qemu_img._init()
                # print("init:%sqemu_img")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._qemu_img,"_init2"):
                self._qemu_img._init2()
                # print("init2:%sqemu_img")
        return self._qemu_img
    @property
    def btrfs(self):
        if self._btrfs is None:
            from Jumpscale.sal.btrfs.BtrfsExtension import BtfsExtensionFactory
            self._btrfs =  BtfsExtensionFactory()
            # print("load:%sbtrfs")
            if hasattr(self._btrfs,"_init"):
                self._btrfs._init()
                # print("init:%sbtrfs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._btrfs,"_init2"):
                self._btrfs._init2()
                # print("init2:%sbtrfs")
        return self._btrfs
    @property
    def nettools(self):
        if self._nettools is None:
            from Jumpscale.sal.nettools.NetTools import NetTools
            self._nettools =  NetTools()
            # print("load:%snettools")
            if hasattr(self._nettools,"_init"):
                self._nettools._init()
                # print("init:%snettools")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._nettools,"_init2"):
                self._nettools._init2()
                # print("init2:%snettools")
        return self._nettools
    @property
    def ssl(self):
        if self._ssl is None:
            from Jumpscale.sal.ssl.SSLFactory import SSLFactory
            self._ssl =  SSLFactory()
            # print("load:%sssl")
            if hasattr(self._ssl,"_init"):
                self._ssl._init()
                # print("init:%sssl")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ssl,"_init2"):
                self._ssl._init2()
                # print("init2:%sssl")
        return self._ssl
    @property
    def disklayout(self):
        if self._disklayout is None:
            from Jumpscale.sal.disklayout.DiskManager import DiskManager
            self._disklayout =  DiskManager()
            # print("load:%sdisklayout")
            if hasattr(self._disklayout,"_init"):
                self._disklayout._init()
                # print("init:%sdisklayout")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._disklayout,"_init2"):
                self._disklayout._init2()
                # print("init2:%sdisklayout")
        return self._disklayout
    @property
    def nic(self):
        if self._nic is None:
            from Jumpscale.sal.nic.UnixNetworkManager import UnixNetworkManager
            self._nic =  UnixNetworkManager()
            # print("load:%snic")
            if hasattr(self._nic,"_init"):
                self._nic._init()
                # print("init:%snic")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._nic,"_init2"):
                self._nic._init2()
                # print("init2:%snic")
        return self._nic
    @property
    def nfs(self):
        if self._nfs is None:
            from Jumpscale.sal.nfs.NFS import NFS
            self._nfs =  NFS()
            # print("load:%snfs")
            if hasattr(self._nfs,"_init"):
                self._nfs._init()
                # print("init:%snfs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._nfs,"_init2"):
                self._nfs._init2()
                # print("init2:%snfs")
        return self._nfs
    @property
    def sshd(self):
        if self._sshd is None:
            from Jumpscale.sal.sshd.SSHD import SSHD
            self._sshd =  SSHD()
            # print("load:%ssshd")
            if hasattr(self._sshd,"_init"):
                self._sshd._init()
                # print("init:%ssshd")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sshd,"_init2"):
                self._sshd._init2()
                # print("init2:%ssshd")
        return self._sshd
    @property
    def hostsfile(self):
        if self._hostsfile is None:
            from Jumpscale.sal.hostfile.HostFile import HostFile
            self._hostsfile =  HostFile()
            # print("load:%shostsfile")
            if hasattr(self._hostsfile,"_init"):
                self._hostsfile._init()
                # print("init:%shostsfile")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._hostsfile,"_init2"):
                self._hostsfile._init2()
                # print("init2:%shostsfile")
        return self._hostsfile
    @property
    def rsync(self):
        if self._rsync is None:
            from Jumpscale.sal.rsync.RsyncFactory import RsyncFactory
            self._rsync =  RsyncFactory()
            # print("load:%srsync")
            if hasattr(self._rsync,"_init"):
                self._rsync._init()
                # print("init:%srsync")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._rsync,"_init2"):
                self._rsync._init2()
                # print("init2:%srsync")
        return self._rsync
    @property
    def unix(self):
        if self._unix is None:
            from Jumpscale.sal.unix.Unix import UnixSystem
            self._unix =  UnixSystem()
            # print("load:%sunix")
            if hasattr(self._unix,"_init"):
                self._unix._init()
                # print("init:%sunix")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._unix,"_init2"):
                self._unix._init2()
                # print("init2:%sunix")
        return self._unix
    @property
    def tls(self):
        if self._tls is None:
            from Jumpscale.sal.tls.TLSFactory import TLSFactory
            self._tls =  TLSFactory()
            # print("load:%stls")
            if hasattr(self._tls,"_init"):
                self._tls._init()
                # print("init:%stls")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tls,"_init2"):
                self._tls._init2()
                # print("init2:%stls")
        return self._tls
    @property
    def samba(self):
        if self._samba is None:
            from Jumpscale.sal.samba.Samba import Samba
            self._samba =  Samba()
            # print("load:%ssamba")
            if hasattr(self._samba,"_init"):
                self._samba._init()
                # print("init:%ssamba")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._samba,"_init2"):
                self._samba._init2()
                # print("init2:%ssamba")
        return self._samba
    @property
    def nginx(self):
        if self._nginx is None:
            from Jumpscale.sal.nginx.Nginx import NginxFactory
            self._nginx =  NginxFactory()
            # print("load:%snginx")
            if hasattr(self._nginx,"_init"):
                self._nginx._init()
                # print("init:%snginx")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._nginx,"_init2"):
                self._nginx._init2()
                # print("init2:%snginx")
        return self._nginx
    @property
    def netconfig(self):
        if self._netconfig is None:
            from Jumpscale.sal.netconfig.Netconfig import Netconfig
            self._netconfig =  Netconfig()
            # print("load:%snetconfig")
            if hasattr(self._netconfig,"_init"):
                self._netconfig._init()
                # print("init:%snetconfig")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._netconfig,"_init2"):
                self._netconfig._init2()
                # print("init2:%snetconfig")
        return self._netconfig
    @property
    def kvm(self):
        if self._kvm is None:
            from Jumpscale.sal.kvm.KVM import KVM
            self._kvm =  KVM()
            # print("load:%skvm")
            if hasattr(self._kvm,"_init"):
                self._kvm._init()
                # print("init:%skvm")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._kvm,"_init2"):
                self._kvm._init2()
                # print("init2:%skvm")
        return self._kvm
    @property
    def windows(self):
        if self._windows is None:
            from Jumpscale.sal.windows.Windows import WindowsSystem
            self._windows =  WindowsSystem()
            # print("load:%swindows")
            if hasattr(self._windows,"_init"):
                self._windows._init()
                # print("init:%swindows")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._windows,"_init2"):
                self._windows._init2()
                # print("init2:%swindows")
        return self._windows
    @property
    def ufw(self):
        if self._ufw is None:
            from Jumpscale.sal.ufw.UFWManager import UFWManager
            self._ufw =  UFWManager()
            # print("load:%sufw")
            if hasattr(self._ufw,"_init"):
                self._ufw._init()
                # print("init:%sufw")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ufw,"_init2"):
                self._ufw._init2()
                # print("init2:%sufw")
        return self._ufw
    @property
    def bind(self):
        if self._bind is None:
            from Jumpscale.sal.bind.BindDNS import BindDNS
            self._bind =  BindDNS()
            # print("load:%sbind")
            if hasattr(self._bind,"_init"):
                self._bind._init()
                # print("init:%sbind")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._bind,"_init2"):
                self._bind._init2()
                # print("init2:%sbind")
        return self._bind
    @property
    def fswalker(self):
        if self._fswalker is None:
            from Jumpscale.sal.fs.SystemFSWalker import SystemFSWalker
            self._fswalker =  SystemFSWalker()
            # print("load:%sfswalker")
            if hasattr(self._fswalker,"_init"):
                self._fswalker._init()
                # print("init:%sfswalker")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._fswalker,"_init2"):
                self._fswalker._init2()
                # print("init2:%sfswalker")
        return self._fswalker
    @property
    def fs(self):
        if self._fs is None:
            from Jumpscale.sal.fs.SystemFS import SystemFS
            self._fs =  SystemFS()
            # print("load:%sfs")
            if hasattr(self._fs,"_init"):
                self._fs._init()
                # print("init:%sfs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._fs,"_init2"):
                self._fs._init2()
                # print("init2:%sfs")
        return self._fs
    @property
    def ubuntu(self):
        if self._ubuntu is None:
            from Jumpscale.sal.ubuntu.Ubuntu import Ubuntu
            self._ubuntu =  Ubuntu()
            # print("load:%subuntu")
            if hasattr(self._ubuntu,"_init"):
                self._ubuntu._init()
                # print("init:%subuntu")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ubuntu,"_init2"):
                self._ubuntu._init2()
                # print("init2:%subuntu")
        return self._ubuntu
    @property
    def openvswitch(self):
        if self._openvswitch is None:
            from Jumpscale.sal.openvswitch.NetConfigFactory import NetConfigFactory
            self._openvswitch =  NetConfigFactory()
            # print("load:%sopenvswitch")
            if hasattr(self._openvswitch,"_init"):
                self._openvswitch._init()
                # print("init:%sopenvswitch")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._openvswitch,"_init2"):
                self._openvswitch._init2()
                # print("init2:%sopenvswitch")
        return self._openvswitch
    @property
    def dnsmasq(self):
        if self._dnsmasq is None:
            from Jumpscale.sal.dnsmasq.DnsmasqFactory import DnsmasqFactory
            self._dnsmasq =  DnsmasqFactory()
            # print("load:%sdnsmasq")
            if hasattr(self._dnsmasq,"_init"):
                self._dnsmasq._init()
                # print("init:%sdnsmasq")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._dnsmasq,"_init2"):
                self._dnsmasq._init2()
                # print("init2:%sdnsmasq")
        return self._dnsmasq
    @property
    def process(self):
        if self._process is None:
            from Jumpscale.sal.process.SystemProcess import SystemProcess
            self._process =  SystemProcess()
            # print("load:%sprocess")
            if hasattr(self._process,"_init"):
                self._process._init()
                # print("init:%sprocess")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._process,"_init2"):
                self._process._init2()
                # print("init2:%sprocess")
        return self._process

j.sal = group_sal()
j.core._groups["sal"] = j.sal


class group_tutorials(JSGroup):
    def __init__(self):
        
        self._base = None

    
    @property
    def base(self):
        if self._base is None:
            from Jumpscale.tutorials.base.Tutorial import Tutorial
            self._base =  Tutorial()
            # print("load:%sbase")
            if hasattr(self._base,"_init"):
                self._base._init()
                # print("init:%sbase")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._base,"_init2"):
                self._base._init2()
                # print("init2:%sbase")
        return self._base

j.tutorials = group_tutorials()
j.core._groups["tutorials"] = j.tutorials


class group_data_units(JSGroup):
    def __init__(self):
        
        self._sizes = None

    
    @property
    def sizes(self):
        if self._sizes is None:
            from Jumpscale.data.numtools.units.Units import Bytes
            self._sizes =  Bytes()
            # print("load:%ssizes")
            if hasattr(self._sizes,"_init"):
                self._sizes._init()
                # print("init:%ssizes")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sizes,"_init2"):
                self._sizes._init2()
                # print("init2:%ssizes")
        return self._sizes

j.data_units = group_data_units()
j.core._groups["data_units"] = j.data_units


class group_builder(JSGroup):
    def __init__(self):
        
        self._systemtools = None
        self._tools = None
        self._web = None
        self._network = None
        self._runtimes = None
        self.__template = None
        self._storage = None
        self._libs = None
        self._libs = None
        self._blockchain = None
        self._system = None
        self._db = None
        self._monitoring = None
        self.__template = None
        self._apps = None
        self._buildenv = None

    
    @property
    def systemtools(self):
        if self._systemtools is None:
            from Jumpscale.builder.systemtools.BuilderSystemToolsFactory import BuilderSystemToolsFactory
            self._systemtools =  BuilderSystemToolsFactory()
            # print("load:%ssystemtools")
            if hasattr(self._systemtools,"_init"):
                self._systemtools._init()
                # print("init:%ssystemtools")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._systemtools,"_init2"):
                self._systemtools._init2()
                # print("init2:%ssystemtools")
        return self._systemtools
    @property
    def tools(self):
        if self._tools is None:
            from Jumpscale.builder.tools.BuilderTools import BuilderTools
            self._tools =  BuilderTools()
            # print("load:%stools")
            if hasattr(self._tools,"_init"):
                self._tools._init()
                # print("init:%stools")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tools,"_init2"):
                self._tools._init2()
                # print("init2:%stools")
        return self._tools
    @property
    def web(self):
        if self._web is None:
            from Jumpscale.builder.web.BuilderWebFactory import BuilderWebFactory
            self._web =  BuilderWebFactory()
            # print("load:%sweb")
            if hasattr(self._web,"_init"):
                self._web._init()
                # print("init:%sweb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._web,"_init2"):
                self._web._init2()
                # print("init2:%sweb")
        return self._web
    @property
    def network(self):
        if self._network is None:
            from Jumpscale.builder.network.BuilderNetworkFactory import BuilderNetworkFactory
            self._network =  BuilderNetworkFactory()
            # print("load:%snetwork")
            if hasattr(self._network,"_init"):
                self._network._init()
                # print("init:%snetwork")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._network,"_init2"):
                self._network._init2()
                # print("init2:%snetwork")
        return self._network
    @property
    def runtimes(self):
        if self._runtimes is None:
            from Jumpscale.builder.runtimes.BuilderRuntimesFactory import BuilderRuntimesFactory
            self._runtimes =  BuilderRuntimesFactory()
            # print("load:%sruntimes")
            if hasattr(self._runtimes,"_init"):
                self._runtimes._init()
                # print("init:%sruntimes")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._runtimes,"_init2"):
                self._runtimes._init2()
                # print("init2:%sruntimes")
        return self._runtimes
    @property
    def _template(self):
        if self.__template is None:
            from Jumpscale.builder.TEMPLATE.BuilderGrafanaFactory import GrafanaFactory
            self.__template =  GrafanaFactory()
            # print("load:%s_template")
            if hasattr(self.__template,"_init"):
                self.__template._init()
                # print("init:%s_template")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self.__template,"_init2"):
                self.__template._init2()
                # print("init2:%s_template")
        return self.__template
    @property
    def storage(self):
        if self._storage is None:
            from Jumpscale.builder.storage.BuilderStorageFactory import BuilderAppsFactory
            self._storage =  BuilderAppsFactory()
            # print("load:%sstorage")
            if hasattr(self._storage,"_init"):
                self._storage._init()
                # print("init:%sstorage")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._storage,"_init2"):
                self._storage._init2()
                # print("init2:%sstorage")
        return self._storage
    @property
    def libs(self):
        if self._libs is None:
            from Jumpscale.builder.libs.BuilderLibs import BuilderLibs
            self._libs =  BuilderLibs()
            # print("load:%slibs")
            if hasattr(self._libs,"_init"):
                self._libs._init()
                # print("init:%slibs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._libs,"_init2"):
                self._libs._init2()
                # print("init2:%slibs")
        return self._libs
    @property
    def libs(self):
        if self._libs is None:
            from Jumpscale.builder.libs.BuilderLibsFactory import BuilderLibsFactory
            self._libs =  BuilderLibsFactory()
            # print("load:%slibs")
            if hasattr(self._libs,"_init"):
                self._libs._init()
                # print("init:%slibs")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._libs,"_init2"):
                self._libs._init2()
                # print("init2:%slibs")
        return self._libs
    @property
    def blockchain(self):
        if self._blockchain is None:
            from Jumpscale.builder.blockchain.BuilderBlockchainFactory import BuilderBlockchainFactory
            self._blockchain =  BuilderBlockchainFactory()
            # print("load:%sblockchain")
            if hasattr(self._blockchain,"_init"):
                self._blockchain._init()
                # print("init:%sblockchain")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._blockchain,"_init2"):
                self._blockchain._init2()
                # print("init2:%sblockchain")
        return self._blockchain
    @property
    def system(self):
        if self._system is None:
            from Jumpscale.builder.system.BuilderSystemFactory import BuilderSystemPackage
            self._system =  BuilderSystemPackage()
            # print("load:%ssystem")
            if hasattr(self._system,"_init"):
                self._system._init()
                # print("init:%ssystem")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._system,"_init2"):
                self._system._init2()
                # print("init2:%ssystem")
        return self._system
    @property
    def db(self):
        if self._db is None:
            from Jumpscale.builder.db.BuildDBFactory import BuildDBFactory
            self._db =  BuildDBFactory()
            # print("load:%sdb")
            if hasattr(self._db,"_init"):
                self._db._init()
                # print("init:%sdb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._db,"_init2"):
                self._db._init2()
                # print("init2:%sdb")
        return self._db
    @property
    def monitoring(self):
        if self._monitoring is None:
            from Jumpscale.builder.monitoring.BuilderMonitoringFactory import BuilderMonitoringFactory
            self._monitoring =  BuilderMonitoringFactory()
            # print("load:%smonitoring")
            if hasattr(self._monitoring,"_init"):
                self._monitoring._init()
                # print("init:%smonitoring")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._monitoring,"_init2"):
                self._monitoring._init2()
                # print("init2:%smonitoring")
        return self._monitoring
    @property
    def _template(self):
        if self.__template is None:
            from Jumpscale.builder.monitoring.BuilderGrafanaFactory import BuilderGrafanaFactory
            self.__template =  BuilderGrafanaFactory()
            # print("load:%s_template")
            if hasattr(self.__template,"_init"):
                self.__template._init()
                # print("init:%s_template")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self.__template,"_init2"):
                self.__template._init2()
                # print("init2:%s_template")
        return self.__template
    @property
    def apps(self):
        if self._apps is None:
            from Jumpscale.builder.apps.BuilderAppsFactory import BuilderAppsFactory
            self._apps =  BuilderAppsFactory()
            # print("load:%sapps")
            if hasattr(self._apps,"_init"):
                self._apps._init()
                # print("init:%sapps")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._apps,"_init2"):
                self._apps._init2()
                # print("init2:%sapps")
        return self._apps
    @property
    def buildenv(self):
        if self._buildenv is None:
            from Jumpscale.builder.buildenv.BuildEnv import BuildEnv
            self._buildenv =  BuildEnv()
            # print("load:%sbuildenv")
            if hasattr(self._buildenv,"_init"):
                self._buildenv._init()
                # print("init:%sbuildenv")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._buildenv,"_init2"):
                self._buildenv._init2()
                # print("init2:%sbuildenv")
        return self._buildenv

j.builder = group_builder()
j.core._groups["builder"] = j.builder


class group_sal_zos(JSGroup):
    def __init__(self):
        
        self._farm = None
        self._zt_bootstrap = None
        self._stats_collector = None
        self._zrobot = None
        self._zerodb = None
        self._network = None
        self._grafana = None
        self._minio = None
        self._mongodb = None
        self._storagepools = None
        self._influx = None
        self._primitives = None
        self._capacity = None
        self._containers = None
        self._zstor = None
        self._vm = None
        self._sandbox = None
        self._tfchain = None
        self._disks = None
        self._ftpclient = None
        self._etcd = None
        self._ippoolmanager = None
        self._node = None
        self._coredns = None
        self._hypervisor = None
        self._traefik = None
        self._gateway = None

    
    @property
    def farm(self):
        if self._farm is None:
            from Jumpscale.sal_zos.farm.FarmFactory import FarmFactory
            self._farm =  FarmFactory()
            # print("load:%sfarm")
            if hasattr(self._farm,"_init"):
                self._farm._init()
                # print("init:%sfarm")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._farm,"_init2"):
                self._farm._init2()
                # print("init2:%sfarm")
        return self._farm
    @property
    def zt_bootstrap(self):
        if self._zt_bootstrap is None:
            from Jumpscale.sal_zos.zerotier_bootstrap.ZerotierBootstrapFactory import ZerotierBootstrapFactory
            self._zt_bootstrap =  ZerotierBootstrapFactory()
            # print("load:%szt_bootstrap")
            if hasattr(self._zt_bootstrap,"_init"):
                self._zt_bootstrap._init()
                # print("init:%szt_bootstrap")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zt_bootstrap,"_init2"):
                self._zt_bootstrap._init2()
                # print("init2:%szt_bootstrap")
        return self._zt_bootstrap
    @property
    def stats_collector(self):
        if self._stats_collector is None:
            from Jumpscale.sal_zos.stats_collector.stats_collector_factory import StatsCollectorFactory
            self._stats_collector =  StatsCollectorFactory()
            # print("load:%sstats_collector")
            if hasattr(self._stats_collector,"_init"):
                self._stats_collector._init()
                # print("init:%sstats_collector")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._stats_collector,"_init2"):
                self._stats_collector._init2()
                # print("init2:%sstats_collector")
        return self._stats_collector
    @property
    def zrobot(self):
        if self._zrobot is None:
            from Jumpscale.sal_zos.zrobot.ZRobotFactory import ZeroRobotFactory
            self._zrobot =  ZeroRobotFactory()
            # print("load:%szrobot")
            if hasattr(self._zrobot,"_init"):
                self._zrobot._init()
                # print("init:%szrobot")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zrobot,"_init2"):
                self._zrobot._init2()
                # print("init2:%szrobot")
        return self._zrobot
    @property
    def zerodb(self):
        if self._zerodb is None:
            from Jumpscale.sal_zos.zerodb.zerodbFactory import ZerodbFactory
            self._zerodb =  ZerodbFactory()
            # print("load:%szerodb")
            if hasattr(self._zerodb,"_init"):
                self._zerodb._init()
                # print("init:%szerodb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zerodb,"_init2"):
                self._zerodb._init2()
                # print("init2:%szerodb")
        return self._zerodb
    @property
    def network(self):
        if self._network is None:
            from Jumpscale.sal_zos.network.NetworkFactory import NetworkFactory
            self._network =  NetworkFactory()
            # print("load:%snetwork")
            if hasattr(self._network,"_init"):
                self._network._init()
                # print("init:%snetwork")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._network,"_init2"):
                self._network._init2()
                # print("init2:%snetwork")
        return self._network
    @property
    def grafana(self):
        if self._grafana is None:
            from Jumpscale.sal_zos.grafana.grafanaFactory import GrafanaFactory
            self._grafana =  GrafanaFactory()
            # print("load:%sgrafana")
            if hasattr(self._grafana,"_init"):
                self._grafana._init()
                # print("init:%sgrafana")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._grafana,"_init2"):
                self._grafana._init2()
                # print("init2:%sgrafana")
        return self._grafana
    @property
    def minio(self):
        if self._minio is None:
            from Jumpscale.sal_zos.minio.MinioFactory import MinioFactory
            self._minio =  MinioFactory()
            # print("load:%sminio")
            if hasattr(self._minio,"_init"):
                self._minio._init()
                # print("init:%sminio")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._minio,"_init2"):
                self._minio._init2()
                # print("init2:%sminio")
        return self._minio
    @property
    def mongodb(self):
        if self._mongodb is None:
            from Jumpscale.sal_zos.mongodb.MongodbFactory import MongodbFactory
            self._mongodb =  MongodbFactory()
            # print("load:%smongodb")
            if hasattr(self._mongodb,"_init"):
                self._mongodb._init()
                # print("init:%smongodb")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._mongodb,"_init2"):
                self._mongodb._init2()
                # print("init2:%smongodb")
        return self._mongodb
    @property
    def storagepools(self):
        if self._storagepools is None:
            from Jumpscale.sal_zos.storage.StorageFactory import ContainerFactory
            self._storagepools =  ContainerFactory()
            # print("load:%sstoragepools")
            if hasattr(self._storagepools,"_init"):
                self._storagepools._init()
                # print("init:%sstoragepools")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._storagepools,"_init2"):
                self._storagepools._init2()
                # print("init2:%sstoragepools")
        return self._storagepools
    @property
    def influx(self):
        if self._influx is None:
            from Jumpscale.sal_zos.influxdb.influxdbFactory import InfluxDBFactory
            self._influx =  InfluxDBFactory()
            # print("load:%sinflux")
            if hasattr(self._influx,"_init"):
                self._influx._init()
                # print("init:%sinflux")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._influx,"_init2"):
                self._influx._init2()
                # print("init2:%sinflux")
        return self._influx
    @property
    def primitives(self):
        if self._primitives is None:
            from Jumpscale.sal_zos.primitives.PrimitivesFactory import PrimitivesFactory
            self._primitives =  PrimitivesFactory()
            # print("load:%sprimitives")
            if hasattr(self._primitives,"_init"):
                self._primitives._init()
                # print("init:%sprimitives")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._primitives,"_init2"):
                self._primitives._init2()
                # print("init2:%sprimitives")
        return self._primitives
    @property
    def capacity(self):
        if self._capacity is None:
            from Jumpscale.sal_zos.capacity.CapacityFactory import CapacityFactory
            self._capacity =  CapacityFactory()
            # print("load:%scapacity")
            if hasattr(self._capacity,"_init"):
                self._capacity._init()
                # print("init:%scapacity")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._capacity,"_init2"):
                self._capacity._init2()
                # print("init2:%scapacity")
        return self._capacity
    @property
    def containers(self):
        if self._containers is None:
            from Jumpscale.sal_zos.container.ContainerFactory import ContainerFactory
            self._containers =  ContainerFactory()
            # print("load:%scontainers")
            if hasattr(self._containers,"_init"):
                self._containers._init()
                # print("init:%scontainers")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._containers,"_init2"):
                self._containers._init2()
                # print("init2:%scontainers")
        return self._containers
    @property
    def zstor(self):
        if self._zstor is None:
            from Jumpscale.sal_zos.zstor.ZStorFactory import ZeroStorFactory
            self._zstor =  ZeroStorFactory()
            # print("load:%szstor")
            if hasattr(self._zstor,"_init"):
                self._zstor._init()
                # print("init:%szstor")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._zstor,"_init2"):
                self._zstor._init2()
                # print("init2:%szstor")
        return self._zstor
    @property
    def vm(self):
        if self._vm is None:
            from Jumpscale.sal_zos.vm.ZOS_VMFactory import ZOS_VMFactory
            self._vm =  ZOS_VMFactory()
            # print("load:%svm")
            if hasattr(self._vm,"_init"):
                self._vm._init()
                # print("init:%svm")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._vm,"_init2"):
                self._vm._init2()
                # print("init2:%svm")
        return self._vm
    @property
    def sandbox(self):
        if self._sandbox is None:
            from Jumpscale.sal_zos.sandbox.ZOSSandboxFactory import ZOSSandboxFactory
            self._sandbox =  ZOSSandboxFactory()
            # print("load:%ssandbox")
            if hasattr(self._sandbox,"_init"):
                self._sandbox._init()
                # print("init:%ssandbox")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._sandbox,"_init2"):
                self._sandbox._init2()
                # print("init2:%ssandbox")
        return self._sandbox
    @property
    def tfchain(self):
        if self._tfchain is None:
            from Jumpscale.sal_zos.tfchain.TfChainFactory import TfChainFactory
            self._tfchain =  TfChainFactory()
            # print("load:%stfchain")
            if hasattr(self._tfchain,"_init"):
                self._tfchain._init()
                # print("init:%stfchain")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._tfchain,"_init2"):
                self._tfchain._init2()
                # print("init2:%stfchain")
        return self._tfchain
    @property
    def disks(self):
        if self._disks is None:
            from Jumpscale.sal_zos.disks.DisksFactory import DisksFactory
            self._disks =  DisksFactory()
            # print("load:%sdisks")
            if hasattr(self._disks,"_init"):
                self._disks._init()
                # print("init:%sdisks")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._disks,"_init2"):
                self._disks._init2()
                # print("init2:%sdisks")
        return self._disks
    @property
    def ftpclient(self):
        if self._ftpclient is None:
            from Jumpscale.sal_zos.ftpClient.ftpFactory import FtpFactory
            self._ftpclient =  FtpFactory()
            # print("load:%sftpclient")
            if hasattr(self._ftpclient,"_init"):
                self._ftpclient._init()
                # print("init:%sftpclient")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ftpclient,"_init2"):
                self._ftpclient._init2()
                # print("init2:%sftpclient")
        return self._ftpclient
    @property
    def etcd(self):
        if self._etcd is None:
            from Jumpscale.sal_zos.ETCD.ETCDFactory import ETCDFactory
            self._etcd =  ETCDFactory()
            # print("load:%setcd")
            if hasattr(self._etcd,"_init"):
                self._etcd._init()
                # print("init:%setcd")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._etcd,"_init2"):
                self._etcd._init2()
                # print("init2:%setcd")
        return self._etcd
    @property
    def ippoolmanager(self):
        if self._ippoolmanager is None:
            from Jumpscale.sal_zos.ip_pool_manager.IPPoolManagerFactory import IPPoolManagerFactory
            self._ippoolmanager =  IPPoolManagerFactory()
            # print("load:%sippoolmanager")
            if hasattr(self._ippoolmanager,"_init"):
                self._ippoolmanager._init()
                # print("init:%sippoolmanager")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._ippoolmanager,"_init2"):
                self._ippoolmanager._init2()
                # print("init2:%sippoolmanager")
        return self._ippoolmanager
    @property
    def node(self):
        if self._node is None:
            from Jumpscale.sal_zos.node.NodeFactory import PrimitivesFactory
            self._node =  PrimitivesFactory()
            # print("load:%snode")
            if hasattr(self._node,"_init"):
                self._node._init()
                # print("init:%snode")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._node,"_init2"):
                self._node._init2()
                # print("init2:%snode")
        return self._node
    @property
    def coredns(self):
        if self._coredns is None:
            from Jumpscale.sal_zos.coredns.CorednsFactory import CorednsFactory
            self._coredns =  CorednsFactory()
            # print("load:%scoredns")
            if hasattr(self._coredns,"_init"):
                self._coredns._init()
                # print("init:%scoredns")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._coredns,"_init2"):
                self._coredns._init2()
                # print("init2:%scoredns")
        return self._coredns
    @property
    def hypervisor(self):
        if self._hypervisor is None:
            from Jumpscale.sal_zos.hypervisor.HypervisorFactory import HypervisorFactory
            self._hypervisor =  HypervisorFactory()
            # print("load:%shypervisor")
            if hasattr(self._hypervisor,"_init"):
                self._hypervisor._init()
                # print("init:%shypervisor")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._hypervisor,"_init2"):
                self._hypervisor._init2()
                # print("init2:%shypervisor")
        return self._hypervisor
    @property
    def traefik(self):
        if self._traefik is None:
            from Jumpscale.sal_zos.traefik.TraefikFactory import TraefikFactory
            self._traefik =  TraefikFactory()
            # print("load:%straefik")
            if hasattr(self._traefik,"_init"):
                self._traefik._init()
                # print("init:%straefik")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._traefik,"_init2"):
                self._traefik._init2()
                # print("init2:%straefik")
        return self._traefik
    @property
    def gateway(self):
        if self._gateway is None:
            from Jumpscale.sal_zos.gateway.gatewayFactory import GatewayFactory
            self._gateway =  GatewayFactory()
            # print("load:%sgateway")
            if hasattr(self._gateway,"_init"):
                self._gateway._init()
                # print("init:%sgateway")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._gateway,"_init2"):
                self._gateway._init2()
                # print("init2:%sgateway")
        return self._gateway

j.sal_zos = group_sal_zos()
j.core._groups["sal_zos"] = j.sal_zos



