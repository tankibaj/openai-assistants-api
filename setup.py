from setuptools import setup, find_packages

# Read the requirements.txt file and store each line as an element in a list.
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='openai-assistants-api',
    version='0.1.0',
    packages=find_packages(),
    install_requires=required,
)

# Install Your Package
# pip install -e .
