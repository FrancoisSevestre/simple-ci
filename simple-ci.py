#! /bin/python3

############## Imports   ##############
import sys, os, subprocess
import yaml

############## Functions ##############
def get_root_dir():
    """ Get the root directory og the git repo.
    Returns:
        An absolute path.
    """
    return subprocess.getoutput("git rev-parse --show-toplevel")

def get_git_branch():
    """ Get the current git branch.
    Returns:
        A string, the name of the branch.
    """
    return subprocess.getoutput("git branch | grep '*' | awk '{print $2}'")

def manage_hook(git_root_dir, present=True):
    """ Creates or remove the hook from the .git/hook/ folder.

    Args:
        present (bool): True -> create, False -> remove
    Returns:
        A bool.
    Raises:
        FileExistsError: The file already exists, can't be created.
        FileNotFoundError: The file doesn't exists, can't delete.
    """

    # Git hook script
    post_commit_hook = """
    #!/bin/env bash

    simple-ci exec
    """
    # TODO: Check if file exists and is accessible
    # manage hook
    if present:
        with open(git_root_dir+"/.git/hooks/post-commit", 'w') as file:
            file.write(post_commit_hook)
        os.chmod(git_root_dir+"/.git/hooks/post-commit", 0o755)
        print("Git hook created. It will execute the pipeline after the next commit. \n Alternatively, you can trigger the pipeline with \'simple-ci exec\'")
    else:
        os.remove(git_root_dir+"/.git/hooks/post-commit")
    return True

def get_pipeline_data(git_root_dir):
    """ Get the pipeline data from file.
    Returns:
        A dict.
    """
    data = False
    with open(git_root_dir+"/.simple-ci.yml", 'r') as file:
        data = yaml.load(file, Loader=yaml.Loader)
    return data
    # TODO check if file exists (.simple-ci.yml or .simple-ci/*)

############## handle args ##############
args = sys.argv
script_name = args.pop(0) # Remove script name from the list
selector = args[0]

if selector == "start":
    # Create the hook file
    git_root_dir = get_root_dir()
    exit(manage_hook(git_root_dir))


elif selector == "stop":
    # Delete the hook file
    git_root_dir = get_root_dir()
    exit(manage_hook(git_root_dir, False))

elif selector == "init":
    # start + create the .simple-ci.yml file
    git_root_dir = get_root_dir()
    exit(manage_hook(git_root_dir))
    # TODO Add example file

elif selector == "exec":
    data = get_pipeline_data(get_root_dir())
    # stages?
    if stages:=data['stages']:
        # Run jobs concomitantly
        print("Stages found: {}".format(str(stages)))
        for stage in stages:
            if jobs:=data[stage]['jobs']:
                print("In stage: {}, the jobs are {}".format(str(stage), str(jobs)))
                for job in jobs:
                    if script:=data[job]['script']:
                        print("The script of the job {} is {}".format(str(job), str(script)))
                        # export variables
                        for command in script:
                            print(command)
                            print(subprocess.getoutput(command))
                    else:
                        print("No script found for the job") # TODO raise an error
            else:
                print("No jobs found fo this stage.") # TODO raise an error
    else:
        # jobs?
        if jobs:=data['jobs']:
            for job in jobs:
                print(job)
        else:
            # use script
            pass

elif selector == "cron":
    # Create cron job
    pass

elif selector == "test":
    with open(".simple-ci.yml", 'r') as file:
        data = yaml.load(file, Loader=yaml.Loader)
    a = data['stages']
    print(a)
