#!/usr/bin/env python3

import configparser
import os
import subprocess
import sys

from git import Repo


class Deploy:

    def __init__(self):

        if not os.path.isfile('deploy/deploy.cfg'):
            print('\n!!!! File "deploy/deploy.cfg" not exists !!!!')
            print('Copy or check the file "deploy/deploy.cfg.example"')
            sys.exit(1)

        deploy_cfg = configparser.ConfigParser()
        deploy_cfg.read('deploy/deploy.cfg')

        self.mode = deploy_cfg['options']['mode']

        if self.mode == 'cloud':
            self.deploy_cfg = configparser.ConfigParser()
            self.deploy_cfg.read('deploy/deploy-cloud.cfg')
        elif self.mode == 'docker':
            self.deploy_cfg = configparser.ConfigParser()
            self.deploy_cfg.read('deploy/deploy-docker.cfg')
        else:
            msg = 'n!!!! Unsupported mode: {mode}. Supported modes: cloud, docker !!!!'.format(
                mode = deploy.cfg['options']['mode']
            )
            print(msg)
            sys.exit(1)

        self.common_cfg = configparser.ConfigParser()
        self.common_cfg.read('deploy/deploy-common.cfg')

        self.sys_user = self.deploy_cfg['server.odoo']['sys_user']

        self.odoo_root = None
        self.set_odoo_root()

        # TODO improve setter
        self.supervisor = True if self.deploy_cfg['server.odoo'].get('supervisor', False) == 'True' else False

        
        self.odoo_log_dir = '{odoo_root}/var/log'.format(odoo_root=self.odoo_root)

        # Odoo Core
        self.odoo_build_dir = '{odoo_root}/odoo'.format(odoo_root=self.odoo_root)
        self.odoo_git_url = self.common_cfg['odoo.core']['git_url']
        self.odoo_branch = self.common_cfg['odoo.core']['branch']

        # Odoo Enterprise
        self.with_enterprise = 'odoo.enterprise' in self.common_cfg.sections()
        if self.with_enterprise:
            self.enterprise_build_dir = '{odoo_root}/enterprise'.format(odoo_root=self.odoo_root)
            self.enterprise_git_url = self.common_cfg['odoo.enterprise']['git_url']
            self.enterprise_branch = self.common_cfg['odoo.enterprise']['branch']

        # Odoo Custom
        self.with_custom = 'odoo.custom' in self.common_cfg.sections()
        if self.with_custom:
            self.custom_build_dir = '{odoo_root}/custom'.format(odoo_root=self.odoo_root)
            self.custom_git_url = self.common_cfg['odoo.custom']['git_url']
            self.custom_branch = self.common_cfg['odoo.custom']['branch']

    def set_odoo_root(self):
        self.odoo_root = self.deploy_cfg['server.odoo']['odoo_root']

    def odoo_core(self):
        print("\n==== Deploy: Odoo Core ====\n")
        print("(i) odoo_build_dir: %s" % self.odoo_build_dir)

        if self.mode == 'docker':
            if not os.path.exists(self.odoo_build_dir):
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

        if self.mode == 'docker':
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

        if self.mode == 'docker':
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

        # TODO odoo (self.sys_user)
        subprocess.call(['chown', '-R', 'odoo:', self.odoo_root])

    # def switch_current_build(self):
    #     print("\n==== Change current build ====")
    #     print ('* %s -> %s' % (self.current_build, self.build_dir))

    #     subprocess.call(['ln', '-sfn', self.build_dir, self.current_build])

    # def supervisor(self):
    #     print("\n---- Create Supervisor config file ----")
    #     print("\nOdoo start command: {command}".format(command=self.odoo_bin))

    #     # ? TODO: -c odoo.cfg (for admin_passwd)
    #     with open('/etc/supervisor/conf.d/odoo.conf', 'w') as f:
    #         conf = '\n'.join(
    #             ['[program:odoo]',
    #              'command={COMMAND}',
    #              'numprocs=1',
    #              'directory={CURRENT_BUILD}/odoo',
    #              'stdout_logfile={CURRENT_BUILD}/var/log/odoo/odoo-server.log',
    #              'redirect_stderr=true',
    #              'autostart=true',
    #              'autorestart=true',
    #              'stopsignal=TERM',
    #              'stopasgroup=true',
    #              'user={SYS_USER}']
    #         ).format(
    #             COMMAND=self.odoo_bin,
    #             CURRENT_BUILD=self.current_build,
    #             SYS_USER=self.sys_user,
    #         )
    #         f.write(conf)

    #     print("\n* Reload Supervisor config")
    #     subprocess.call(['supervisorctl', 'reread'])
    #     subprocess.call(['supervisorctl', 'update'])
        
    #     print("\n* (Re)starting Supervisor Odoo service")
    #     subprocess.call(['supervisorctl', 'restart', 'odoo'])

    def run(self):
        self.prepare_build()
        self.build_odoo()

        # TODO deploy/config.cfg
        # self.switch_current_build()
        
        # TODO-1: chown -R odoo: /opt/odoo
        # TODO-2: With Linux "odoo" user.. import ERRORS for PyPDF2 etc.
        # chmod -R ugo+rx /usr/local/lib/python3.6/dist-packages/
        if self.supervisor:
            self.supervisor()
        
if __name__ == '__main__':
    deploy = Deploy()
    deploy.run()
