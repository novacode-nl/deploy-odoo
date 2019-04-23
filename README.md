# deploy-odoo

A tool to deploy Odoo in *Docker* or *on-premise* on a Debian/Ubuntu server.

## Branches recommendation

It's strongly recommended to work with (Git) branches, to distinguish
deployment stages (development, staging, production).
So you can isolate settings and packages to install.

Example branches:

- `12.0` => production
- `12.0-staging` => staging
- `12.0-dev` => development

## Deploy - Docker

### Requirements

Install Docker by packagemanager

`apt-get install docker`

### Docker Compose

Install Docker Compose by Python pip. To get latest stable version.

`pip3 install docker-compose`

### Git clone

To avoid clashes in Docker containers (naming), clone into a named
target.

`git clone <URL>/deploy-odoo.git <PROJECT>`

Example:

`git clone https://github.com/novacode-nl/deploy-odoo.git novacode`

### Configuration

Make changes if needed.

- `docker-compose.yml`
  - Odoo ports mapping and such.

- `docker/db/Dockerfile`
  - **PostreSQL** version.

- `docker/odoo/Dockerfile`
  - **Ubuntu** version.

- `deploy/install_odoo_server.py`
  - Add/change OS and Python packages
**!! TODO shall be moved to `deploy.cfg` !!**

- Copy `deploy/deploy.cfg.example` to `deploy/deploy.cfg`.
  - Ensure: `mode = docker`

- Put **Odoo Core** into `<PROJECT>/odoo/odoo`
- Put **Enterprise** (if) into `<PROJECT>/odoo/enterprise`
- Put **Custom** (if) into `<PROJECT>/odoo/custom`

### Install (init)

`./init`

Installs the Docker containers with required packages (OS, Python etc).

### Deploy and start services (run)

`./run`

- Deploy Odoo Core by Git.
- Also deploy Enterprise and/or Custom if configured in `deploy/deploy-common.cfg` and 'deploy/deploy-docker.cfg`.
- Install Odoo/pip requirements.
- Create the Odoo start command by `deploy-docker.cfg` options.
- Start the Odoo server.

## Deploy - Cloud / on-premise

### Bootstrap (Git)

Recommendation is to create a directory, where the
deployment tool and Odoo shall be placed. E.g: `/opt/approot`.

```
mkdir /opt/approot
cd /opt/approot
```

```
git clone <URL>/deploy-odoo.git
```

Example:

```
git clone https://github.com/novacode-nl/deploy-odoo.git
```

Shall result in:

`/opt/approot/deploy-odoo`

Checkout (version) branch:

`git checkout <BRANCH>`

### Configuration

#### `deploy/deploy.cfg`

- Copy `deploy/deploy.cfg.example` to `deploy/deploy.cfg`.
- Ensure: `mode = cloud`

#### `deploy/deploy-cloud.cfg`

Edit `deploy/deploy-cloud.cfg`

Ensure the *db* credentials are set:
- `db_user =`
- `db_password =`

Optionally change to `build_system = True`\
For each `deploy.py` run, a build directory (UUID) shall be created.\
On success the build directory shall be set as the `current` by symlink.

### Install PostgreSQL server

If the PostgreSQL server is on the same host, it's that easy.

From `/opt/approot`

`./deploy-odoo/deploy/install_postgres_server.py`

### Install the Odoo Linux (Debian, Ubuntu) server

From `/opt/approot`

`./deploy-odoo/deploy/install_odoo_server.py`

Installs the required packages (OS, Python etc).

### Deploy/build Odoo

From `/opt/approot`

`./deploy-odoo/deploy/deploy.py`

- Deploy Odoo Core by Git.
- Also deploy Enterprise and/or addons (custom, external etc.), if configured in `deploy/deploy-common.cfg` and `deploy/deploy-cloud.cfg`.
- Install Odoo/pip requirements.
- Creates the Odoo start command by `deploy/deploy-cloud.cfg` options. (TODO: Supervisor control).

### Start/stop Odoo

Script `./deploy-odoo/deploy/start_odoo.py`

Manually add the Odoo start/stop script, e.g. to Supervisor.\
(TODO: Start the Odoo server managed by Supervisor)

## Wkhtmltopdf

In case of troubles (layout, styling), rename or remove the `report.url` System parameter.

## Python debugger (pdb)

The debugger is running inside the container, so we need to attach into the container to use it.

1. Find the container id using docker container ps and copy the first two or three letters of the container id column.
2. Use the command `docker attach CONTAINER_ID` to attach to the container.

Ensure following are set in `docker-compose.yml`:

```
stdin_open: true
tty: true
```

## (?) Filesystem mapping Docker Container => Host

Following on host:

- Edit: `/etc/services/daemon.json`
`{'userns-remap': 'bob'}`

Check uid/groupid user. Change to 1000000 (very big int).

- Edit: `/etc/subuid`
`bob:<UID>:1000000`

- Edit: `/etc/subgid`
bob:<GID>:1000000