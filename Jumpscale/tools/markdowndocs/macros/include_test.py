import include
from uuid import uuid4
from Jumpscale import j
import pytest

markdowndocs_client = j.tools.markdowndocs
doc=markdowndocs_client.load("https://github.com/threefoldtech/jumpscale_weblibs/blob/master/docsites_examples/test/blog/",name="test")   
test_doc = doc.doc_get("include_test")   

def test_include_from_repo(doc=test_doc):
    data =include.include(doc=test_doc,name="test5")
    assert "ag_from_test5" in data 

def test_include_part_of_file_using_start_and_end_line(doc=test_doc):
    data =include.include(doc=test_doc,name="Fixer.py", repo="https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tools/fixer",start="def find_changes",end="self.replacer.dir_process(")
    assert "JSGENERATE_DEBUG" in data 
    assert "BE CAREFULL THIS WILL WRITE THE CHANGES AS FOUND IN self.find_changes" not in data
    assert "Fixer" not in data 

@pytest.mark.skip("https://github.com/threefoldtech/jumpscaleX/issues/162")
def test_include_part_of_file_using_the_paragraph_argument(doc=test_doc):
    data = include.include(doc=test_doc,name="Fixer.py", repo="https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tools/fixer",start="def find_changes", paragraph=True, codeblock=True)
    assert "JSGENERATE_DEBUG" in data 
    assert "BE CAREFULL THIS WILL WRITE THE CHANGES AS FOUND IN self.find_changes" not in data
    assert "Fixer" not in data 

def test_include_document_string_from_python_method(doc=test_doc):
    data = include.include(doc=test_doc,name="Fixer.py", repo="https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tools/fixer", docstring="find_changes")
    assert "JSGENERATE_DEBUG" not in data 
    assert "j.tools.fixer.find_changes" in data 

def test_include_from_any_file(doc=test_doc):
    data = include.include(doc=test_doc,name="tutorials/base/README.md", repo="https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/")
    assert "see tutorials folder for examples" in data 

def test_include_from_other_repo(doc=test_doc):
    markdowndocs_client = j.tools.markdowndocs
    doc=markdowndocs_client.load("https://github.com/threefoldtech/jumpscaleX/tree/master/Jumpscale/tutorials/base/",name="newrepo")
    data = include.include(doc=test_doc,name="newrepo:README.md")
    assert "see tutorials folder for examples" in data 
