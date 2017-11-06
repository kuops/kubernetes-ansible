# kubernetes-ansible

 使用 ansible 搭建二进制 kubernetes 集群
 
 主机名用作 etcd 的名称，所以不能有重复的
 
 高可用使用的是 nginx 反向代理， 每个 kube-apiserver-client 访问的 api-server 地址都为本机的 `127.0.0.1:6443`
 
 inventory 中 nginx-proxy 中的地址为 node 节点的 ip  ， 如果 master 节点复用 node 节点，则 ansible 的  nginx-proxy 不能添加该 master 节点 ip

# 主机列表

|IP|OS|hostname|
|---|---|---|
|10.0.7.1|CentOS 7.3|k8s-node1|
|10.0.7.2|CentOS 7.3|k8s-node2|
|10.0.7.3|CentOS 7.3|k8s-node3|
|10.0.7.4|CentOS 7.3|k8s-node4|


# 使用前提
- 安装 epel yum 源
- 关闭 selinux
- 设置 时间同步

# git clone
```
git clone https://github.com/opspy/kubernetes-ansible.git
cd kubernetes-ansible
```

# 分发秘钥
```
ssh-keygen -t rsa  -f '/root/.ssh/id_rsa' -N ''
for i in `seq 1 4`;do
  ssh-copy-id root@10.0.7.${i}
done
```

# 准备 kubernetes 的二进制文件
```
mkdir -p roles/common/files/bin
TAG=v1.7.9
URL=https://storage.googleapis.com/kubernetes-release/release/$TAG/bin/linux/amd64
curl -# -L -o roles/common/files/bin/kube-apiserver $URL/kube-apiserver
curl -# -L -o roles/common/files/bin/kube-controller-manager $URL/kube-controller-manager
curl -# -L -o roles/common/files/bin/kube-scheduler $URL/kube-scheduler
curl -# -L -o roles/common/files/bin/kube-proxy $URL/kube-proxy
curl -# -L -o roles/common/files/bin/kubelet $URL/kubelet
curl -# -L -o roles/common/files/bin/kubectl $URL/kubectl
```

# 准备 etcd 的二进制文件
```
mkdir -p roles/etcd/files/bin
ETCD_VER=v3.2.5
wget -O /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz https://storage.googleapis.com/etcd/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz
tar xf  /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz --strip-components 1 -C roles/etcd/files/bin
```

# 准备 flannel 的二进制文件
```
mkdir -p roles/flannel/files/bin
flannel_VER=v0.8.0
wget -O /tmp/flannel.tar.gz https://github.com/coreos/flannel/releases/download/${flannel_VER}/flannel-${flannel_VER}-linux-amd64.tar.gz
tar xf /tmp/flannel.tar.gz -C /tmp
cp /tmp/{flanneld,mk-docker-opts.sh} roles/flannel/files/bin/
```

# 生成 token 替换 ansible 变量

使用 bootstrap 时需要用到
```
TOKEN=$(head -c 16 /dev/urandom | od -An -t x | tr -d ' ')
sed -ri "s@(bootstrap_token:) .*@\1 $TOKEN@g" group_vars/all.yml
```

# 执行 ansible
```
ansible-playbook k8s-cluster.yml
```

# 启动完成之后动态生成 kubelet 证书

创建 clustererolebinding ，在 ansible 的 ssl 主机执行
```
kubectl create clusterrolebinding kubelet-bootstrap \
  --clusterrole=system:node-bootstrapper \
  --user=kubelet-bootstrap
```

通过 kublet 的 TLS 证书请求 ， 需要等待 node 节点 的 nginx 和 kubelet 启动完毕，才会出现该请求
```
#查看未授权的 CSR 请求
~]# kubectl get csr
NAME                                                   AGE       REQUESTOR           CONDITION
node-csr-Bozk_ncqfXA05Jh4wCGLDCpDFjhpysBbDHh_jAqo74M   1m        kubelet-bootstrap   Pending
#通过 CSR 请求
kubectl certificate approve node-csr-Bozk_ncqfXA05Jh4wCGLDCpDFjhpysBbDHh_jAqo74M
```
# 测试集群是否正常
```
[root@k8s-node1 ~]# kubectl  run nginx --image=nginx:1.7.9
[root@k8s-node1 ~]# kubectl  get pod
NAME                     READY     STATUS    RESTARTS   AGE
nginx-1480123054-kv5t4   1/1       Running   2          2h
```
