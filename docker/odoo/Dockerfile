FROM ubuntu:18.04

RUN mkdir /root/deploy-odoo
COPY deploy /root/deploy-odoo/deploy

RUN apt-get -qq update && apt-get -qq install python3 python3-dev
RUN /root/deploy-odoo/deploy/install_deploy_dependencies.py
RUN /root/deploy-odoo/deploy/install_odoo_dependencies.py

# FIXME Crash on node-gyp. Needed for Odoo/Enterprise ?
# nodejs npm node-clean-css node-less
# RUN npm install -g less
# RUN npm install -g less-plugin-clean-css

# Maybe usermapping required?
# RUN useradd odoo
