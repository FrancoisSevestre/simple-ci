"""
This module containes multilines string variables used as template file creation.
"""

example_file_data = \
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

pre_commit_hook = \
"""
#!/bin/env bash

simpleci exec
"""
