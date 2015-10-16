# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  config.ssh.insert_key = true

  config.vm.box = "stereoit/fedora22-cloud"

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

  config.vm.provision "DB setup file", type: "file", source: "deployment/create_db.sql", destination: "/tmp/create_db.sql"
  config.vm.provision "DB pga file", type: "file", source: "deployment/pg_hba.conf", destination: "/tmp/pg_hba/conf"


  config.vm.provision "SW layer", type: "shell", inline: <<-SHELL
    echo "configured" > /etc/vagrant
    dnf install -y glibc-common python-virtualenv python-pip
    dnf -y -v groupinstall "C Development Tools and Libraries"
    dnf install -y graphviz postgresql-server postgresql-contrib postgresql-devel
    systemctl enable postgresql &&  postgresql-setup initdb && systemctl start postgresql
    mv /tmp/pg_hba.conf /var/lib/pgsql/data/ && chown postgres:postgres /var/lib/pgsql/data/pg_hba.conf
    sed -i "s/#listen_addresses.*/listen_addresses='*'/" /var/lib/pgsql/data/postgresql.conf
    systemctl start postgresql
    cd /tmp && sudo -H -u postgres bash -c 'psql -f /tmp/create_db.sql -v passwd=dauction -v user=dauction'
    dd if=/dev/zero of=/swapfile bs=1024 count=524288
    chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  SHELL

  config.vm.provision "App layer", type: "shell", privileged: false, inline: <<-SHELL
    export PYTHONUNBUFFERED=true
    virtualenv venv && source venv/bin/activate
    echo "PIP install, will take some time (like 5mins)"
    pip install --upgrade pip
    pip install -r /vagrant/requirements.txt
    cd /vagrant && ./manage.py migrate && ./manage.py collectstatic -c -l --noinput
    echo "source ~/venv/bin/activate\ncd /vagrant/" >> ~/.bashrc
  SHELL

end
