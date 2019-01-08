
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
        
        self.__template = None
        self._btc_electrum = None
        self._tfchain = None
        self._btc_alpha = None
        self._coredns = None
        self._currencylayer = None
        self._etcd = None
        self._git = None
        self._gitea = None
        self._github = None
        self._google_compute = None
        self._grafana = None
        self._graphite = None
        self._http = None
        self._influxdb = None
        self._intercom = None
        self._ipmi = None
        self._itsyouonline = None
        self._kraken = None
        self._kubernetes = None
        self._email = None
        self._sendgrid = None
        self._mongoengine = None
        self._mongodb = None
        self._mysql = None
        self._oauth = None
        self._openvcloud = None
        self._ovh = None
        self._packetnet = None
        self._peewee = None
        self._portal = None
        self._postgres = None
        self._racktivity = None
        self._credis_core = None
        self._redis = None
        self._redis_config = None
        self._rogerthat = None
        self._s3 = None
        self._sqlalchemy = None
        self._ssh = None
        self._sshagent = None
        self._sshkey = None
        self._syncthing = None
        self._tarantool = None
        self._telegram_bot = None
        self._threefold_directory = None
        self._traefik = None
        self._trello = None
        self._virtualbox = None
        self._webgateway = None
        self._zdb = None
        self._zboot = None
        self._zhub = None
        self._zhubdirect = None
        self._zos_protocol = None
        self._zerostor = None
        self._zstor = None
        self._zerotier = None
        self._zos = None
        self._gedis = None
        self._gedis_backend = None
        self._multicast = None

    
    @property
    def _template(self):
        if self.__template is None:
            # print("LOAD:GrafanaFactory")
            try:
                from Jumpscale.clients.TEMPLATE.TemplateGrafanaFactory import GrafanaFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.TEMPLATE.TemplateGrafanaFactory", e)
                raise e
            # print("RUN:GrafanaFactory")
            try:
                self.__template =  GrafanaFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.TEMPLATE.TemplateGrafanaFactory",e)
                return None
            # print("OK")
        return self.__template
    @property
    def btc_electrum(self):
        if self._btc_electrum is None:
            # print("LOAD:ElectrumClientFactory")
            try:
                from Jumpscale.clients.blockchain.electrum.ElectrumClientFactory import ElectrumClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.blockchain.electrum.ElectrumClientFactory", e)
                raise e
            # print("RUN:ElectrumClientFactory")
            try:
                self._btc_electrum =  ElectrumClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.blockchain.electrum.ElectrumClientFactory",e)
                return None
            # print("OK")
        return self._btc_electrum
    @property
    def tfchain(self):
        if self._tfchain is None:
            # print("LOAD:TfchainClientFactory")
            try:
                from Jumpscale.clients.blockchain.tfchain.TfchainClientFactory import TfchainClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.blockchain.tfchain.TfchainClientFactory", e)
                raise e
            # print("RUN:TfchainClientFactory")
            try:
                self._tfchain =  TfchainClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.blockchain.tfchain.TfchainClientFactory",e)
                return None
            # print("OK")
        return self._tfchain
    @property
    def btc_alpha(self):
        if self._btc_alpha is None:
            # print("LOAD:GitHubFactory")
            try:
                from Jumpscale.clients.btc_alpha.BTCFactory import GitHubFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.btc_alpha.BTCFactory", e)
                raise e
            # print("RUN:GitHubFactory")
            try:
                self._btc_alpha =  GitHubFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.btc_alpha.BTCFactory",e)
                return None
            # print("OK")
        return self._btc_alpha
    @property
    def coredns(self):
        if self._coredns is None:
            # print("LOAD:CoreDNSFactory")
            try:
                from Jumpscale.clients.coredns.CoreDNSFactory import CoreDNSFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.coredns.CoreDNSFactory", e)
                raise e
            # print("RUN:CoreDNSFactory")
            try:
                self._coredns =  CoreDNSFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.coredns.CoreDNSFactory",e)
                return None
            # print("OK")
        return self._coredns
    @property
    def currencylayer(self):
        if self._currencylayer is None:
            # print("LOAD:CurrencyLayerFactory")
            try:
                from Jumpscale.clients.currencylayer.CurrencyLayerFactory import CurrencyLayerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.currencylayer.CurrencyLayerFactory", e)
                raise e
            # print("RUN:CurrencyLayerFactory")
            try:
                self._currencylayer =  CurrencyLayerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.currencylayer.CurrencyLayerFactory",e)
                return None
            # print("OK")
        return self._currencylayer
    @property
    def etcd(self):
        if self._etcd is None:
            # print("LOAD:EtcdFactory")
            try:
                from Jumpscale.clients.etcd.EtcdFactory import EtcdFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.etcd.EtcdFactory", e)
                raise e
            # print("RUN:EtcdFactory")
            try:
                self._etcd =  EtcdFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.etcd.EtcdFactory",e)
                return None
            # print("OK")
        return self._etcd
    @property
    def git(self):
        if self._git is None:
            # print("LOAD:GitFactory")
            try:
                from Jumpscale.clients.git.GitFactory import GitFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.git.GitFactory", e)
                raise e
            # print("RUN:GitFactory")
            try:
                self._git =  GitFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.git.GitFactory",e)
                return None
            # print("OK")
        return self._git
    @property
    def gitea(self):
        if self._gitea is None:
            # print("LOAD:GiteaFactory")
            try:
                from Jumpscale.clients.gitea.GiteaFactory import GiteaFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.gitea.GiteaFactory", e)
                raise e
            # print("RUN:GiteaFactory")
            try:
                self._gitea =  GiteaFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.gitea.GiteaFactory",e)
                return None
            # print("OK")
        return self._gitea
    @property
    def github(self):
        if self._github is None:
            # print("LOAD:GitHubFactory")
            try:
                from Jumpscale.clients.github.GitHubFactory import GitHubFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.github.GitHubFactory", e)
                raise e
            # print("RUN:GitHubFactory")
            try:
                self._github =  GitHubFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.github.GitHubFactory",e)
                return None
            # print("OK")
        return self._github
    @property
    def google_compute(self):
        if self._google_compute is None:
            # print("LOAD:GoogleComputeFactory")
            try:
                from Jumpscale.clients.google_compute.GoogleComputeFactory import GoogleComputeFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.google_compute.GoogleComputeFactory", e)
                raise e
            # print("RUN:GoogleComputeFactory")
            try:
                self._google_compute =  GoogleComputeFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.google_compute.GoogleComputeFactory",e)
                return None
            # print("OK")
        return self._google_compute
    @property
    def grafana(self):
        if self._grafana is None:
            # print("LOAD:GrafanaFactory")
            try:
                from Jumpscale.clients.grafana.GrafanaFactory import GrafanaFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.grafana.GrafanaFactory", e)
                raise e
            # print("RUN:GrafanaFactory")
            try:
                self._grafana =  GrafanaFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.grafana.GrafanaFactory",e)
                return None
            # print("OK")
        return self._grafana
    @property
    def graphite(self):
        if self._graphite is None:
            # print("LOAD:GraphiteFactory")
            try:
                from Jumpscale.clients.graphite.GraphiteFactory import GraphiteFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.graphite.GraphiteFactory", e)
                raise e
            # print("RUN:GraphiteFactory")
            try:
                self._graphite =  GraphiteFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.graphite.GraphiteFactory",e)
                return None
            # print("OK")
        return self._graphite
    @property
    def http(self):
        if self._http is None:
            # print("LOAD:HttpClient")
            try:
                from Jumpscale.clients.http.HttpClient import HttpClient
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.http.HttpClient", e)
                raise e
            # print("RUN:HttpClient")
            try:
                self._http =  HttpClient()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.http.HttpClient",e)
                return None
            # print("OK")
        return self._http
    @property
    def influxdb(self):
        if self._influxdb is None:
            # print("LOAD:InfluxdbFactory")
            try:
                from Jumpscale.clients.influxdb.InfluxdbFactory import InfluxdbFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.influxdb.InfluxdbFactory", e)
                raise e
            # print("RUN:InfluxdbFactory")
            try:
                self._influxdb =  InfluxdbFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.influxdb.InfluxdbFactory",e)
                return None
            # print("OK")
        return self._influxdb
    @property
    def intercom(self):
        if self._intercom is None:
            # print("LOAD:Intercom")
            try:
                from Jumpscale.clients.intercom.IntercomFactory import Intercom
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.intercom.IntercomFactory", e)
                raise e
            # print("RUN:Intercom")
            try:
                self._intercom =  Intercom()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.intercom.IntercomFactory",e)
                return None
            # print("OK")
        return self._intercom
    @property
    def ipmi(self):
        if self._ipmi is None:
            # print("LOAD:IpmiFactory")
            try:
                from Jumpscale.clients.ipmi.IpmiFactory import IpmiFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.ipmi.IpmiFactory", e)
                raise e
            # print("RUN:IpmiFactory")
            try:
                self._ipmi =  IpmiFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.ipmi.IpmiFactory",e)
                return None
            # print("OK")
        return self._ipmi
    @property
    def itsyouonline(self):
        if self._itsyouonline is None:
            # print("LOAD:IYOFactory")
            try:
                from Jumpscale.clients.itsyouonline.IYOFactory import IYOFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.itsyouonline.IYOFactory", e)
                raise e
            # print("RUN:IYOFactory")
            try:
                self._itsyouonline =  IYOFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.itsyouonline.IYOFactory",e)
                return None
            # print("OK")
        return self._itsyouonline
    @property
    def kraken(self):
        if self._kraken is None:
            # print("LOAD:KrakenFactory")
            try:
                from Jumpscale.clients.kraken.KrakenFactory import KrakenFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.kraken.KrakenFactory", e)
                raise e
            # print("RUN:KrakenFactory")
            try:
                self._kraken =  KrakenFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.kraken.KrakenFactory",e)
                return None
            # print("OK")
        return self._kraken
    @property
    def kubernetes(self):
        if self._kubernetes is None:
            # print("LOAD:KubernetesFactory")
            try:
                from Jumpscale.clients.kubernetes.KubernetesFactory import KubernetesFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.kubernetes.KubernetesFactory", e)
                raise e
            # print("RUN:KubernetesFactory")
            try:
                self._kubernetes =  KubernetesFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.kubernetes.KubernetesFactory",e)
                return None
            # print("OK")
        return self._kubernetes
    @property
    def email(self):
        if self._email is None:
            # print("LOAD:EmailFactory")
            try:
                from Jumpscale.clients.mail.EmailFactory import EmailFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.mail.EmailFactory", e)
                raise e
            # print("RUN:EmailFactory")
            try:
                self._email =  EmailFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.mail.EmailFactory",e)
                return None
            # print("OK")
        return self._email
    @property
    def sendgrid(self):
        if self._sendgrid is None:
            # print("LOAD:SendGridClient")
            try:
                from Jumpscale.clients.mail.sendgrid.SendGridClient import SendGridClient
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.mail.sendgrid.SendGridClient", e)
                raise e
            # print("RUN:SendGridClient")
            try:
                self._sendgrid =  SendGridClient()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.mail.sendgrid.SendGridClient",e)
                return None
            # print("OK")
        return self._sendgrid
    @property
    def mongoengine(self):
        if self._mongoengine is None:
            # print("LOAD:MongoEngineFactory")
            try:
                from Jumpscale.clients.mongodbclient.MongoEngineFactory import MongoEngineFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.mongodbclient.MongoEngineFactory", e)
                raise e
            # print("RUN:MongoEngineFactory")
            try:
                self._mongoengine =  MongoEngineFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.mongodbclient.MongoEngineFactory",e)
                return None
            # print("OK")
        return self._mongoengine
    @property
    def mongodb(self):
        if self._mongodb is None:
            # print("LOAD:MongoFactory")
            try:
                from Jumpscale.clients.mongodbclient.MongoFactory import MongoFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.mongodbclient.MongoFactory", e)
                raise e
            # print("RUN:MongoFactory")
            try:
                self._mongodb =  MongoFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.mongodbclient.MongoFactory",e)
                return None
            # print("OK")
        return self._mongodb
    @property
    def mysql(self):
        if self._mysql is None:
            # print("LOAD:MySQLFactory")
            try:
                from Jumpscale.clients.mysql.MySQLFactory import MySQLFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.mysql.MySQLFactory", e)
                raise e
            # print("RUN:MySQLFactory")
            try:
                self._mysql =  MySQLFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.mysql.MySQLFactory",e)
                return None
            # print("OK")
        return self._mysql
    @property
    def oauth(self):
        if self._oauth is None:
            # print("LOAD:OauthFactory")
            try:
                from Jumpscale.clients.oauth.OauthFactory import OauthFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.oauth.OauthFactory", e)
                raise e
            # print("RUN:OauthFactory")
            try:
                self._oauth =  OauthFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.oauth.OauthFactory",e)
                return None
            # print("OK")
        return self._oauth
    @property
    def openvcloud(self):
        if self._openvcloud is None:
            # print("LOAD:OVCClientFactory")
            try:
                from Jumpscale.clients.openvcloud.OVCFactory import OVCClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.openvcloud.OVCFactory", e)
                raise e
            # print("RUN:OVCClientFactory")
            try:
                self._openvcloud =  OVCClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.openvcloud.OVCFactory",e)
                return None
            # print("OK")
        return self._openvcloud
    @property
    def ovh(self):
        if self._ovh is None:
            # print("LOAD:OVHFactory")
            try:
                from Jumpscale.clients.ovh.OVHFactory import OVHFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.ovh.OVHFactory", e)
                raise e
            # print("RUN:OVHFactory")
            try:
                self._ovh =  OVHFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.ovh.OVHFactory",e)
                return None
            # print("OK")
        return self._ovh
    @property
    def packetnet(self):
        if self._packetnet is None:
            # print("LOAD:PacketNetFactory")
            try:
                from Jumpscale.clients.packetnet.PacketNetFactory import PacketNetFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.packetnet.PacketNetFactory", e)
                raise e
            # print("RUN:PacketNetFactory")
            try:
                self._packetnet =  PacketNetFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.packetnet.PacketNetFactory",e)
                return None
            # print("OK")
        return self._packetnet
    @property
    def peewee(self):
        if self._peewee is None:
            # print("LOAD:PeeweeFactory")
            try:
                from Jumpscale.clients.peewee.PeeweeFactory import PeeweeFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.peewee.PeeweeFactory", e)
                raise e
            # print("RUN:PeeweeFactory")
            try:
                self._peewee =  PeeweeFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.peewee.PeeweeFactory",e)
                return None
            # print("OK")
        return self._peewee
    @property
    def portal(self):
        if self._portal is None:
            # print("LOAD:PortalClientFactory")
            try:
                from Jumpscale.clients.portal.PortalClientFactory import PortalClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.portal.PortalClientFactory", e)
                raise e
            # print("RUN:PortalClientFactory")
            try:
                self._portal =  PortalClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.portal.PortalClientFactory",e)
                return None
            # print("OK")
        return self._portal
    @property
    def postgres(self):
        if self._postgres is None:
            # print("LOAD:PostgresqlFactory")
            try:
                from Jumpscale.clients.postgresql.PostgresqlFactory import PostgresqlFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.postgresql.PostgresqlFactory", e)
                raise e
            # print("RUN:PostgresqlFactory")
            try:
                self._postgres =  PostgresqlFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.postgresql.PostgresqlFactory",e)
                return None
            # print("OK")
        return self._postgres
    @property
    def racktivity(self):
        if self._racktivity is None:
            # print("LOAD:RacktivityFactory")
            try:
                from Jumpscale.clients.racktivity.RacktivityFactory import RacktivityFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.racktivity.RacktivityFactory", e)
                raise e
            # print("RUN:RacktivityFactory")
            try:
                self._racktivity =  RacktivityFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.racktivity.RacktivityFactory",e)
                return None
            # print("OK")
        return self._racktivity
    @property
    def credis_core(self):
        if self._credis_core is None:
            # print("LOAD:RedisCoreClient")
            try:
                from Jumpscale.clients.redis.RedisCoreClient import RedisCoreClient
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.redis.RedisCoreClient", e)
                raise e
            # print("RUN:RedisCoreClient")
            try:
                self._credis_core =  RedisCoreClient()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.redis.RedisCoreClient",e)
                return None
            # print("OK")
        return self._credis_core
    @property
    def redis(self):
        if self._redis is None:
            # print("LOAD:RedisFactory")
            try:
                from Jumpscale.clients.redis.RedisFactory import RedisFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.redis.RedisFactory", e)
                raise e
            # print("RUN:RedisFactory")
            try:
                self._redis =  RedisFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.redis.RedisFactory",e)
                return None
            # print("OK")
        return self._redis
    @property
    def redis_config(self):
        if self._redis_config is None:
            # print("LOAD:RedisConfigFactory")
            try:
                from Jumpscale.clients.redisconfig.RedisConfigFactory import RedisConfigFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.redisconfig.RedisConfigFactory", e)
                raise e
            # print("RUN:RedisConfigFactory")
            try:
                self._redis_config =  RedisConfigFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.redisconfig.RedisConfigFactory",e)
                return None
            # print("OK")
        return self._redis_config
    @property
    def rogerthat(self):
        if self._rogerthat is None:
            # print("LOAD:RogerthatFactory")
            try:
                from Jumpscale.clients.rogerthat.RogerthatFactory import RogerthatFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.rogerthat.RogerthatFactory", e)
                raise e
            # print("RUN:RogerthatFactory")
            try:
                self._rogerthat =  RogerthatFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.rogerthat.RogerthatFactory",e)
                return None
            # print("OK")
        return self._rogerthat
    @property
    def s3(self):
        if self._s3 is None:
            # print("LOAD:S3Factory")
            try:
                from Jumpscale.clients.s3.S3Factory import S3Factory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.s3.S3Factory", e)
                raise e
            # print("RUN:S3Factory")
            try:
                self._s3 =  S3Factory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.s3.S3Factory",e)
                return None
            # print("OK")
        return self._s3
    @property
    def sqlalchemy(self):
        if self._sqlalchemy is None:
            # print("LOAD:SQLAlchemyFactory")
            try:
                from Jumpscale.clients.sqlalchemy.SQLAlchemyFactory import SQLAlchemyFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.sqlalchemy.SQLAlchemyFactory", e)
                raise e
            # print("RUN:SQLAlchemyFactory")
            try:
                self._sqlalchemy =  SQLAlchemyFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.sqlalchemy.SQLAlchemyFactory",e)
                return None
            # print("OK")
        return self._sqlalchemy
    @property
    def ssh(self):
        if self._ssh is None:
            # print("LOAD:SSHClientFactory")
            try:
                from Jumpscale.clients.ssh.SSHClientFactory import SSHClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.ssh.SSHClientFactory", e)
                raise e
            # print("RUN:SSHClientFactory")
            try:
                self._ssh =  SSHClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.ssh.SSHClientFactory",e)
                return None
            # print("OK")
        return self._ssh
    @property
    def sshagent(self):
        if self._sshagent is None:
            # print("LOAD:SSHAgent")
            try:
                from Jumpscale.clients.sshagent.SSHAgent import SSHAgent
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.sshagent.SSHAgent", e)
                raise e
            # print("RUN:SSHAgent")
            try:
                self._sshagent =  SSHAgent()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.sshagent.SSHAgent",e)
                return None
            # print("OK")
        return self._sshagent
    @property
    def sshkey(self):
        if self._sshkey is None:
            # print("LOAD:SSHKeys")
            try:
                from Jumpscale.clients.sshkey.SSHKeys import SSHKeys
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.sshkey.SSHKeys", e)
                raise e
            # print("RUN:SSHKeys")
            try:
                self._sshkey =  SSHKeys()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.sshkey.SSHKeys",e)
                return None
            # print("OK")
        return self._sshkey
    @property
    def syncthing(self):
        if self._syncthing is None:
            # print("LOAD:SyncthingFactory")
            try:
                from Jumpscale.clients.syncthing.SyncthingFactory import SyncthingFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.syncthing.SyncthingFactory", e)
                raise e
            # print("RUN:SyncthingFactory")
            try:
                self._syncthing =  SyncthingFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.syncthing.SyncthingFactory",e)
                return None
            # print("OK")
        return self._syncthing
    @property
    def tarantool(self):
        if self._tarantool is None:
            # print("LOAD:TarantoolFactory")
            try:
                from Jumpscale.clients.tarantool.TarantoolFactory import TarantoolFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.tarantool.TarantoolFactory", e)
                raise e
            # print("RUN:TarantoolFactory")
            try:
                self._tarantool =  TarantoolFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.tarantool.TarantoolFactory",e)
                return None
            # print("OK")
        return self._tarantool
    @property
    def telegram_bot(self):
        if self._telegram_bot is None:
            # print("LOAD:TelegramBotFactory")
            try:
                from Jumpscale.clients.telegram_bot.TelegramBotFactory import TelegramBotFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.telegram_bot.TelegramBotFactory", e)
                raise e
            # print("RUN:TelegramBotFactory")
            try:
                self._telegram_bot =  TelegramBotFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.telegram_bot.TelegramBotFactory",e)
                return None
            # print("OK")
        return self._telegram_bot
    @property
    def threefold_directory(self):
        if self._threefold_directory is None:
            # print("LOAD:GridCapacityFactory")
            try:
                from Jumpscale.clients.threefold_directory.GridCapacityFactory import GridCapacityFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.threefold_directory.GridCapacityFactory", e)
                raise e
            # print("RUN:GridCapacityFactory")
            try:
                self._threefold_directory =  GridCapacityFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.threefold_directory.GridCapacityFactory",e)
                return None
            # print("OK")
        return self._threefold_directory
    @property
    def traefik(self):
        if self._traefik is None:
            # print("LOAD:TraefikFactory")
            try:
                from Jumpscale.clients.traefik.TraefikFactory import TraefikFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.traefik.TraefikFactory", e)
                raise e
            # print("RUN:TraefikFactory")
            try:
                self._traefik =  TraefikFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.traefik.TraefikFactory",e)
                return None
            # print("OK")
        return self._traefik
    @property
    def trello(self):
        if self._trello is None:
            # print("LOAD:Trello")
            try:
                from Jumpscale.clients.trello.TrelloFactory import Trello
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.trello.TrelloFactory", e)
                raise e
            # print("RUN:Trello")
            try:
                self._trello =  Trello()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.trello.TrelloFactory",e)
                return None
            # print("OK")
        return self._trello
    @property
    def virtualbox(self):
        if self._virtualbox is None:
            # print("LOAD:VirtualboxFactory")
            try:
                from Jumpscale.clients.virtualbox.VirtualboxFactory import VirtualboxFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.virtualbox.VirtualboxFactory", e)
                raise e
            # print("RUN:VirtualboxFactory")
            try:
                self._virtualbox =  VirtualboxFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.virtualbox.VirtualboxFactory",e)
                return None
            # print("OK")
        return self._virtualbox
    @property
    def webgateway(self):
        if self._webgateway is None:
            # print("LOAD:WebGatewayFactory")
            try:
                from Jumpscale.clients.webgateway.WebGatewayFactory import WebGatewayFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.webgateway.WebGatewayFactory", e)
                raise e
            # print("RUN:WebGatewayFactory")
            try:
                self._webgateway =  WebGatewayFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.webgateway.WebGatewayFactory",e)
                return None
            # print("OK")
        return self._webgateway
    @property
    def zdb(self):
        if self._zdb is None:
            # print("LOAD:ZDBFactory")
            try:
                from Jumpscale.clients.zdb.ZDBFactory import ZDBFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zdb.ZDBFactory", e)
                raise e
            # print("RUN:ZDBFactory")
            try:
                self._zdb =  ZDBFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zdb.ZDBFactory",e)
                return None
            # print("OK")
        return self._zdb
    @property
    def zboot(self):
        if self._zboot is None:
            # print("LOAD:ZerobootFactory")
            try:
                from Jumpscale.clients.zero_boot.ZerobootFactory import ZerobootFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zero_boot.ZerobootFactory", e)
                raise e
            # print("RUN:ZerobootFactory")
            try:
                self._zboot =  ZerobootFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zero_boot.ZerobootFactory",e)
                return None
            # print("OK")
        return self._zboot
    @property
    def zhub(self):
        if self._zhub is None:
            # print("LOAD:ZeroHubFactory")
            try:
                from Jumpscale.clients.zero_hub.ZeroHubFactory import ZeroHubFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zero_hub.ZeroHubFactory", e)
                raise e
            # print("RUN:ZeroHubFactory")
            try:
                self._zhub =  ZeroHubFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zero_hub.ZeroHubFactory",e)
                return None
            # print("OK")
        return self._zhub
    @property
    def zhubdirect(self):
        if self._zhubdirect is None:
            # print("LOAD:HubDirectFactory")
            try:
                from Jumpscale.clients.zero_hub_direct.HubDirectFactory import HubDirectFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zero_hub_direct.HubDirectFactory", e)
                raise e
            # print("RUN:HubDirectFactory")
            try:
                self._zhubdirect =  HubDirectFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zero_hub_direct.HubDirectFactory",e)
                return None
            # print("OK")
        return self._zhubdirect
    @property
    def zos_protocol(self):
        if self._zos_protocol is None:
            # print("LOAD:ZeroOSFactory")
            try:
                from Jumpscale.clients.zero_os_protocol.ZeroOSFactory import ZeroOSFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zero_os_protocol.ZeroOSFactory", e)
                raise e
            # print("RUN:ZeroOSFactory")
            try:
                self._zos_protocol =  ZeroOSFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zero_os_protocol.ZeroOSFactory",e)
                return None
            # print("OK")
        return self._zos_protocol
    @property
    def zerostor(self):
        if self._zerostor is None:
            # print("LOAD:ZeroStorFactoryDeprecated")
            try:
                from Jumpscale.clients.zero_stor.ZeroStorFactoryDeprecated import ZeroStorFactoryDeprecated
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zero_stor.ZeroStorFactoryDeprecated", e)
                raise e
            # print("RUN:ZeroStorFactoryDeprecated")
            try:
                self._zerostor =  ZeroStorFactoryDeprecated()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zero_stor.ZeroStorFactoryDeprecated",e)
                return None
            # print("OK")
        return self._zerostor
    @property
    def zstor(self):
        if self._zstor is None:
            # print("LOAD:ZeroStorFactory")
            try:
                from Jumpscale.clients.zero_stor.ZeroStorFactory import ZeroStorFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zero_stor.ZeroStorFactory", e)
                raise e
            # print("RUN:ZeroStorFactory")
            try:
                self._zstor =  ZeroStorFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zero_stor.ZeroStorFactory",e)
                return None
            # print("OK")
        return self._zstor
    @property
    def zerotier(self):
        if self._zerotier is None:
            # print("LOAD:ZerotierFactory")
            try:
                from Jumpscale.clients.zerotier.ZerotierFactory import ZerotierFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zerotier.ZerotierFactory", e)
                raise e
            # print("RUN:ZerotierFactory")
            try:
                self._zerotier =  ZerotierFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zerotier.ZerotierFactory",e)
                return None
            # print("OK")
        return self._zerotier
    @property
    def zos(self):
        if self._zos is None:
            # print("LOAD:ZeroOSClientFactory")
            try:
                from Jumpscale.clients.zero_os.ZeroOsFactory import ZeroOSClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.zero_os.ZeroOsFactory", e)
                raise e
            # print("RUN:ZeroOSClientFactory")
            try:
                self._zos =  ZeroOSClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.zero_os.ZeroOsFactory",e)
                return None
            # print("OK")
        return self._zos
    @property
    def gedis(self):
        if self._gedis is None:
            # print("LOAD:GedisClientFactory")
            try:
                from DigitalMe.clients.gedis.GedisClientFactory import GedisClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.clients.gedis.GedisClientFactory", e)
                raise e
            # print("RUN:GedisClientFactory")
            try:
                self._gedis =  GedisClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.clients.gedis.GedisClientFactory",e)
                return None
            # print("OK")
        return self._gedis
    @property
    def gedis_backend(self):
        if self._gedis_backend is None:
            # print("LOAD:GedisBackendClientFactory")
            try:
                from DigitalMe.clients.gedis_backends.GedisBackendClientFactory import GedisBackendClientFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.clients.gedis_backends.GedisBackendClientFactory", e)
                raise e
            # print("RUN:GedisBackendClientFactory")
            try:
                self._gedis_backend =  GedisBackendClientFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.clients.gedis_backends.GedisBackendClientFactory",e)
                return None
            # print("OK")
        return self._gedis_backend
    @property
    def multicast(self):
        if self._multicast is None:
            # print("LOAD:MulticastFactory")
            try:
                from DigitalMe.clients.multicast.MulticastFactory import MulticastFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.clients.multicast.MulticastFactory", e)
                raise e
            # print("RUN:MulticastFactory")
            try:
                self._multicast =  MulticastFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.clients.multicast.MulticastFactory",e)
                return None
            # print("OK")
        return self._multicast

