import click
import os

class Builder:
    build_help = """
        --- Overview ---\n
        Output kubernetes manifests (yaml) where all ${{ VARIABLES }} are converted into the values defined in file specified by PATH.\n
        --- Conventions ---\n
        It is convention for the file at PATH to take the format *.kubervar.yaml therefore there is no need to append ".kubevar.yaml" to the PATH if convention is followed.\n
        If the file you are referencing is simply named "kubevar.yaml", then PATH only needs to specify the directory. Additionally, PATH does not need to be specified if you currently reside in the target directory\n
        --- *.kubevar.yaml format ---\n
    """

    def __init__(self):
        self.file = ""
    ###

    def checkPath(self, path: str):
        path = path.strip()
        if not os.path.exists(path):
            print("\033[1;31mERROR: \033[mThe PATH specified is not a file nor a directory!")
            exit(1)

        self.file = os.path.join(path, "kubevar.yaml") if os.path.isdir(path) else path
        if not os.path.isfile(self.file) or not self.file.endswith(".yaml"):
            print("\033[1;31mERROR: \033[mIncorrect path.")
            print(" * If you specified a \033[1;33mdirectory\033[m, no kubevar.yaml is present in that directory")
            print(" * If you specified a \033[1;33mfile\033[m, it is not a yaml file")
            exit(1)    
    ###
        

    def build(self, path: str):
        self.checkPath(path)
        
        contents = ""
        with open(self.file, mode='r') as file:
            contents = file.read()
        print(f"Your file is {self.file}. The contents is:\n{contents}")
    ###


###

@click.command(help=Builder.build_help)
@click.argument("PATH", required=False, default='.')
def build(path: str):
    builder = Builder()
    builder.build(path)
###