import click

def get_globbed_paths(paths) -> list:
    from glob import glob
    from .util.checking import err

    paths = list(paths)
    if len(paths) == 0:
        paths = ('.',)

    temp_paths = paths
    paths = []
    for i, p in enumerate(temp_paths):
        paths = [*paths, *glob(p, recursive=True)]
        if len(paths) == 0:
            err(f"{p} does not match any files or directories")
    return paths



@click.command(help="s to be added in the future")
@click.argument("PATHS", required=False, nargs=-1)
def build(paths: list):
    paths = get_globbed_paths(paths)

    for p in paths:
        from .builder import Builder
        builder = Builder()
        print(builder.build(str(p)), flush=True)



# //TODO: add help msg
"Paths to the .kubevar.yaml config files. Globs are allowed (so you can recursively apply)"
@click.command(help="Help is to be added in the future")
@click.argument("PATHS", required=False, nargs=-1)
@click.option("-o", "--output", help="Output built yaml to console", default=False, required=False, type=bool,
              is_flag=True)
def apply(paths: list, output: bool):
    pipe_to("kubectl apply -f -", paths, output)



# //TODO: add help msg
@click.command(help="Help is to be added in the future")
@click.argument("PATHS", required=False, nargs=-1)
@click.option("-o", "--output", help="Output built yaml to console", default=False, required=False, type=bool,
              is_flag=True)
def delete(paths: list, output: bool):
    pipe_to("kubectl delete -f -", paths, output)


# //TODO: add help msg
@click.command(help="Help is to be added in the future")
@click.argument("PATHS", required=False, nargs=-1)
@click.option("-o", "--output", help="Output built yaml to console", default=False, required=False, type=bool,
              is_flag=True)
def create(paths: list, output: bool):
    pipe_to("kubectl create -f -", paths, output)


def pipe_to(dest_command: str, paths: list, output: bool):
    paths = get_globbed_paths(paths)

    import subprocess
    from .builder import Builder

    for p in paths:
        builder = Builder()  # //TODO: allow build to be called more than once on a single object (do cleanup)
        yaml = builder.build(p)
        if output == True:
            print(yaml)
        print(f"\n----\n\033[1;34mConfiguration built for {p}, applying...\033[m\n----\n")

        command = f"cat - | {dest_command}"
        proc = subprocess.Popen(["/bin/bash", "-c", "--", command], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        # This has to be one step. Doing this in two steps (give stdin, get stdout) will cause subprocess to close prematurely
        stdout = proc.communicate(bytes(yaml, "utf-8"))[0].decode("utf-8")
        print(stdout)

