import subprocess

import click

from eightpack.magic import do_imports


@click.group()
def cli():
    pass


@cli.command()
def dev_db():
    """
    Launches the development pgsql DB (long process). Requires Docker.
    """

    subprocess.run(["docker", "volume", "create", "8pack-postgres"])
    subprocess.run(
        [
            "docker",
            "run",
            "-p",
            "127.0.0.1:5432:5432",
            "-e",
            "POSTGRES_USER=user",
            "-e",
            "POSTGRES_PASSWORD=password",
            "-e",
            "POSTGRES_DB=dev",
            "-v",
            "8pack-postgres:/var/lib/postgresql/data",
            "postgres",
        ]
    )


@cli.command()
@click.argument("gzip_file", default="../draft_data_public.MKM.PremierDraft.csv.gz")
@click.argument("db_url", default="postgresql+psycopg2://user:password@localhost/dev")
def import_drafts(gzip_file, db_url):
    do_imports(db_url, gzip_file)


if __name__ == "__main__":
    cli()
