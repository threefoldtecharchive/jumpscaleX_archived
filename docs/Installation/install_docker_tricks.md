## tricks how to use docker for install


### example

#### start from an image

```
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py -3 --portrange=3 --name=test --image=despiegk:jsx_develop -d -y -c
```

- will be unattended
  
#### continue where left off last time

```
python3 /sandbox/code/github/threefoldtech/jumpscaleX/install/install.py -3 --portrange=3 --name=test -y -c
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


