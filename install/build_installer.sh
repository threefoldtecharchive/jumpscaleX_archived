set -ex
rm -rf /tmp/jsxbuilder
mkdir -p /tmp/jsxbuilder

ln -s /sandbox/lib/jumpscale/install/install.spec /tmp/jsxbuilder/install.spec
ln -s /sandbox/lib/jumpscale/install/InstallTools.py /tmp/jsxbuilder/InstallTools.py
ln -s /sandbox/lib/jumpscale/install/kosmos.py /tmp/jsxbuilder/kosmos.py

pushd /tmp/jsxbuilder
pyinstaller install.spec

popd

