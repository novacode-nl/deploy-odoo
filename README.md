# deploy-odoo

## Branches recommendation

It's strongly recommended to work with (Git) branches, to distinguish
deployment stages (dev, staging, production).
So you can isolate things like `deploy/config.cfg` settings and
packages to install.

Example branches:

- `11.0`: Production
- `11.0-staging`: Staging
- `11.0-dev`: Development

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
**!! TODO shall be moved to `config.cfg` !!**

- Copy `config.cfg.docker` to `config.cfg`. Change settings if needed.

- Put **Odoo Core** into `<PROJECT>/odoo/odoo`
- Put **Enterprise** (if) into `<PROJECT>/odoo/enterprise`
- Put **Custom** (if) into `<PROJECT>/odoo/custom`

### Install (init)

`./init`

Installs the Docker containers with required packages (OS, Python etc).

### Deploy and start services (run)

`./run`

- Deploy Odoo Core by Git.
- Also deploy Enterprise and/or Custom if configured in `config.cfg.docker`.
- Install Odoo/pip requirements.
- Create the Odoo start command by `config.cfg.docker` options.
- Start the Odoo server.

## Deploy - Cloud / on-premise

### Requirement

It's a requirement to `git clone` under `/root` (home-dir of root user).

```
cd /root
git clone <URL>/deploy-odoo.git
```

Example:

```
cd /root
git clone https://github.com/novacode-nl/deploy-odoo.git
```

Shall result in:

`/root/deploy-odoo`

### Install PostgreSQL server

If the PostgreSQL server is on the same host, it's that easy.

`./deploy/install_postgres_server.py`

### Install the Odoo Linux (Debian, Ubuntu) server

`./deploy/install_odoo_server.py`

Installs the required packages (OS, Python etc).

### Deploy and start services

`./deploy/deploy.py`

- Deploy Odoo Core by Git.
- Also deploy Enterprise and/or Custom if configured in `config.cfg.docker`.
- Install Odoo/pip requirements.
- Create the Odoo start command by `config.cfg` options.
- Start the Odoo server managed by Supervisor

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