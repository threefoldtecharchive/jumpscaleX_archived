from Jumpscale import j


JSConfigClient = j.application.JSBaseConfigClass


class TrelloClient(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.trello.client
    api_key_ = "" (S)
    secret_ = "" (S)
    token_ = "" (S)
    token_secret_= "" (S)
    """

    def _init(self):
        from trello import TrelloClient

        if not self.token_secret_:
            print("**WILL TRY TO DO OAUTH SESSION")
            from trello.util import create_oauth_token
            access_token = create_oauth_token(
                key=self.api_key_, secret=self.secret_)
            self.token_ = access_token["oauth_token"]
            self.token_secret_ = access_token["oauth_token_secret"]

        self.client = TrelloClient(
            api_key=self.api_key_,
            api_secret=self.secret_,
            token=self.token_,
            token_secret=self.token_secret_
        )

    def test(self):

        boards = self.client.list_boards()
        print(boards)
