Details
The extension is located under jumpscaleX/lib/Jumpscale/lib/kvm
Images under /mnt/vmstor/kvm/images, and
VMs to be created under /mnt/vmstor/kvm
a fabric module responsible for configuring the vm after creation (pushing ssh keys, configure network, etc), in libvirt contains basic info name, description, etc and most importantly IP address of the VM, login credentials and a fabric module which contains network configuration logic which varies by os type, thus more flexibility installing/configuring network on the created VM. 

How to use it
Please note that this extension requires libvirt to be installed on your system
you need to configure the following bridges on your host:
brmgmt (ip 192.168.66.254/24)
brpub
brtmp
Images

id=1
name=openwrt
ostype = linux
arch=x86
version=
description=
bootstrap.ip=192.168.66.253
bootstrap.login=root
bootstrap.passwd=rooter
bootstrap.type=ssh
fabric.module=openwrt

mkdir -p /mnt/vmstor/kvm/images
rsync -arv --partial --progress /mnt/ftp/images/ubuntu1404/ /mnt/vmstor/kvm/images/
rsync -arv --partial --progress /mnt/ftp/images/openwrt/ /mnt/vmstor/kvm/images/

Available Images
The following images are available now on the FTP server on 94.23.33.39:
Ubuntu 14.04 (image name: ubuntu1404)
Ubuntu 14.10 (image name: ubuntu1410)
OpenWRT (image name: openwrt)

Notes when creating images
Provide username and password  of the machine xml onto libvirt.
Create your image with three network interfaces:
eth0 (management interface): default ip address 192.168.66.253 (to be changed later via the fabric setupNetwork function)
eth1 (public interface)
eth2 (tmp interface): for openwrt image, customer network, maybe? (need to be discussed)
Provide a fabric module with your image, contains at least one function setupNetwork with the logic to get executed to configure the network interfaces on your image
Image should have an enabled SSH server
compress images using lrzip
lrzip -v ubuntu1410.qcow2

Creating the physical bridges on host

brctl addbr brmgmt
brctl addbr brpub
brctl addbr brtmp
ip a a 192.168.66.254/24 dev brmgmt
ifconfig brmgmt up

or in jshell

import lib.kvm
j.sal.kvm.initPhysicalBridges(pubinterface="<pubinterface_name_on_host>")


Creating vnetworks in libvirt

import lib.kvm
j.sal.kvm.initLibvirtNetwork()


Sample code

import lib.kvm
j.sal.kvm.create('test-ubuntu', 'ubuntu1404')

where ‘test-ubuntu’ is your VM name, and ‘ubuntu1404’ is the image name
args (j.sal.kvm.create(self, name, baseimage, replace=True, description='', size=10, memory=512, cpu_count=1)):
name: your vmachine name
baseimage: image name, one of oyur installed images
replace: if True, vmachine (if exists) will be destroyed, and create a new one with same name
description: your vmachine desription
size: vmachine disk size in GBs
memory: vmachine RAM size in MBs, and 
cpu_count: number of vCPUs to be provided to your vmachine
