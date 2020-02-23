# -*- mode: ruby -*-
# vi: set ft=ruby :

BOX_URL             = 'https://mirrors.nju.edu.cn/centos-cloud/centos/7/vagrant/x86_64/images/CentOS-7-x86_64-Vagrant-1910_01.VirtualBox.box'
BOX                 = 'centos/7'
VAGRANT_DIR         = File.expand_path(File.dirname(__FILE__))
LOCAL_CERT_DIR      = "#{VAGRANT_DIR}/.cert"
LOCAL_BIN_DIR  = "#{VAGRANT_DIR}/.bin"
KUBE_MASTER_NUM     = ENV["KUBE_MASTER_NUM"] || 3
KUBE_NODE_NUM       = ENV["KUBE_NODE_NUM"] || 1
KUBE_NODE_MEM       = ENV["KUBE_NODE_MEM"] || 16384
KUBE_MASTER_MEM     = ENV["KUBE_MASTER_MEM"] || 4096
ANSIBLE_VERBOSE     = "v" * ENV["ANSIBLE_DEBUG"].to_i
VAGRANT_CLUSTER     = {
      "kube_master" => (1..KUBE_MASTER_NUM).each_with_index.map{ |i| 'kube-master' + i.to_s},
      "kube_node"   => (1..KUBE_NODE_NUM).each_with_index.map{ |i| 'kube-node' + i.to_s},
      "k8s_cluster:children" => ["kube_master", "kube_node"],
      "etcd"        => (1..KUBE_MASTER_NUM).each_with_index.map{ |i| 'kube-master' + i.to_s},
      "all:vars"    => {"docker_version" => "19.03.4",
                        "docker_storage_dir" => "/data/docker",
                        "docker_cgroup_driver" => "systemd",
                        "etcd_version" => "3.4.3",
                        "etcd_certs_dir" => "/etc/kubernetes/pki/etcd",
                        "etcd_ca_cert" => "/etc/kubernetes/pki/etcd/ca.crt",
                        "etcd_ca_key" => "/etc/kubernetes/pki/etcd/ca.key",
                        "kubernetes_version" => "1.17.3",
                        "kubernetes_conf_dir" => "/etc/kubernetes",
                        "kubernetes_certs_dir" => "/etc/kubernetes/pki",
                        "kubernetes_ca_key" => "/etc/kubernetes/pki/ca.key",
                        "kubernetes_ca_cert" => "/etc/kubernetes/pki/ca.crt",
                        "kubelet_manifests_dir" => "/etc/kubernetes/manifests",
                        "kubernetes_cluster_name" => "kubernetes",
                        "kubernetes_cluster_ip_range" => "10.96.0.0/16",
                        "kubernetes_service_ip" => "10.96.0.1",
                        "kubernetes_cluster_dns" => "10.96.0.10",
                        "kubernetes_cluster_domain" => "cluster.local",
                        "kubernetes_image_repo" => "gcr.azk8s.cn/google_containers",
                        "kubernetes_apiserver_lb_ip" => "127.0.0.1",
                        "kubernetes_apiserver_lb_port" => "8443",
                        "kubernetes_apiserver_lb_url" => "https://127.0.0.1:8443",
                        "kubernetes_bootstrap_token" => File.read("#{LOCAL_CERT_DIR}/token.csv"),
                        "kubernetes_kubeconfig_bootstrap_conf" => "/etc/kubernetes/bootstrap-kubelet.conf",
                        "kubernetes_kubeconfig_admin_conf" => "/etc/kubernetes/admin.conf",
                        "kubernetes_logs_dir" => "/var/log/kubernetes",
                        "kubernetes_addons_dir" => "/etc/kubernetes/addons",
                        "openssl_conf" => "/etc/kubernetes/pki/openssl.cnf",
                        "local_bin_dir" => "#{LOCAL_BIN_DIR}",
                        "local_etcd_ca_key" => "#{LOCAL_CERT_DIR}/etcd_ca.key",
                        "local_etcd_ca_cert" => "#{LOCAL_CERT_DIR}/etcd_ca.crt",
                        "local_kube_ca_key" => "#{LOCAL_CERT_DIR}/kube_ca.key",
                        "local_kube_ca_cert" => "#{LOCAL_CERT_DIR}/kube_ca.crt",
                        "local_front_proxy_ca_key" => "#{LOCAL_CERT_DIR}/front-proxy-ca.key",
                        "local_front_proxy_ca_cert" => "#{LOCAL_CERT_DIR}/front-proxy-ca.crt",
                        "local_sa_key" => "#{LOCAL_CERT_DIR}/sa.key",
                        "local_sa_pub" => "#{LOCAL_CERT_DIR}/sa.pub"}
                        }
VAGRANT_NODES       = VAGRANT_CLUSTER.select { |key, value| key.to_s.match(/^kube_(master|node)/) }.values.flatten
ANSIBLE_EXTRA_VARS  = {
                       "is_vagrant_vm" => "yes",
                       "vagrant_ifname" => "eth1"
                      }

require 'openssl'
require 'fileutils'

if !Dir.exist?(LOCAL_CERT_DIR)
  FileUtils.mkdir_p "#{LOCAL_CERT_DIR}"
end

if !Dir.exist?(LOCAL_BIN_DIR)
  FileUtils.mkdir_p "#{LOCAL_BIN_DIR}"
end

