#!/usr/bin/python3

import os
import web
import json
import time
import socket
import subprocess
import fcntl
import select
import requests
import dns.resolver

from web.httpserver import StaticMiddleware
from datetime import datetime
from jinja2 import Template

FILECONFIG = "/etc/haproxy/haproxy.cfg"
FILECONFIG_TEMPLATE = "/etc/haproxy/haproxy.template"
with open(FILECONFIG_TEMPLATE) as f:
    HAPROXY_TEMPLATE = f.read()

FQDN = os.environ['FQDN']
STACK = os.environ['STACK']
PORT_HTTP = os.environ['PORT_HTTP']
PORT_HTTPS = os.environ['PORT_HTTPS']
TAG = os.environ['TAG']
NETWORK_MNG = os.environ['NETWORK_MNG']


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
        raise web.seeother(
            f"https://{os.environ['FQDN']}/services-static/img/logo.svg"
        )


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
        """
        return Template(template).render(context)


class message:
    def GET(self):
        web.header('Content-Type', 'application/json')
        if int((datetime.now() - global_data['now']).total_seconds()) >= 1:
            global_data['now'] = datetime.now()

            pms = os.environ['PMS_ENABLED'].split(',')
            services = [
                'console',
                'core', 'beat', 'worker',
                'public',
                *pms,
                'database',
                'datastore',
                'database_console',
                'datastore_console',
                'datashare_console',
                'worker_console',
                'sql',
                'proxy',
                'portainer'
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
                global_data['services'][f'{STACK}_{_service}']['missing'] = (nodes < 1)
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
                            reload_haproxy()
                            global_data['need_reload'] = False
                        global_data['ok'] = True

        return json.dumps({
            'last_message': global_data['last_message'],
            'services': global_data['services'],
            'ok': global_data['ok'],
            'stack': STACK,
            'tag': f"migasfree {TAG}"
        })

    def POST(self):
        try:
            data = json.loads(web.data())
        except Exception:
            print("ERROR", web.data())
            data = {}
        ips = dns.resolver.resolve('tasks.proxy', 'A')
        for ip in ips:
            requests.post(f"http://{str(ip)}:8001/services/update_message", json=data)


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
            'container': os.environ['HOSTNAME']
        }

        make_global_data(data)
        config_haproxy()


def make_global_data(data):
    global_data['ok'] = False

    if 'service' in data:
        if data['service'] not in global_data['services']:
            global_data['services'][data['service']] = {
                'message': '',
                'node': '',
                'container': '',
                'missing': True
            }

        if 'text' in data:
            global_data['services'][data['service']]['message'] = data['text']
            global_data['last_message'] = data['service']
        if 'node' in data:
            global_data['services'][data['service']]['node'] = data['node']
        if 'container' in data:
            global_data['services'][data['service']]['container'] = data['container']


def status_page(context):
    template = """
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="user-scalable=no,initial-scale=1,maximum-scale=1,minimum-scale=1,width=device-width">

<style>
@font-face {
  font-family: 'Virgil';
  src: url('/services-static/fonts/Virgil.ttf') format('truetype');
}

.tooltip {
  position: relative;
  display: inline-block;
  border-bottom: 1px dotted black;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: #555;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 5px 0;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -60px;
  opacity: 0;
  transition: opacity 0.3s;
}

.tooltip .tooltiptext::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #555 transparent transparent transparent;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}

