import os
import re
from functools import partial
from Jumpscale import j
from Jumpscale.tools.markdowndocs.Link import MarkdownLinkParser, GithubLinker, Link


def with_code_block(content, _type=""):
    if not _type:
        return content
    return "\n".join(("```%s" % _type, content, "```"))


def update_header_level(line, level):
    current_level = 0
    for c in line:
        if c == " ":
            continue
        if c != "#":
            break
        current_level += 1

    if current_level:
        new_level = current_level + level
        return "%s%s" % ("#" * new_level, line[current_level:])
    return line


def get_by_marker(lines, marker):
    found = False
    matched = []

    marker = re.compile(marker.strip(), re.IGNORECASE)
    for line in lines:
        if marker.findall(line):
            found = not found
            matched.append(marker.sub("", line))
            continue

        if not found:
            continue
        matched.append(line)

    return matched


DOCSTRING_RE = re.compile(r"(?:\'\'\'|\"\"\")([\w\W]*?)(?:\'\'\'|\"\"\")", re.MULTILINE)


def get_docstrings(content):
    return "\n\n".join(DOCSTRING_RE.findall(content))


def append_docs_to_path(path):
    if not path.endswith("/docs"):
        path = j.sal.fs.joinPaths(path, "docs")
    return path


def get_abs_path(*paths):
    return j.sal.fs.pathNormalize(j.sal.fs.joinPaths(*paths))


def exapnd_doc_path(docs_root_dir, doc_dir, path):
    if path.startswith("/"):
        # if it's an absolute path, get full path from docs_root
        paths = docs_root_dir, path[1:]
    else:
        paths = docs_root_dir, doc_dir, path
    return get_abs_path(*paths)


def copy_links(main_doc, included_docs_root, included_doc_path, links):
    """copy files that are referenced with links inside the included content (like images...)

    :param main_doc: the document where include is called
    :type main_dic: Doc
    :param included_docs_root: the root path of all docs where the document content inclucded from
    :type included_doc_root: str
    :param included_doc_path: the path of the document the content inclucded from
    :type included_doc_path: str
    :param links: a list of tuples with (description, source)
    :type links: [tuple]
    """
    included_docs_root = append_docs_to_path(included_docs_root)
    main_docs_outpath = main_doc.docsite.outpath

    if j.sal.fs.getFileExtension(included_doc_path):
        included_doc_dir = j.sal.fs.getDirName(included_doc_path)
    else:
        included_doc_dir = included_doc_path

    for _, source in links:
        if source.lower().strip().startswith("http"):
            continue
        if "?" in source:
            source, _, _ = source.partition("?")
        # source is either absolute (from docs_root) or relative to doc_path
        # so we get the real path of such source
        real_path = exapnd_doc_path(included_docs_root, included_doc_dir, source)

        # the destination is just the output path with the relative directory and the source
        destination = exapnd_doc_path(main_docs_outpath, main_doc.path_dir_rel, source)
        if not j.sal.fs.exists(destination):
            j.sal.fs.copyFile(real_path, destination, createDirIfNeeded=True)


def process_content(content, marker, doc_only, header_levels_modify, ignore):
    def should_skip(line):
        return not any([re.findall(pattern, line.strip()) for pattern in ignore])

    lines = content.split("\n")
    if marker:
        marker = "!!%s!!" % marker
        lines = get_by_marker(lines, marker)

    lines = filter(should_skip, lines)

    update_header = partial(update_header_level, level=header_levels_modify)
    if header_levels_modify:
        lines = map(update_header, lines)

    new_content = "\n".join(lines)
    if doc_only:
        return get_docstrings(new_content)
    return new_content


def include(
    doc,
    link,
    docsite_name=None,
    doc_only=False,
    remarks_skip=False,
    header_levels_modify=0,
    ignore=None,
    codeblock_type=None,
    **kwargs,
):
    """include other documents or files

    :param doc: curent document (that include was called from)
    :type doc: Doc
    :param link: the link using our custom link format, can include markers/parts like e.g. 'wiki/document.md!A'
    :type link: str
    :param docsite_name: name of the docsite, if provided, will search for link in it, defaults to None
    :type docsite_name: str, optional
    :param doc_only: only docstring will be captured, relevant for python code, defaults to False
    :type doc_only: bool, optional
    :param remarks_skip: all lines that starts with `#` will be skipped, relevant for python code, defaults to False
    :type remarks_skip: bool, optional
    :param header_levels_modify: modify (increase or decrease) headers level with the given value, defaults to 0
    :type header_levels_modify: int, optional
    :param ignore: a list of regular expressions to ignore (the whole line will be ignored), defaults to None
    :type ignore: list of str, optional
    :param codeblock_type: the type of code block, if not provided, the content won't be inside a codeblock , defaults to None
    :type codeblock_type: str , optional
    :raises RuntimeError: in case a document cannot be found or more than 1 document found
    :return: the content to be included
    :rtype: str
    """
    current_docsite = doc.docsite
    j = current_docsite._j
    custom_link = MarkdownLinkParser(link)

    if docsite_name:
        docsite = j.tools.markdowndocs.docsite_get(docsite_name)
    else:
        repo = current_docsite.get_real_source(custom_link)
        if not MarkdownLinkParser(repo).is_url:
            # not an external url, use current docsite
            docsite = current_docsite
        else:
            # the real source is a url outside this docsite
            # get a new link and docsite
            new_link = GithubLinker.to_custom_link(repo)
            # to match any path, start with root `/`
            url = GithubLinker(new_link.account, new_link.repo).tree("/")
            docsite = j.tools.markdowndocs.load(url, name=new_link.repo)
            custom_link.path = new_link.path

    try:
        full_path = docsite.file_get(custom_link.path)
        content = j.sal.fs.readFile(full_path)
    except j.exceptions.BaseJSException:
        included_doc = docsite.doc_get(custom_link.path)
        content = included_doc.markdown_source
        full_path = included_doc.path

    if not ignore:
        ignore = []
    if remarks_skip:
        ignore.append(r"^\#")

    if custom_link.marker or ignore or doc_only or header_levels_modify:
        content = process_content(
            content,
            marker=custom_link.marker,
            doc_only=doc_only,
            header_levels_modify=header_levels_modify,
            ignore=ignore,
        )

    if not custom_link.path.lower().strip().endswith("_sidebar.md"):
        all_links = Link.LINK_MARKDOWN_RE.findall(content)
        copy_links(doc, docsite.path, full_path, all_links)

    return with_code_block(content, _type=codeblock_type)
