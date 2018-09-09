# HA-Kubernetes-Ansible 

拉取代码

```
git clone xxx  kubernetes-ansible
cd kubernetes-ansible
mkdir -p files/ssh-keys
```
生成 `ssh-keys` 并启动集群

```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -N '' -f files/ssh-keys/id_rsa
vagrant up
ansible all -m ping
```

保存 bootstrap 令牌

```
TOKEN_PUB=$(openssl rand -hex 3)
TOKEN_SECRET=$(openssl rand -hex 8)
BOOTSTRAP_TOKEN="${TOKEN_PUB}.${TOKEN_SECRET}"
sed -i "s@bootstrap_token: .*@bootstrap_token: ${BOOTSTRAP_TOKEN}@" group_vars/all.yml
sed -i "s@bootstrap_token_pub: .*@bootstrap_token_pub: ${TOKEN_PUB}@" group_vars/all.yml
sed -i "s@bootstrap_token_secret: .*@bootstrap_token_secret: ${TOKEN_SECRET}@" group_vars/all.yml
```

下载 kubernetes-二进制文件

```
mkdir -p roles/distribution_file/files/
KUBE_VERSION="v1.11.0"
curl  https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/kubernetes-server-linux-amd64.tar.gz > kubernetes-server-linux-amd64.tar.gz
tar xf kubernetes-server-linux-amd64.tar.gz  --strip-components=3  -C roles/distribution_file/files/ kubernetes/server/bin/{kubelet,kubectl,kubeadm,kube-apiserver,kube-controller-manager,kube-scheduler,kube-proxy}
rm -f kubernetes-server-linux-amd64.tar.gz
```

下载 etcd 二进制文件

```
mkdir -p roles/etcd/files/
ETCD_VER=v3.2.18
curl -L -4 https://storage.googleapis.com/etcd/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz > etcd-${ETCD_VER}-linux-amd64.tar.gz
tar xf etcd-${ETCD_VER}-linux-amd64.tar.gz  --strip-components=1 -C roles/etcd/files/ etcd-${ETCD_VER}-linux-amd64/{etcd,etcdctl}
rm -f etcd-${ETCD_VER}-linux-amd64.tar.gz
```

下载 CNI 插件

```
mkdir -p roles/flannel/files/bin
CNI_VER="v0.6.0"
curl -sSLO --retry 5 https://storage.googleapis.com/kubernetes-release/network-plugins/cni-plugins-amd64-${CNI_VER}.tgz
tar -xf cni-plugins-amd64-${CNI_VER}.tgz -C roles/flannel/files/bin
rm -f cni-plugins-amd64-${CNI_VER}.tgz
```

初始化系统，升级内核
```
ansible-playbook os-init.yml
```

等待系统启动完成后

```
ansible-playbook kubernetes-cluster.yml
```

登陆 node1 检查

```
kubectl get node
```

只安装了kubernetes 基础组件和 flannel 网络插件，DNS 等其他插件自行使用 yaml 文件进行安装