j.clients = group_clients()
j.core._groups["clients"] = j.clients


class group_sal(JSGroup):
    def __init__(self):
        
        self._coredns = None
        self._bind = None
        self._btrfs = None
        self._disklayout = None
        self._dnsmasq = None
        self._fswalker = None
        self._fs = None
        self._hostsfile = None
        self._kvm = None
        self._netconfig = None
        self._nettools = None
        self._nfs = None
        self._nginx = None
        self._nic = None
        self._openvswitch = None
        self._process = None
        self._qemu_img = None
        self._rsync = None
        self._samba = None
        self._sshd = None
        self._ssl = None
        self._tls = None
        self._ubuntu = None
        self._ufw = None
        self._unix = None
        self._windows = None
        self._docker = None

    
    @property
    def coredns(self):
        if self._coredns is None:
            # print("LOAD:CoreDnsFactory")
            try:
                from Jumpscale.clients.coredns.alternative.CoreDnsFactory import CoreDnsFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.clients.coredns.alternative.CoreDnsFactory", e)
                raise e
            # print("RUN:CoreDnsFactory")
            try:
                self._coredns =  CoreDnsFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.clients.coredns.alternative.CoreDnsFactory",e)
                return None
            # print("OK")
        return self._coredns
    @property
    def bind(self):
        if self._bind is None:
            # print("LOAD:BindDNS")
            try:
                from Jumpscale.sal.bind.BindDNS import BindDNS
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.bind.BindDNS", e)
                raise e
            # print("RUN:BindDNS")
            try:
                self._bind =  BindDNS()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.bind.BindDNS",e)
                return None
            # print("OK")
        return self._bind
    @property
    def btrfs(self):
        if self._btrfs is None:
            # print("LOAD:BtfsExtensionFactory")
            try:
                from Jumpscale.sal.btrfs.BtrfsExtension import BtfsExtensionFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.btrfs.BtrfsExtension", e)
                raise e
            # print("RUN:BtfsExtensionFactory")
            try:
                self._btrfs =  BtfsExtensionFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.btrfs.BtrfsExtension",e)
                return None
            # print("OK")
        return self._btrfs
    @property
    def disklayout(self):
        if self._disklayout is None:
            # print("LOAD:DiskManager")
            try:
                from Jumpscale.sal.disklayout.DiskManager import DiskManager
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.disklayout.DiskManager", e)
                raise e
            # print("RUN:DiskManager")
            try:
                self._disklayout =  DiskManager()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.disklayout.DiskManager",e)
                return None
            # print("OK")
        return self._disklayout
    @property
    def dnsmasq(self):
        if self._dnsmasq is None:
            # print("LOAD:DnsmasqFactory")
            try:
                from Jumpscale.sal.dnsmasq.DnsmasqFactory import DnsmasqFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.dnsmasq.DnsmasqFactory", e)
                raise e
            # print("RUN:DnsmasqFactory")
            try:
                self._dnsmasq =  DnsmasqFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.dnsmasq.DnsmasqFactory",e)
                return None
            # print("OK")
        return self._dnsmasq
    @property
    def fswalker(self):
        if self._fswalker is None:
            # print("LOAD:SystemFSWalker")
            try:
                from Jumpscale.sal.fs.SystemFSWalker import SystemFSWalker
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.fs.SystemFSWalker", e)
                raise e
            # print("RUN:SystemFSWalker")
            try:
                self._fswalker =  SystemFSWalker()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.fs.SystemFSWalker",e)
                return None
            # print("OK")
        return self._fswalker
    @property
    def fs(self):
        if self._fs is None:
            # print("LOAD:SystemFS")
            try:
                from Jumpscale.sal.fs.SystemFS import SystemFS
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.fs.SystemFS", e)
                raise e
            # print("RUN:SystemFS")
            try:
                self._fs =  SystemFS()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.fs.SystemFS",e)
                return None
            # print("OK")
        return self._fs
    @property
    def hostsfile(self):
        if self._hostsfile is None:
            # print("LOAD:HostFile")
            try:
                from Jumpscale.sal.hostfile.HostFile import HostFile
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.hostfile.HostFile", e)
                raise e
            # print("RUN:HostFile")
            try:
                self._hostsfile =  HostFile()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.hostfile.HostFile",e)
                return None
            # print("OK")
        return self._hostsfile
    @property
    def kvm(self):
        if self._kvm is None:
            # print("LOAD:KVM")
            try:
                from Jumpscale.sal.kvm.KVM import KVM
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.kvm.KVM", e)
                raise e
            # print("RUN:KVM")
            try:
                self._kvm =  KVM()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.kvm.KVM",e)
                return None
            # print("OK")
        return self._kvm
    @property
    def netconfig(self):
        if self._netconfig is None:
            # print("LOAD:Netconfig")
            try:
                from Jumpscale.sal.netconfig.Netconfig import Netconfig
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.netconfig.Netconfig", e)
                raise e
            # print("RUN:Netconfig")
            try:
                self._netconfig =  Netconfig()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.netconfig.Netconfig",e)
                return None
            # print("OK")
        return self._netconfig
    @property
    def nettools(self):
        if self._nettools is None:
            # print("LOAD:NetTools")
            try:
                from Jumpscale.sal.nettools.NetTools import NetTools
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.nettools.NetTools", e)
                raise e
            # print("RUN:NetTools")
            try:
                self._nettools =  NetTools()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.nettools.NetTools",e)
                return None
            # print("OK")
        return self._nettools
    @property
    def nfs(self):
        if self._nfs is None:
            # print("LOAD:NFS")
            try:
                from Jumpscale.sal.nfs.NFS import NFS
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.nfs.NFS", e)
                raise e
            # print("RUN:NFS")
            try:
                self._nfs =  NFS()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.nfs.NFS",e)
                return None
            # print("OK")
        return self._nfs
    @property
    def nginx(self):
        if self._nginx is None:
            # print("LOAD:NginxFactory")
            try:
                from Jumpscale.sal.nginx.Nginx import NginxFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.nginx.Nginx", e)
                raise e
            # print("RUN:NginxFactory")
            try:
                self._nginx =  NginxFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.nginx.Nginx",e)
                return None
            # print("OK")
        return self._nginx
    @property
    def nic(self):
        if self._nic is None:
            # print("LOAD:UnixNetworkManager")
            try:
                from Jumpscale.sal.nic.UnixNetworkManager import UnixNetworkManager
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.nic.UnixNetworkManager", e)
                raise e
            # print("RUN:UnixNetworkManager")
            try:
                self._nic =  UnixNetworkManager()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.nic.UnixNetworkManager",e)
                return None
            # print("OK")
        return self._nic
    @property
    def openvswitch(self):
        if self._openvswitch is None:
            # print("LOAD:NetConfigFactory")
            try:
                from Jumpscale.sal.openvswitch.NetConfigFactory import NetConfigFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.openvswitch.NetConfigFactory", e)
                raise e
            # print("RUN:NetConfigFactory")
            try:
                self._openvswitch =  NetConfigFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.openvswitch.NetConfigFactory",e)
                return None
            # print("OK")
        return self._openvswitch
    @property
    def process(self):
        if self._process is None:
            # print("LOAD:SystemProcess")
            try:
                from Jumpscale.sal.process.SystemProcess import SystemProcess
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.process.SystemProcess", e)
                raise e
            # print("RUN:SystemProcess")
            try:
                self._process =  SystemProcess()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.process.SystemProcess",e)
                return None
            # print("OK")
        return self._process
    @property
    def qemu_img(self):
        if self._qemu_img is None:
            # print("LOAD:QemuImg")
            try:
                from Jumpscale.sal.qemu_img.Qemu_img import QemuImg
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.qemu_img.Qemu_img", e)
                raise e
            # print("RUN:QemuImg")
            try:
                self._qemu_img =  QemuImg()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.qemu_img.Qemu_img",e)
                return None
            # print("OK")
        return self._qemu_img
    @property
    def rsync(self):
        if self._rsync is None:
            # print("LOAD:RsyncFactory")
            try:
                from Jumpscale.sal.rsync.RsyncFactory import RsyncFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.rsync.RsyncFactory", e)
                raise e
            # print("RUN:RsyncFactory")
            try:
                self._rsync =  RsyncFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.rsync.RsyncFactory",e)
                return None
            # print("OK")
        return self._rsync
    @property
    def samba(self):
        if self._samba is None:
            # print("LOAD:Samba")
            try:
                from Jumpscale.sal.samba.Samba import Samba
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.samba.Samba", e)
                raise e
            # print("RUN:Samba")
            try:
                self._samba =  Samba()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.samba.Samba",e)
                return None
            # print("OK")
        return self._samba
    @property
    def sshd(self):
        if self._sshd is None:
            # print("LOAD:SSHD")
            try:
                from Jumpscale.sal.sshd.SSHD import SSHD
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.sshd.SSHD", e)
                raise e
            # print("RUN:SSHD")
            try:
                self._sshd =  SSHD()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.sshd.SSHD",e)
                return None
            # print("OK")
        return self._sshd
    @property
    def ssl(self):
        if self._ssl is None:
            # print("LOAD:SSLFactory")
            try:
                from Jumpscale.sal.ssl.SSLFactory import SSLFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.ssl.SSLFactory", e)
                raise e
            # print("RUN:SSLFactory")
            try:
                self._ssl =  SSLFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.ssl.SSLFactory",e)
                return None
            # print("OK")
        return self._ssl
    @property
    def tls(self):
        if self._tls is None:
            # print("LOAD:TLSFactory")
            try:
                from Jumpscale.sal.tls.TLSFactory import TLSFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.tls.TLSFactory", e)
                raise e
            # print("RUN:TLSFactory")
            try:
                self._tls =  TLSFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.tls.TLSFactory",e)
                return None
            # print("OK")
        return self._tls
    @property
    def ubuntu(self):
        if self._ubuntu is None:
            # print("LOAD:Ubuntu")
            try:
                from Jumpscale.sal.ubuntu.Ubuntu import Ubuntu
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.ubuntu.Ubuntu", e)
                raise e
            # print("RUN:Ubuntu")
            try:
                self._ubuntu =  Ubuntu()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.ubuntu.Ubuntu",e)
                return None
            # print("OK")
        return self._ubuntu
    @property
    def ufw(self):
        if self._ufw is None:
            # print("LOAD:UFWManager")
            try:
                from Jumpscale.sal.ufw.UFWManager import UFWManager
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.ufw.UFWManager", e)
                raise e
            # print("RUN:UFWManager")
            try:
                self._ufw =  UFWManager()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.ufw.UFWManager",e)
                return None
            # print("OK")
        return self._ufw
    @property
    def unix(self):
        if self._unix is None:
            # print("LOAD:UnixSystem")
            try:
                from Jumpscale.sal.unix.Unix import UnixSystem
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.unix.Unix", e)
                raise e
            # print("RUN:UnixSystem")
            try:
                self._unix =  UnixSystem()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.unix.Unix",e)
                return None
            # print("OK")
        return self._unix
    @property
    def windows(self):
        if self._windows is None:
            # print("LOAD:WindowsSystem")
            try:
                from Jumpscale.sal.windows.Windows import WindowsSystem
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.windows.Windows", e)
                raise e
            # print("RUN:WindowsSystem")
            try:
                self._windows =  WindowsSystem()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.windows.Windows",e)
                return None
            # print("OK")
        return self._windows
    @property
    def docker(self):
        if self._docker is None:
            # print("LOAD:Docker")
            try:
                from Jumpscale.tools.docker.Docker import Docker
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.docker.Docker", e)
                raise e
            # print("RUN:Docker")
            try:
                self._docker =  Docker()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.docker.Docker",e)
                return None
            # print("OK")
        return self._docker