def CreateCaCert(key_path,cert_path,cn)
  root_key = OpenSSL::PKey::RSA.new 2048 # the CA's public/private key
  root_ca = OpenSSL::X509::Certificate.new
  root_ca.version = 2 # cf. RFC 5280 - to make it a "v3" certificate
  root_ca.serial = 0
  root_ca.subject = OpenSSL::X509::Name.parse "CN=#{cn}"
  root_ca.issuer = root_ca.subject # root CA's are "self-signed"
  root_ca.public_key = root_key.public_key
  root_ca.not_before = Time.now
  root_ca.not_after = root_ca.not_before + 100 * 365 * 24 * 60 * 60 # 100 years validity
  ef = OpenSSL::X509::ExtensionFactory.new
  ef.subject_certificate = root_ca
  ef.issuer_certificate = root_ca
  root_ca.add_extension(ef.create_extension("keyUsage","digitalSignature,keyEncipherment,keyCertSign", true))
  root_ca.add_extension(ef.create_extension("basicConstraints","CA:TRUE",true))
  root_ca.sign(root_key, OpenSSL::Digest::SHA256.new)
  File.open(key_path, "wb") { |f| f.print root_key.to_pem }
  File.open(cert_path, "wb") { |f| f.print root_ca.to_pem }
end

def CreatePubkeyPair(sa_key_path,sa_pub_path)
  sa_key = OpenSSL::PKey::RSA.new 2048
  sa_pub = sa_key.public_key
  File.open(sa_key_path, "wb") { |f| f.print sa_key.to_pem }
  File.open(sa_pub_path, "wb") { |f| f.print sa_pub.to_pem }
end

if !File.exist?("#{LOCAL_CERT_DIR}/etcd_ca.crt")
  CreateCaCert("#{LOCAL_CERT_DIR}/etcd_ca.key","#{LOCAL_CERT_DIR}/etcd_ca.crt","etcd-ca")
end

if !File.exist?("#{LOCAL_CERT_DIR}/kube_ca.crt")
  CreateCaCert("#{LOCAL_CERT_DIR}/kube_ca.key","#{LOCAL_CERT_DIR}/kube_ca.crt","kubernetes")
end

if !File.exist?("#{LOCAL_CERT_DIR}/front-proxy-ca.crt")
  CreateCaCert("#{LOCAL_CERT_DIR}/front-proxy-ca.key","#{LOCAL_CERT_DIR}/front-proxy-ca.crt","front-proxy-ca")
end

if !File.exist?("#{LOCAL_CERT_DIR}/sa.pub")
  CreatePubkeyPair("#{LOCAL_CERT_DIR}/sa.key","#{LOCAL_CERT_DIR}/sa.pub")
end

def BootstrapToken()
  pattern = [('a'..'z'),(0..9)].map(&:to_a).flatten
  token_id = (0...6).map{ pattern[rand(pattern.length)] }.join
  token_secret = (0...16).map{ pattern[rand(pattern.length)] }.join
  File.open("#{LOCAL_CERT_DIR}/token.csv", "wb") { |f| f.print "%s.%s\n" % [token_id, token_secret] }
end

if !File.exist?("#{LOCAL_CERT_DIR}/token.csv")
  BootstrapToken()
end

Vagrant.require_version ">= 2.2.6"

Vagrant.configure(2) do |config|

  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  VAGRANT_NODES.each_with_index do |hostname,index|
    config.vm.synced_folder ".", "/vagrant", disabled: true
    config.vm.define hostname do |node|
        node.vm.box_url = "#{BOX_URL}"
        node.vm.box = "centos/7"
        node.vm.box_check_update = false
        node.vm.box_download_insecure = true
        node.vm.graceful_halt_timeout = 120
        node.vm.hostname = hostname
        node.vm.network "private_network", ip: "10.7.0.10#{index+1}"
        node.vm.provider "virtualbox" do |vb|
          vb.linked_clone = true
          vb.gui = false
          vb.name = hostname
          case
            when (hostname.start_with? 'kube-master')
              vb.memory = KUBE_MASTER_MEM
            when (hostname.start_with? 'kube-node')
              vb.memory = KUBE_NODE_MEM
          end
          vb.cpus = 4
          if !File.exist?("#{VAGRANT_DIR}/#{hostname}.vmdk")
            vb.customize ['createhd', '--filename', "#{VAGRANT_DIR}/#{hostname}.vmdk", '--size', 100 * 1024]
          end
          unless (system( "vboxmanage showvminfo #{hostname} 2>/dev/null |grep -q '^SATA Controller'" )) then
            vb.customize ["storagectl", :id, "--name", "SATA Controller", "--add", "sata"]
          end
          vb.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 1, "--device", 0, "--medium", "#{VAGRANT_DIR}/#{hostname}.vmdk", "--type", "hdd"]
        end #end for vb
        if VAGRANT_NODES.last == hostname
          node.vm.provision "ansible" do |ansible|
            ansible.limit = "all"
            ansible.compatibility_mode = "2.0"
            ansible.playbook = "site.yml"
            ansible.verbose = ANSIBLE_VERBOSE
            ansible.groups = VAGRANT_CLUSTER
            ansible.extra_vars =  ANSIBLE_EXTRA_VARS
          end #end for ansible
        end #end for if
    end #end for node
  end #end for hostname
  config.vm.provision "shell", inline: <<-SHELL
    #!/bin/bash
    set -exu

    # setting data storage
    FORMATED_FILE="/etc/default/disk-format"
    if ! [ -f /etc/default/disk-format ] && ! mountpoint -q /data ;then
      mkdir -p /data
      parted /dev/sdb mklabel gpt
      parted /dev/sdb mkpart primary 0% 100%
      partprobe /dev/sdb
      sleep 1
      mkfs.ext4 /dev/sdb1
      grep '/data' /etc/fstab || echo "/dev/sdb1 /data  ext4 defaults 0 0" >> /etc/fstab
      mount -a
      echo "ok" > /etc/default/disk-format
    fi
  SHELL
end #end for config
