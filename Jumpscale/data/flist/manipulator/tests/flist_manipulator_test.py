import os
import shutil
import tempfile
from unittest import TestCase
import tarfile
import time
import pytest

from Jumpscale import j

# from ..flist_manipulator import FlistManipulatorFactory


class FromExisting(TestCase):
    def setUp(self):
        cur_dir = os.path.dirname(__file__)
        flist_tar = os.path.join(cur_dir, "flist.tgz")
        self.flist_path = "flist.d"

        # extract tar
        if os.path.exists(self.flist_path):
            shutil.rmtree(self.flist_path)
        os.mkdir(self.flist_path)
        tar = tarfile.open(flist_tar)
        tar.extractall(self.flist_path)

        self.manipulator = FlistManipulatorFactory.get(self.flist_path)

    def tearDown(self):
        self.manipulator.close()

        if os.path.exists(self.flist_path):
            shutil.rmtree(self.flist_path)

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_open_existing_flist(self):
        root = self.manipulator.root
        assert root._flist is not None
        assert root._flist.dirCollection is not None
        assert root._flist.aciCollection is not None
        assert root._flist.userGroupCollection is not None
        assert root._flist.rootpath == "/"
        assert not root._flist.namespace
        (size, nrfiles, nrdirs, nrlinks, nrspecial) = root._flist.count()
        assert (size, nrfiles, nrdirs, nrlinks, nrspecial) == (227934503, 8970, 1083, 1811, 79)

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_root_dir(self):
        root = self.manipulator.root
        assert root.basename == "/"
        assert root.basename == root.name
        assert root.abspath == "/"
        assert root.size == 132
        assert len(root.files()) == 0
        assert len(root.dirs()) == 19
        assert len(root.specials()) == 0
        assert len(root.links()) == 0
        assert root.parent is None

        assert [d.basename for d in self.manipulator.root.dirs()] == [
            "bin",
            "boot",
            "dev",
            "etc",
            "home",
            "lib",
            "lib64",
            "media",
            "mnt",
            "opt",
            "proc",
            "root",
            "run",
            "sbin",
            "srv",
            "sys",
            "tmp",
            "usr",
            "var",
        ]

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_sub_dir(self):
        dir = self.manipulator.root.dirs()[0]
        assert dir.basename == "bin"
        assert dir.basename == dir.name
        assert dir.abspath == "/bin"
        assert dir.size == 1658
        assert len(dir.files()) == 110
        assert len(dir.dirs()) == 0
        assert len(dir.specials()) == 0
        assert len(dir.links()) == 19
        assert dir.parent is not None
        assert dir.parent == self.manipulator.root

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_file(self):
        dir = self.manipulator.root.dirs()[0]
        f = dir.files()[0]
        assert f.basename == "which"
        assert f.basename == f.name
        assert f.abspath == "/bin/which"
        assert f.size == 946
        assert f.parent == dir
        assert f.parent.name == "bin"

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_mkdir(self):
        now = int(time.time())
        test = self.manipulator.root.mkdir("test")

        assert test.name == "test"
        assert test.abspath == "/test"
        assert test.parent == self.manipulator.root

        assert test.size == 0
        assert test.ctime >= now
        assert test.mtime == test.ctime
        assert "test" in [x.name for x in self.manipulator.root.dirs()]

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_file_copy(self):
        b = os.urandom(4096)
        with open("/tmp/foo", "wb") as f:
            f.write(b)

        foo = self.manipulator.root.copy("/tmp/foo")
        assert foo.name == "foo"
        assert foo.basename == foo.name
        assert foo.size == 4096
        assert foo.parent == self.manipulator.root

        assert foo.abspath == "/foo"
        assert "foo" in [x.name for x in self.manipulator.root.files()]

        with pytest.raises(ValueError, message="copy should raise Value error when trying to copy a directory"):
            self.manipulator.root.copy("/tmp")

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_copy_dir(self):
        # create test direcory tree
        # ├── foo
        # │   ├── bar
        # │   │   ├── file1
        # │   │   └── file2
        # │   ├── file3
        # │   └── file4

        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "foo", "bar"))
            j.sal.fs.writeFile(os.path.join(tmp, "foo/bar", "file1"), "content")
            j.sal.fs.writeFile(os.path.join(tmp, "foo/bar", "file2"), "content")
            j.sal.fs.writeFile(os.path.join(tmp, "foo/file3"), "content")
            j.sal.fs.writeFile(os.path.join(tmp, "foo/file4"), "content")
            self.manipulator.root.copytree(tmp)

            src = self.manipulator.root.dirs(os.path.basename(tmp))[0]
            foo = src.dirs("foo")[0]
            bar = foo.dirs("bar")[0]
            foo_files = [x.name for x in foo.files()]
            bar_files = [x.name for x in bar.files()]
            assert foo_files == ["file3", "file4"]
            assert bar_files == ["file1", "file2"]

    @pytest.mark.skip(reason="Importing FlistManipulatorFactory is failing")
    def test_filter(self):
        assert [b.basename for b in self.manipulator.root.dirs("b*")] == ["bin", "boot"]
