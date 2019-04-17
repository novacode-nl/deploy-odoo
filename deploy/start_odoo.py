#!/usr/bin/env python3

import configparser
import os
import subprocess
import sys


class StartOdoo:

    def __init__(self, argv=[]):

        self.argv = argv

        # TODO Somehow DRY from the Deploy object.
        # Change needs to be tested in both modes: docker, cloud.
        if not os.path.isfile('deploy/deploy.cfg'):
            print('\n!!!! File "deploy/config.cfg" not exists !!!!')
            print('Copy or check the file "deploy/config.cfg.example"')
            sys.exit(1)

        deploy_cfg = configparser.ConfigParser()
        deploy_cfg.read('deploy/deploy.cfg')

        self.mode = deploy_cfg['options']['mode']

        if self.mode == 'cloud':
            self.config = configparser.ConfigParser()
            self.config.read('deploy/deploy-cloud.cfg')
        elif self.mode == 'docker':
            self.config = configparser.ConfigParser()
            self.config.read('deploy/deploy-docker.cfg')
        else:
            msg = 'n!!!! Unsupported mode: {mode}. Supported modes: cloud, docker !!!!'.format(
                mode = deploy.cfg['options']['mode']
            )
            print(msg)
            sys.exit(1)

        self.odoo_root = None
        self.set_odoo_root()

        self.odoo_bin_path = None
        self.set_odoo_bin_path()

        self.odoo_bin_options = None
        self.set_odoo_bin_options()

        self.odoo_bin = None
        self.set_odoo_bin()

    def set_odoo_root(self):
        self.odoo_root = self.config['server.odoo']['odoo_root']

    def set_odoo_bin_path(self):
        self.odoo_bin_path = '{odoo_root}/odoo/odoo-bin'.format(odoo_root=self.odoo_root)

    def set_odoo_bin_options(self):
        """ odoo-bin command, with server specific configuration.
        Project specific settings e.g. `addons_path` should go into ~/.odoorc """
        
        options = self.argv
        for k, v in self.config['odoo-bin'].items():
            option = '--{key} {val}'.format(key=k, val=v)
            options.append(option)
        self.odoo_bin_options = options

    def set_odoo_bin(self):
        if self.mode == 'docker':
            self.odoo_bin_options.append('-s')
        options = ' '.join(self.odoo_bin_options)
        self.odoo_bin = '{odoo_bin_path} {options}'.format(
            odoo_bin_path=self.odoo_bin_path,
            options=options)

    def run(self):
        print('Starting Odoo... %s' % self.odoo_bin)
        subprocess.run(self.odoo_bin, shell=True)
        
if __name__ == '__main__':
    argv = sys.argv[1:]
    start_odoo = StartOdoo(argv)
    start_odoo.run()
