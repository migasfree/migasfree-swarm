import os
import sys
import importlib.util
from pathlib import Path

_PATH = "/stack"
_FILE_CLUSTER_VARS = os.path.join(_PATH, "env.py")


def get_stacks():

    # SHARED DATA
    if not os.path.exists("/mnt/cluster/"):
        os.mkdir("/mnt/cluster/")
    if not os.path.exists("/mnt/cluster/datashares"):
        os.mkdir("/mnt/cluster/datashares")
    if not os.path.exists("/mnt/cluster/portainer"):
        os.mkdir("/mnt/cluster/portainer")

    path = "/mnt/cluster/datashares"
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
        self.load()

    def prompt(self, name, default, options=[]):
        if name in vars(self.module):
            self.context[name] = vars(self.module)[name]
        elif len(options) == 0:
            self.context[name] = input(f"{name} ({default}): ") or default
        else:
            self.context[name] = input(f"{name} ({' | '.join(options)}): ")
            if not self.context[name] in options:
                self.context[name] = ""
                self.prompt(name, default, options)

    def default(self, name, default):
        if name in vars(self.module):
            self.context[name] = vars(self.module)[name]
        else:
            self.context[name] = default

    def load(self):
        self.context = {}

        if not os.path.exists(_FILE_CLUSTER_VARS):
            with open(_FILE_CLUSTER_VARS, "w") as f:
                f.write("")

        self.module = import_source_file(Path(_FILE_CLUSTER_VARS))

        # Cluster context
        # ===============
        self.prompt("DATASHARE_FS", "local", ["local", "nfs"])

        # nfs || s3 || local (datashare)
        # ==============================
        # self.default("DATASHARE_PLUGING","rexray/s3fs:0.11.4")
        # self.default("DATASHARE_SERVER","")  # Empty -> Internal s3/nfs
        # self.default("DATASHARE_FS","local")
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

    def load_stack(self, stack=""):

        self.prompt("STACK", stack)

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

        # Ports
        # =====
        self.default("PORT_HTTP", "80")
        self.default("PORT_HTTPS", "443")
        self.default("HTTPSMODE", "manual")


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
        self.default("REPLICAS_console", "1")
        self.default("REPLICAS_core", "1")
        self.default("REPLICAS_public", "1")
        self.default("REPLICAS_worker", "1")
        self.default("REPLICAS_database_console", "1")
        self.default("REPLICAS_datastore_console", "1")
        self.default("REPLICAS_worker_console", "1")


        # BACKUP
        # ======
        self.default("BACKUP_CRON", "00 00 * * *")

        # ASSISTANT
        # =========
        self.default("GOOGLE_API_KEY", "")
        self.default("OLLAMA_BASE_URL", "")

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
            "HTTPSMODE": f"""# {line}
# HTTPSMODE
#     Sets the mode in which certificates are generated for the FQDN and its subdomains.
#     Accepted values are 'manual' or 'auto'.
#     In manual mode, self-signed certificates are created.
#     In auto mode, certificates are issued using the ACME HTTP-01 challenge provided by Let's Encrypt.
# {line}
""",

            "POSTGRES_HOST": f"""# {line}
# POSTGRES_HOST
#    Domain name or IP address of the PostgreSQL database server.
#    If you are not using an external database outside the Swarm cluster, this variable should be set to 'database'.
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
        string = """
# ENVIRONMENT
# To apply the changes to these variables, you need to run:
#     ./migasfree-swarm undeploy
#     ./migasfree-swarm deploy


"""

        for key, value in self.context.items():
            string += self.comment(key)
            string += f"{key}='{value}'\n\n\n"
        return string

    def save(self):
        with open(_FILE_CLUSTER_VARS, "w") as f:
            f.write(self.environment())

    def save_stack(self):
        _PATH_STACK = f"/mnt/cluster/datashares/{self.context['STACK']}"
        if not os.path.exists(_PATH_STACK):
            os.mkdir(_PATH_STACK)
        with open(os.path.join(_PATH_STACK, "env.py"), "w") as f:
            f.write(self.environment())