j.sal = group_sal()
j.core._groups["sal"] = j.sal


class group_data(JSGroup):
    def __init__(self):
        
        self._bcdb = None
        self._cachelru = None
        self._capnp = None
        self._encryption = None
        self._hash = None
        self._html = None
        self._idgenerator = None
        self._indexfile = None
        self._latex = None
        self._markdown = None
        self._nacl = None
        self._randomnames = None
        self._regex = None
        self._schema = None
        self._serializers = None
        self._time = None
        self._timeinterval = None
        self._treemanager = None
        self._types = None
        self._worksheets = None
        self._dict_editor = None
        self._inifile = None
        self._docs = None
        self._nltk = None

    
    @property
    def bcdb(self):
        if self._bcdb is None:
            # print("LOAD:BCDBFactory")
            try:
                from Jumpscale.data.bcdb.BCDBFactory import BCDBFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.bcdb.BCDBFactory", e)
                raise e
            # print("RUN:BCDBFactory")
            try:
                self._bcdb =  BCDBFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.bcdb.BCDBFactory",e)
                return None
            # print("OK")
        return self._bcdb
    @property
    def cachelru(self):
        if self._cachelru is None:
            # print("LOAD:LRUCacheFactory")
            try:
                from Jumpscale.data.cachelru.LRUCacheFactory import LRUCacheFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.cachelru.LRUCacheFactory", e)
                raise e
            # print("RUN:LRUCacheFactory")
            try:
                self._cachelru =  LRUCacheFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.cachelru.LRUCacheFactory",e)
                return None
            # print("OK")
        return self._cachelru
    @property
    def capnp(self):
        if self._capnp is None:
            # print("LOAD:Capnp")
            try:
                from Jumpscale.data.capnp.Capnp import Capnp
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.capnp.Capnp", e)
                raise e
            # print("RUN:Capnp")
            try:
                self._capnp =  Capnp()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.capnp.Capnp",e)
                return None
            # print("OK")
        return self._capnp
    @property
    def encryption(self):
        if self._encryption is None:
            # print("LOAD:EncryptionFactory")
            try:
                from Jumpscale.data.encryption.EncryptionFactory import EncryptionFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.encryption.EncryptionFactory", e)
                raise e
            # print("RUN:EncryptionFactory")
            try:
                self._encryption =  EncryptionFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.encryption.EncryptionFactory",e)
                return None
            # print("OK")
        return self._encryption
    @property
    def hash(self):
        if self._hash is None:
            # print("LOAD:HashTool")
            try:
                from Jumpscale.data.hash.HashTool import HashTool
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.hash.HashTool", e)
                raise e
            # print("RUN:HashTool")
            try:
                self._hash =  HashTool()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.hash.HashTool",e)
                return None
            # print("OK")
        return self._hash
    @property
    def html(self):
        if self._html is None:
            # print("LOAD:HTMLFactory")
            try:
                from Jumpscale.data.html.HTMLFactory import HTMLFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.html.HTMLFactory", e)
                raise e
            # print("RUN:HTMLFactory")
            try:
                self._html =  HTMLFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.html.HTMLFactory",e)
                return None
            # print("OK")
        return self._html
    @property
    def idgenerator(self):
        if self._idgenerator is None:
            # print("LOAD:IDGenerator")
            try:
                from Jumpscale.data.idgenerator.IDGenerator import IDGenerator
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.idgenerator.IDGenerator", e)
                raise e
            # print("RUN:IDGenerator")
            try:
                self._idgenerator =  IDGenerator()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.idgenerator.IDGenerator",e)
                return None
            # print("OK")
        return self._idgenerator
    @property
    def indexfile(self):
        if self._indexfile is None:
            # print("LOAD:IndexDB")
            try:
                from Jumpscale.data.indexFile.IndexFiles import IndexDB
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.indexFile.IndexFiles", e)
                raise e
            # print("RUN:IndexDB")
            try:
                self._indexfile =  IndexDB()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.indexFile.IndexFiles",e)
                return None
            # print("OK")
        return self._indexfile
    @property
    def latex(self):
        if self._latex is None:
            # print("LOAD:Latex")
            try:
                from Jumpscale.data.latex.Latex import Latex
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.latex.Latex", e)
                raise e
            # print("RUN:Latex")
            try:
                self._latex =  Latex()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.latex.Latex",e)
                return None
            # print("OK")
        return self._latex
    @property
    def markdown(self):
        if self._markdown is None:
            # print("LOAD:MarkdownFactory")
            try:
                from Jumpscale.data.markdown.MarkdownFactory import MarkdownFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.markdown.MarkdownFactory", e)
                raise e
            # print("RUN:MarkdownFactory")
            try:
                self._markdown =  MarkdownFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.markdown.MarkdownFactory",e)
                return None
            # print("OK")
        return self._markdown
    @property
    def nacl(self):
        if self._nacl is None:
            # print("LOAD:NACLFactory")
            try:
                from Jumpscale.data.nacl.NACLFactory import NACLFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.nacl.NACLFactory", e)
                raise e
            # print("RUN:NACLFactory")
            try:
                self._nacl =  NACLFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.nacl.NACLFactory",e)
                return None
            # print("OK")
        return self._nacl
    @property
    def randomnames(self):
        if self._randomnames is None:
            # print("LOAD:RandomNames")
            try:
                from Jumpscale.data.random_names.RandomNames import RandomNames
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.random_names.RandomNames", e)
                raise e
            # print("RUN:RandomNames")
            try:
                self._randomnames =  RandomNames()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.random_names.RandomNames",e)
                return None
            # print("OK")
        return self._randomnames
    @property
    def regex(self):
        if self._regex is None:
            # print("LOAD:RegexTools")
            try:
                from Jumpscale.data.regex.RegexTools import RegexTools
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.regex.RegexTools", e)
                raise e
            # print("RUN:RegexTools")
            try:
                self._regex =  RegexTools()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.regex.RegexTools",e)
                return None
            # print("OK")
        return self._regex
    @property
    def schema(self):
        if self._schema is None:
            # print("LOAD:SchemaFactory")
            try:
                from Jumpscale.data.schema.SchemaFactory import SchemaFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.schema.SchemaFactory", e)
                raise e
            # print("RUN:SchemaFactory")
            try:
                self._schema =  SchemaFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.schema.SchemaFactory",e)
                return None
            # print("OK")
        return self._schema
    @property
    def serializers(self):
        if self._serializers is None:
            # print("LOAD:SerializersFactory")
            try:
                from Jumpscale.data.serializers.SerializersFactory import SerializersFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.serializers.SerializersFactory", e)
                raise e
            # print("RUN:SerializersFactory")
            try:
                self._serializers =  SerializersFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.serializers.SerializersFactory",e)
                return None
            # print("OK")
        return self._serializers
    @property
    def time(self):
        if self._time is None:
            # print("LOAD:Time_")
            try:
                from Jumpscale.data.time.Time import Time_
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.time.Time", e)
                raise e
            # print("RUN:Time_")
            try:
                self._time =  Time_()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.time.Time",e)
                return None
            # print("OK")
        return self._time
    @property
    def timeinterval(self):
        if self._timeinterval is None:
            # print("LOAD:TimeInterval")
            try:
                from Jumpscale.data.time.TimeInterval import TimeInterval
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.time.TimeInterval", e)
                raise e
            # print("RUN:TimeInterval")
            try:
                self._timeinterval =  TimeInterval()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.time.TimeInterval",e)
                return None
            # print("OK")
        return self._timeinterval
    @property
    def treemanager(self):
        if self._treemanager is None:
            # print("LOAD:TreemanagerFactory")
            try:
                from Jumpscale.data.treemanager.Treemanager import TreemanagerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.treemanager.Treemanager", e)
                raise e
            # print("RUN:TreemanagerFactory")
            try:
                self._treemanager =  TreemanagerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.treemanager.Treemanager",e)
                return None
            # print("OK")
        return self._treemanager
    @property
    def types(self):
        if self._types is None:
            # print("LOAD:Types")
            try:
                from Jumpscale.data.types.Types import Types
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.types.Types", e)
                raise e
            # print("RUN:Types")
            try:
                self._types =  Types()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.types.Types",e)
                return None
            # print("OK")
        return self._types
    @property
    def worksheets(self):
        if self._worksheets is None:
            # print("LOAD:Sheets")
            try:
                from Jumpscale.data.worksheets.Sheets import Sheets
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.worksheets.Sheets", e)
                raise e
            # print("RUN:Sheets")
            try:
                self._worksheets =  Sheets()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.worksheets.Sheets",e)
                return None
            # print("OK")
        return self._worksheets
    @property
    def dict_editor(self):
        if self._dict_editor is None:
            # print("LOAD:DictEditorFactory")
            try:
                from Jumpscale.data.dicteditor.DictEditor import DictEditorFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.dicteditor.DictEditor", e)
                raise e
            # print("RUN:DictEditorFactory")
            try:
                self._dict_editor =  DictEditorFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.dicteditor.DictEditor",e)
                return None
            # print("OK")
        return self._dict_editor
    @property
    def inifile(self):
        if self._inifile is None:
            # print("LOAD:InifileTool")
            try:
                from Jumpscale.data.inifile.IniFile import InifileTool
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.inifile.IniFile", e)
                raise e
            # print("RUN:InifileTool")
            try:
                self._inifile =  InifileTool()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.inifile.IniFile",e)
                return None
            # print("OK")
        return self._inifile
    @property
    def docs(self):
        if self._docs is None:
            # print("LOAD:DocsFactory")
            try:
                from Jumpscale.data.docs.DocsFactory import DocsFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.docs.DocsFactory", e)
                raise e
            # print("RUN:DocsFactory")
            try:
                self._docs =  DocsFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.docs.DocsFactory",e)
                return None
            # print("OK")
        return self._docs
    @property
    def nltk(self):
        if self._nltk is None:
            # print("LOAD:NLTKFactory")
            try:
                from DigitalMe.data.nltk.NLTK import NLTKFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.data.nltk.NLTK", e)
                raise e
            # print("RUN:NLTKFactory")
            try:
                self._nltk =  NLTKFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.data.nltk.NLTK",e)
                return None
            # print("OK")
        return self._nltk

