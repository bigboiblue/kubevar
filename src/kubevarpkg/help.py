build_help = """
--- Overview ---\n
Output kubernetes manifests (yaml) where all ${{ VARIABLES }} are converted into the values defined in file specified by PATH.\n
--- Conventions ---\n
It is convention for the file at PATH to take the format *.kubervar.yaml therefore there is no need to append ".kubevar.yaml" to the PATH if convention is followed.\n
If the file you are referencing is simply named "kubevar.yaml", then PATH only needs to specify the directory. Additionally, PATH does not need to be specified if you currently reside in the target directory\n
--- *.kubevar.yaml format ---\n
"""

