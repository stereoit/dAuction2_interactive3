# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  config.ssh.insert_key = true

  config.vm.box = "fedora-22-cloud"

  config.vm.hostname = "dauction2.server"


  config.vm.network "forwarded_port", guest: 80, host: 8000
  config.vm.network "forwarded_port", guest: 8080, host: 8080

  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.name = "dAuction2 staging"
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", "50"]
    vb.memory = "512"
    vb.cpus = 2
  end


  config.vm.provision "SW layer", type: "shell", inline: <<-SHELL
    echo "configured" > /etc/vagrant
    dnf install -y glibc-common python-virtualenv python-pip
    dnf -y -v groupinstall "C Development Tools and Libraries"
    dnf install -y graphviz postgresql-server postgresql-contrib postgresql-devel
    systemctl enable postgresql &&  postgresql-setup initdb && systemctl start postgresql
  SHELL

  config.vm.provision "App layer", type: "shell", privileged: false, inline: <<-SHELL
    export PYTHONUNBUFFERED=true
    virtualenv venv && source venv/bin/activate
    echo "PIP install, will take some time (like 5mins)"
    pip install --upgrade pip
    pip install -r /vagrant/requirements.txt
    echo "source ~/venv/bin/activate\ncd /vagrant/" >> ~/.bashrc
  SHELL

end
