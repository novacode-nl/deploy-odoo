#!/usr/bin/env python3

import subprocess

from deploy import Deploy


class InstallPostgresServer:

    def __init__(self):
        self.deploy = Deploy()

    def run(self):
        print("\n==== Install PostgreSQL ====\n")
        command = 'apt-get -qq update && apt-get -qq upgrade && apt-get -qq install postgresql'
        apt_process = subprocess.Popen(command, shell=True)
        apt_process.wait()

        print("* Creating the Odoo PostgreSQL User")
        psql_command = "CREATE USER {USER} WITH LOGIN CREATEDB PASSWORD '{PASSWORD}';".format(
            USER=self.deploy.config['odoo-bin']['db_user'],
            PASSWORD=self.deploy.config['odoo-bin']['db_password']
        )
        subprocess.call('sudo -u postgres psql -c "%s"' % psql_command, shell=True)

if __name__ == '__main__':
    install = InstallPostgresServer()
    install.run()
