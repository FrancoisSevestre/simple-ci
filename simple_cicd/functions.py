"""
SIMPLE CI: Dead simple CI/CD pipeline executor.
author: François Sevestre
email: francois.sevestre.35@gmail.com

This modules contains functions.
"""
###########################################
import sys
import os
import time
from subprocess import getoutput, PIPE, run
from datetime import datetime

import yaml

from simple_cicd.ci_files import EXAMPLE_FILE_DATA, PRE_COMMIT_HOOK
###########################################

def get_root_dir():
    """ Get the root directory of the git repo.
    Returns:
        An absolute path.
    """
    return getoutput("git rev-parse --show-toplevel")

def get_git_branch():
    """ Get the current git branch.
    Returns:
        A string, the name of the branch.
    """
    return getoutput("git branch | grep '*' | awk '{print $2}'")

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

    # manage hook
    if present:                                             # Create the hook file
        with open(git_root_dir+"/.git/hooks/pre-commit", 'w', encoding="utf-8") as file:
            file.write(PRE_COMMIT_HOOK)
        os.chmod(git_root_dir+"/.git/hooks/pre-commit", 0o755)
        print("Git hook created.                                 \
            \nIt will execute the pipeline before the next commit.\
            \nAlternatively, you can trigger the pipeline with \'simple-ci exec\'")
    else:
        os.remove(git_root_dir+"/.git/hooks/pre-commit")   # Remove the hook file
    return True

def create_example_file(git_root_dir):
    """
    Creates an example .simple-ci.yml file at the git root dir if it doesn't exists
    """
    # check if file exists
    if os.path.isfile(git_root_dir+"/.simple-ci.yml"):
        print("File exists: Example creation skipped.")
    else:
        # create file
        with open(git_root_dir+"/.simple-ci.yml", 'w', encoding="utf-8") as file:
            file.write(EXAMPLE_FILE_DATA)
        print("The .simple-ci.yml file has been created. Check it, try it and customize it!")

def get_pipeline_data(git_root_dir, ci_script=".simple-ci.yml"):
    """ Get the pipeline data from file.
    Returns:
        A dict.
    """
    try:
        yaml_data = False
        with open(git_root_dir+"/"+ci_script, 'r', encoding="utf-8") as file:
            yaml_data = yaml.load(file, Loader=yaml.Loader)
        return yaml_data
    except FileNotFoundError:
        log("Pipeline file not found", "red")
        sys.exit(1)

def log(line, color=""):
    """ Prints line and saves it to simple.log file
    Args:
        line (str)
        color (bool)
    """
    with open("simple.log", 'a', encoding="utf-8") as log_file:
        log_file.write(line+"\n")
    if color == "green":
        print("\033[32m"+line+"\033[0m")
    elif color == "red":
        print("\033[31m"+line+"\033[0m")
    elif color == "blue":
        print("\033[36m"+line+"\033[0m")
    else:
        print(line)

def command_execution(command_to_execute):
    """
    Executes the given command, manage logs and exit pipeline if necessary
    """
    res = run(command_to_execute, shell=True, stdout=PIPE, stderr=PIPE, \
            universal_newlines=True, check=False)
    log(res.stdout)
    if res.returncode != 0:
        log(f"return code: {res.returncode}", "red")
        log(res.stdout, "red")
        return False
    return True

def exec_script_command(script_command, env):
    """  Execute a command with a given env
    Args:
        command (str)
        env (dict)
    """
    env_cmd = "true"

    for var_key in env:                                         # Add env variables declaration
        env_cmd = env_cmd + \
                " && " +    \
                var_key + "=\"" + str(env[var_key]) + "\""

    passed_command = "bash -c \'" + \
            env_cmd +               \
            " && " +                \
            script_command +        \
            "\'"                                                # Assemble final command
    return command_execution(passed_command)

def create_container(docker_image):
    """
    Creates a docker container of the specified image.
    Returns:
        container_hash (str)
    """
    cont = getoutput("docker run -td " + docker_image) # Create container
    cont = cont.split(sep='\n')[-1][0:11]
    # os.system("docker container start " + cont + " > /dev/null")          # start container
    return cont

