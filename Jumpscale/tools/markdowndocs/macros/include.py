import os
import re
from Jumpscale.tools.markdowndocs.Link import CustomLink, GithubLinker


def with_code_block(content, _type=''):
    if not _type:
        return content
    return '\n'.join(('```%s' % _type, content, '```'))


def modify_header_level(line, level):
    line = line.strip()

    header_chars = ''
    for c in line:
        if c != '#':
            break
        header_chars += '#'

    current_level = len(header_chars)
    new_level = current_level + level
    return '%s%s' % ('#' * new_level, line[current_level:])


def get_by_marker(lines, marker):
    found = False
    matched = []

    marker = marker.lower().strip()
    for line in lines:
        if marker in line.lower():
            found = not found
            matched.append(line.replace(marker, ''))
            continue

        if not found:
            continue
        matched.append(line)

    return matched


def get_docstrings(lines):
    # TODO
    return lines


def process_content(content, marker, doc_only, header_levels_modify, ignore):
    def should_skip(line):
        return any([re.findall(pattern, line) for pattern in ignore])

    lines = content.split('\n')
    if marker:
        marker = '!!%s!!' % marker
        lines = get_by_marker(lines, marker)

    lines = list(filter(should_skip, lines))
    if doc_only:
        return get_docstrings(lines)

    if header_levels_modify:
        lines = list(map(modify_header_level, lines))

    return '\n'.join(lines)


def include(
        doc, link, docsite_name=None, doc_only=False, remarks_skip=False, header_levels_modify=0, ignore=None,
        codeblock_type=None, **kwargs):
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
    custom_link = CustomLink(link)

    if docsite_name:
        docsite = j.tools.markdowndocs.docsite_get(docsite_name)
    else:
        repo = current_docsite.get_real_source(custom_link)
        if not CustomLink(repo).is_url:
            docsite = current_docsite
        else:
            # the real source is a url, get a new link and docsite
            custom_link = GithubLinker.to_custom_link(repo)
            # to match any path, start with root `/`
            url = GithubLinker(custom_link.account, custom_link.repo).tree('/')
            docsite = j.tools.markdowndocs.load(url, name=custom_link.repo)

    doc = docsite.doc_get(custom_link.path)
    content = j.core.text.strip(doc.markdown_source)

    if not ignore:
        ignore = []
    if remarks_skip:
        ignore.append(r'^\#')

    if custom_link.marker or ignore or doc_only or header_levels_modify:
        content = process_content(
            content, marker=custom_link.marker, doc_only=doc,
            header_levels_modify=header_levels_modify, ignore=ignore)
    return with_code_block(content, _type=codeblock_type)
