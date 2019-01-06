
def dot(doc, name, content):

    j=doc.docsite._j

    if content.strip() == "":
        raise RuntimeError("no content given for dot macro for:%s"%doc)

    md5 = j.data.hash.md5_string(content)
    md5 = bytes(md5.encode())
    md5b = j.core.db.get("docsite:dot:%s" % name)

    link_src = "![%s.png](%s.png)" % (name,name)

    if md5b != md5:
        path = j.sal.fs.getTmpFilePath()
        j.sal.fs.writeFile(filename=path, contents=content)
        dest = j.sal.fs.joinPaths(j.sal.fs.getDirName(doc.path), "%s.png" % name)
        j.sal.process.execute("dot '%s' -Tpng > '%s'" % (path, dest))
        j.sal.fs.remove(path)
        j.core.db.set("docsite:dot:%s" % name, md5)

    doc.link_add(link_src)

    return link_src
