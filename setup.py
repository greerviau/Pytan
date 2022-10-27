import setuptools
import pkg_resources
import os

readme_path = os.path.abspath(os.path.join(__file__, '..', 'README.md'))

with open(readme_path, 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pytan',
    version='0.0.1',
    packages=['pytan.core', 'pytan.ui', 'pytan.log', 'pytan.gym'],
    package_path='pytan',
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    entry_points = {
        'console_scripts': ['pytan=pytan.cli:main'],
    },
    author='Greer Viau',
    author_email='gviau2@gmail.com',
    description='Python Settlers of Catan Implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/greerviau/Pytan'
)