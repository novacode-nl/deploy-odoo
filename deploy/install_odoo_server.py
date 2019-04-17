#!/usr/bin/env python3

import configparser
import subprocess

# from deploy import Deploy


class InstallOdooServer:

    def __init__(self):
        ## TODO `self.sys_user` from Deploy object.
        ## However Deploy() instantiation fails.
        ##
        # self.deploy = Deploy()
        # self.config = self.deploy.config
        # print(self.config.sections())
        # self.sys_user = self.config['server.odoo']['sys_user']
        self.sys_user = 'odoo'

    def run(self):
        print('\n==== Install Odoo Server ====\n')
        print('* APT packages')
        command = 'apt-get -qq update && apt-get -qq upgrade && apt-get -qq install postgresql-client supervisor wget gdebi-core libpq-dev libjpeg-dev libxml2-dev libxslt1-dev zlib1g-dev libldap2-dev libsasl2-dev libssl-dev node-less'
        apt_process = subprocess.Popen(command, shell=True)
        apt_process.wait()

        print('* wkhtmltopdf')
        subprocess.call(['wget', '-q', 'https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb'])
        subprocess.call(['gdebi', '--n', 'wkhtmltox_0.12.5-1.bionic_amd64.deb'])
        subprocess.call(['ln', '-sf', '/usr/local/bin/wkhtmltopdf', '/usr/bin'])
        subprocess.call(['ln', '-sf', '/usr/local/bin/wkhtmltoimage', '/usr/bin'])

        # Odoo system user
        print("* Create Odoo system user")
        cmd_adduser = "adduser --system --quiet --shell=/bin/bash --gecos 'ODOO' --group {sys_user}".format(
            sys_user=self.sys_user
        )
        adduser_process = subprocess.Popen(cmd_adduser, shell=True)
        adduser_process.wait()

if __name__ == '__main__':
    install = InstallOdooServer()
    install.run()
