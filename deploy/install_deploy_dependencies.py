#!/usr/bin/env python3

import configparser
import subprocess


class InstallDeployDependencies:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

    def run(self):
        print('\n==== Install Deploy Dependencies ====\n')
        print('* APT packages')
        command = 'apt-get -qq update && apt-get -qq upgrade && apt-get -qq install python3 python3-dev python3-pip git'
        apt_process = subprocess.Popen(command, shell=True)
        apt_process.wait()

        print('* pip3 packages')
        subprocess.call(['pip3', 'install', '-Uq', 'gitpython', 'num2words', 'ofxparse'])

if __name__ == '__main__':
    install = InstallDeployDependencies()
    install.run()