j.data = group_data()
j.core._groups["data"] = j.data


class group_tools(JSGroup):
    def __init__(self):
        
        self._email = None
        self._flist = None
        self._numtools = None
        self._tarfile = None
        self._zipfile = None
        self._issuemanager = None
        self._bash = None
        self._aggregator = None
        self._realityprocess = None
        self._notapplicableyet = None
        self._capacity = None
        self._codeloader = None
        self._code = None
        self._code = None
        self._console = None
        self._cython = None
        self._dash = None
        self._dnstools = None
        self._executor = None
        self._executorLocal = None
        self._expect = None
        self._fixer = None
        self._imagelib = None
        self._itenv_manager = None
        self._jinja2 = None
        self._legal_contracts = None
        self._memusagetest = None
        self._objectinspector = None
        self._offliner = None
        self._rexplorer = None
        self._path = None
        self._performancetrace = None
        self._reportlab = None
        self._sandboxer = None
        self._storybot = None
        self._syncer = None
        self._team_manager = None
        self._testengine = None
        self._timer = None
        self._tmux = None
        self._typechecker = None
        self._formatters = None
        self._kosmos = None
        self._codegenerator = None
        self._markdowndocs = None
        self._tfbot = None
        self._zos = None

    
    @property
    def email(self):
        if self._email is None:
            # print("LOAD:EmailTool")
            try:
                from Jumpscale.data.email.Email import EmailTool
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.email.Email", e)
                raise e
            # print("RUN:EmailTool")
            try:
                self._email =  EmailTool()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.email.Email",e)
                return None
            # print("OK")
        return self._email
    @property
    def flist(self):
        if self._flist is None:
            # print("LOAD:FListFactory")
            try:
                from Jumpscale.data.flist.FListFactory import FListFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.flist.FListFactory", e)
                raise e
            # print("RUN:FListFactory")
            try:
                self._flist =  FListFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.flist.FListFactory",e)
                return None
            # print("OK")
        return self._flist
    @property
    def numtools(self):
        if self._numtools is None:
            # print("LOAD:NumTools")
            try:
                from Jumpscale.data.numtools.NumTools import NumTools
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.numtools.NumTools", e)
                raise e
            # print("RUN:NumTools")
            try:
                self._numtools =  NumTools()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.numtools.NumTools",e)
                return None
            # print("OK")
        return self._numtools
    @property
    def tarfile(self):
        if self._tarfile is None:
            # print("LOAD:TarFileFactory")
            try:
                from Jumpscale.data.tarfile.TarFile import TarFileFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.tarfile.TarFile", e)
                raise e
            # print("RUN:TarFileFactory")
            try:
                self._tarfile =  TarFileFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.tarfile.TarFile",e)
                return None
            # print("OK")
        return self._tarfile
    @property
    def zipfile(self):
        if self._zipfile is None:
            # print("LOAD:ZipFileFactory")
            try:
                from Jumpscale.data.zip.ZipFile import ZipFileFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.zip.ZipFile", e)
                raise e
            # print("RUN:ZipFileFactory")
            try:
                self._zipfile =  ZipFileFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.zip.ZipFile",e)
                return None
            # print("OK")
        return self._zipfile
    @property
    def issuemanager(self):
        if self._issuemanager is None:
            # print("LOAD:IssueManager")
            try:
                from Jumpscale.data.issuemanager.IssueManager import IssueManager
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.issuemanager.IssueManager", e)
                raise e
            # print("RUN:IssueManager")
            try:
                self._issuemanager =  IssueManager()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.issuemanager.IssueManager",e)
                return None
            # print("OK")
        return self._issuemanager
    @property
    def bash(self):
        if self._bash is None:
            # print("LOAD:BashFactory")
            try:
                from Jumpscale.sal.bash.BashFactory import BashFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal.bash.BashFactory", e)
                raise e
            # print("RUN:BashFactory")
            try:
                self._bash =  BashFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal.bash.BashFactory",e)
                return None
            # print("OK")
        return self._bash
    @property
    def aggregator(self):
        if self._aggregator is None:
            # print("LOAD:Aggregator")
            try:
                from Jumpscale.tools.aggregator.Aggregator import Aggregator
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.aggregator.Aggregator", e)
                raise e
            # print("RUN:Aggregator")
            try:
                self._aggregator =  Aggregator()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.aggregator.Aggregator",e)
                return None
            # print("OK")
        return self._aggregator
    @property
    def realityprocess(self):
        if self._realityprocess is None:
            # print("LOAD:RealitProcess")
            try:
                from Jumpscale.tools.aggregator.RealityProcess import RealitProcess
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.aggregator.RealityProcess", e)
                raise e
            # print("RUN:RealitProcess")
            try:
                self._realityprocess =  RealitProcess()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.aggregator.RealityProcess",e)
                return None
            # print("OK")
        return self._realityprocess
    @property
    def notapplicableyet(self):
        if self._notapplicableyet is None:
            # print("LOAD:Builder")
            try:
                from Jumpscale.tools.builder.Builder import Builder
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.builder.Builder", e)
                raise e
            # print("RUN:Builder")
            try:
                self._notapplicableyet =  Builder()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.builder.Builder",e)
                return None
            # print("OK")
        return self._notapplicableyet
    @property
    def capacity(self):
        if self._capacity is None:
            # print("LOAD:Factory")
            try:
                from Jumpscale.tools.capacity.Factory import Factory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.capacity.Factory", e)
                raise e
            # print("RUN:Factory")
            try:
                self._capacity =  Factory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.capacity.Factory",e)
                return None
            # print("OK")
        return self._capacity
    @property
    def codeloader(self):
        if self._codeloader is None:
            # print("LOAD:CodeLoader")
            try:
                from Jumpscale.tools.codeloader.CodeLoader import CodeLoader
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.codeloader.CodeLoader", e)
                raise e
            # print("RUN:CodeLoader")
            try:
                self._codeloader =  CodeLoader()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.codeloader.CodeLoader",e)
                return None
            # print("OK")
        return self._codeloader
    @property
    def code(self):
        if self._code is None:
            # print("LOAD:CodeTools")
            try:
                from Jumpscale.tools.codeloader.CodeTools import CodeTools
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.codeloader.CodeTools", e)
                raise e
            # print("RUN:CodeTools")
            try:
                self._code =  CodeTools()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.codeloader.CodeTools",e)
                return None
            # print("OK")
        return self._code
    @property
    def code(self):
        if self._code is None:
            # print("LOAD:CodeTools")
            try:
                from Jumpscale.tools.codetools.CodeTools import CodeTools
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.codetools.CodeTools", e)
                raise e
            # print("RUN:CodeTools")
            try:
                self._code =  CodeTools()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.codetools.CodeTools",e)
                return None
            # print("OK")
        return self._code
    @property
    def console(self):
        if self._console is None:
            # print("LOAD:Console")
            try:
                from Jumpscale.tools.console.Console import Console
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.console.Console", e)
                raise e
            # print("RUN:Console")
            try:
                self._console =  Console()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.console.Console",e)
                return None
            # print("OK")
        return self._console
    @property
    def cython(self):
        if self._cython is None:
            # print("LOAD:CythonFactory")
            try:
                from Jumpscale.tools.cython.CythonFactory import CythonFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.cython.CythonFactory", e)
                raise e
            # print("RUN:CythonFactory")
            try:
                self._cython =  CythonFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.cython.CythonFactory",e)
                return None
            # print("OK")
        return self._cython
    @property
    def dash(self):
        if self._dash is None:
            # print("LOAD:DASH")
            try:
                from Jumpscale.tools.dash.DASH import DASH
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.dash.DASH", e)
                raise e
            # print("RUN:DASH")
            try:
                self._dash =  DASH()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.dash.DASH",e)
                return None
            # print("OK")
        return self._dash
    @property
    def dnstools(self):
        if self._dnstools is None:
            # print("LOAD:DNSTools")
            try:
                from Jumpscale.tools.dnstools.DNSTools import DNSTools
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.dnstools.DNSTools", e)
                raise e
            # print("RUN:DNSTools")
            try:
                self._dnstools =  DNSTools()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.dnstools.DNSTools",e)
                return None
            # print("OK")
        return self._dnstools
    @property
    def executor(self):
        if self._executor is None:
            # print("LOAD:ExecutorFactory")
            try:
                from Jumpscale.tools.executor.ExecutorFactory import ExecutorFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.executor.ExecutorFactory", e)
                raise e
            # print("RUN:ExecutorFactory")
            try:
                self._executor =  ExecutorFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.executor.ExecutorFactory",e)
                return None
            # print("OK")
        return self._executor
    @property
    def executorLocal(self):
        if self._executorLocal is None:
            # print("LOAD:ExecutorLocal")
            try:
                from Jumpscale.tools.executor.ExecutorLocal import ExecutorLocal
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.executor.ExecutorLocal", e)
                raise e
            # print("RUN:ExecutorLocal")
            try:
                self._executorLocal =  ExecutorLocal()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.executor.ExecutorLocal",e)
                return None
            # print("OK")
        return self._executorLocal
    @property
    def expect(self):
        if self._expect is None:
            # print("LOAD:ExpectTool")
            try:
                from Jumpscale.tools.expect.Expect import ExpectTool
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.expect.Expect", e)
                raise e
            # print("RUN:ExpectTool")
            try:
                self._expect =  ExpectTool()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.expect.Expect",e)
                return None
            # print("OK")
        return self._expect
    @property
    def fixer(self):
        if self._fixer is None:
            # print("LOAD:Fixer")
            try:
                from Jumpscale.tools.fixer.Fixer import Fixer
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.fixer.Fixer", e)
                raise e
            # print("RUN:Fixer")
            try:
                self._fixer =  Fixer()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.fixer.Fixer",e)
                return None
            # print("OK")
        return self._fixer
    @property
    def imagelib(self):
        if self._imagelib is None:
            # print("LOAD:ImageLib")
            try:
                from Jumpscale.tools.imagelib.ImageLib import ImageLib
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.imagelib.ImageLib", e)
                raise e
            # print("RUN:ImageLib")
            try:
                self._imagelib =  ImageLib()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.imagelib.ImageLib",e)
                return None
            # print("OK")
        return self._imagelib
    @property
    def itenv_manager(self):
        if self._itenv_manager is None:
            # print("LOAD:ITEnvManager")
            try:
                from Jumpscale.tools.itenvmgr.ITEnvManager import ITEnvManager
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.itenvmgr.ITEnvManager", e)
                raise e
            # print("RUN:ITEnvManager")
            try:
                self._itenv_manager =  ITEnvManager()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.itenvmgr.ITEnvManager",e)
                return None
            # print("OK")
        return self._itenv_manager
    @property
    def jinja2(self):
        if self._jinja2 is None:
            # print("LOAD:Jinja2")
            try:
                from Jumpscale.tools.jinja2.Jinja2 import Jinja2
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.jinja2.Jinja2", e)
                raise e
            # print("RUN:Jinja2")
            try:
                self._jinja2 =  Jinja2()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.jinja2.Jinja2",e)
                return None
            # print("OK")
        return self._jinja2
    @property
    def legal_contracts(self):
        if self._legal_contracts is None:
            # print("LOAD:LegalContractsFactory")
            try:
                from Jumpscale.tools.legal_contracts.LegalContractsFactory import LegalContractsFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.legal_contracts.LegalContractsFactory", e)
                raise e
            # print("RUN:LegalContractsFactory")
            try:
                self._legal_contracts =  LegalContractsFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.legal_contracts.LegalContractsFactory",e)
                return None
            # print("OK")
        return self._legal_contracts
    @property
    def memusagetest(self):
        if self._memusagetest is None:
            # print("LOAD:MemUsageTest")
            try:
                from Jumpscale.tools.memusagetest.MemUsageTest import MemUsageTest
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.memusagetest.MemUsageTest", e)
                raise e
            # print("RUN:MemUsageTest")
            try:
                self._memusagetest =  MemUsageTest()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.memusagetest.MemUsageTest",e)
                return None
            # print("OK")
        return self._memusagetest
    @property
    def objectinspector(self):
        if self._objectinspector is None:
            # print("LOAD:ObjectInspector")
            try:
                from Jumpscale.tools.objectinspector.ObjectInspector import ObjectInspector
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.objectinspector.ObjectInspector", e)
                raise e
            # print("RUN:ObjectInspector")
            try:
                self._objectinspector =  ObjectInspector()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.objectinspector.ObjectInspector",e)
                return None
            # print("OK")
        return self._objectinspector
    @property
    def offliner(self):
        if self._offliner is None:
            # print("LOAD:Offliner")
            try:
                from Jumpscale.tools.offliner.Offliner import Offliner
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.offliner.Offliner", e)
                raise e
            # print("RUN:Offliner")
            try:
                self._offliner =  Offliner()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.offliner.Offliner",e)
                return None
            # print("OK")
        return self._offliner
    @property
    def rexplorer(self):
        if self._rexplorer is None:
            # print("LOAD:Rexplorer")
            try:
                from Jumpscale.tools.offliner.Rexplorer import Rexplorer
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.offliner.Rexplorer", e)
                raise e
            # print("RUN:Rexplorer")
            try:
                self._rexplorer =  Rexplorer()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.offliner.Rexplorer",e)
                return None
            # print("OK")
        return self._rexplorer
    @property
    def path(self):
        if self._path is None:
            # print("LOAD:PathFactory")
            try:
                from Jumpscale.tools.path.PathFactory import PathFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.path.PathFactory", e)
                raise e
            # print("RUN:PathFactory")
            try:
                self._path =  PathFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.path.PathFactory",e)
                return None
            # print("OK")
        return self._path
    @property
    def performancetrace(self):
        if self._performancetrace is None:
            # print("LOAD:PerformanceTraceFactory")
            try:
                from Jumpscale.tools.performancetrace.PerformanceTrace import PerformanceTraceFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.performancetrace.PerformanceTrace", e)
                raise e
            # print("RUN:PerformanceTraceFactory")
            try:
                self._performancetrace =  PerformanceTraceFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.performancetrace.PerformanceTrace",e)
                return None
            # print("OK")
        return self._performancetrace
    @property
    def reportlab(self):
        if self._reportlab is None:
            # print("LOAD:ReportlabFactory")
            try:
                from Jumpscale.tools.reportlab.ReportlabFactory import ReportlabFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.reportlab.ReportlabFactory", e)
                raise e
            # print("RUN:ReportlabFactory")
            try:
                self._reportlab =  ReportlabFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.reportlab.ReportlabFactory",e)
                return None
            # print("OK")
        return self._reportlab
    @property
    def sandboxer(self):
        if self._sandboxer is None:
            # print("LOAD:Sandboxer")
            try:
                from Jumpscale.tools.sandboxer.Sandboxer import Sandboxer
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.sandboxer.Sandboxer", e)
                raise e
            # print("RUN:Sandboxer")
            try:
                self._sandboxer =  Sandboxer()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.sandboxer.Sandboxer",e)
                return None
            # print("OK")
        return self._sandboxer
    @property
    def storybot(self):
        if self._storybot is None:
            # print("LOAD:StoryBotFactory")
            try:
                from Jumpscale.tools.storybot.StoryBotFactory import StoryBotFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.storybot.StoryBotFactory", e)
                raise e
            # print("RUN:StoryBotFactory")
            try:
                self._storybot =  StoryBotFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.storybot.StoryBotFactory",e)
                return None
            # print("OK")
        return self._storybot
    @property
    def syncer(self):
        if self._syncer is None:
            # print("LOAD:SyncerFactory")
            try:
                from Jumpscale.tools.syncer.SyncerFactory import SyncerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.syncer.SyncerFactory", e)
                raise e
            # print("RUN:SyncerFactory")
            try:
                self._syncer =  SyncerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.syncer.SyncerFactory",e)
                return None
            # print("OK")
        return self._syncer
    @property
    def team_manager(self):
        if self._team_manager is None:
            # print("LOAD:Teammgr")
            try:
                from Jumpscale.tools.teammgr.Teammgr import Teammgr
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.teammgr.Teammgr", e)
                raise e
            # print("RUN:Teammgr")
            try:
                self._team_manager =  Teammgr()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.teammgr.Teammgr",e)
                return None
            # print("OK")
        return self._team_manager
    @property
    def testengine(self):
        if self._testengine is None:
            # print("LOAD:TestEngine")
            try:
                from Jumpscale.tools.testengine.TestEngine import TestEngine
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.testengine.TestEngine", e)
                raise e
            # print("RUN:TestEngine")
            try:
                self._testengine =  TestEngine()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.testengine.TestEngine",e)
                return None
            # print("OK")
        return self._testengine
    @property
    def timer(self):
        if self._timer is None:
            # print("LOAD:TIMER")
            try:
                from Jumpscale.tools.timer.Timer import TIMER
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.timer.Timer", e)
                raise e
            # print("RUN:TIMER")
            try:
                self._timer =  TIMER()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.timer.Timer",e)
                return None
            # print("OK")
        return self._timer
    @property
    def tmux(self):
        if self._tmux is None:
            # print("LOAD:Tmux")
            try:
                from Jumpscale.tools.tmux.Tmux import Tmux
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.tmux.Tmux", e)
                raise e
            # print("RUN:Tmux")
            try:
                self._tmux =  Tmux()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.tmux.Tmux",e)
                return None
            # print("OK")
        return self._tmux
    @property
    def typechecker(self):
        if self._typechecker is None:
            # print("LOAD:TypeCheckerFactory")
            try:
                from Jumpscale.tools.typechecker.TypeChecker import TypeCheckerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.typechecker.TypeChecker", e)
                raise e
            # print("RUN:TypeCheckerFactory")
            try:
                self._typechecker =  TypeCheckerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.typechecker.TypeChecker",e)
                return None
            # print("OK")
        return self._typechecker
    @property
    def formatters(self):
        if self._formatters is None:
            # print("LOAD:FormattersFactory")
            try:
                from Jumpscale.tools.formatters.FormattersFactory import FormattersFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.formatters.FormattersFactory", e)
                raise e
            # print("RUN:FormattersFactory")
            try:
                self._formatters =  FormattersFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.formatters.FormattersFactory",e)
                return None
            # print("OK")
        return self._formatters
    @property
    def kosmos(self):
        if self._kosmos is None:
            # print("LOAD:Kosmos")
            try:
                from Jumpscale.tools.kosmos.Kosmos import Kosmos
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.kosmos.Kosmos", e)
                raise e
            # print("RUN:Kosmos")
            try:
                self._kosmos =  Kosmos()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.kosmos.Kosmos",e)
                return None
            # print("OK")
        return self._kosmos
    @property
    def codegenerator(self):
        if self._codegenerator is None:
            # print("LOAD:CodeGenerator")
            try:
                from Jumpscale.tools.codegenerator.CodeGenerator import CodeGenerator
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.codegenerator.CodeGenerator", e)
                raise e
            # print("RUN:CodeGenerator")
            try:
                self._codegenerator =  CodeGenerator()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.codegenerator.CodeGenerator",e)
                return None
            # print("OK")
        return self._codegenerator
    @property
    def markdowndocs(self):
        if self._markdowndocs is None:
            # print("LOAD:MarkDownDocs")
            try:
                from Jumpscale.tools.markdowndocs.MarkDownDocs import MarkDownDocs
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tools.markdowndocs.MarkDownDocs", e)
                raise e
            # print("RUN:MarkDownDocs")
            try:
                self._markdowndocs =  MarkDownDocs()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tools.markdowndocs.MarkDownDocs",e)
                return None
            # print("OK")
        return self._markdowndocs
    @property
    def tfbot(self):
        if self._tfbot is None:
            # print("LOAD:TFBotFactory")
            try:
                from DigitalMe.tools.tfbot.TFBotFactory import TFBotFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.tools.tfbot.TFBotFactory", e)
                raise e
            # print("RUN:TFBotFactory")
            try:
                self._tfbot =  TFBotFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.tools.tfbot.TFBotFactory",e)
                return None
            # print("OK")
        return self._tfbot
    @property
    def zos(self):
        if self._zos is None:
            # print("LOAD:ZOSFactory")
            try:
                from DigitalMe.tools.zos.ZOSFactory import ZOSFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.tools.zos.ZOSFactory", e)
                raise e
            # print("RUN:ZOSFactory")
            try:
                self._zos =  ZOSFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.tools.zos.ZOSFactory",e)
                return None
            # print("OK")
        return self._zos

