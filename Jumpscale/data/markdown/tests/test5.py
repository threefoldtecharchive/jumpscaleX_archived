C = """
* [Home](/)
* [docsify](docsify)
* docsify plugins
    * [mermaid](mermaid)
    * [echart](echart)
    * [plantuml](plantuml)
    * [google_slides](google_slides)
    * [extensions](extensions)
* Tools Used On Our Websites
    * [disqus](disqus)
"""

from Jumpscale import j


def test():
    md = j.data.markdown.document_get(C)

    C2 = j.core.text.strip(C).strip()
    assert j.core.text.strip(md.markdown).strip() == C2

    l = md.parts[0]

    assert (
        l.html
        == '<ul>\n<li><a href="/">Home</a></li>\n<li><a href="docsify">docsify</a></li>\n<li>docsify plugins<ul>\n<li><a href="mermaid">mermaid</a></li>\n<li><a href="echart">echart</a></li>\n<li><a href="plantuml">plantuml</a></li>\n<li><a href="google_slides">google_slides</a></li>\n<li><a href="extensions">extensions</a></li>\n</ul>\n</li>\n<li>Tools Used On Our Websites<ul>\n<li><a href="disqus">disqus</a></li>\n</ul>\n</li>\n</ul>\n'
    )


if __name__ == "__main__":
    test()
