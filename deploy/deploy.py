#!/usr/bin/env python3

import configparser
import logging
import os
import subprocess
import sys
import uuid

from git import Repo

_logger = logging.getLogger(__name__)


class Deploy:

    def __init__(self):

        if not os.path.isfile('/root/deploy-odoo/deploy/config.cfg'):
            print('File not exists: /root/deploy-odoo/deploy/config.cfg')
            sys.exit()

        self.config = configparser.ConfigParser()
        self.config.read('/root/deploy-odoo/deploy/config.cfg')

        self.sys_user = self.config['server.odoo']['sys_user']

        # TODO improve setter (cleanup)
        self.development = True if self.config['server.odoo'].get('development', False) == 'True' else False
        if self.development:
            self.build_name = 'dev'
        else:
            self.build_name = str(uuid.uuid4())

        self.build_dir = '/opt/odoo/{build_name}'.format(build_name=self.build_name)
        self.current_build = '/opt/odoo/current'
        
        self.odoo_log_dir = '{build_dir}/var/log/odoo'.format(build_dir=self.build_dir)

        self.odoo_bin_options = None
        self.set_odoo_bin_options()

        self.odoo_bin_path = None
        self.odoo_bin = None
        self.set_odoo_bin()

        ####
        # TODO setters and props for Odoo
        ####
        
        # Odoo Core
        self.odoo_build_dir = '{build_dir}/odoo'.format(build_dir=self.build_dir)
        self.odoo_git_url = self.config['apps.odoo.core']['git_url']
        self.odoo_branch = self.config['apps.odoo.core']['branch']

        # Odoo Enterprise
        self.with_enterprise = 'apps.odoo.enterprise' in self.config.sections()
        if self.with_enterprise:
            self.enterprise_build_dir = '{build_dir}/enterprise'.format(build_dir=self.build_dir)
            self.enterprise_git_url = self.config['apps.odoo.enterprise']['git_url']
            self.enterprise_branch = self.config['apps.odoo.enterprise']['branch']

        # Odoo Custom
        self.with_custom = 'apps.odoo.custom' in self.config.sections()
        if self.with_custom:
            self.custom_build_dir = '{build_dir}/custom'.format(build_dir=self.build_dir)
            self.custom_git_url = self.config['apps.odoo.custom']['git_url']
            self.custom_branch = self.config['apps.odoo.custom']['branch']

    def set_odoo_bin_options(self):
        """ odoo-bin command, with server specific configuration.
        Project specific settings e.g. `addons_path` should go into odoo.conf"""
        
        options = []
        for k, v in self.config['odoo-bin'].items():
            key = '--{key}'.format(key=k)
            option = (key, v)
            options.append(option)
        self.odoo_bin_options = options

    def set_odoo_bin(self):
        """ odoo-bin command, with server specific configuration.
        Project specific settings e.g. `addons_path` should go into odoo.conf"""

        self.odoo_bin_path = '{build_dir}/odoo/odoo-bin'.format(
            build_dir=self.build_dir
        )
        options = ' '.join([item for option in self.odoo_bin_options for item in option])
        self.odoo_bin = '{current_build}/odoo/odoo-bin {options}'.format(
            current_build=self.current_build,
            options=options
        )

    def odoo_core(self):
        print("\n==== Deploy: Odoo Core ====\n")
        print("(i) odoo_build_dir: %s" % self.odoo_build_dir)

        if self.development:
            if not os.path.exists(self.odoo_bin_path):
                print("\n!!!! Development/Docker ERROR !!!!")
                print("* odoo_build_dir is invalid: %s" % self.odoo_build_dir)
                print("* Check the local Docker volume /odoo/odoo")
                sys.exit(1)
        elif not os.path.exists(self.odoo_build_dir):
            print("\n* Git clone Odoo")
            Repo.clone_from(self.odoo_git_url , self.odoo_build_dir, branch=self.odoo_branch, single_branch=True)

        # pip3 install -Ur requirements.txt
        if os.path.exists(self.odoo_build_dir):
            print("\n* Install Python/pip Odoo requirements\n")
            filepath = '{path}/requirements.txt'.format(path=self.odoo_build_dir)
            subprocess.call(['pip3', 'install', '-Ur', filepath])

    def odoo_enterprise(self):
        if not self.with_enterprise:
            print("\n==== No Odoo Enterprise ====")
            return # No pip install -r requirements

        print("\n==== Deploy: Odoo Enterprise ====")
        print("(i) enterprise_build_dir: %s" % self.enterprise_build_dir)

        if self.development:
            if not os.path.exists(self.enterprise_build_dir):
                # TODO check whether empty, because Docker volumes already mount.
                print("\n!!!! Development/Docker ERROR !!!!")
                print("* enterprise_build_dir not exists: %s" % self.enterprise_build_dir)
                print("* Check the local Docker volume /odoo/enterprise")
        elif not os.path.exists(self.enterprise_build_dir):
            print("\n* Git clone Enterprise")
            Repo.clone_from(self.enterprise_git_url , self.enterprise_build_dir, branch=self.enterprise_branch, single_branch=True)

        # pip3 install -Ur requirements.txt
        if os.path.exists(self.enterprise_build_dir):
            print("\n* Find and install Python/pip Enteprise requirements\n")
            for root, dirs, files in os.walk(self.enterprise_build_dir):
                for fname in files:
                    if fname == 'requirements.txt':
                        filepath = os.path.join(root, file)
                        subprocess.call(['pip3', 'install', '-Ur', filepath])

    def odoo_custom(self):
        if not self.with_custom:
            print("\n==== No Odoo Custom ====")
            return # No pip install -r requirements

        print("\n==== Deploy: Odoo Custom ====")
        print("(i) custom_build_dir: %s" % self.custom_build_dir)

        if self.development:
            if not os.path.exists(self.custom_build_dir):
                # TODO check whether empty, because Docker volumes already mount.
                print("\n!!!! Development/Docker ERROR !!!!")
                print("* custom_build_dir not exists: %s" % self.custom_build_dir)
                print("* Check the local Docker volume /odoo/custom")
        elif not os.path.exists(self.custom_build_dir):
            print("\n---- Git clone Custom ----")
            Repo.clone_from(self.custom_git_url , self.custom_build_dir, branch=self.custom_branch, single_branch=True)

        # pip3 install -Ur requirements.txt
        if os.path.exists(self.custom_build_dir):
            print("\n* Find and install Python/pip Custom requirements\n")
            for root, dirs, files in os.walk(self.custom_build_dir):
                for fname in files:
                    if fname == 'requirements.txt':
                        filepath = os.path.join(root, file)
                        subprocess.call(['pip3', 'install', '-Ur', filepath])

    def build_odoo(self):
        # TODO async (concurrent clones)
        self.odoo_core()
        self.odoo_enterprise()
        self.odoo_custom()

    def prepare_build(self):
        print("\n---- Prepare build ----")

        subprocess.call(['mkdir', '-p', self.odoo_log_dir])
        odoo_server_log = '{log_dir}/odoo-server.log'.format(log_dir=self.odoo_log_dir)
        subprocess.call(['touch', odoo_server_log])
        subprocess.call(['chown', '-R', 'odoo:', self.build_dir])

    def switch_current_build(self):
        print("\n==== Change current build ====")
        print ('* %s -> %s' % (self.current_build, self.build_dir))

        subprocess.call(['ln', '-sfn', self.build_dir, self.current_build])

    def supervisor(self):
        print("\n---- Create Supervisor config file ----")
        print("\nOdoo start command: {command}".format(command=self.odoo_bin))

        # ? TODO: -c odoo.cfg (for admin_passwd)
        with open('/etc/supervisor/conf.d/odoo.conf', 'w') as f:
            conf = '\n'.join(
                ['[program:odoo]',
                 'command={COMMAND}',
                 'numprocs=1',
                 'directory={CURRENT_BUILD}/odoo',
                 'stdout_logfile={CURRENT_BUILD}/var/log/odoo/odoo-server.log',
                 'redirect_stderr=true',
                 'autostart=true',
                 'autorestart=true',
                 'stopsignal=TERM',
                 'stopasgroup=true',
                 'user={SYS_USER}']
            ).format(
                COMMAND=self.odoo_bin,
                CURRENT_BUILD=self.current_build,
                SYS_USER=self.sys_user,
            )
            f.write(conf)

        print("\n* Reload Supervisor config")
        subprocess.call(['supervisorctl', 'reread'])
        subprocess.call(['supervisorctl', 'update'])
        
        print("\n* (Re)starting Supervisor Odoo service")
        subprocess.call(['supervisorctl', 'restart', 'odoo'])

    def run(self):
        self.prepare_build()
        self.build_odoo()

        self.switch_current_build()
        # TODO-1: chown -R odoo: /opt/odoo
        # TODO-2: With Linux "odoo" user.. import ERRORS for PyPDF2 etc.
        # chmod -R ugo+rx /usr/local/lib/python3.6/dist-packages/
        self.supervisor()
        
if __name__ == '__main__':
    deploy = Deploy()
    deploy.run()
