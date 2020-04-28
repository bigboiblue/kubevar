

import click

@click.group()
def cli():
    pass


@click.command(help="Help is to be added in the future")
@click.argument("PATH", required=False, default='.')
def build(path: str):
    from .operations.Builder import Builder
    builder = Builder()
    print(builder.build(path), flush=True)



#//TODO: add help msg
@click.command(help="Help is to be added in the future")
@click.argument("PATH", required=False, default='.')
@click.option("-o", "--output", help="Output built yaml to console", default=False, required=False, type=bool, is_flag=True)
def apply(path: str, output):
    import subprocess
    from .operations.Builder import Builder

    builder = Builder()
    yaml = builder.build(path)
    print("Configuration built, applying...")
    

    if output == True:
        print(yaml)

    # subprocess.call([f"printf({output})", "|", "kubectl", "apply" "-f=-"], stdout=subprocess.PIPE)
    command = "cat - | kubectl apply -f -"
    proc = subprocess.Popen(["/bin/bash", "-c", "--", command], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    proc.communicate(bytes(yaml, "utf-8"))
    stdout = proc.communicate()[0]
    print(stdout.decode("utf-8"))
    


def main():
    cli.add_command(build, name="build")
    cli.add_command(apply, name="apply")
    cli()

if __name__ == "__main__":
    main()