j.tools = group_tools()
j.core._groups["tools"] = j.tools


class group_data_units(JSGroup):
    def __init__(self):
        
        self._sizes = None

    
    @property
    def sizes(self):
        if self._sizes is None:
            # print("LOAD:Bytes")
            try:
                from Jumpscale.data.numtools.units.Units import Bytes
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.data.numtools.units.Units", e)
                raise e
            # print("RUN:Bytes")
            try:
                self._sizes =  Bytes()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.data.numtools.units.Units",e)
                return None
            # print("OK")
        return self._sizes

j.data_units = group_data_units()
j.core._groups["data_units"] = j.data_units


class group_servers(JSGroup):
    def __init__(self):
        
        self._errbot = None
        self._capacity = None
        self._jsrun = None
        self._openresty = None
        self._web = None
        self._zdb = None
        self._digitalme = None
        self._dns = None
        self._gedis = None
        self._myjobs = None
        self._raftserver = None

    
    @property
    def errbot(self):
        if self._errbot is None:
            # print("LOAD:ErrBotFactory")
            try:
                from Jumpscale.servers.errbot.ErrBotFactory import ErrBotFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.servers.errbot.ErrBotFactory", e)
                raise e
            # print("RUN:ErrBotFactory")
            try:
                self._errbot =  ErrBotFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.servers.errbot.ErrBotFactory",e)
                return None
            # print("OK")
        return self._errbot
    @property
    def capacity(self):
        if self._capacity is None:
            # print("LOAD:CapacityFactory")
            try:
                from Jumpscale.servers.grid_capacity.CapacityFactory import CapacityFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.servers.grid_capacity.CapacityFactory", e)
                raise e
            # print("RUN:CapacityFactory")
            try:
                self._capacity =  CapacityFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.servers.grid_capacity.CapacityFactory",e)
                return None
            # print("OK")
        return self._capacity
    @property
    def jsrun(self):
        if self._jsrun is None:
            # print("LOAD:JSRun")
            try:
                from Jumpscale.servers.jsrun.JSRun import JSRun
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.servers.jsrun.JSRun", e)
                raise e
            # print("RUN:JSRun")
            try:
                self._jsrun =  JSRun()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.servers.jsrun.JSRun",e)
                return None
            # print("OK")
        return self._jsrun
    @property
    def openresty(self):
        if self._openresty is None:
            # print("LOAD:OpenRestyFactory")
            try:
                from Jumpscale.servers.openresty.OpenRestyFactory import OpenRestyFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.servers.openresty.OpenRestyFactory", e)
                raise e
            # print("RUN:OpenRestyFactory")
            try:
                self._openresty =  OpenRestyFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.servers.openresty.OpenRestyFactory",e)
                return None
            # print("OK")
        return self._openresty
    @property
    def web(self):
        if self._web is None:
            # print("LOAD:JSWebServers")
            try:
                from Jumpscale.servers.webserver.JSWebServers import JSWebServers
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.servers.webserver.JSWebServers", e)
                raise e
            # print("RUN:JSWebServers")
            try:
                self._web =  JSWebServers()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.servers.webserver.JSWebServers",e)
                return None
            # print("OK")
        return self._web
    @property
    def zdb(self):
        if self._zdb is None:
            # print("LOAD:ZDBServer")
            try:
                from Jumpscale.servers.zdb.ZDBServer import ZDBServer
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.servers.zdb.ZDBServer", e)
                raise e
            # print("RUN:ZDBServer")
            try:
                self._zdb =  ZDBServer()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.servers.zdb.ZDBServer",e)
                return None
            # print("OK")
        return self._zdb
    @property
    def digitalme(self):
        if self._digitalme is None:
            # print("LOAD:DigitalMe")
            try:
                from DigitalMe.servers.digitalme.DigitalMe import DigitalMe
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.servers.digitalme.DigitalMe", e)
                raise e
            # print("RUN:DigitalMe")
            try:
                self._digitalme =  DigitalMe()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.servers.digitalme.DigitalMe",e)
                return None
            # print("OK")
        return self._digitalme
    @property
    def dns(self):
        if self._dns is None:
            # print("LOAD:DNSServerFactory")
            try:
                from DigitalMe.servers.dns.DNSServerFactory import DNSServerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.servers.dns.DNSServerFactory", e)
                raise e
            # print("RUN:DNSServerFactory")
            try:
                self._dns =  DNSServerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.servers.dns.DNSServerFactory",e)
                return None
            # print("OK")
        return self._dns
    @property
    def gedis(self):
        if self._gedis is None:
            # print("LOAD:GedisFactory")
            try:
                from DigitalMe.servers.gedis.GedisFactory import GedisFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.servers.gedis.GedisFactory", e)
                raise e
            # print("RUN:GedisFactory")
            try:
                self._gedis =  GedisFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.servers.gedis.GedisFactory",e)
                return None
            # print("OK")
        return self._gedis
    @property
    def myjobs(self):
        if self._myjobs is None:
            # print("LOAD:MyJobs")
            try:
                from DigitalMe.servers.myjobs.MyJobs import MyJobs
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.servers.myjobs.MyJobs", e)
                raise e
            # print("RUN:MyJobs")
            try:
                self._myjobs =  MyJobs()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.servers.myjobs.MyJobs",e)
                return None
            # print("OK")
        return self._myjobs
    @property
    def raftserver(self):
        if self._raftserver is None:
            # print("LOAD:RaftServerFactory")
            try:
                from DigitalMe.servers.raft.RaftServerFactory import RaftServerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.servers.raft.RaftServerFactory", e)
                raise e
            # print("RUN:RaftServerFactory")
            try:
                self._raftserver =  RaftServerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.servers.raft.RaftServerFactory",e)
                return None
            # print("OK")
        return self._raftserver

