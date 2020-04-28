

import click

@click.group()
def cli():
    pass


def get_globbed_paths(paths) -> list:
    from os import path
    from glob import glob

    paths = list(paths)
    if len(paths) == 0:
        paths = ('.',)
    
    temp_paths = paths
    paths = []
    for i, p in enumerate(temp_paths):
        # if path.isdir(str(p)):
        #     p = path.join(p, "kubevar.yaml")
        paths = [*paths, *glob(p, recursive=True)]
    return paths

"Paths to the .kubevar.yaml config files. Globs are allowed (so you can recursively apply)"
@click.command(help="Help is to be added in the future")
@click.argument("PATHS", required=False, nargs=-1)
def build(paths: list):
    
    paths = get_globbed_paths(paths)

    for p in paths:
        print(f"\n----\n\033[1;34mBuilding path: {p}\033[m\n----\n")
        from .operations.Builder import Builder
        builder = Builder()
        print(builder.build(str(p)), flush=True)



#//TODO: add help msg
"Paths to the .kubevar.yaml config files. Globs are allowed (so you can recursively apply)"
@click.command(help="Help is to be added in the future")
@click.argument("PATHS", required=False, nargs=-1)
@click.option("-o", "--output", help="Output built yaml to console", default=False, required=False, type=bool, is_flag=True)
def apply(paths: list, output: bool):
    import subprocess
    from .operations.Builder import Builder

    paths = get_globbed_paths(paths)

    for p in paths:
        builder = Builder() #//TODO: allow build to be called more than once on a single object (do cleanup)
        yaml = builder.build(p)
        if output == True:
            print(yaml)
        print(f"\n----\n\033[1;34mConfiguration built for {p}, applying...\033[m\n----\n")
        
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