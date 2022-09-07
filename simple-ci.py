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

def log(line, color=False):
    # TODO insert timestamp
    with open("simple.log", 'a') as log_file:
        log_file.write(line+"\n")
    if color:
        print("\033[32m"+line+"\033[0m")
    else:
        print(line)

def exec_script_command(command, env):
    """ 
    Args:
        command (str)
        env (dict)
    """
    env_cmd = "true"

    for var_key in env:                                                 # Add env variables declaration
        env_cmd = env_cmd+" && "+var_key+"=\""+str(env[var_key])+"\""

    passed_command = "bash -c \'"+env_cmd+" && "+command+"\'"           # Assemble final command
    log(str(subprocess.getoutput(passed_command)))                      # Exec and log

############## Main ##############
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

elif selector == "exec":                        # Execution of the .simple-ci.yml script

    ### Global scope ###
    data = get_pipeline_data(get_root_dir())        # Collect data from script
    
    # Variables
    if 'variables' in data:                         # if user declared variables in global scope
        global_env = data['variables']
    else:
        global_env = {}
    
    # Inside docker                                 # if user declared a docker option in the global scope
    # TODO

    # stages
    if 'stages' in data:                            # if user declared stages in global scope
        for stage in data['stages']:
            log("###### Stage \'" + str(stage) + "\' ######", True)

            ### Stage scope ###
            stage = data[stage]                     # get data from stage

            # variables
            if 'variables' in stage:                # if user declared variables in the stage scope
                stage_env = global_env | stage['variables'] # merge dicts with putative overwrite of global values
            else:
                stage_env = global_env

            # Inside docker                         # if user declared a docker option in the stage scope
            # TODO

            # Jobs
            if 'jobs' in stage:                     # Check if user declared jobs in this stage
                for job in stage['jobs']:
                    log("#### Job \'" + str(job) + "\' ####", True)

                    ### Job scope ###
                    job = data[job]                 # get data from job

                    # variables
                    if 'variables' in job:          # if user declared variables in the job scope
                        job_env = stage_env | job['variables']
                    else:
                        job_env = stage_env

                    # Inside docker                 # if user declared a docker option in the job scope
                    # TODO

                    # Script
                    if 'script' in job:             # Check if user defined script in this job
                        script = job['script']
                        for command in script:
                            log("## > " + str(command), True)
                            exec_script_command(command, job_env)
                    else:
                        print("No script found for the job") # TODO raise an error
            else:
                print("No jobs found fo this stage.") # TODO raise an error

    # Jobs
    else:
        if 'jobs' in data:                          # if user declared jobs in global scope
            for job in data['jobs']:
                log("#### Job \'" + str(job) + "\' ####", True)
                
                ### Job scope ###
                job = data[job]

                # variables                         # if user declared variables in the job scope
                if 'variables' in job:
                    job_env = global_env | job['variables']
                else:
                    job_env = global_env
 
                # Inside docker                      # if user declared a docker option in the job scope
                # TODO
 
                # Script
                if 'script' in job:                  # Check if user defined script in this job
                    script = job['script']
                    for command in script:
                        log("## > " + str(command), True)
                        exec_script_command(command, job_env)
                else:
                    print("No script found for the job") # TODO raise an error

    # Script
        else:
            if 'script' in data:                     # Check if user defined script in the global scope
               script = data['script']
               for command in script:
                    log("## > " + str(command), True)
                    exec_script_command(command, global_env)
            else:
               print("No script found") # TODO raise an error
   
elif selector == "cron":
    # Create cron job
    pass

elif selector == "test":
    pass
