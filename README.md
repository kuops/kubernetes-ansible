# Kubernetes-Ansible

This Repository is Using Ansible Deploy a Production high availability Kubernetes Cluster. Roles step Fllow the offical tools Kubeadm.

## High availability 

each node running a envoy loadbalancer on 127.0.0.1:8443 proxy the kube-apiserver serivce.

## Dependencies

- **Linux Distribution**: CentOS/7
- **Ansible**: 2.9.4
- **Vagrant**: 2.2.7
- **VirtualBox**: 6.1.4
- **Docker**: 19.03
- **Kubernetes**: 1.17.3

## Quick Start

### Vagrant

If you want using vagrant up local cluster, do this:

```
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
export KUBE_NODE_MEM=16384
```

If running has some error, setting debug variables:

> then you can try `vagrant provision` continue running ansible.

```bash
# ansbile verbose level 0-4
export ANSIBLE_DEBUG=3
```

### Ansible

generator ca cert and bootstrap token, you can run:

```bash
# generator cert at base directory in .cert
make cert
```

add your inventory on inventories directory, like `example` inventory:

```
inventories/example
├── group_vars
│   └── all.yml
└── hosts
```

run deploy:

```bash
ansible-playbook -i inventories/example/hosts site.yml
```
