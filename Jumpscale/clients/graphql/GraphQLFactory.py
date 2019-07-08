from .GraphQLClient import GraphQLClient
from Jumpscale import j


JSConfigs = j.application.JSBaseConfigsClass

class GraphQLFactory(JSConfigs):

    __jslocation__ = "j.clients.graphql"
    _CHILDCLASS = GraphQLClient
