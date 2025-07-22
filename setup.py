from setuptools import setup, find_packages

setup(
    name='pyfeetech',
    version='0.2.0',
    author='LR',
    author_email='luca.rand4zzo@gmail.com',
    description='A Python library to control Feetch servomotors',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/luca-randazzo/pyfeetech',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your library's dependencies here
        "pyserial>=3.0",
    ],
)