j.servers = group_servers()
j.core._groups["servers"] = j.servers


class group_tutorials(JSGroup):
    def __init__(self):
        
        self._base = None

    
    @property
    def base(self):
        if self._base is None:
            # print("LOAD:Tutorial")
            try:
                from Jumpscale.tutorials.base.Tutorial import Tutorial
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.tutorials.base.Tutorial", e)
                raise e
            # print("RUN:Tutorial")
            try:
                self._base =  Tutorial()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.tutorials.base.Tutorial",e)
                return None
            # print("OK")
        return self._base

j.tutorials = group_tutorials()
j.core._groups["tutorials"] = j.tutorials


class group_builder(JSGroup):
    def __init__(self):
        
        self._apps = None
        self._buildenv = None
        self._db = None
        self._network = None
        self._runtimes = None
        self._system = None
        self._tools = None
        self.__template = None
        self._blockchain = None
        self._libs = None
        self._libs = None
        self._monitoring = None
        self.__template = None
        self._systemtools = None
        self._web = None

    
    @property
    def apps(self):
        if self._apps is None:
            # print("LOAD:BuilderAppsFactory")
            try:
                from Jumpscale.builder.apps.BuilderAppsFactory import BuilderAppsFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.apps.BuilderAppsFactory", e)
                raise e
            # print("RUN:BuilderAppsFactory")
            try:
                self._apps =  BuilderAppsFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.apps.BuilderAppsFactory",e)
                return None
            # print("OK")
        return self._apps
    @property
    def buildenv(self):
        if self._buildenv is None:
            # print("LOAD:BuildEnv")
            try:
                from Jumpscale.builder.buildenv.BuildEnv import BuildEnv
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.buildenv.BuildEnv", e)
                raise e
            # print("RUN:BuildEnv")
            try:
                self._buildenv =  BuildEnv()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.buildenv.BuildEnv",e)
                return None
            # print("OK")
        return self._buildenv
    @property
    def db(self):
        if self._db is None:
            # print("LOAD:BuildDBFactory")
            try:
                from Jumpscale.builder.db.BuildDBFactory import BuildDBFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.db.BuildDBFactory", e)
                raise e
            # print("RUN:BuildDBFactory")
            try:
                self._db =  BuildDBFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.db.BuildDBFactory",e)
                return None
            # print("OK")
        return self._db
    @property
    def network(self):
        if self._network is None:
            # print("LOAD:BuilderNetworkFactory")
            try:
                from Jumpscale.builder.network.BuilderNetworkFactory import BuilderNetworkFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.network.BuilderNetworkFactory", e)
                raise e
            # print("RUN:BuilderNetworkFactory")
            try:
                self._network =  BuilderNetworkFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.network.BuilderNetworkFactory",e)
                return None
            # print("OK")
        return self._network
    @property
    def runtimes(self):
        if self._runtimes is None:
            # print("LOAD:BuilderRuntimesFactory")
            try:
                from Jumpscale.builder.runtimes.BuilderRuntimesFactory import BuilderRuntimesFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.runtimes.BuilderRuntimesFactory", e)
                raise e
            # print("RUN:BuilderRuntimesFactory")
            try:
                self._runtimes =  BuilderRuntimesFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.runtimes.BuilderRuntimesFactory",e)
                return None
            # print("OK")
        return self._runtimes
    @property
    def system(self):
        if self._system is None:
            # print("LOAD:BuilderSystemPackage")
            try:
                from Jumpscale.builder.system.BuilderSystemFactory import BuilderSystemPackage
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.system.BuilderSystemFactory", e)
                raise e
            # print("RUN:BuilderSystemPackage")
            try:
                self._system =  BuilderSystemPackage()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.system.BuilderSystemFactory",e)
                return None
            # print("OK")
        return self._system
    @property
    def tools(self):
        if self._tools is None:
            # print("LOAD:BuilderTools")
            try:
                from Jumpscale.builder.tools.BuilderTools import BuilderTools
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.tools.BuilderTools", e)
                raise e
            # print("RUN:BuilderTools")
            try:
                self._tools =  BuilderTools()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.tools.BuilderTools",e)
                return None
            # print("OK")
        return self._tools
    @property
    def _template(self):
        if self.__template is None:
            # print("LOAD:GrafanaFactory")
            try:
                from Jumpscale.builder.TEMPLATE.BuilderGrafanaFactory import GrafanaFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.TEMPLATE.BuilderGrafanaFactory", e)
                raise e
            # print("RUN:GrafanaFactory")
            try:
                self.__template =  GrafanaFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.TEMPLATE.BuilderGrafanaFactory",e)
                return None
            # print("OK")
        return self.__template
    @property
    def blockchain(self):
        if self._blockchain is None:
            # print("LOAD:BuilderBlockchainFactory")
            try:
                from Jumpscale.builder.blockchain.BuilderBlockchainFactory import BuilderBlockchainFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.blockchain.BuilderBlockchainFactory", e)
                raise e
            # print("RUN:BuilderBlockchainFactory")
            try:
                self._blockchain =  BuilderBlockchainFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.blockchain.BuilderBlockchainFactory",e)
                return None
            # print("OK")
        return self._blockchain
    @property
    def libs(self):
        if self._libs is None:
            # print("LOAD:BuilderLibs")
            try:
                from Jumpscale.builder.libs.BuilderLibs import BuilderLibs
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.libs.BuilderLibs", e)
                raise e
            # print("RUN:BuilderLibs")
            try:
                self._libs =  BuilderLibs()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.libs.BuilderLibs",e)
                return None
            # print("OK")
        return self._libs
    @property
    def libs(self):
        if self._libs is None:
            # print("LOAD:BuilderLibsFactory")
            try:
                from Jumpscale.builder.libs.BuilderLibsFactory import BuilderLibsFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.libs.BuilderLibsFactory", e)
                raise e
            # print("RUN:BuilderLibsFactory")
            try:
                self._libs =  BuilderLibsFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.libs.BuilderLibsFactory",e)
                return None
            # print("OK")
        return self._libs
    @property
    def monitoring(self):
        if self._monitoring is None:
            # print("LOAD:BuilderMonitoringFactory")
            try:
                from Jumpscale.builder.monitoring.BuilderMonitoringFactory import BuilderMonitoringFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.monitoring.BuilderMonitoringFactory", e)
                raise e
            # print("RUN:BuilderMonitoringFactory")
            try:
                self._monitoring =  BuilderMonitoringFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.monitoring.BuilderMonitoringFactory",e)
                return None
            # print("OK")
        return self._monitoring
    @property
    def _template(self):
        if self.__template is None:
            # print("LOAD:BuilderGrafanaFactory")
            try:
                from Jumpscale.builder.monitoring.BuilderGrafanaFactory import BuilderGrafanaFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.monitoring.BuilderGrafanaFactory", e)
                raise e
            # print("RUN:BuilderGrafanaFactory")
            try:
                self.__template =  BuilderGrafanaFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.monitoring.BuilderGrafanaFactory",e)
                return None
            # print("OK")
        return self.__template
    @property
    def systemtools(self):
        if self._systemtools is None:
            # print("LOAD:BuilderSystemToolsFactory")
            try:
                from Jumpscale.builder.systemtools.BuilderSystemToolsFactory import BuilderSystemToolsFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.systemtools.BuilderSystemToolsFactory", e)
                raise e
            # print("RUN:BuilderSystemToolsFactory")
            try:
                self._systemtools =  BuilderSystemToolsFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.systemtools.BuilderSystemToolsFactory",e)
                return None
            # print("OK")
        return self._systemtools
    @property
    def web(self):
        if self._web is None:
            # print("LOAD:BuilderWebFactory")
            try:
                from Jumpscale.builder.web.BuilderWebFactory import BuilderWebFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.builder.web.BuilderWebFactory", e)
                raise e
            # print("RUN:BuilderWebFactory")
            try:
                self._web =  BuilderWebFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.builder.web.BuilderWebFactory",e)
                return None
            # print("OK")
        return self._web

