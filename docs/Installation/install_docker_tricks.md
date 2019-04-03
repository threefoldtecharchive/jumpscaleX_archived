## tricks how to use docker for install

### Install Docker on ubuntu

```bash
#use -A to make sure your SSH key is forwarded to the remote machine
ssh -A root@ipaddress

apt install docker -y
```

### example

make sure you got the jumpscale installer as described in [install](install.md)  (from Git or download over curl)

#### basic docker install

```bash
python3 /tmp/install.py -3 --name=test -d -y -c --secret="ssh"
```

will use secret from ssh and autogenerate the private key

#### start from an image

```
python3 /tmp/install.py -3 --portrange=3 --name=test --image=despiegk:jsx_develop -d -y -c
```

- will be unattended
  
#### continue where left off last time

```
python3 /tmp/install.py -3 --portrange=3 --name=test -y -c
```


### export running docker

```
docker export kds -o ~/Downloads/docker_kds.tar
```

kds is the name of the docker container can see with

### export image

```
docker image save despiegk/jsx_develop -o ~/Downloads/docker_image_despiegk_jsx_develop.tar 

```

### see which dockers running

```docker ps -a ```

### how to do installer from an existing docker image

```

```


