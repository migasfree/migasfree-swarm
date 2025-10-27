from context import ContextLoader, get_stacks


def main():
    # Cluster Context
    cl = ContextLoader()
    cl.save()

    cl.load_stack(" | ".join(get_stacks()))
    cl.save_stack()


if __name__ == '__main__':
    main()
