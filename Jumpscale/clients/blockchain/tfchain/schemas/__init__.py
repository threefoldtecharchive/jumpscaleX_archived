from Jumpscale import j
import os

# load all the schema in the current directory
cwd = os.path.dirname(os.path.abspath(__file__))
for path in j.sal.fs.listFilesInDir(cwd, filter="*.schema"):
    content = j.sal.fs.readFile(path)
    j.data.schema.get_from_text(content)
