# Kubernetes-Ansible

This Repository is Using Ansible Deploy a Production Kubernetes Cluster. Ansible Role Design by Kubeadm.


## Dependencies

- **Linux Distribution**: CentOS/7
- **Ansible**: 2.9.2
- **Vagrant**: 2.2.6
- **VirtualBox**: 6.1.2

> vagrant 2.2.6 support vbox 6.1 solution [link](https://blogs.oracle.com/scoter/getting-vagrant-226-working-with-virtualbox-61-ga)

## Getting Started

custom variables change defaults number of nodes in cluster.

variables:

```bash
# master node nummber, should be deployed with odd numbers
export KUBE_MASTER_NUM=3
# worker node number 
export KUBE_NODE_NUM=1
```

