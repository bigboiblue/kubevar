import click
from .operations import build, apply
from . import token

@click.group()
def cli():
    pass


def main():
    cli.add_command(build, name="build")
    cli.add_command(apply, name="apply")
    cli()

if __name__ == "__main__":
    main()