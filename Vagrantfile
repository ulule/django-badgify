VAGRANTFILE_API_VERSION = '2'

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = 'precise64'
  config.vm.box_url = 'http://files.vagrantup.com/precise64.box'
  config.ssh.forward_agent = true
  config.vm.network :forwarded_port, guest: 8000, host: 8000
  config.vm.provision 'shell', path: 'scripts/vagrant-bootstrap.sh'
  config.vm.provider 'virtualbox' do |v|
    v.name = 'django_badgify'
    v.memory = 2048
    v.cpus = 2
    v.customize ['setextradata', :id, 'VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root', '1']
  end
end