def exec_script_command_in_docker(script_command, env, cont_id):
    """
    Execute a command with the given env in the given container.
    """
    env_cmd = "true"

    for var_key in env:                                         # Add env variables declaration
        env_cmd = env_cmd + \
                " && " +    \
                var_key + "=\"" + str(env[var_key]) + "\""

    passed_command = "sh -c \'" + \
            env_cmd +             \
            " && " +              \
            script_command +      \
            "\'"                                                # Assemble final command
    full_command = "docker exec " + cont_id + " " + passed_command+ " \n"
    return command_execution(full_command)

def copy_files_to_docker(cont_id, path): # TODO Function impure
    """
    Copies the current git folder to container at the given path.
    """
    log(f"Files will be copied to the container {cont_id} at \'{path}\'", "blue")
    # os.system(f"cp -r . {get_root_dir()}_simple-ci/" )
    os.system(f"docker cp . {cont_id}:{path}")

def stop_container(cont_id):
    """
    Stops a docker container.
    """
    os.system("docker rm -f " + cont_id + " > /dev/null")

def create_artifacts_folder(git_root_dir):
    """
    Creates an artifacts folder next to the git folder with same name + '-artifacts'.
    Also creates a sub-folder name after launch time.
    """
    artifacts_dir_to_be_created = git_root_dir+"-artifacts"
    try:
        os.mkdir(artifacts_dir_to_be_created)       # Create the common artifacts folder
        print("Artifacts folder created.")
    except FileExistsError:
        pass
    run_dir = os.path.join(artifacts_dir_to_be_created,\
            datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    try:
        os.mkdir(run_dir)             # Create the run folder
    except FileExistsError:
        print("Run folder already exists. (last one created less than a second ago)")
    return run_dir

def run_script(script_parameters_to_run):
    """Execution of the script commands on the given env"""

    script_to_run = script_parameters_to_run[0]
    job_env_to_run = script_parameters_to_run[1]
    job_docker_to_run = script_parameters_to_run[2]
    job_artifacts_to_run = script_parameters_to_run[3]
    git_root_dir = script_parameters_to_run[4]

    start_script_time = time.time()

    # Prepare artifacts folder
    if job_artifacts_to_run:
        current_artifacts_dir = create_artifacts_folder(git_root_dir)
    else:
        current_artifacts_dir = create_artifacts_folder("/tmp/simpleci")

    if job_docker_to_run != {}: # For inside_docker execution
        log(f"A \'{job_docker_to_run['image']}\' container is required.", "blue")
        container_id = create_container(job_docker_to_run['image'])     # Creating container
        log(f"Container \'{container_id}\' as been created.", "blue")
        copy_files_to_docker(container_id, job_docker_to_run['path'])   # copy files to docker
        for command in script_to_run:                                   # Exec script in docker
            log("## > " + str(command), "green")
            if not exec_script_command_in_docker(command, job_env_to_run, container_id):
                stop_container(container_id)                                    # Kill container
                end_of_pipeline()


        # Artifacts
        if job_artifacts_to_run:
            paths = job_artifacts_to_run['paths']
            for file in paths:
                os.system(f"docker cp {container_id}:{file} {current_artifacts_dir}")
                log(f"Artifact \"{file}\" saved in {current_artifacts_dir}.", "blue")

        stop_container(container_id)                                    # Kill container

    else: # for local execution

        tmp_artifacts_dir = "/tmp/" + os.path.basename(current_artifacts_dir)
        os.system(f"cp -r {git_root_dir} {tmp_artifacts_dir} 2> /dev/null")

        current_dir = os.getcwd()
        os.chdir(tmp_artifacts_dir)
        for command in script_to_run:
            log("## > " + str(command), "green")
            if not exec_script_command(command, job_env_to_run):
                end_of_pipeline()

        # Artifacts
        if job_artifacts_to_run:
            paths = job_artifacts_to_run['paths']
            for file in paths:
                os.system(f"cp -r -t {current_artifacts_dir} {tmp_artifacts_dir}/{file} ")
                log(f"Artifact \"{file}\" saved in {current_artifacts_dir}.", "blue")

        os.chdir(current_dir)
    stop_script_time = time.time()
    return stop_script_time - start_script_time

def end_of_pipeline():
    """
    Display a message when pipeline failed and exits with error.
    """
    log("Pipeline failed.", "red")
    sys.exit(1)
