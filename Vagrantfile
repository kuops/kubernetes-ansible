# -*- mode: ruby -*-
# vi: set ft=ruby :

require "yaml"
require 'openssl'
require 'fileutils'
yaml_config = YAML.load_file("#{File.dirname(__FILE__)}/vagrant.yaml")

Vagrant.require_version ">= 2.2.19"
ENV['VAGRANT_EXPERIMENTAL'] = "disks"
ENV["LC_ALL"] = "en_US.UTF-8"

KUBE_GROUPS = {
    "kube_master"    => (1..yaml_config["master"]["number"]).each_with_index.map{ |i| format("%s-%0.2d",yaml_config["master"]["prefix"],i)},
    "kube_worker"    => (1..yaml_config["worker"]["number"]).each_with_index.map{ |i| format("%s-%0.2d",yaml_config["worker"]["prefix"],i)},
    "etcd"           => (1..yaml_config["master"]["number"]).each_with_index.map{ |i| format("%s-%0.2d",yaml_config["master"]["prefix"],i)},
    "all:vars"       => YAML.load_file("#{File.dirname(__FILE__)}/inventories/vagrant/group_vars/all.yml")
}
KUBE_NODES = KUBE_GROUPS.select { |key, value| key.to_s.match(/^kube_(master|worker)/) }.values.flatten

ANSIBLE_EXTRA_VARS = {
    "is_vagrant" => "yes",
    "vagrant_network_interface" => "eth1",
    # default ansible inventory directory not in this directory
    "local_bin_dir" => "#{File.dirname(__FILE__)}/.bin",
    "local_certs_dir" => "#{File.dirname(__FILE__)}/.certs",
}

ANSIBLE_VERBOSE = "v" * ENV["ANSIBLE_DEBUG"].to_i

def create_ca_certs(key_path,cert_path,cn)
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

def create_pubkey_pair(sa_key_path,sa_pub_path)
    sa_key = OpenSSL::PKey::RSA.new 2048
    sa_pub = sa_key.public_key
    File.open(sa_key_path, "wb") { |f| f.print sa_key.to_pem }
    File.open(sa_pub_path, "wb") { |f| f.print sa_pub.to_pem }
end

def generate_kubernetes_certs(certs_dir="#{File.dirname(__FILE__)}/.certs")
    unless Dir.exist?(certs_dir)
        FileUtils.mkdir_p certs_dir
    end
    unless File.exist?("#{certs_dir}/token.csv")
        pattern = [('a'..'z'),(0..9)].map(&:to_a).flatten
        token_id = (0...6).map{ pattern[rand(pattern.length)] }.join
        token_secret = (0...16).map{ pattern[rand(pattern.length)] }.join
        File.open("#{certs_dir}/token.csv", "wb") { |f| f.print "%s.%s\n" % [token_id, token_secret] }
    end
    unless File.exist?("#{certs_dir}/kube_ca.crt")
        create_ca_certs("#{certs_dir}/kube_ca.key","#{certs_dir}/kube_ca.crt","kubernetes")
    end
    unless File.exist?("#{certs_dir}/etcd_ca.crt")
        create_ca_certs("#{certs_dir}/etcd_ca.key","#{certs_dir}/etcd_ca.crt","etcd-ca")
    end
    unless File.exist?("#{certs_dir}/front-proxy-ca.crt")
        create_ca_certs("#{certs_dir}/front-proxy-ca.key","#{certs_dir}/front-proxy-ca.crt","front-proxy-ca")
    end
    unless File.exist?("#{certs_dir}/sa.pub")
        create_pubkey_pair("#{certs_dir}/sa.key","#{certs_dir}/sa.pub")
    end
end

generate_kubernetes_certs

Vagrant.configure(2) do |config|

    if Vagrant.has_plugin?("vagrant-vbguest")
        config.vbguest.auto_update = false
    end

    KUBE_NODES.each_with_index do |hostname,index|
        config.vm.synced_folder ".", "/vagrant", disabled: true
        config.vm.define hostname do |machine|
            machine.vm.box_url = yaml_config["box_url"]
            machine.vm.box = yaml_config["box"]
            machine.vm.box_check_update = false
            machine.vm.box_download_insecure = true
            machine.vm.graceful_halt_timeout = 120
            machine.vm.hostname = hostname
            machine.vm.network "private_network", ip: "10.7.0.#{index+10}"
            machine.vm.disk :disk, name: "data", size: "100GB"
            machine.vm.provider "virtualbox" do |vb|
                vb.linked_clone = true
                vb.gui = false
                vb.name = hostname
                case
                    when (hostname.start_with? 'kube-master')
                        vb.cpus = yaml_config["master"]["cpu"]
                        vb.memory = yaml_config["master"]["memory"]
                    when (hostname.start_with? 'kube-worker')
                        vb.cpus = yaml_config["master"]["cpu"]
                        vb.memory = yaml_config["worker"]["memory"]
                end # end of case
            end #end of machine.vm.provider
            if hostname == KUBE_NODES.last
                machine.vm.provision "ansible" do |ansible|
                  ansible.limit = "all"
                  ansible.compatibility_mode = "2.0"
                  ansible.playbook = "site.yml"
                  ansible.groups = KUBE_GROUPS
                  ansible.verbose = ANSIBLE_VERBOSE
                  ansible.extra_vars =  ANSIBLE_EXTRA_VARS
                end #end of machine.vm.provision
            end #end of if
        end #end of config.vm.define
    end # end of KUBE_NODES.each_with_index
    config.vm.provision "shell", inline: <<-SHELL
        #!/bin/bash
        set -exu
        # setting data storage
        FORMATED_FILE="/etc/default/disk-format"
        if ! [ -f ${FORMATED_FILE} ] && ! mountpoint -q /data ;then
            mkdir -p /data
            parted -s /dev/sdb mklabel gpt
            yes | mkfs.ext4 /dev/sdb
            grep '/data' /etc/fstab || echo "/dev/sdb /data  ext4 defaults 0 0" >> /etc/fstab
            mount -a
            echo "ok" > ${FORMATED_FILE}
        fi
    SHELL
end #end of config
