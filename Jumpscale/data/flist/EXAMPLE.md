## Installation

Make sure you have the required dependencies

```python
j.builders.db.rocksdb.install()
j.builders.zero_os.zos_stor_client.install()
```

## Creating a flist

```python
kvs = j.data.kvs.getRocksDBStore('flist', namespace=None, dbpath='/tmp/demo-flist.db')
f = j.tools.flist.getFlist(rootpath='/tmp/', kvs=kvs)
f.add('/tmp/')
f.upload("ardb.server", 16379)
```

