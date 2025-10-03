#!/usr/bin/python3

import os
import json
import time
import socket
import subprocess
import fcntl
import select
import requests
import web
import dns.resolver
import html

from datetime import datetime
from web.httpserver import StaticMiddleware
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape
from collections import deque

FILECONFIG = '/etc/haproxy/haproxy.cfg'
FILECONFIG_TEMPLATE = '/etc/haproxy/haproxy.template'
with open(FILECONFIG_TEMPLATE, encoding='utf-8') as f:
    HAPROXY_TEMPLATE = f.read()

FQDN = os.environ['FQDN']
STACK = os.environ['STACK']
PORT_HTTP = os.environ['PORT_HTTP']
PORT_HTTPS = os.environ['PORT_HTTPS']
HTTPSMODE = os.environ['HTTPSMODE']
TAG = os.environ['TAG']
NETWORK_MNG = os.environ['NETWORK_MNG']

MESSAGES_LOG = deque(maxlen=500)

# Global Variable
# ===============
global_data = {
    'services': {},
    'message': '',
    'need_reload': True,
    'extensions': [],
    'ok': False,
    'now': datetime.now()
}


class icon:
    def GET(self):
        raise web.seeother(f'https://{os.environ["FQDN"]}/services-static/img/logo.svg')


class status:
    def GET(self):
        # param = web.input()
        return status_page(global_data)


class manifest:
    def GET(self):
        context = {}
        web.header('Content-Type', 'text/cache-manifest')
        template = """CACHE MANIFEST
/services/status
/services-static/*
/services/logs
        """
        return Template(template).render(context)


