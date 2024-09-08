import os
import sys
import json
import importlib.util
import subprocess
import socket
from pathlib import Path
from importlib.machinery import SourceFileLoader

_PATH = "/stack"
_FILE_CLUSTER_VARS = os.path.join(_PATH, f"env.py")

def get_stacks():

    # SHARED DATA 
    if not os.path.exists("/mnt/cluster/datashares"):
        os.mkdir("/mnt/cluster/datashares")
    if not os.path.exists("/mnt/cluster/portainer"):
        os.mkdir("/mnt/cluster/portainer")

    path="/mnt/cluster/datashares"
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
        elif len(options)==0:
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
        self.context={}

        if not os.path.exists(_FILE_CLUSTER_VARS):
            with open(_FILE_CLUSTER_VARS,"w") as f:
                f.write("")

        self.module = import_source_file(Path(_FILE_CLUSTER_VARS))


        # Cluster context
        # ===============
        self.prompt("DATASHARE_FS", "local", ["local","nfs"])

        # nfs || s3 || local (datashare)
        # ==============================
        #self.default("DATASHARE_PLUGING","rexray/s3fs:0.11.4")
        #self.default("DATASHARE_SERVER","")  # Empty -> Internal s3/nfs
        #self.default("DATASHARE_FS","local") 
        if self.context["DATASHARE_FS"] == "local":
            self.default("DATASHARE_PATH",f"")
        elif self.context["DATASHARE_FS"] == "nfs":
            # NFS server Ip
            self.prompt("DATASHARE_SERVER", "x.x.x.x")  
            # Path in NFS server for cluster 
            self.prompt("DATASHARE_PATH",f"/exports/migasfree-swarm")
            # NFS Port
            self.default("DATASHARE_PORT","2049")
        elif self.context["DATASHARE_FS"] == "s3":
            self.default("DATASHARE_PATH",f"{self.context['FQDN']}")
            self.default("DATASHARE_PORT","9000")
        
        self.save()


    def load_stack(self, stack=""):

        self.prompt("STACK", stack)

        _PATH_STACK = f"/mnt/cluster/datashares/{self.context['STACK']}"
        if not os.path.exists(_PATH_STACK):
            os.mkdir(_PATH_STACK)

        _FILE_STACK_VARS = os.path.join(_PATH_STACK, "env.py")
        if not os.path.exists(_FILE_STACK_VARS):
            with open(_FILE_STACK_VARS,"w") as f:
                f.write("")

        self.module = import_source_file(Path(_FILE_STACK_VARS))


        # Minimal context
        # ===============
        self.prompt("FQDN", "migasfree.acme.com")
        self.default("TZ","Europe/Madrid")
        self.default("EMAIL","admin@domain.com")

        # Ports
        # =====
        self.default("PORT_HTTP","80")
        self.default("PORT_HTTPS","443")
        self.default("HTTPSMODE","manual")

        # TODO
        # ====
        self.default("SUPERADMIN_NAME","migasfree")

        # Redis (datastore)
        # =================
        self.default("REDIS_HOST","datastore")
        self.default("REDIS_PORT","6379")
        self.default("REDIS_DB","0")

        # Postgres (database)
        # ===================
        self.default("POSTGRES_CRON","00 00 * * *")
        self.default("POSTGRES_HOST","database")
        self.default("POSTGRES_PORT","5432")
        self.default("POSTGRES_DB","migasfree")



        # Mount point inside containers
        # =============================
        self.default("DATASHARE_MOUNT_PATH",f"/mnt/datashare")

        # PMS
        # ===
        #self.default("PMS_ENABLED","pms-apt,pms-yum,pms-pacman,pms-winget")
        self.default("PMS_ENABLED","pms-apt,pms-yum")
        self.default("REPLICAS_console","1")
        self.default("REPLICAS_core","1")
        self.default("REPLICAS_public","1")
        self.default("REPLICAS_worker","1")

    def environment(self):
        string = ""
        for key, value in self.context.items():
            string +=f"{key}='{value}'\n"
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

