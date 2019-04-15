# deploy-odoo

## Recommendations

### Git clone

Avoid clashed in Docker containers (naming) by cloning into a named
target.

`git clone <URL>/deploy-odoo.git <PROJECT-NAME>`

Example:

`git clone https://github.com/novacode-nl/deploy-odoo.git novacode`

### Branches

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

### Project Bootstrap

1. Fork this repo to `<PROJECT>-docker-odoo`
2. `git clone <PROJECT>-docker-odoo`
3. cd `<PROJECT>-docker-odoo`
4. Edit `docker-compose.yml`. Change (Odoo) ports mapping.
5. Edit `docker/db/Dockerfile`.
    - Change **PostreSQL** version.
6. Edit `docker/odoo/Dockerfile`
    - Change **Ubuntu** version
    - Add/change OS and Python packages
7. Copy `config.cfg.docker` to `config.cfg`. Change settings if needed.
8. Put **Odoo Core** into `<PROJECT>/odoo/odoo`
9. Put **Enterprise** (if) into `<PROJECT>/odoo/enterprise`
10. Put **Custom** (if) into `<PROJECT>/odoo/custom`

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