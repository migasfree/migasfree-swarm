import os
import sys
import importlib.util

from pathlib import Path

_PATH = '/stack'
_FILE_CLUSTER_VARS = os.path.join(_PATH, 'env.py')


def get_stacks():
    # SHARED DATA
    base = Path('/mnt/cluster')
    (base / 'datashares').mkdir(parents=True, exist_ok=True)
    (base / 'portainer').mkdir(parents=True, exist_ok=True)

    path = base / 'datashares'

    return [d.name for d in Path(path).iterdir() if d.is_dir()]


def import_source_file(filename):
    modname = os.path.basename(filename)
    spec = importlib.util.spec_from_file_location(modname, filename)
    if spec is None:
        raise ImportError(f"Could not load spec for module '{modname}' at: {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as e:
        raise ImportError(f"{e.strerror}: {filename}") from e

    return module


class ContextLoader:
    def __init__(self):
        self.context = {}
        self.load()

    def _getval(self, name, default):
        if hasattr(self.module, name):
            return getattr(self.module, name)

        return default

    def prompt(self, name, default, options=[]):
        val = self._getval(name, None)
        if val is not None:
            self.context[name] = val
        elif not options:
            self.context[name] = input(f"{name} ({default}): ") or default
        else:
            while True:
                answer = input(f"{name} ({' | '.join(options)}) [{default}]: ") or default
                if answer in options:
                    self.context[name] = answer
                    break
                print(f"Value must be one of: {options}.")

    def default(self, name, default):
        val = self._getval(name, None)
        self.context[name] = val if val is not None else default

    def load(self):
        path = Path(_FILE_CLUSTER_VARS)
        if not path.exists():
            path.write_text('')

        self.module = import_source_file(path)

        # Cluster context
        # ===============
        self.prompt("DATASHARE_FS", "local", ["local", "nfs"])

        # nfs || s3 || local (datashare)
        # ==============================
        if self.context["DATASHARE_FS"] == "local":
            self.default("DATASHARE_PATH", "")
        elif self.context["DATASHARE_FS"] == "nfs":
            # NFS server Ip
            self.prompt("DATASHARE_SERVER", "x.x.x.x")
            # Path in NFS server for cluster
            self.prompt("DATASHARE_PATH", "/exports/migasfree-swarm")
            # NFS Port
            self.default("DATASHARE_PORT", "2049")
        elif self.context["DATASHARE_FS"] == "s3":
            self.default("DATASHARE_PATH", f"{self.context['FQDN']}")
            self.default("DATASHARE_PORT", "9000")

        self.save()

    def load_stack(self, stacks=""):
        self.context['STACK'] = os.getenv('STACK', '')
        if not self.context['STACK']:
            self.prompt("STACK", stacks)

        _PATH_STACK = f"/mnt/cluster/datashares/{self.context['STACK']}"
        if not os.path.exists(_PATH_STACK):
            os.mkdir(_PATH_STACK)

        _FILE_STACK_VARS = os.path.join(_PATH_STACK, "env.py")
        if not os.path.exists(_FILE_STACK_VARS):
            with open(_FILE_STACK_VARS, "w") as f:
                f.write("")

        self.module = import_source_file(Path(_FILE_STACK_VARS))

        # Minimal context
        # ===============
        self.prompt("FQDN", "migasfree.acme.com")
        self.default("TZ", "Europe/Madrid")

        # Network Management
        # ==================
        self.default("NETWORK_MNG", "0.0.0.0/0")

        # Exposed Ports
        # =============
        self.default("PORT_HTTP", "80")
        self.default("PORT_HTTPS", "443")
        self.default("PORT_DATABASE", "")

        # Server Certificate  mode
        # ========================
        self.default("HTTPSMODE", "manual")

        # mTLS
        # ====
        self.default("MTLS", "False")

        # Postgres (database)
        # ===================
        self.default("POSTGRES_HOST", "database")
        self.default("POSTGRES_PORT", "5432")
        self.default("POSTGRES_DB", "migasfree")
        self.default("POSTGRES_USER", "migasfree")

        # Redis (datastore)
        # =================
        self.default("REDIS_HOST", "datastore")
        self.default("REDIS_PORT", "6379")
        self.default("REDIS_DB", "0")

        # PMS
        # ===
        # self.default("PMS_ENABLED", "pms-apt,pms-yum,pms-pacman,pms-wpt")
        self.default("PMS_ENABLED", "pms-apt,pms-yum")

        for key in [
            "REPLICAS_console", "REPLICAS_core", "REPLICAS_public",
            "REPLICAS_worker", "REPLICAS_database_console",
            "REPLICAS_datastore_console", "REPLICAS_worker_console"
        ]:
            self.default(key, "1")

        # BACKUP
        # ======
        self.default("BACKUP_CRON", "00 00 * * *")

        # ASSISTANT
        # =========
        self.default("GOOGLE_API_KEY", "")
        self.default("OLLAMA_BASE_URL", "")

        self.save_stack()

    def comment(self, key):
        line = '-' * 120

        comments = {
            "DATASHARE_FS": f"""# {line}
# DATASHARE_FS
#     Volume type (local or nfs)
#     Use nfs when your Swarm cluster consists of more than one node.
# {line}
""",
            "DATASHARE_SERVER": f"""# {line}
# DATASHARE_SERVER
#     IP address or domain name of the NFS server
#     Required when DATASHARE_FS is set to nfs.
# {line}
""",
            "DATASHARE_PATH": f"""# {line}
# DATASHARE_PATH
#     Path on the NFS server that exports the data, default is /exports/migasfree-swarm
#     Required when DATASHARE_FS is set to nfs.
# {line}
""",
            "DATASHARE_PORT": f"""# {line}
# DATASHARE_PORT
#     NFS Port
#     Required when DATASHARE_FS is set to nfs.
# {line}
""",
            "STACK": f"""# {line}
# STACK
#     Stack name
#     Please do not modify this variable.
# {line}
""",
            "FQDN": f"""# {line}
# FQDN
#     Fully Qualified Domain Name for this stack
# {line}
""",
            "TZ": f"""# {line}
# TZ
#     Set the system time zone.
# {line}
""",
            "NETWORK_MNG": f"""# {line}
# NETWORK_MNG
#     Networks or hosts that are permitted to access the administrative consoles.
#     Default value: 0.0.0.0/0
#     You can add multiple IPs or networks separated by spaces
#     Example: '172.0.0.10/32 172.0.1/24'
# {line}
""",
            "PORT_HTTP": f"""# {line}
# PORT_HTTP
#     Port where the Swarm cluster serves HTTP.
# {line}
""",
            "PORT_HTTPS": f"""# {line}
# PORT_HTTPS
#     Port where the Swarm cluster serves HTTPS.
# {line}
""",

            "PORT_DATABASE": f"""# {line}
# PORT_DATABASE
#     Port used to expose PostgreSQL externally.
#     It's best practice to keep the PostgreSQL port closed to the outside world and
#     only accessible within trusted networks.
#     Default value: ''  # Port not exposed
# {line}
""",

            "HTTPSMODE": f"""# {line}
# HTTPSMODE
#     Sets the mode in which certificates are generated for the FQDN and its subdomains.
#     Accepted values are 'manual' or 'auto'.
#     In manual mode, self-signed certificates are created.
#     In auto mode, certificates are issued using the ACME HTTP-01 challenge provided by Let's Encrypt.
# {line}
""",

            "MTLS": f"""# {line}
# MTLS
#     This variable controls whether client certificate authentication is required in browsers
#     in addition to traditional username and password verification. When set to 'True',
#     mutual TLS (mTLS) is enforced, mandating clients to present valid X.509 certificates
#     during the TLS handshake. This mechanism significantly strengthens security by adding
#     an additional authentication layer based on cryptographic client identity verification,
#     beyond standard credential checks.
#     The default value is 'False', meaning client certificates are not required.
#     Related commands:
#         ./migasfree-swarm url-client-certificate
#         ./migasfree-swarm revoke-client-certificate
#         ./migasfree-swarm list-client-certificate
# {line}
""",


            "POSTGRES_HOST": f"""# {line}
# POSTGRES_HOST
#    Domain name or IP address of the PostgreSQL database server.
#    If you are not using an external database outside the Swarm cluster, set
#        POSTGRES_HOST='database' and
#        POSTGRES_PORT='5432' to connect internally.
#    This ensures the service uses the internal Swarm network for better security.
# {line}
""",

            "REDIS_HOST": f"""# {line}
# REDIS_HOST
#    Domain name or IP address of the Redis database server.
#    If you are not using an external Redis database outside the Swarm cluster,
#    this variable should be set to 'datastore'.
# {line}
""",

            "PMS_ENABLED": f"""# {line}
# PMS_ENABLED
#     Enabled Package Management Systems. They allow working with deb, rpm, etc.
#     The official PMS options you can set are: 'pms-apt', 'pms-yum', 'pms-pacman' and 'pms-wpt'
#     The default value is 'pms-apt,pms-yum'
# {line}
""",

            "REPLICAS_console": f"""# {line}
# REPLICAS_console
#     Sets the number of Migasfree administrative console instances that will run when deploying the stack.
#     The default value is '1'
# {line}
""",

            "REPLICAS_core": f"""# {line}
# REPLICAS_core
#     Sets the number of Migasfree core instances that will run when deploying the stack.
#     The default value is '1'
# {line}
""",

            "REPLICAS_public": f"""# {line}
# REPLICAS_public
#     Sets the number of public instances that will run when deploying the stack.
#     The default value is '1'
# {line}
""",

            "REPLICAS_worker": f"""# {line}
# REPLICAS_worker
#     Sets the number worker instances that will run when deploying the stack.
#     The default value is '1'
# {line}
""",

            "REPLICAS_database_console": f"""# {line}
# REPLICAS_database_console
#     Sets the number database_console instances that will run when deploying the stack.
#     The default value is '1' for development
#     Set 0 for production
# {line}
""",

            "REPLICAS_datastore_console": f"""# {line}
# REPLICAS_datastore_console
#     Sets the number datastore_console instances that will run when deploying the stack.
#     The default value is '1' for development
#     Set 0 for production
# {line}
""",

            "REPLICAS_worker_console": f"""# {line}
# REPLICAS_worker_console
#     Sets the number worker_console instances that will run when deploying the stack.
#     The default value is '1' for development
#     Set 0 for production
# {line}
""",

            "BACKUP_CRON": f"""# {line}
# BACKUP_CRON
#    Scheduling PostgreSQL and Redis Database Dumps.
#    Use crontab syntax (minute  hour  day_of_month  month  weekday)
#    By default, every day at midnight (12:00 AM): '00 00 * * *'
# {line}
""",

            "GOOGLE_API_KEY": f"""# {line}
# GOOGLE_API_KEY
#    Obtain a Google API Key to access Gemini and utilize the 'migasfree assistant'.
#    Visit https://aistudio.google.com/app/apikey to get yours.
# {line}
""",

            "OLLAMA_BASE_URL": f"""# {line}
# OLLAMA_BASE_URL
#     The base URL of the Ollama server that the assistant migasfree (Open-WebUI application) connects
#     to in order to interact with local LLM (Large Language Model) models. This URL typically points
#     to the location where Ollama is running, such as http://172.0.0.10:11434.
#     The default value is ''
# {line}
""",
        }

        if key in comments:
            return comments[key]

        return ""

    def environment(self):
        lines = [
            "# ENVIRONMENT\n"
            "# To apply changes to these variables, run:\n"
            "#     ./migasfree-swarm undeploy\n"
            "#     ./migasfree-swarm deploy\n\n"
        ]
        for k, v in self.context.items():
            lines.append(f"{self.comment(k)}{k}='{v}'\n\n")

        return ''.join(lines)

    def save(self):
        with open(_FILE_CLUSTER_VARS, "w") as f:
            f.write(self.environment())

    def save_stack(self):
        _PATH_STACK = f"/mnt/cluster/datashares/{self.context['STACK']}"
        if not os.path.exists(_PATH_STACK):
            os.mkdir(_PATH_STACK)

        with open(os.path.join(_PATH_STACK, "env.py"), "w") as f:
            f.write(self.environment())
