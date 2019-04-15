from Jumpscale import j
from Jumpscale.tools.markdowndocs.Link import CustomLink


def filter_on(data, attr, values):
    values = set(values)

    def filter_by_attr(person):
        return any([value in person[attr] for value in values])

    return list(filter(filter_by_attr, data))


def team(doc, link, order='random', projects=None, contribution_types=None, **kwargs):
    """generate the json requried for docify team plugin
       for the full list of project ids, contribution types, also the toml data see
       https://github.com/threefoldfoundation/data_team/tree/master/README.md

    :param doc: current doc
    :type doc: Doc
    :param link: a link to team data repository, e.g. https://github.com/threefoldfoundation/data_team/tree/master/team
    :type link: str
    :param order: listing order, either 'random' or 'rank', defaults to 'random'
    :type order: str, optional
    :param projects: project ids to filter by, defaults to None, will include all projects
    :type projects: [int], optional
    :param contribution_types: contribution types to filter by
    :type contribution_types: [int], optional
    :return: a codeblock content with type `team`
    :rtype: str
    """

    repo = doc.docsite.get_real_source(CustomLink(link))
    path = j.clients.git.getContentPathFromURLorPath(repo)

    # options passed to team plugin (docsify)
    options = {'order': order}

    data = []
    for directory in j.sal.fs.listDirsInDir(path):
        person_data = {}
        for filepath in j.sal.fs.listFilesInDir(directory):
            if 'publicinfo.toml' in filepath.lower():
                person_data.update(j.data.serializers.toml.load(filepath))
            elif j.sal.fs.getFileExtension(filepath).lower() in ('png', 'jpg', 'jpeg'):
                person_data['avatar'] = j.sal.fs.getBaseName(filepath)
                doc_dir = j.sal.fs.joinPaths(doc.docsite.outpath, doc.path_dir_rel)
                j.sal.fs.copyFile(filepath, doc_dir, createDirIfNeeded=True)
            data.append(person_data)

    if projects:
        data = filter_on(data, 'project_ids', projects)
    if contribution_types:
        data = filter_on(data, 'contribution_ids', contribution_types)

    options['dataset'] = data
    return "```team\n%s```" % j.data.serializers.json.dumps(options)
