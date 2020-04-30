# Kubernetes-Ansible

[![Build Status](https://travis-ci.com/kuops/kubernetes-ansible.svg?branch=master)](https://travis-ci.com/kuops/kubernetes-ansible)
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

## Calico

calico disable ipip modules, in vagrant this settings require:

```bash
# calico node variables
IP_AUTODETECTION_METHOD="skip-interface=eth0"
# kubelet settings
--node-ip=x.x.x.x
```

## Dependencies

- **Linux Distribution**: CentOS/7
- **Ansible**: 2.9.7
- **Vagrant**: 2.2.7
- **VirtualBox**: 6.1.6
- **Docker**: 19.03
- **Kubernetes**: 1.17.5
- **Calico**: 3.12.0

## Quick Start

### Vagrant

If you want using vagrant up local cluster, do this:

```bash
git clone https://github.com/kuops/kubernetes-ansible.git
cd kubernetes-ansible
vagrant up
```

Custom variables change defaults values of cluster in Vagrant.

> this variables export before in `vagrant up`.

Variables:

```bash
# master node nummber, should be deployed with odd numbers
export KUBE_MASTER_NUM=3
# worker node number
export KUBE_NODE_NUM=1
# master node machine memory size
export KUBE_MASTER_MEM=4096
# worker node machine memory size
export KUBE_NODE_MEM=4096
```

If running has some error, setting debug variables:

> then you can try `vagrant provision` continue running ansible.

```bash
# ansbile verbose level 0-4
export ANSIBLE_DEBUG=3
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

If you not use vagrant, `is_vagrant_vm` variables value set to `no`:

```yaml
is_vagrant_vm: no
```

run deploy example:

```bash
ansible-playbook -i inventories/example/hosts site.yml
```
