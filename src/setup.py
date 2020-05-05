from setuptools import setup, find_packages
import os

script_dir = os.path.dirname(os.path.realpath(__file__))
requirements_path = os.path.normpath(os.path.join(script_dir, "../requirements.txt"))

requires = []
with open(requirements_path) as req:
    for line in req:
        requires.append(line.strip())
setup(
    name="kubevarpkg",
    packages=find_packages(script_dir),
    version="0.1",
    description="Bringing variable substitution to kubernetes! Both static and dynamic... Scrap Kustomize!",
    install_requires=requires
)
