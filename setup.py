import setuptools
import os

readme_path = os.path.abspath(os.path.join(__file__, '..', 'README.md'))

with open(readme_path, 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pytan',
    version='0.0.1',
    packages=['pytan.core', 'pytan.ui'],
    package_path='pytan',
    author='Greer Viau',
    author_email='gviau2@gmail.com',
    description='Python Settlers of Catan Implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/greerviau/Pytan'
)