j.builder = group_builder()
j.core._groups["builder"] = j.builder


class group_sal_zos(JSGroup):
    def __init__(self):
        
        self._capacity = None
        self._containers = None
        self._disks = None
        self._gateway = None
        self._hypervisor = None
        self._ippoolmanager = None
        self._minio = None
        self._mongodb = None
        self._network = None
        self._node = None
        self._primitives = None
        self._storagepools = None
        self._vm = None
        self._zerodb = None
        self._etcd = None
        self._pubsub = None
        self._coredns = None
        self._farm = None
        self._ftpclient = None
        self._grafana = None
        self._influx = None
        self._sandbox = None
        self._stats_collector = None
        self._tfchain = None
        self._traefik = None
        self._zt_bootstrap = None
        self._zrobot = None
        self._zstor = None

    
    @property
    def capacity(self):
        if self._capacity is None:
            # print("LOAD:CapacityFactory")
            try:
                from Jumpscale.sal_zos.capacity.CapacityFactory import CapacityFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.capacity.CapacityFactory", e)
                raise e
            # print("RUN:CapacityFactory")
            try:
                self._capacity =  CapacityFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.capacity.CapacityFactory",e)
                return None
            # print("OK")
        return self._capacity
    @property
    def containers(self):
        if self._containers is None:
            # print("LOAD:ContainerFactory")
            try:
                from Jumpscale.sal_zos.container.ContainerFactory import ContainerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.container.ContainerFactory", e)
                raise e
            # print("RUN:ContainerFactory")
            try:
                self._containers =  ContainerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.container.ContainerFactory",e)
                return None
            # print("OK")
        return self._containers
    @property
    def disks(self):
        if self._disks is None:
            # print("LOAD:DisksFactory")
            try:
                from Jumpscale.sal_zos.disks.DisksFactory import DisksFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.disks.DisksFactory", e)
                raise e
            # print("RUN:DisksFactory")
            try:
                self._disks =  DisksFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.disks.DisksFactory",e)
                return None
            # print("OK")
        return self._disks
    @property
    def gateway(self):
        if self._gateway is None:
            # print("LOAD:GatewayFactory")
            try:
                from Jumpscale.sal_zos.gateway.gatewayFactory import GatewayFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.gateway.gatewayFactory", e)
                raise e
            # print("RUN:GatewayFactory")
            try:
                self._gateway =  GatewayFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.gateway.gatewayFactory",e)
                return None
            # print("OK")
        return self._gateway
    @property
    def hypervisor(self):
        if self._hypervisor is None:
            # print("LOAD:HypervisorFactory")
            try:
                from Jumpscale.sal_zos.hypervisor.HypervisorFactory import HypervisorFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.hypervisor.HypervisorFactory", e)
                raise e
            # print("RUN:HypervisorFactory")
            try:
                self._hypervisor =  HypervisorFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.hypervisor.HypervisorFactory",e)
                return None
            # print("OK")
        return self._hypervisor
    @property
    def ippoolmanager(self):
        if self._ippoolmanager is None:
            # print("LOAD:IPPoolManagerFactory")
            try:
                from Jumpscale.sal_zos.ip_pool_manager.IPPoolManagerFactory import IPPoolManagerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.ip_pool_manager.IPPoolManagerFactory", e)
                raise e
            # print("RUN:IPPoolManagerFactory")
            try:
                self._ippoolmanager =  IPPoolManagerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.ip_pool_manager.IPPoolManagerFactory",e)
                return None
            # print("OK")
        return self._ippoolmanager
    @property
    def minio(self):
        if self._minio is None:
            # print("LOAD:MinioFactory")
            try:
                from Jumpscale.sal_zos.minio.MinioFactory import MinioFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.minio.MinioFactory", e)
                raise e
            # print("RUN:MinioFactory")
            try:
                self._minio =  MinioFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.minio.MinioFactory",e)
                return None
            # print("OK")
        return self._minio
    @property
    def mongodb(self):
        if self._mongodb is None:
            # print("LOAD:MongodbFactory")
            try:
                from Jumpscale.sal_zos.mongodb.MongodbFactory import MongodbFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.mongodb.MongodbFactory", e)
                raise e
            # print("RUN:MongodbFactory")
            try:
                self._mongodb =  MongodbFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.mongodb.MongodbFactory",e)
                return None
            # print("OK")
        return self._mongodb
    @property
    def network(self):
        if self._network is None:
            # print("LOAD:NetworkFactory")
            try:
                from Jumpscale.sal_zos.network.NetworkFactory import NetworkFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.network.NetworkFactory", e)
                raise e
            # print("RUN:NetworkFactory")
            try:
                self._network =  NetworkFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.network.NetworkFactory",e)
                return None
            # print("OK")
        return self._network
    @property
    def node(self):
        if self._node is None:
            # print("LOAD:PrimitivesFactory")
            try:
                from Jumpscale.sal_zos.node.NodeFactory import PrimitivesFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.node.NodeFactory", e)
                raise e
            # print("RUN:PrimitivesFactory")
            try:
                self._node =  PrimitivesFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.node.NodeFactory",e)
                return None
            # print("OK")
        return self._node
    @property
    def primitives(self):
        if self._primitives is None:
            # print("LOAD:PrimitivesFactory")
            try:
                from Jumpscale.sal_zos.primitives.PrimitivesFactory import PrimitivesFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.primitives.PrimitivesFactory", e)
                raise e
            # print("RUN:PrimitivesFactory")
            try:
                self._primitives =  PrimitivesFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.primitives.PrimitivesFactory",e)
                return None
            # print("OK")
        return self._primitives
    @property
    def storagepools(self):
        if self._storagepools is None:
            # print("LOAD:ContainerFactory")
            try:
                from Jumpscale.sal_zos.storage.StorageFactory import ContainerFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.storage.StorageFactory", e)
                raise e
            # print("RUN:ContainerFactory")
            try:
                self._storagepools =  ContainerFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.storage.StorageFactory",e)
                return None
            # print("OK")
        return self._storagepools
    @property
    def vm(self):
        if self._vm is None:
            # print("LOAD:ZOS_VMFactory")
            try:
                from Jumpscale.sal_zos.vm.ZOS_VMFactory import ZOS_VMFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.vm.ZOS_VMFactory", e)
                raise e
            # print("RUN:ZOS_VMFactory")
            try:
                self._vm =  ZOS_VMFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.vm.ZOS_VMFactory",e)
                return None
            # print("OK")
        return self._vm
    @property
    def zerodb(self):
        if self._zerodb is None:
            # print("LOAD:ZerodbFactory")
            try:
                from Jumpscale.sal_zos.zerodb.zerodbFactory import ZerodbFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.zerodb.zerodbFactory", e)
                raise e
            # print("RUN:ZerodbFactory")
            try:
                self._zerodb =  ZerodbFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.zerodb.zerodbFactory",e)
                return None
            # print("OK")
        return self._zerodb
    @property
    def etcd(self):
        if self._etcd is None:
            # print("LOAD:ETCDFactory")
            try:
                from Jumpscale.sal_zos.ETCD.ETCDFactory import ETCDFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.ETCD.ETCDFactory", e)
                raise e
            # print("RUN:ETCDFactory")
            try:
                self._etcd =  ETCDFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.ETCD.ETCDFactory",e)
                return None
            # print("OK")
        return self._etcd
    @property
    def pubsub(self):
        if self._pubsub is None:
            # print("LOAD:PubsubFactory")
            try:
                from Jumpscale.sal_zos.Pubsub.PubsubFactory import PubsubFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.Pubsub.PubsubFactory", e)
                raise e
            # print("RUN:PubsubFactory")
            try:
                self._pubsub =  PubsubFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.Pubsub.PubsubFactory",e)
                return None
            # print("OK")
        return self._pubsub
    @property
    def coredns(self):
        if self._coredns is None:
            # print("LOAD:CorednsFactory")
            try:
                from Jumpscale.sal_zos.coredns.CorednsFactory import CorednsFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.coredns.CorednsFactory", e)
                raise e
            # print("RUN:CorednsFactory")
            try:
                self._coredns =  CorednsFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.coredns.CorednsFactory",e)
                return None
            # print("OK")
        return self._coredns
    @property
    def farm(self):
        if self._farm is None:
            # print("LOAD:FarmFactory")
            try:
                from Jumpscale.sal_zos.farm.FarmFactory import FarmFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.farm.FarmFactory", e)
                raise e
            # print("RUN:FarmFactory")
            try:
                self._farm =  FarmFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.farm.FarmFactory",e)
                return None
            # print("OK")
        return self._farm
    @property
    def ftpclient(self):
        if self._ftpclient is None:
            # print("LOAD:FtpFactory")
            try:
                from Jumpscale.sal_zos.ftpClient.ftpFactory import FtpFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.ftpClient.ftpFactory", e)
                raise e
            # print("RUN:FtpFactory")
            try:
                self._ftpclient =  FtpFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.ftpClient.ftpFactory",e)
                return None
            # print("OK")
        return self._ftpclient
    @property
    def grafana(self):
        if self._grafana is None:
            # print("LOAD:GrafanaFactory")
            try:
                from Jumpscale.sal_zos.grafana.grafanaFactory import GrafanaFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.grafana.grafanaFactory", e)
                raise e
            # print("RUN:GrafanaFactory")
            try:
                self._grafana =  GrafanaFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.grafana.grafanaFactory",e)
                return None
            # print("OK")
        return self._grafana
    @property
    def influx(self):
        if self._influx is None:
            # print("LOAD:InfluxDBFactory")
            try:
                from Jumpscale.sal_zos.influxdb.influxdbFactory import InfluxDBFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.influxdb.influxdbFactory", e)
                raise e
            # print("RUN:InfluxDBFactory")
            try:
                self._influx =  InfluxDBFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.influxdb.influxdbFactory",e)
                return None
            # print("OK")
        return self._influx
    @property
    def sandbox(self):
        if self._sandbox is None:
            # print("LOAD:ZOSSandboxFactory")
            try:
                from Jumpscale.sal_zos.sandbox.ZOSSandboxFactory import ZOSSandboxFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.sandbox.ZOSSandboxFactory", e)
                raise e
            # print("RUN:ZOSSandboxFactory")
            try:
                self._sandbox =  ZOSSandboxFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.sandbox.ZOSSandboxFactory",e)
                return None
            # print("OK")
        return self._sandbox
    @property
    def stats_collector(self):
        if self._stats_collector is None:
            # print("LOAD:StatsCollectorFactory")
            try:
                from Jumpscale.sal_zos.stats_collector.stats_collector_factory import StatsCollectorFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.stats_collector.stats_collector_factory", e)
                raise e
            # print("RUN:StatsCollectorFactory")
            try:
                self._stats_collector =  StatsCollectorFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.stats_collector.stats_collector_factory",e)
                return None
            # print("OK")
        return self._stats_collector
    @property
    def tfchain(self):
        if self._tfchain is None:
            # print("LOAD:TfChainFactory")
            try:
                from Jumpscale.sal_zos.tfchain.TfChainFactory import TfChainFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.tfchain.TfChainFactory", e)
                raise e
            # print("RUN:TfChainFactory")
            try:
                self._tfchain =  TfChainFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.tfchain.TfChainFactory",e)
                return None
            # print("OK")
        return self._tfchain
    @property
    def traefik(self):
        if self._traefik is None:
            # print("LOAD:TraefikFactory")
            try:
                from Jumpscale.sal_zos.traefik.TraefikFactory import TraefikFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.traefik.TraefikFactory", e)
                raise e
            # print("RUN:TraefikFactory")
            try:
                self._traefik =  TraefikFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.traefik.TraefikFactory",e)
                return None
            # print("OK")
        return self._traefik
    @property
    def zt_bootstrap(self):
        if self._zt_bootstrap is None:
            # print("LOAD:ZerotierBootstrapFactory")
            try:
                from Jumpscale.sal_zos.zerotier_bootstrap.ZerotierBootstrapFactory import ZerotierBootstrapFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.zerotier_bootstrap.ZerotierBootstrapFactory", e)
                raise e
            # print("RUN:ZerotierBootstrapFactory")
            try:
                self._zt_bootstrap =  ZerotierBootstrapFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.zerotier_bootstrap.ZerotierBootstrapFactory",e)
                return None
            # print("OK")
        return self._zt_bootstrap
    @property
    def zrobot(self):
        if self._zrobot is None:
            # print("LOAD:ZeroRobotFactory")
            try:
                from Jumpscale.sal_zos.zrobot.ZRobotFactory import ZeroRobotFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.zrobot.ZRobotFactory", e)
                raise e
            # print("RUN:ZeroRobotFactory")
            try:
                self._zrobot =  ZeroRobotFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.zrobot.ZRobotFactory",e)
                return None
            # print("OK")
        return self._zrobot
    @property
    def zstor(self):
        if self._zstor is None:
            # print("LOAD:ZeroStorFactory")
            try:
                from Jumpscale.sal_zos.zstor.ZStorFactory import ZeroStorFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "Jumpscale.sal_zos.zstor.ZStorFactory", e)
                raise e
            # print("RUN:ZeroStorFactory")
            try:
                self._zstor =  ZeroStorFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","Jumpscale.sal_zos.zstor.ZStorFactory",e)
                return None
            # print("OK")
        return self._zstor

