import codecs, os, re
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

here = os.path.abspath(os.path.dirname(__file__))

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='pony-express',
    version=find_version('ponyexpress', '__init__.py'),
    packages=['ponyexpress', ],
    include_package_data=True,
    license='MIT License',  # example license
    description='Python-based shipping package. Integrates with USPS, UPS, FedEx services.',
    long_description=README,
    url='https://github.com/miketheredherring/ponyexpress',
    author='Mike Hearing',
    author_email='miketheredherring@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
    ],
)