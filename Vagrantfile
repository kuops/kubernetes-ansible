# -*- mode: ruby -*-
# vi: set ft=ruby :

cluster = {
  "k8s-master1" => { :ip => "10.0.7.101", :mem => 2048 },
  "k8s-master2" => { :ip => "10.0.7.102", :mem => 2048 },
  "k8s-master3" => { :ip => "10.0.7.103", :mem => 2048 },
  "k8s-node1" =>   { :ip => "10.0.7.104", :mem => 16384 },
}

Vagrant.configure("2") do |config|
  config.vm.box = 'centos/7'
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = true
  config.hostmanager.ignore_private_ip = false
  config.hostmanager.include_offline = true
  config.vm.box_check_update = false 
  config.vbguest.auto_update = false
  #config.vbguest.iso_path = "/mnt/d/localrepo/VBoxGuestAdditions_5.2.18.iso"
  config.vm.boot_timeout = 600
  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    v.cpus = 2
  end

  cluster.each_with_index do |(hostname, info), index|
    config.vm.define hostname do |cfg|
      cfg.vm.provider :virtualbox do |vb, override|
        override.vm.network :private_network, ip: "#{info[:ip]}"
        override.vm.hostname = hostname
        vb.name = hostname
        vb.customize ["modifyvm", :id, "--memory", info[:mem], "--hwvirtex", "on"]
      end # end provider
      config.vm.provision "shell", inline: <<-SHELL
         if ! [ -d /root/.ssh/ ];then
             mkdir -p /root/.ssh/
             chmod 700 /root/.ssh/
         fi
         cat  /vagrant/files/ssh-keys/id_rsa.pub >> /root/.ssh/authorized_keys
      SHELL
    end # end config
  end # end cluster
end