j.sal_zos = group_sal_zos()
j.core._groups["sal_zos"] = j.sal_zos


class group_world(JSGroup):
    def __init__(self):
        
        self._system = None
        self._hypervisor = None
        self._zos = None

    
    @property
    def system(self):
        if self._system is None:
            # print("LOAD:WorldSystem")
            try:
                from DigitalMe.tools.kosmos.WorldSystem import WorldSystem
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.tools.kosmos.WorldSystem", e)
                raise e
            # print("RUN:WorldSystem")
            try:
                self._system =  WorldSystem()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.tools.kosmos.WorldSystem",e)
                return None
            # print("OK")
        return self._system
    @property
    def hypervisor(self):
        if self._hypervisor is None:
            # print("LOAD:CoordinatorHypervisor")
            try:
                from DigitalMe.tools.kosmos.world_example.HyperVisorCoordinator.CoordinatorHypervisor import CoordinatorHypervisor
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.tools.kosmos.world_example.HyperVisorCoordinator.CoordinatorHypervisor", e)
                raise e
            # print("RUN:CoordinatorHypervisor")
            try:
                self._hypervisor =  CoordinatorHypervisor()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.tools.kosmos.world_example.HyperVisorCoordinator.CoordinatorHypervisor",e)
                return None
            # print("OK")
        return self._hypervisor
    @property
    def zos(self):
        if self._zos is None:
            # print("LOAD:ZOSCmdFactory")
            try:
                from DigitalMe.kosmos.zos.ZOSFactory import ZOSCmdFactory
            except Exception as e:
                msg = j.core.application.error_init("import", "DigitalMe.kosmos.zos.ZOSFactory", e)
                raise e
            # print("RUN:ZOSCmdFactory")
            try:
                self._zos =  ZOSCmdFactory()
            except Exception as e:
                msg = j.core.application.error_init("execute","DigitalMe.kosmos.zos.ZOSFactory",e)
                return None
            # print("OK")
        return self._zos

j.world = group_world()
j.core._groups["world"] = j.world



