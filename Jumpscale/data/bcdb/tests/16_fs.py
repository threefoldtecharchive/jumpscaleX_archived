from Jumpscale import j

def main(self):
    """
    to run:

    kosmos 'j.data.bcdb.test(name="fs")'

    """
    tags = ["color:blue", "color:white", "font:arial", "font:tahoma", "style:italian"]
    types = ["md", "pdf", "xls", "doc", "jpg"]
    contents = ["threefold foundation", "the new internet", "change the world", "digital freedom", "the future of IT"]
    bcdb = j.data.bcdb.get("test_fs")
    bcdb.reset()
    file_model = bcdb.model_get_from_file("{}/models_system/FILE.py".format(self._dirpath_))
    dir_model = bcdb.model_get_from_file("{}/models_system/DIR.py".format(self._dirpath_))

    parent = None
    subdir = None
    file = None
    root = dir_model.new()
    root.name = "root"
    root.path = "/"
    root.save()
    # import ipdb; ipdb.set_trace()
    for i in range(1, 3):

        parent = dir_model.new()
        parent.name = i
        parent.path = "{}{}/".format(root.path, i)
        parent.save()
        root.dirs.append(parent.id)


        # create subdirs
        for k in range(1, 3):
            subdir = dir_model.new()
            subdir.name = "{}_{}".format(k, i)
            subdir.path = "{}{}/".format(parent.path, k)
            subdir.save()
            parent.dirs.append(subdir.id)


        # create files
        for k in range(1, 3):
            file = file_model.new()
            file.name = "file_{}_{}".format(k, i)
            file.content = contents[(k-1) % 5]
            file.type = types[(k-1) % 5]
            file.tags.append(tags[(k-1) % 5])
            file.save()
            parent.files.append(file.id)

        parent.save()
    root.save()
    j.shell()
    res = file_model.files_search(tags="color:blue")
