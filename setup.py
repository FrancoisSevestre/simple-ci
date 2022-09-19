from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    readme = file.read()

setup(
    name='simple_cicd',
    version='0.0.8',    
    description='Dead simple CI/CD pipeline executor',
    url='https://gitlab.com/FrancoisSevestre/simple-ci',
    author='François Sevestre',
    author_email='francois.sevestre.35@gmail.com',
    license='GPLv3',
    long_description_content_type="text/markdown",
    long_description=readme,
    packages=find_packages(),
    # py_modules=['simple_cicd.lib'],
    install_requires=['pyyaml'],

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'console_scripts': [
            'simpleci = simple_cicd.simple_cicd:main'
            ]
        },
)
