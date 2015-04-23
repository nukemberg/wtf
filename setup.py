from setuptools import find_packages, setup

def requirements_file(f):
      with open(f, 'r') as fs:
            return fs.read().splitlines()

setup(name='wtf',
      version='0.1.0',
      description='A first responder aid',
      packages=find_packages(exclude=['tests']),
      scripts=['bin/wtf'],
      data_files=["requirements.txt", "test_requirements.txt"],
      requires=requirements_file("requirements.txt"),
      tests_require=requirements_file("test_requirements.txt"))
