import setuptools
import os

readme_path = os.path.abspath(os.path.join(__file__, '..', 'README.md'))

with open(readme_path, 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pytan',
    version='3.9.2',
    author='Greer Viau',
    author_email='gviau2@gmail.com',
    description='Python Settlers of Catan Implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/greerviau/Pytan',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=['networkx'],
)