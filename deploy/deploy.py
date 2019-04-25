#!/usr/bin/env python3

import configparser
import os
import subprocess
import sys
import uuid

from git import Repo


class Deploy:

    def __init__(self, path):

        self.path = path
        self.path_deploy_cfg = '{path}/deploy.cfg'.format(path=path)
        self.path_deploy_common_cfg = '{path}/deploy-common.cfg'.format(path=path)
        self.path_deploy_cloud_cfg = '{path}/deploy-cloud.cfg'.format(path=path)
        self.path_deploy_docker_cfg = '{path}/deploy-docker.cfg'.format(path=path)

        if not os.path.isfile(self.path_deploy_cfg):
            print('\n!!!! File "deploy/deploy.cfg" not exists !!!!')
            print('Copy or check the file "deploy/deploy.cfg.example"\n')
            sys.exit(1)

        deploy_cfg = configparser.ConfigParser()
        deploy_cfg.read(self.path_deploy_cfg)

        self.mode = deploy_cfg['options']['mode']

        if self.mode == 'cloud':
            self.mode_cfg = configparser.ConfigParser()
            self.mode_cfg.read(self.path_deploy_cloud_cfg)
        elif self.mode == 'docker':
            self.mode_cfg = configparser.ConfigParser()
            self.mode_cfg.read(self.path_deploy_docker_cfg)
        else:
            msg = '\n!!!! Unsupported mode: {mode}. Supported modes: cloud, docker !!!!'.format(
                mode = deploy.cfg['options']['mode']
            )
            print(msg)
            sys.exit(1)

        self.common_cfg = configparser.ConfigParser()
        self.common_cfg.read(self.path_deploy_common_cfg)

        self.sys_user = self.mode_cfg['server.odoo']['sys_user']

        # Build System
        self.build_system = self.mode_cfg['server.odoo'].getboolean('build_system')
        self.build_dir = None
        self.set_build_dir()

        # Odoo root/build dir
        self.odoo_root_dir = self.mode_cfg['server.odoo']['odoo_root_dir']
        self.root_build_dir = None
        self.set_root_build_dir()
        self.make_root_build_dir()

        self.current_build_dir = None
        self.set_current_build_dir()

        # TODO improve setter
        self.supervisor = self.mode_cfg['server.odoo'].getboolean('supervisor')

        self.odoo_log_dir = '{root_build_dir}/var/log'.format(root_build_dir=self.root_build_dir)

        # Odoo Core
        self.odoo_build_dir = '{root_build_dir}/odoo'.format(root_build_dir=self.root_build_dir)
        self.odoo_git_url = self.common_cfg['odoo.core']['git_url']
        self.odoo_git_branch = self.common_cfg['odoo.core']['git_branch']

        # Odoo Enterprise
        self.with_enterprise = 'odoo.enterprise' in self.common_cfg.sections()
        if self.with_enterprise:
            self.enterprise_build_dir = '{root_build_dir}/enterprise'.format(root_build_dir=self.root_build_dir)
            self.enterprise_git_url = self.common_cfg['odoo.enterprise']['git_url']
            self.enterprise_git_branch = self.common_cfg['odoo.enterprise']['git_branch']

        # Odoo addons (custom, external etc)
        self.with_addons = 'odoo.addons' in self.common_cfg.sections()
        if self.with_addons:
            self.addons_build_dir = '{root_build_dir}/addons'.format(root_build_dir=self.root_build_dir)
            self.addons_git_url = self.common_cfg['odoo.addons']['git_url']
            self.addons_git_branch = self.common_cfg['odoo.addons']['git_branch']

    def set_build_dir(self):
        if self.build_system:
            self.build_dir = 'build.{uuid}'.format(uuid=str(uuid.uuid4()))

    def set_root_build_dir(self):
        if self.build_system and self.build_dir:
            self.root_build_dir = '{odoo_root_dir}/{build_dir}'.format(
                odoo_root_dir=self.odoo_root_dir,
                build_dir=self.build_dir)
        else:
            self.root_build_dir = self.odoo_root_dir

    def make_root_build_dir(self):
         subprocess.call(['mkdir', '-p', self.root_build_dir])

    def set_current_build_dir(self):
        if self.build_system:
            self.current_build_dir = '{odoo_root_dir}/current'.format(odoo_root_dir=self.odoo_root_dir)

    def odoo_core(self):
        print("\n==== Deploy: Odoo Core ====\n")
        print("(i) odoo_build_dir: %s" % self.odoo_build_dir)

        if self.mode == 'docker':
            if not os.path.exists(self.odoo_build_dir):
                print("\n!!!! Development/Docker ERROR !!!!")
                print("* odoo_build_dir is invalid: %s" % self.odoo_build_dir)
                print("* Check the local Docker volume /odoo/odoo\n")
                sys.exit(1)
        elif not os.path.exists(self.odoo_build_dir):
            print("\n* Git clone Odoo")
            Repo.clone_from(self.odoo_git_url , self.odoo_build_dir, branch=self.odoo_git_branch, single_branch=True)

        # pip install -Ur requirements.txt
        if os.path.exists(self.odoo_build_dir):
            print("\n* Install Python/pip Odoo requirements\n")
            filepath = '{path}/requirements.txt'.format(path=self.odoo_build_dir)
            subprocess.call(['pip', 'install', '-Ur', filepath])

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
                print("* Check the local Docker volume /odoo/enterprise\n")
        elif not os.path.exists(self.enterprise_build_dir):
            print("\n* Git clone Enterprise")
            Repo.clone_from(self.enterprise_git_url , self.enterprise_build_dir, branch=self.enterprise_git_branch, single_branch=True)

        # pip install -Ur requirements.txt
        if os.path.exists(self.enterprise_build_dir):
            print("\n* Find and install Python/pip Enteprise requirements\n")
            for root, dirs, files in os.walk(self.enterprise_build_dir):
                for fname in files:
                    if fname == 'requirements.txt':
                        filepath = os.path.join(root, file)
                        subprocess.call(['pip', 'install', '-Ur', filepath])

    def odoo_addons(self):
        if not self.with_addons:
            print("\n==== No Odoo addons (custom, external) ====")
            return # No pip install -r requirements

        print("\n==== Deploy: Odoo addons (custom, external) ====")
        print("(i) addons_build_dir: %s" % self.addons_build_dir)

        if self.mode == 'docker':
            if not os.path.exists(self.addons_build_dir):
                # TODO check whether empty, because Docker volumes already mount.
                print("\n!!!! Development/Docker ERROR !!!!")
                print("* addons_build_dir not exists: %s" % self.addons_build_dir)
                print("* Check the local Docker volume /odoo/addons\n")
        elif not os.path.exists(self.addons_build_dir):
            print("\n---- Git clone addons ----")
            Repo.clone_from(self.addons_git_url , self.addons_build_dir, branch=self.addons_git_branch, single_branch=True)

        # pip install -Ur requirements.txt
        if os.path.exists(self.addons_build_dir):
            print("\n* Find and install Python/pip addons requirements\n")
            for root, dirs, files in os.walk(self.addons_build_dir):
                for fname in files:
                    if fname == 'requirements.txt':
                        filepath = os.path.join(root, file)
                        subprocess.call(['pip', 'install', '-Ur', filepath])

    def build_odoo(self):
        # TODO async (concurrent clones)
        self.odoo_core()
        self.odoo_enterprise()
        self.odoo_addons()

    def prepare_build(self):
        print("\n---- Prepare build ----")

        subprocess.call(['mkdir', '-p', self.odoo_log_dir])
        odoo_server_log = '{log_dir}/odoo-server.log'.format(log_dir=self.odoo_log_dir)
        subprocess.call(['touch', odoo_server_log])

    def finish_build(self):
        user_grp = '{user}:'.format(user=self.sys_user)
        subprocess.call(['chown', '-R', user_grp, self.root_build_dir])

    def switch_current_build(self):
        # TODO symlink previous build
        # TODO check path exists ?
        if self.build_system and self.build_dir:
            print("\n==== Swich current build ====")
            print ('* %s -> %s' % (self.current_build_dir, self.build_dir))
            subprocess.call(['ln', '-sfn', self.build_dir, self.current_build_dir])

    # def remove_old_build_dir(self):
    #     # TODO remove old build dir(s)

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
        self.switch_current_build()
        self.finish_build()
        
        # chmod -R ugo+rx /usr/local/lib/python3.6/dist-packages/
        if self.supervisor:
            self.supervisor()
        
if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    deploy = Deploy(path)
    deploy.run()
