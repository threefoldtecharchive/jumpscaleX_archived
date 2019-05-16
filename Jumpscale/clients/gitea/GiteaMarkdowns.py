from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaMarkdowns(j.application.JSBaseClass):
    def __init__(self, client):
        JSBASE.__init__(self)
        self.client = client

    def render(self, text, context=None, mode=None, wiki=True):
        return self.client.api.markdown.renderMarkdown(
            data={"Context": context, "Mode": mode, "Text": text, "Wiki": wiki}
        ).content

    def render_raw(self, text):
        return self.client.api.markdown.renderMarkdownRaw(data={"body": text}).content

    def test(self):
        assert self.render(text="##This is header") == b"<h2>This is header</h2>\n"
        assert self.render_raw(text="##This is header") == b"<p>{&quot;body&quot;: &quot;##This is header&quot;}</p>\n"

    __str__ = __repr__ = lambda self: "<Gitea MarkDown Manager>"
