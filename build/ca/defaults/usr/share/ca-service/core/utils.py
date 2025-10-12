from fastapi import Request
from core.config import PATH_CERTIFICATES
import re


def grep(file, pattern):
    regex = re.compile(pattern)
    with open(file, "r") as f:
        for line in f:
            if regex.search(line):
                return line.strip()


def get_variable(file, variable):
    line = grep(file, r"^" + variable + r"\s*=")
    if line:
        _, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        return value
    else:
        return ""


def get_host(stack) -> str:
    fqdn = get_fqdn(stack)
    port = get_variable( str(PATH_CERTIFICATES/stack/"env.py"), "PORT_HTTPS")
    if port == "443":
        return fqdn
    return f"{fqdn}:{port}"


def get_fqdn(stack) -> str:
    return get_variable( str(PATH_CERTIFICATES/stack/"env.py"), "FQDN")

