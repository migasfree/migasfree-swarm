import os
import jinja2

from jinja2 import Environment, FileSystemLoader


@jinja2.pass_context
def get_context(c):
    return c


def render(path_templates, template, context):
    context['TAG'] = os.getenv("TAG")
    context['DATASHARE_MOUNT_PATH'] = '/mnt/datashare'

    # https://docs.docker.com/reference/cli/docker/service/create/#create-services-using-templates
    context['NODE'] = '{{.Node.Hostname}}'
    context['SERVICE'] = '{{.Service.Name}}'
    context['TASK'] = '{{.Task.Name}}'

    env = Environment(loader=FileSystemLoader(path_templates))
    template = env.get_template(template)
    template.globals['context'] = get_context
    template.globals['callable'] = callable

    return template.render(**context)