class logs:
    def GET(self):
        web.header('Content-Type', 'text/html; charset=utf-8')
        columns = ["text", "service", "node", "container", "time"]
        env = Environment(
            loader=FileSystemLoader('services-static/templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('logs.html')
        try:
            # Envía columns pero no registros, porque se cargarán por AJAX
            return template.render(columns=columns)
        except Exception as e:
            return f"<p>Error: {html.escape(str(e))}</p>"


class logs_json:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return json.dumps(list(MESSAGES_LOG))


class message:
    def GET(self):
        web.header('Content-Type', 'application/json')
        if int((datetime.now() - global_data['now']).total_seconds()) >= 1:
            global_data['now'] = datetime.now()

            pms = os.environ['PMS_ENABLED'].split(',')
            services = [
                'console',
                'core',
                'beat',
                'worker',
                'public',
                *pms,
                'database',
                'datastore',
                'database_console',
                'datastore_console',
                'datashare_console',
                'worker_console',
                'assistant',
                'proxy',
                'portainer',
                'certbot',
            ]

            if 'services' not in global_data:
                global_data['services'] = {}

            if 'last_message' not in global_data:
                global_data['last_message'] = ''

            missing = False
            message = False

            for _service in services:
                if f'{STACK}_{_service}' not in global_data['services']:
                    global_data['services'][f'{STACK}_{_service}'] = {
                        'message': '',
                        'node': '',
                        'container': '',
                        'missing': True,
                    }

                # missing
                nodes = len(get_nodes(_service))
                global_data['services'][f'{STACK}_{_service}']['missing'] = nodes < 1
                global_data['services'][f'{STACK}_{_service}']['nodes'] = nodes

                if global_data['services'][f'{STACK}_{_service}']['missing']:
                    global_data['need_reload'] = True
                    missing = True

                if global_data['services'][f'{STACK}_{_service}']['message']:
                    message = True

                global_data['ok'] = False
                if not message:
                    if missing:
                        global_data['need_reload'] = True
                    else:
                        if global_data['need_reload']:
                            global_data['need_reload'] = False
                        global_data['ok'] = True

        return json.dumps(
            {
                'last_message': global_data['last_message'],
                'services': global_data['services'],
                'ok': global_data['ok'],
                'stack': STACK,
                'tag': f'migasfree {TAG}',
            }
        )

    def POST(self):
        try:
            data = json.loads(web.data())
        except Exception:
            print('ERROR', web.data())
            data = {}
        data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        MESSAGES_LOG.append(data)
        ips = dns.resolver.resolve('tasks.proxy', 'A')
        for ip in ips:
            requests.post(f'http://{str(ip)}:8001/services/update_message', json=data)


class update_message:
    def POST(self):
        data = json.loads(web.data())
        make_global_data(data)


class reconfigure:
    def POST(self):
        data = {
            'text': 'reconfigure',
            'service': os.environ['SERVICE'],
            'node': os.environ['NODE'],
            'container': os.environ['HOSTNAME'],
        }

        make_global_data(data)
        config_haproxy()


def make_global_data(data):
    global_data['ok'] = False

    if 'service' in data:
        if data['service'] not in global_data['services']:
            global_data['services'][data['service']] = {'message': '', 'node': '', 'container': '', 'missing': True}

        if 'text' in data:
            global_data['services'][data['service']]['message'] = data['text']
            global_data['last_message'] = data['service']
        if 'node' in data:
            global_data['services'][data['service']]['node'] = data['node']
        if 'container' in data:
            global_data['services'][data['service']]['container'] = data['container']


def status_page(context):
    web.header('Content-Type', 'text/html; charset=utf-8')
    env = Environment(
        loader=FileSystemLoader('services-static/templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('status.html')
    try:
        return template.render(context)
    except Exception as e:
        return f"<p>Error: {html.escape(str(e))}</p>"


def notfound():
    raise NotFound()


class ServiceUnavailable(web.HTTPError):
    def __init__(self):
        status = '503 Service Unavailable'
        headers = {'Content-Type': 'text/html'}
        data = status_page(global_data)
        web.HTTPError.__init__(self, status, headers, data)


class NotFound(web.HTTPError):
    def __init__(self):
        status = '404 Not Found'
        headers = {'Content-Type': 'text/html'}
        data = status_page(global_data)
        web.HTTPError.__init__(self, status, headers, data)


class Forbidden(web.HTTPError):
    def __init__(self):
        status = '403 Forbidden'
        headers = {'Content-Type': 'text/html'}
        data = status_page(global_data)
        web.HTTPError.__init__(self, status, headers, data)


def execute(cmd, verbose=False, interactive=True):
    """
    (int, string, string) execute(
        string cmd,
        bool verbose=False,
        bool interactive=True
    )
    """
    _output_buffer = ''
    if verbose:
        print(cmd)

    if interactive:
        _process = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
    else:
        _process = subprocess.Popen(
            cmd, shell=True, executable='/bin/bash', stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        if verbose:
            fcntl.fcntl(
                _process.stdout.fileno(),
                fcntl.F_SETFL,
                fcntl.fcntl(_process.stdout.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
            )
            while _process.poll() is None:
                readx = select.select([_process.stdout.fileno()], [], [])[0]
                if readx:
                    chunk = _process.stdout.read()
                    if chunk and chunk != '\n':
                        print(chunk)
                    _output_buffer = '%s%s' % (_output_buffer, chunk)

    _output, _error = _process.communicate()
    if not interactive and _output_buffer:
        _output = _output_buffer

    return _process.returncode, _output, _error


def get_extensions():
    pms_enabled = os.environ['PMS_ENABLED']
    extensions = []
    _code, _out, _err = execute('curl -X GET core:8080/api/v1/public/pms/', interactive=False)
    if _code == 0:
        try:
            all_pms = json.loads(_out.decode('utf-8'))
        except Exception:
            return ''.join(set(extensions))
        for pms in all_pms:
            if f'pms-{pms}' in pms_enabled:
                for extension in all_pms[pms]['extensions']:
                    extensions.append(extension)

    return list(set(extensions))


class nginx_extensions:
    def GET(self):
        web.header('Content-Type', 'text/plain')
        template = """
            # External Deployments. Auto-generated from proxy (in services.py -> config_nginx)
            # ========================================================================
        {% for extension in extensions %}
            location ~* /src/?(.*){{extension}}$ {
                alias /var/migasfree/public/$1{{extension}};
                error_page 404 = @backend;
            }
        {% endfor %}
            # ========================================================================
        """

        if len(global_data['extensions']) > 0:
            return Template(template).render({'extensions': global_data['extensions']})
        else:
            return ''


class update_haproxy:
    def POST(self):
        try:
            data = json.loads(web.data())
        except Exception:
            print('ERROR', web.data())
            data = {}

        if 'haproxy.cfg' in data:
            with open(FILECONFIG, 'w', encoding='utf-8') as f:
                f.write(data['haproxy.cfg'])
                f.write('\n')
            reload_haproxy()

        time.sleep(1)
        _data = {
            'text': '',
            'service': os.environ['SERVICE'],
            'node': os.environ['NODE'],
            'container': os.environ['HOSTNAME'],
        }
        make_global_data(_data)


def config_haproxy():
    context = {
        'FQDN': FQDN,
        'STACK': STACK,
        'mf_public': get_nodes('public'),
        'mf_core': get_nodes('core'),
        'mf_console': get_nodes('console'),
        'mf_database': get_nodes('database'),
        'mf_datashare_console': get_nodes('datashare_console'),
        'mf_datastore_console': get_nodes('datastore_console'),
        'mf_database_console': get_nodes('database_console'),
        'mf_worker_console': get_nodes('worker_console'),
        'mf_assistant': get_nodes('assistant'),
        'mf_portainer_console': get_nodes('portainer'),
        'mf_certbot': get_nodes('certbot'),
        'PORT_HTTP': PORT_HTTP,
        'PORT_HTTPS': PORT_HTTPS,
        'certbot': HTTPSMODE == 'auto',
        'USERLIST_STACK': USERLIST_STACK,
        'USERLIST_CLUSTER': USERLIST_CLUSTER,
        'NETWORK_MNG': NETWORK_MNG,
    }

    if len(global_data['extensions']) == 0 and len(context['mf_core']) > 0:
        global_data['extensions'] = get_extensions()

    if len(global_data['extensions']) == 0:
        context['extensions'] = '.deb .rpm'
    else:
        context['extensions'] = '.' + ' .'.join(global_data['extensions'])

    # Sync configuration haproxy in all proxies.
    payload = {'haproxy.cfg': Template(HAPROXY_TEMPLATE).render(context)}
    if not os.path.exists(FILECONFIG):
        with open(FILECONFIG, 'w') as f:
            f.write(payload['haproxy.cfg'])
            f.write('\n')
    else:
        ips = dns.resolver.resolve('tasks.proxy', 'A')
        for ip in ips:
            requests.post(f'http://{str(ip)}:8001/services/update_haproxy', json=payload)


def reload_haproxy():
    _code, _out, _err = execute('/usr/bin/reload', interactive=False)


def get_nodes(service):
    nodes = []
    _code, _out, _err = execute(f"dig tasks.{service} | grep ^tasks.{service} | awk '{{print $5}}'", interactive=False)
    if _code == 0:
        for node in _out.decode('utf-8').replace('\n', ' ').split(' '):
            if node:
                nodes.append(node)

    return nodes


def ckeck_server(host: str, port: int):
    try:
        args = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    except Exception:
        return False

    for family, socktype, proto, canonname, sockaddr in args:
        s = socket.socket(family, socktype, proto)
        try:
            s.connect(sockaddr)
        except socket.error:
            return False
        else:
            s.close()
            return True


class servicesStaticMiddleware(StaticMiddleware):
    def __init__(self, app, prefix='/services-static/'):
        StaticMiddleware.__init__(self, app, prefix)


def render_error_pages():
    context = {'FQDN': os.environ['FQDN']}
    _PATH = '/etc/haproxy/errors-custom'
    _PATH_TEMPLATE = '/etc/haproxy/errors-custom/templates'
    for f_template in os.listdir(_PATH_TEMPLATE):
        _file = os.path.join(_PATH, os.path.basename(f_template))
        if _file.endswith('.http'):
            with open(os.path.join(_PATH_TEMPLATE, f_template), 'r', encoding='utf-8') as f:
                content = f.read()
            with open(_file, 'w', encoding='utf-8') as f:
                f.write(Template(content).render(context))
                f.write('\n')


def userlist_stack():
    with open(f'/run/secrets/{STACK}_superadmin_name', 'r', encoding='utf-8') as f:
        USERNAME = f.read()
    with open(f'/run/secrets/{STACK}_superadmin_pass', 'r', encoding='utf-8') as f:
        PASSWORD = f.read()
    _code, _out, _err = execute(f'mkpasswd -m sha-512 {PASSWORD}', interactive=False)
    return f'    user {USERNAME} password {_out.decode("utf-8")}'


def userlist_cluster():
    # swarm-credential
    with open('/run/secrets/swarm-credential', 'r', encoding='utf-8') as f:
        USERNAME, PASSWORD = f.read().split(':')
    _code, _out, _err = execute(f'mkpasswd -m sha-512 {PASSWORD}', interactive=False)
    return f'    user {USERNAME} password {_out.decode("utf-8")}'


if __name__ == '__main__':
    urls = (
        '/favicon.ico',
        'icon',
        '/services/status/?',
        'status',
        '/services/manifest',
        'manifest',
        '/services/message',
        'message',
        '/services/reconfigure',
        'reconfigure',
        '/services/update_haproxy',
        'update_haproxy',
        '/services/update_message',
        'update_message',
        '/services/nginx_extensions',
        'nginx_extensions',
        '/services/logs',
        'logs',
        '/services/logs/json',
        'logs_json'
    )

    global_data = {
        'services': {},
        'message': '',
        'need_reload': True,
        'extensions': [],
        'ok': False,
        'now': datetime.now(),
    }

    render_error_pages()

    USERLIST_CLUSTER = userlist_cluster()
    USERLIST_STACK = userlist_stack()
    config_haproxy()

    app = web.application(urls, globals(), autoreload=False)
    app.notfound = notfound
    app.run(servicesStaticMiddleware)
