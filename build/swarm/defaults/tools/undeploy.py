import subprocess

from context import ContextLoader, get_stacks


def remove_stacks(stack_names):
    for stack_name in stack_names:
        try:
            subprocess.run(['docker', 'stack', 'rm', stack_name], check=True)
            print(f"Stack '{stack_name}' removed successfully.")
        except Exception as e:
            print(f"Unexpected error when attempting to remove the stack '{stack_name}': {e}")


# PROGRAM
# =======

cl = ContextLoader()
CONTEXT = cl.context
cl.save()

cl.load_stack(" |".join(get_stacks()))
CONTEXT = cl.context

remove_stacks([CONTEXT['STACK']])