body {
  width: 100%;
  margin: 0 auto;
  font-family: 'Virgil', sans-serif;
  color: #ddd;
}
</style>

    <title>Status</title>

    <script src="/services-static/js/jquery-1.11.1.min.js" type="text/javascript"></script>

    <script type="text/javascript">
      function sleep(time) {
        return new Promise((resolve) => setTimeout(resolve, time));
      }

      let time = +new Date;
      let circles = "#proxy, #console, #core, #beat, #worker, #public, #pms, #database, #datastore, #datashare_console, #portainer";
      let links = "#proxy_link, #console_link, #public_link, #portainer_link, #database_console_link, #datastore_console_link, #datashare_console_link, #worker_console_link, #sql_link ,#core_link";
      let serv = ""

      $(document).ready(function () {
        setInterval(function () {
          let now = +new Date;
          let retraso = parseInt((now - time) / 1000);

          if (retraso > 1.5) {
            $("#message").text('disconnected');
            $("#message_serv").text('');
            $("#spoon").attr("href", "/services-static/img/spoon-disconnect.svg");
            $(circles).hide(200);
            $(links).hide(200);
            // $("#proxy").show(200);
            // $("#proxy").attr('fill', 'red');
            // $("#datashare").show(200);
            // $("#datashare").attr('fill', 'red');
            $("#start").hide(200);
            $("#start_link").hide(200);
          }

          $.ajax({
            url: '/services/message',
            success: function (data) {
              function missing_pms() {
                let _missing = false;
                let _message = false;
                let _service = "";
                let _nodes = 0;
                let _stack = data["stack"];

                for (const [key, value] of Object.entries(data['services'])) {
                  if (key.startsWith(_stack+'_pms-')) {
                    if (data['services'][key]["missing"]) {
                      _missing = true;
                      _service = key; // last service found in data
                    }
                    if (data['services'][key]["message"] != "" ) {
                      _message = true;
                      _service = key; // last service found in data
                    }
                    _nodes += data['services'][key]["nodes"]
                  }
                }
                if (_message) {
                  _missing = false;
                }

                if (_missing) {
                  $("#pms").attr('fill', 'red');
                  $("#pms").show(500);
                } else if (_message) {
                  $("#pms").attr('fill', 'orange');
                  $("#pms").hide(500);
                  $("#pms").show(500);
                } else {
                  $("#pms").attr('fill', '#a9dfbf'); // GREEN
                  $("#pms").show(500);
                }

                if (_nodes < 2) {
                  $("#nodes_pms").text("");
                } else {
                  $("#nodes_pms").text(_nodes);
                }

                return _service;
              }

              function missing_image(id) {
                let services = data["services"];
                let _missing = false;
                _missing = services[`${_stack}_${id}`]["missing"];
                if (_missing) {
                  document.getElementById(id+'_svg').style.display = 'none';
                } else {
                  document.getElementById(id+'_svg').style.display = 'block';
                }
              }


              function missing_console(id) {
                let services = data["services"];
                let _missing = false;
                _missing = services[`${_stack}_${id}`]["missing"];
                if (_missing) {
                  $(`#${id}_link`).hide(500);
                } else {
                  $(`#${id}_link`).show(500);
                }
              }

              function missing(id) {
                let services = data["services"];
                let _missing = false;
                let _message = "";
                let _nodes = 0;
                let _stack = data["stack"];
                _missing = services[`${_stack}_${id}`]["missing"];
                _message = services[`${_stack}_${id}`]["message"];
                _nodes = services[`${_stack}_${id}`]["nodes"];

                if (_missing) {
                  $(`#${id}`).attr('fill', 'red');
                  $(`#${id}`).show(500);
                  services[`${_stack}_${id}`]["message"]='missing';
                } else if (_message != "") {
                  $(`#${id}`).attr('fill', 'orange');
                  $(`#${id}`).hide(500);
                  $(`#${id}`).show(500);
                } else {
                  $(`#${id}`).attr('fill', '#a9dfbf'); // GREEN
                  $(`#${id}`).show(500);
                }

                if (_nodes < 2) {
                  $(`#nodes_${id}`).text("");
                } else {
                  $(`#nodes_${id}`).text(_nodes);
                }
              }

              time = +new Date;
              let _stack = data["stack"];
              missing("proxy");
              missing("console");
              missing("core");
              missing("beat");
              missing("worker");
              missing("public");
              missing("database");
              missing("datastore");
              missing("portainer");
              missing("datashare_console");

              missing_console("console");
              missing_console("portainer");
              missing_console("proxy");
              missing_console("public");
              missing_console("core");
              missing_console("database_console");
              missing_console("datastore_console");
              missing_console("datashare_console");
              missing_console("worker_console");

              missing_console("sql");
              missing_image("sql");

              let message_pms = missing_pms();
              let message_from = "";
              let message_serv = `${_stack}_${serv}`;

              if (serv == "") {
                message_serv = data['last_message'];
              } else if (serv == "datashare_console") {
                message_serv = `${_stack}_${serv}`;
              } //else if (serv == "proxy") {
              //  message_serv = `${_stack}_${serv}`;
              //}

              if (typeof(data) != "undefined") {
                if (serv == "pms" && message_pms != "") {
                  message = data['services'][message_pms]['message'];
                  message_serv = message_pms;
                  message_from = `${data['services'][message_pms]['container']}@${data['services'][message_pms]['node']}`;
                } else {
                  message = data['services'][message_serv]['message'];
                  message_from = `${data['services'][message_serv]['container']}@${data['services'][message_serv]['node']}`;
                }
              }

              let sprite;
              if (data['ok']) {
                sprite = parseInt((now / 1000) % 2);
                $("#spoon").attr("href", `/services-static/img/spoon-ok-${sprite}.svg`);
                $(".bocadillo").hide(200);
                $("#start").show(100);
                $("#start_link").show(100);

              } else if (message_serv in data['services'] && data['services'][message_serv]['missing']) {
                sprite = parseInt((now / 1000) % 2);
                $("#spoon").attr("href", `/services-static/img/spoon-starting-${sprite}.svg`);
                $(".bocadillo").show(200);
                $("#start").hide(200);
                $("#start_link").hide(200);
              } else {
                sprite = parseInt((now / 1000) % 3);
                $("#spoon").attr("href", `/services-static/img/spoon-checking-${sprite}.svg`);
                $(".bocadillo").show(200);
                $("#start").hide(200);
                $("#start_link").hide(200);

              }

              $("#stack").text(data['stack']);
              $("#tag").text(data['tag']);

              if (message == "") {
                $("#message").text('ready');
              } else {
                $("#message").text(message);
              }

              //$("#message_serv").text(message_serv);
              $("#message_serv").text(message_serv.split('_').slice(1).join('_'));

              $("#message_from").text(message_from);

              if (! location.pathname.startsWith('/services/status')) {
                if (data["ok"]) {
                  $(location).attr('href', location.href);
                }
              }
            },
          });
        }, 1000);
      });

      $(window).load(function () {
        // force download image
        $("#spoon-disconnected").attr('href', '/services-static/img/spoon-disconnect.svg');

        $("#start").hide(1)
        $("#start_link").hide(1)
        $("#start").attr('href', '/services-static/img/start.svg');

        $("#database-svg").attr('href', '/services-static/img/database.svg');

        $(circles).attr('fill', 'orange');
        $(circles).hide(200);
        $(links).hide(200);
        $("#spoon").hide(200);
        $("#spoon").attr('href', '/services-static/img/spoon-welcome.svg');
        $("#spoon").show(100);

        const welcome = ["salut!", "Hi!", "¡hola!", "¡hola, co!", "kaixo!", "ola!", "Hallo!"];
        $("#message").text(welcome[Math.floor(Math.random() * 7)]);

        // tooltips
        $("#proxy_link title").text(
          'proxy statistics:' + String.fromCharCode(10) + 'https://' + location.hostname + '/stats'
        );
        $("#console_link title").text('migasfree console:' + String.fromCharCode(10) +'https://'+location.hostname);
        $("#public_link title").text('public files:' + String.fromCharCode(10) +'https://'+location.hostname+'/pool/');
        $("#core_link title").text('API:' + String.fromCharCode(10) +'https://'+location.hostname+'/docs/');
        $("#portainer_link title").text(
          'portainer console:' + String.fromCharCode(10) + 'https://portainer.' + location.hostname
        );
        $("#database_console_link title").text(
          'database console:' + String.fromCharCode(10) + 'https://database.' + location.hostname
        );
        $("#datastore_console_link title").text(
          'datastore console:' + String.fromCharCode(10) + 'https://datastore.' + location.hostname
        );
        $("#datashare_console_link title").text(
          'datashare console:' + String.fromCharCode(10) + 'https://datashare.' + location.hostname
        );
        $("#worker_console_link title").text(
          'worker console:' + String.fromCharCode(10) + 'https://worker.' + location.hostname
        );

        $("#sql_link title").text(
          'AI SQL Interpreter:' + String.fromCharCode(10) + 'https://' + location.hostname + '/services/sql/'
        );

        $("#start_link title").text('migasfree console:' + String.fromCharCode(10) + 'https://' + location.hostname);
      });
    </script>
  </head>
  <body>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="5 60 180 70">
      <image href="/services-static/img/background.svg" x=30 y=50 height="100" width="100" />

      <-- force download file spoon-disconnect.svg-->
      <image id="spoon-disconnected" href="/" x=0 y=0 height="0" width="0" />

      <image id="spoon" href="/" x=155 y=120 height="10" width="10" />

      <switch>
        <foreignObject x="145" y="107.5" width="38" height="10" font-size="2" color="#999999">
          <p class="bocadillo" id="message_serv">  </p>
        </foreignObject>
      </switch>
      <switch>
        <foreignObject x="145" y="109" width="38" height="10" font-size="2.5" color="#999999">
          <p class="bocadillo" id="message"> one moment, please </p>
        </foreignObject>
      </switch>

      <switch>
        <foreignObject x="66" y="123" width="38" height="6">
          <div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; font-size: 3px; color: #999999;">
            <p id="stack"> </p>
          </div>
        </foreignObject>
      </switch>

      <switch>
        <foreignObject x="66" y="125" width="38" height="6" font-size="1.6" color="#999999">
          <div xmlns="http://www.w3.org/1999/xhtml" style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; font-size: 2px; color: #999999;">
            <p id="tag"> </p>
          </div>
        </foreignObject>
      </switch>

