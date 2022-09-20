"""
SIMPLE CI: Dead simple CI/CD pipeline executor.
author: François Sevestre
email: francois.sevestre.35@gmail.com

This module containes multilines string variables used as template file creation.
"""

EXAMPLE_FILE_DATA = \
"""---
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
  script:
    - echo "This is the first job."

job2:
  inside_docker:
    image: ruby:2.7
    path: /tmp/
  script:
    - echo "This is the $MYVAR job."

job3:
  script:
    - echo "This is the $GLOBAL_VAR job, that will be executed after stage1 is completed."
"""

PRE_COMMIT_HOOK = \
"""
#!/bin/env bash

simpleci exec
"""

PRE_COMMIT_HOOK_SUDO = \
"""#!/bin/bash

simpleci exec --sudo
"""

DOCKER_ERROR_MESSAGE= \
"""User can't access Docker services.
Check if docker is installed and enabled.
If Docker requires sudo priviledges on your system,
use \"simpleci start --sudo\" and \"simpleci exec --sudo \".
"""
