import os
import jinja2
from jinja2 import Environment, FileSystemLoader

@jinja2.pass_context
def get_context(c):
    return c


def render(path_templates, template, context):
    env = Environment(loader=FileSystemLoader(path_templates))
    template = env.get_template(template)
    template.globals['context'] = get_context
    template.globals['callable'] = callable
    return template.render(**context)
