from Jumpscale import j
import os


def test():
    dname = j.sal.fs.getDirName(os.path.abspath(__file__))

    C = j.sal.fs.readFile("%s/MarkdownExample.md" % dname)

    md = j.data.markdown.document_get(C)

    j.sal.fs.writeFile("%s/out/test3.md" % dname, md.markdown)
    j.sal.fs.writeFile("%s/out/test3.html" % dname, md.html)

    htmlpage = md.htmlpage_get()

    j.sal.fs.writeFile("%s/out/test3b.html" % dname, htmlpage.html_get())


if __name__ == "__main__":
    test()
