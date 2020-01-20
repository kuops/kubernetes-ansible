# -*- mode: ruby -*-
# vi: set ft=ruby :

BOX_URL             = 'https://mirrors.nju.edu.cn/centos-cloud/centos/7/vagrant/x86_64/images/CentOS-7-x86_64-Vagrant-1910_01.VirtualBox.box'
BOX                 = 'centos/7'
VAGRANT_DIR         = File.expand_path(File.dirname(__FILE__))
KUBE_MASTER_NUM     = ENV["KUBE_MASTER_NUM"] || 3
KUBE_NODE_NUM       = ENV["KUBE_NODE_NUM"] || 1
KUBE_NODE_MEM       = ENV["KUBE_NODE_MEM"] || 16384
KUBE_MASTER_MEM     = ENV["KUBE_MASTER_MEM"] || 2048
VAGRANT_CLUSTER     = {
      "kube_master" => (1..KUBE_MASTER_NUM).each_with_index.map{ |i| 'kube-master' + i.to_s},
      "kube_node"   => (1..KUBE_NODE_NUM).each_with_index.map{ |i| 'kube-node' + i.to_s},
      "k8s_cluster:children" => ["kube-master", "kube-node"],
}
VAGRANT_NODES       = VAGRANT_CLUSTER.delete_if { |key, value| key == ("k8s_cluster:children") }.values.flatten

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
          vb.name = hostname
          vb.gui = false
          case
            when (hostname.start_with? 'kube-master')
              vb.memory = KUBE_MASTER_MEM
            when (hostname.start_with? 'kube-node')
              vb.memory = KUBE_NODE_MEM
          end
          vb.cpus = 2
          if !File.exist?("#{VAGRANT_DIR}/#{hostname}.vmdk")
            vb.customize ['createhd', '--filename', "#{VAGRANT_DIR}/#{hostname}.vmdk", '--size', 100 * 1024]
          end
          vb.customize ["storagectl", :id, "--name", "SATA Controller", "--add", "scsi", "--controller", "LsiLogic", "--bootable", "off"]
          vb.customize ["storageattach", :id, "--storagectl", "SATA Controller", "--port", 0, "--device", 0, "--medium", "#{VAGRANT_DIR}/#{hostname}.vmdk", "--type", "hdd"]
        end #end for vb
        if VAGRANT_NODES.last == hostname
          node.vm.provision "ansible" do |ansible|
            ansible.limit = "all"
            ansible.become = true
            ansible.compatibility_mode = "2.0"
            ansible.playbook = "cluster.yml"
            ansible.groups   = VAGRANT_CLUSTER
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
