from Jumpscale import j
import os


def test():
    dname = j.sal.fs.getDirName(os.path.abspath(__file__))

    C = j.sal.fs.readFile("%s/SimpleMD.md" % dname)

    md = j.data.markdown.document_get(C)

    j.sal.fs.writeFile("%s/out/test4.md" % dname, md.markdown)
    j.sal.fs.writeFile("%s/out/test4.html" % dname, md.html)

    htmlpage = md.htmlpage_get()

    j.sal.fs.writeFile("%s/out/test4b.html" % dname, htmlpage.html_get())


if __name__ == "__main__":
    test()
