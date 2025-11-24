#!/usr/bin/python3

import os
import subprocess
from jinja2 import Template

# Configuration
FILECONFIG = '/etc/haproxy/haproxy.cfg'
FILECONFIG_TEMPLATE = '/etc/haproxy/haproxy.template'
with open(FILECONFIG_TEMPLATE, encoding='utf-8') as f:
    HAPROXY_TEMPLATE = f.read()

FQDN = os.environ['FQDN']
STACK = os.environ['STACK']
PORT_HTTPS = os.environ['PORT_HTTPS']
HTTPSMODE = os.environ['HTTPSMODE']
MTLS = os.environ['MTLS']
NETWORK_MNG = os.environ['NETWORK_MNG']

def userlist_stack() -> str:
    with open(f'/run/secrets/{STACK}_superadmin_name', 'r', encoding='utf-8') as f:
        username = f.read()
    with open(f'/run/secrets/{STACK}_superadmin_pass', 'r', encoding='utf-8') as f:
        password = f.read()

    result = subprocess.run(['mkpasswd', '-m', 'sha-512', password], capture_output=True, text=True, check=True)

    return f'    user {username} password {result.stdout}'


def config_haproxy():
    context = {
        'FQDN': FQDN,
        'STACK': STACK,
        'certbot': HTTPSMODE == 'auto',
        'PORT_HTTPS': PORT_HTTPS,
        'USERLIST_STACK': userlist_stack(),
        'NETWORK_MNG': NETWORK_MNG,
        'MTLS': MTLS == 'True',
    }

    payload = {'haproxy.cfg': Template(HAPROXY_TEMPLATE).render(context)}
    with open(FILECONFIG, 'w', encoding='utf-8') as f:
        f.write(payload['haproxy.cfg'])
        f.write('\n')


def render_error_pages():
    context = {'FQDN': FQDN}
    _path = '/etc/haproxy/errors-custom'
    _path_template = '/etc/haproxy/errors-custom/templates'
    for f_template in os.listdir(_path_template):
        _file = os.path.join(_path, os.path.basename(f_template))
        if _file.endswith('.http'):
            with open(os.path.join(_path_template, f_template), 'r', encoding='utf-8') as f:
                content = f.read()
            with open(_file, 'w', encoding='utf-8') as f:
                f.write(Template(content).render(context))
                f.write('\n')

render_error_pages()
config_haproxy()