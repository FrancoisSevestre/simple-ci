# Simple-CI - Dead simple CI/CD pipeline executor.
Simple-CI is a CI/CD pipeline executor similar to gitlab CI/CD but in local.
It's triggered by a git hook after a commit and executes directives given by user in a simple script named .simple-ci.yml, placed at the root of the directory.
The artifacts (logs, compiled binairies, etc) are stored in a folder at the same level that the project folder named <project name>-simple-ci.

## Why simple-CI?
Automation pipelines like GitLab CI/CD are great tools for improving software development.
However, the syntax can be tidious and the user relies completely on gitlab and it's runners (even though you can create your own runners).
Furthermore, installing tools like gitlab or jenkins locally consumes a lot of resources and requires having them running in the background.

Simple-CI/CD solves these issues by providing a dead simple way for the user to run a CI/CD pipeline:
  1. Start simple-ci in your repository.
  2. Build your pipeline in the .simple-ci.yml file.
  3. Commit a change with git and let the pipeline execute itself.
  4. Profit!

Check the [Wiki](https://gitlab.com/FrancoisSevestre/simple-ci/-/wikis/home) for more in-depth documentation.

## Commands
- `simpleci start`: Create the git hook.
- `simpleci stop`: Delete git hook (The pipeline will not be executed).
- `simpleci init`: Create the git hook and the .simple-ci.yml file. 
- `simpleci exec`: Executes the pipeline.
- `simpleci clean`: Remove all artifacts files.
- `simpleci cron [time specification]`: Create a cron job.

## Simple example of .simple-ci.yml script
``` yaml
variables:
  GLOBAL_VAR: "last"

stages:
  - stage1
  - stage2

stage1:
  variables:
    MYVAR: "second"
  jobs:
    - job1
    - job2

stage2:
  inside_docker:
    image: ruby:2.7
    path: /tmp/
  jobs:
    - job3

job1:
  variables:
    fie_name: "new_file"
  artifacts:
    paths:
      - new_file
  script:
    - echo "This is the first job."
    - touch $file_name

job2:
  inside_docker:
    image: ubuntu
    path: /
  script:
    - echo "This is the $MYVAR job."

job3:
    script:
    - echo "This is the $GLOBAL_VAR job, that will be executed after stage1 is completed."
```
You will find the complete syntax documentation on the [Wiki](https://gitlab.com/FrancoisSevestre/simple-ci/-/wikis/Pipeline-syntax)

## Installation
Simple-CI is packaged in pypi.org under the name "simple-cicd" and can be installed with pip.
``` bash
pip install simple-cicd
# or 
python3 -m pip install simple-cicd
```

### Dependencies
- bash
- git
- [yaml](https://pyyaml.org/wiki/PyYAMLDocumentation) (python module)

## Contributing
Feel free to submit issues is you want to contribute.

## Roadmap
- [ ] Deliver basic features (0.1.0)
- [ ] Manage errors and logs in a clean way (0.1.1)
- [ ] Implement secrets (0.1.2)
- [ ] Implement rules and conditionals (0.2.0)
