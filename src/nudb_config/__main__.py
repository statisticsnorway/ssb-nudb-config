"""Command-line interface."""

import click


@click.command()
@click.version_option()
def main() -> None:
    """Nudb_Config."""


if __name__ == "__main__":
    main(prog_name="nudb_config")  # pragma: no cover
