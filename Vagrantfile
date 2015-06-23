# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.provision :shell, :path => "provision.sh"
  config.vm.synced_folder './vagrant_data', '/vagrant_data'
  config.vm.network "private_network", ip: "33.33.33.10"
  config.vm.network :forwarded_port, host:1234, guest: 80
  config.vm.provider "virtualbox" do |v|
    v.memory = 512
    v.cpus = 1
  end
end
