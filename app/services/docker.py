import docker
from typing import Dict, List
from docker.types import Mount
from app.schemas.app import Environment, Port, Volume, Ingress, App

#client = docker.DockerClient(base_url='unix://var/run/docker.sock')
client = docker.from_env()
namespace = 'mblocks'

try:
    client.networks.get(namespace)
except docker.errors.NotFound:
    client.api.create_network(namespace)


def generate_volumes(volumes: List[Volume]):
    result = []
    for volume in volumes:
        result.append(Mount(target=volume.mount_path,
                      source=volume.host_path, type="bind"))
    return result


def generate_commands(commands: List[str]):
    return commands


def generate_environments(envs: List[Environment]):
    result = {}
    for env in envs:
        result[env.name] = env.value
    return result


def generate_ports(ports: List[Port]):
    result = {}
    for port in ports:
        result[port.container_port] = port.host_port
    return result


def generate_host_config(*, ports: Dict[str, str], volumes: Dict[str, str]):
    return client.api.create_host_config(port_bindings=generate_ports(ports), mounts=generate_volumes(volumes))


def generate_labels(ingress: List[Ingress], prefix: str):
    result = {}
    for item in ingress:
        result['traefik.enable'] = "true"
        rule = []
        name = '{}-{}'.format(prefix, item.name)
        if item.domain:
            rule.append('Host(`{}`)'.format(item.domain))
        if item.path:
            rule.append('PathPrefix(`{}`)'.format(item.path))
        result['traefik.http.routers.{}.rule'.format(name)] = ' && '.join(rule)
        result['traefik.http.routers.{}.entrypoints'.format(name)] = "web"
        result['traefik.http.routers.{}.service'.format(name)] = name
        result['traefik.http.services.{}.loadbalancer.server.port'.format(
            name)] = '{}'.format(item.target.port)
        result['traefik.http.middlewares.{}.stripprefix.prefixes'.format(
            name)] = item.path
        result['traefik.http.routers.{}.middlewares'.format(
            name)] = '{}@docker'.format(name)
    return result


def get_container(*, name=None, image=None):
    if name:
        try:
            return client.containers.get(name)
        except docker.errors.NotFound:
            return None
    elif image:
        find_containers = client.containers.list(
            filters={'ancestor': image, 'status': 'running'})
        if len(find_containers) == 0:
            return None
        return find_containers[0]
    return None


def query_container(*, name: str = ''):
    result = {}
    for item in client.containers.list(filters={'name': '{}-{}'.format(namespace, name)}):
        result[item.name[8:]] = {
            'id': item.id,
            'short_id': item.short_id,
            'name': item.name,
            'status': item.status,
            'ip': item.attrs['NetworkSettings']['Networks'][namespace]['IPAddress'],
        }
        # Ports
        # item.attrs['HostConfig']['PortBindings']
        # Mounts
        # item.attrs['Mounts']
    return result


def create_container(app: App, network: str, parent: str = None):
    if hasattr(app, 'depends'):
        for depend in app.depends:
            create_container(app=depend, network=network, parent=app.name)
    settings = {
        'environment': generate_environments(app.environment),
        'command': generate_commands(app.command),
        'host_config': generate_host_config(ports=app.ports, volumes=app.volumes),
        'ports': list(generate_ports(app.ports).keys()),
        'labels': generate_labels(app.ingress, '{}-{}'.format(parent, app.name) if parent else app.name),
        'networking_config': client.api.create_networking_config({network: client.api.create_endpoint_config(aliases=get_container_aliases(app_name=app.name, parent=app.parent))}),
    }
    container_name = get_container_name(app_name=app.name, parent=parent, version=app.version)
    container = get_container(name=container_name)
    if container is None:
        client.api.create_container(
            app.image, name=container_name, detach=True, **settings)
    client.api.start(container_name)
    return get_container(name=container_name)


def remove_container(filters):
    for item in client.containers.list(all=True, filters=filters):
        item.remove(force=True)


def update_app(app: App, parent: str):
    """
    disable change app.name to protect the container name
    """
    # update a container only
    fix = {k: getattr(app, k) for k in app.__table__.columns.keys()}
    exists_host_ports = len(
        [item.get('host_port') != None for item in app.ports])
    # remove container first then create new one if used host ports
    container_name = get_container_name(app_name=app.name, parent=parent)
    if exists_host_ports:
        remove_container(filters={'name': container_name})
        create_container(App(**fix, depends=[]),
                         network=namespace, parent=parent)
    else:
        created_container = create_container(App(**fix, depends=[]),
                                             network=namespace, parent=parent)
        remove_container(
            filters={'name': container_name, 'before': created_container.id})


def get_image(name):
    try:
        return client.images.get(name)
    except docker.errors.ImageNotFound:
        for line in client.api.pull(name, stream=True, decode=True):
            print(line)
        return client.images.get(name)


def deploy_app(app):
    """
    convert sqlalchemy object app to schema App,
    app.depends not declared in sqlalchemy models and ingress is named as _ingress in sqlalchemy models
    I have't find better method to do this, so just below code
    """
    fix = {k: getattr(app, k) for k in app.__table__.columns.keys()}
    get_image(app.image)
    for depend in app.depends:
        get_image(depend.image)
    create_container(App(**fix, depends=app.depends), network=namespace)


def remove_app(app: App, parent: str):
    container_name = get_container_name(app_name=app.name, parent=parent)
    remove_container(filters={'name': container_name})


def rename_container(container_id: str, name: str) -> bool:
    container = get_container(name=container_id)
    if container:
        container.rename(name)
        return True
    return False


def get_container_name(*, app_name, parent = None, version = None):
    container_name = '{}-{}-{}'.format(namespace, parent,
                                       app_name) if parent else '{}-{}'.format(namespace, app_name)
    if version:
        return '{}-{}'.format(container_name, version)
    return container_name

def get_container_aliases(*, app_name, parent = None):
    if parent:
        return ['{}.{}.{}'.format(app_name, parent, namespace)]
    return ['{}.{}'.format(app_name, namespace)]
