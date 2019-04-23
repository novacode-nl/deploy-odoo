#!/usr/bin/env python3

import configparser
import os
import subprocess
import sys

from deploy import Deploy


class StartOdoo:

    def __init__(self, argv=[]):
        self.argv = argv

        path = os.path.dirname(os.path.abspath(__file__))
        self.deploy = Deploy(path)

        self.odoo_bin_path = None
        self.set_odoo_bin_path()

        self.odoo_bin_options = None
        self.set_odoo_bin_options()

        self.odoo_bin = None
        self.set_odoo_bin()

    def set_odoo_bin_path(self):
        self.odoo_bin_path = '{root_build_dir}/odoo/odoo-bin'.format(
            root_build_dir=self.deploy.root_build_dir)

    def set_odoo_bin_options(self):
        """ odoo-bin command, with server specific configuration.
        Project specific settings e.g. `addons_path` should go into ~/.odoorc """
        
        options = self.argv
        for k, v in self.deploy.mode_cfg['odoo-bin'].items():
            option = '--{key} {val}'.format(key=k, val=v)
            options.append(option)
        self.odoo_bin_options = options

    def set_odoo_bin(self):
        if self.deploy.mode == 'docker':
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
