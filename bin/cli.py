import click
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

from bin.commands.server import server


@click.group()
def cli():
    pass


cli.add_command(server)

if __name__ == "__main__":
    cli()
