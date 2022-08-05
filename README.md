# Kubernetes-Ansible

[![Repo Size](https://img.shields.io/github/repo-size/kuops/kubernetes-ansible)](https://github.com/kuops/kubernetes-ansible)

<!-- markdownlint-disable MD013 -->
This Repository is Using Ansible Deploy a Binary High Availability Kubernetes Cluster. Roles step Fllow the offical deploy tools Kubeadm.

## High availability

each node running a envoy loadbalancer on 127.0.0.1:8443 proxy the kube-apiserver serivce.

```bash
                                            upstream    +-------------------+
                           +--------------------------> | kube-master1:6443 |
                           |                            +-------------------+
                           |
                           |
                           |
+-----------+  request   +----------------+  upstream   +-------------------+
| kube-node | ---------> | 127.0.0.1:8443 | ----------> | kube-master2:6443 |
+-----------+            +----------------+             +-------------------+
                           |
                           |
                           |
                           |                upstream    +-------------------+
                           +--------------------------> | kube-master3:6443 |
                                                        +-------------------+

```

## VirtualBox Network

If virtualbox > 2.2.18 /etc/vbox/networks.conf

```bash
* 10.0.0.0/8 192.168.0.0/16 172.16.0.0/12
```

## Calico

calico disable ipip modules, in vagrant this settings require:

```bash
# change calico.yaml variable
IP_AUTODETECTION_METHOD="skip-interface=eth0"
CALICO_IPV4POOL_IPIP="Never"
CALICO_IPV4POOL_CIDR="{{ kubernetes_pod_network_cidr }}"
# kubelet 10-kubeadm.conf add --node-ip
--node-ip="{{ ansible_host_ip }}"
```

## Dependencies

On Host machine:

- **OS**: macOS Monterey
- **Vagrant**: 2.2.19
- **VirtualBox**: 6.1.36
- **Ansible**: 2.13.0

On Guest machine:

- **Linux Distribution**: CentOS/7
- **Containerd**: 1.6.6
- **Critools**: 1.24.2
- **Kubernetes**: 1.24.3
- **Calico**: 3.23.3

## Quick Start

### Vagrant

Clone this repository, then use vagrant create kubernetes cluster:

```bash
git clone https://github.com/kuops/kubernetes-ansible.git
cd kubernetes-ansible
vagrant up
```

Default config in `vagrant.yaml`, this config load before `vagrant up`:

```bash
box: centos/7
box_url:  https://mirrors.ustc.edu.cn/centos-cloud/centos/7/vagrant/x86_64/images/CentOS-7-x86_64-Vagrant-2004_01.VirtualBox.box
master:
  prefix: kube-master
  number: 3
  cpu: 2
  memory: 4096
worker:
  prefix: kube-worker
  number: 2
  cpu: 1
  memory: 2048
```

If has some ansible error, setting debug variables:

then you can try `vagrant provision` or `vagrant up --provision` continue running ansible.

```bash
# ansbile verbose level 0-4
ANSIBLE_DEBUG=2 vagrant up --provision
```

### Ansible

Generator ca cert and bootstrap token, you can run:

```bash
# generator cert at base directory in .cert
make cert
```

Add your inventory on inventories directory, like `example` inventory:

```bash
inventories/example
├── group_vars
│   └── all.yml
└── hosts
```

`is_vagrant` variable add a route `8.8.8.8 dev eth1 scope link` change `ansible_default_ipv4` value to `vagrant_network_interface` ip address, if not use vagrant, change to `no`:

```yaml
is_vagrant: no
# comment vagrant_network_interface variable
# vagrant_network_interface: eth1
```

run deploy example:

```bash
ansible-playbook -i inventories/example/hosts site.yml
```