<!--
      <switch>
        <foreignObject x="145" y="106" width="38" height="4" font-size="1.2">
          <p class="bocadillo" id="message_from">  </p>
        </foreignObject>
      </switch>
-->

      <image id="start" href="/" x=142 y=89 height="16" width="16" onclick="$(location).attr('href','/');" />
      <circle id="start_link" cx="150" cy="97" r="6"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://' + location.hostname);"
      >
        <title> migasfree console </title>
      </circle>


      <circle id="proxy" cx="29" cy="103.5" r="1.5" fill="orange"
        onmouseenter="serv='proxy';"
        onmouseout="serv='';"
        onclick="$(location).attr('href', 'https://' + location.hostname + '/stats');"
        />
      <circle id="proxy_link" cx="36" cy="97" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://' + location.hostname + '/stats');"
      >
        <title> proxy statistics </title>
      </circle>


      <circle id="console" cx="48" cy="82" r="1.5" fill="orange"
        onmouseenter="serv='console';"
        onmouseout="serv='';"
        />
      <text id="nodes_console" x="48" y="82.5" text-anchor="middle" font-size="3"></text>
      <circle id="console_link" cx="55" cy="76" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://' + location.hostname);"
      >
        <title> migasfree console </title>
      </circle>

      <circle id="portainer" cx="48" cy="123" r="1.5" fill="orange"
        onmouseenter="serv='portainer';"
        onmouseout="serv='';"
        />
      <circle id="portainer_link" cx="55" cy="117" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://portainer.' + location.hostname);"
      >
        <title> portainer console </title>
      </circle>

      <circle id="core" cx="70" cy="112" r="1.5" fill="orange"
        onmouseenter="serv='core';"
        onmouseout="serv='';" />
      <text id="nodes_core" x="70" y="112.5" text-anchor="middle" font-size="3"></text>
      <circle id="core_link" cx="77.5" cy="105" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://' + location.hostname + '/docs/');"
      >
        <title> migasfree API </title>
      </circle>

      <circle id="beat" cx="90" cy="91" r="1.5" fill="orange"
        onmouseenter="serv='beat';"
        onmouseout="serv='';" />
      <text id="nodes_beat" x="90" y="91.5" text-anchor="middle" font-size="3"></text>

      <circle id="worker" cx="90" cy="112" r="1.5" fill="orange"
        onmouseenter="serv='worker';"
        onmouseout="serv='';" />
      <text id="nodes_worker" x="90" y="112.5" text-anchor="middle" font-size="3"></text>

      <circle id="worker_console_link" cx="97" cy="105" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://worker.' + location.hostname);" >
        <title> worker console </title>
      </circle>


      <image id="sql_svg" href="/services-static/img/sql.svg" x="129" y="69" width="13" height="13" style="display: none;" />

      <circle id="sql_link" cx="136" cy="76" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://' + location.hostname + '/services/sql/');" >
        <title> AI SQL Interpreter </title>
      </circle>


      <circle id="public" cx="48" cy="103.5" r="1.5" fill="orange"
        onmouseenter="serv='public';"
        onmouseout="serv='';"
      />
      <text id="nodes_public" x="48" y="104" text-anchor="middle" font-size="3"
        onclick="$(location).attr('href', 'https://' + location.hostname + '/public/');"
      ></text>
      <circle id="public_link" cx="55" cy="97" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://' + location.hostname + '/pool/');" >
        <title> public files </title>
      </circle>

      <circle id="pms" cx="70" cy="91" r="1.5" fill="orange"
        onmouseenter="serv='pms';"
        onmouseout="serv='';" />
      <text id="nodes_pms" x="70" y="91.5" text-anchor="middle" font-size="3"></text>

      <circle id="database" cx="114" cy="82" r="1.5" fill="orange"
        onmouseenter="serv='database';"
        onmouseout="serv='';"
        />
      <circle id="database_console_link" cx="121" cy="76" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://database.' + location.hostname);"
      >
        <title> database console </title>
      </circle>

      <circle id="datastore" cx="114" cy="103.5" r="1.5" fill="orange"
        onmouseenter="serv='datastore';"
        onmouseout="serv='';"
        onclick="$(location).attr('href', 'https://datastore.' + location.hostname);"
        />
      <circle id="datastore_console_link" cx="121" cy="97" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://datastore.' + location.hostname);"
      >
        <title> datastore console </title>
      </circle>

      <circle id="datashare_console" cx="114" cy="123" r="1.5" fill="orange"
        onmouseenter="serv='datashare_console';"
        onmouseout="serv='';"
        />
      <circle id="datashare_console_link" cx="121" cy="117" r="7"
        style="fill: green; fill-opacity: 0.07;"
        onclick="$(location).attr('href', 'https://datashare.' + location.hostname);"
      >
        <title> datashare console </title>
      </circle>
    </svg>
  </body>
