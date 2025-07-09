from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="cpgateway",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    python_requires='>=3.8',
    author="Your Name",
    author_email="your.email@example.com",
    description="Paycrypt Gateway Service",
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/cpgateway",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
