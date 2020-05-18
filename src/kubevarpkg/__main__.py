import click
from .operations import build, apply, create, delete
from . import token

@click.group()
def cli():
    pass


def main():
    cli.add_command(build, name="build")
    cli.add_command(apply, name="apply")
    cli.add_command(create, name="create")
    cli.add_command(delete, name="delete")
    cli()

if __name__ == "__main__":
    main()