</html>
"""
    return Template(template).render(context)


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
        _process = subprocess.Popen(
            cmd,
            shell=True,
            executable='/bin/bash'
        )
    else:
        _process = subprocess.Popen(
            cmd,
            shell=True,
            executable='/bin/bash',
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        if verbose:
            fcntl.fcntl(
                _process.stdout.fileno(),
                fcntl.F_SETFL,
                fcntl.fcntl(
                    _process.stdout.fileno(),
                    fcntl.F_GETFL
                ) | os.O_NONBLOCK,
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
    _code, _out, _err = execute(
        'curl -X GET core:8080/api/v1/public/pms/',
        interactive=False
    )
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
            return ""


class update_haproxy:
    def POST(self):
        try:
            data = json.loads(web.data())
        except Exception:
            print("ERROR", web.data())
            data = {}

        if "haproxy.cfg" in data:
            with open(FILECONFIG, 'w') as f:
                f.write(data["haproxy.cfg"])
                f.write('\n')
            reload_haproxy()

        # global_data = data["global_data"]

        time.sleep(1)
        _data = {
            'text': '',
            'service': os.environ['SERVICE'],
            'node': os.environ['NODE'],
            'container': os.environ['HOSTNAME']
        }
        make_global_data(_data)


def config_haproxy():
    context = {
        'FQDN': os.environ['FQDN'],
        'cerbot': os.environ['HTTPSMODE'] == 'auto',
        'mf_public': get_nodes('public'),
        'mf_core': get_nodes('core'),
        'mf_console': get_nodes('console'),
        'mf_database': get_nodes('database'),
        'mf_datashare_console': get_nodes('datashare_console'),
        'mf_datastore_console': get_nodes('datastore_console'),
        'mf_database_console': get_nodes('database_console'),
        'mf_worker_console': get_nodes('worker_console'),
        'mf_sql': get_nodes('sql'),
        'mf_portainer_console': get_nodes('portainer'),
        'PORT_HTTP': PORT_HTTP,
        'PORT_HTTPS': PORT_HTTPS,
        'USERLIST_STACK': USERLIST_STACK,
        'USERLIST_CLUSTER': USERLIST_CLUSTER,
        'NETWORK_MNG': NETWORK_MNG,
    }

    if len(global_data['extensions']) == 0 and len(context['mf_core']) > 0:
        global_data['extensions'] = get_extensions()
#        if len(global_data['extensions']) > 0:
#            config_nginx()

    if len(global_data['extensions']) == 0:
        context['extensions'] = '.deb .rpm'
    else:
        context['extensions'] = '.' + ' .'.join(global_data['extensions'])

    # Sync configuguration haproxy in all proxies.
    payload = {
        "haproxy.cfg": Template(HAPROXY_TEMPLATE).render(context)
    }
    if not os.path.exists(FILECONFIG):
        with open(FILECONFIG, 'w') as f:
            f.write(payload["haproxy.cfg"])
            f.write('\n')
    else:
        ips = dns.resolver.resolve('tasks.proxy', 'A')
        for ip in ips:
            requests.post(f"http://{str(ip)}:8001/services/update_haproxy", json=payload)

    """
    time.sleep(1)
    _data = {
        'text': '',
        'service': os.environ['SERVICE'],
        'node': os.environ['NODE'],
        'container': os.environ['HOSTNAME']
    }
    make_global_data(_data)
    """


def reload_haproxy():
    _code, _out, _err = execute("/usr/bin/reload", interactive=False)


def get_nodes(service):
    nodes = []
    _code, _out, _err = execute(
        f"dig tasks.{service} | grep ^tasks.{service} | awk '{{print $5}}'",
        interactive=False
    )
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
    context = {"FQDN": os.environ['FQDN']}
    _PATH = "/etc/haproxy/errors-custom"
    _PATH_TEMPLATE = "/etc/haproxy/errors-custom/templates"
    for f_template in os.listdir(_PATH_TEMPLATE):
        _file = os.path.join(_PATH, os.path.basename(f_template))
        if _file.endswith(".http"):
            with open(os.path.join(_PATH_TEMPLATE, f_template), 'r') as f:
                content = f.read()
            with open(_file, 'w') as f:
                f.write(Template(content).render(context))
                f.write('\n')


def userlist_stack():
    with open(f"/run/secrets/{STACK}_superadmin_name", "r") as f:
        USERNAME = f.read()
    with open(f"/run/secrets/{STACK}_superadmin_pass", "r") as f:
        PASSWORD = f.read()
    _code, _out, _err = execute(f'mkpasswd -m sha-512 {PASSWORD}', interactive=False)
    return f'    user {USERNAME} password {_out.decode("utf-8")}'


def userlist_cluster():
    # swarm-credential
    with open("/run/secrets/swarm-credential", "r") as f:
        USERNAME, PASSWORD = f.read().split(":")
    _code, _out, _err = execute(f'mkpasswd -m sha-512 {PASSWORD}', interactive=False)
    return f'    user {USERNAME} password {_out.decode("utf-8")}'


if __name__ == '__main__':
    urls = (
        '/favicon.ico', 'icon',
        '/services/status/?', 'status',
        '/services/manifest', 'manifest',
        '/services/message', 'message',
        '/services/reconfigure', 'reconfigure',
        '/services/update_haproxy', 'update_haproxy',
        '/services/update_message', 'update_message',
        '/services/nginx_extensions', 'nginx_extensions',
    )

    global_data = {
        'services': {},
        'message': '',
        'need_reload': True,
        'extensions': [],
        'ok': False,
        'now': datetime.now()
    }

    render_error_pages()

    USERLIST_CLUSTER = userlist_cluster()
    USERLIST_STACK = userlist_stack()
    config_haproxy()

    app = web.application(urls, globals(), autoreload=False)
    app.notfound = notfound
    app.run(servicesStaticMiddleware)
