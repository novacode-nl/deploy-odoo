#!/usr/bin/env python3

import configparser
import os
import subprocess
import sys

from deploy import Deploy


class InstallOdooServer:

    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.deploy = Deploy(path)

    def run(self):
        print('\n==== Install Odoo Server ====\n')
        print('* APT packages')
        command = 'apt-get -qq update && apt-get -qq upgrade && apt-get -qq install {packages}'.format(
            packages = self.deploy.common_cfg['apt.install']['odoo_deps'])
        apt_process = subprocess.Popen(command, shell=True)
        apt_process.wait()

        print('* wkhtmltopdf')
        url = 'https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/{release}/{deb}'.format(
            release = self.deploy.common_cfg['wkhtmltopdf']['release'],
            deb = self.deploy.common_cfg['wkhtmltopdf']['deb'])
        subprocess.call(['wget', '-q', url])
        subprocess.call(['gdebi', '--n', self.deploy.common_cfg['wkhtmltopdf']['deb']])
        subprocess.call(['ln', '-sf', '/usr/local/bin/wkhtmltopdf', '/usr/bin'])
        subprocess.call(['ln', '-sf', '/usr/local/bin/wkhtmltoimage', '/usr/bin'])

        # Odoo system user
        print("* Create Odoo system user")
        cmd_adduser = "adduser --system --quiet --shell=/bin/bash --gecos 'ODOO' --group {sys_user}".format(
            sys_user=self.deploy.sys_user
        )
        adduser_process = subprocess.Popen(cmd_adduser, shell=True)
        adduser_process.wait()

if __name__ == '__main__':
    install = InstallOdooServer()
    install.run()
