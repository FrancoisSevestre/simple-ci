#! /bin/python3
"""
SIMPLE CI: Dead simple CI/CD pipeline executor.
author: François Sevestre
email: francois.sevestre.35@gmail.com
"""

############## Imports   ##############
import sys
import time
from getpass import getpass
import argparse

from simple_cicd.functions import \
        log,                      \
        manage_hook,              \
        create_example_file,      \
        get_root_dir,             \
        get_pipeline_data,        \
        run_script,               \
        end_of_pipeline,          \
        command_execution         \
############## Main ##############


def main():
    """
    Main function, call with simpleci command.
    """

    # Arguments parsing
    parser = argparse.ArgumentParser(                     \
            prog="simpleci",                              \
            description="Dead simple pipeline executor.", \
            )
    selector = parser.add_subparsers(dest='selector') # Create parsers for subcommands
    # start
    start_parser = selector.add_parser('start', help="Create the git hook.")
    #       --sudo
    start_parser.add_argument("-S","--sudo",\
            help="Make simpleci use sudo priviledges when triggered.", action="store_true")
    # exec
    exec_parser = selector.add_parser('exec', help="Execute the pipeline.")
    #      --file
    exec_parser.add_argument("-f","--file", help="Specify a file to use as pipeline.")
    #      --sudo
    exec_parser.add_argument("-S","--sudo", \
            help="Execute the pipeline with sudo priviledges.", action="store_true")
    # stop
    selector.add_parser('stop', help="Delete the git hook.")
    # init
    selector.add_parser('init', help="Create the git hook and an example .simple-ci.yml file.")
    # clean
    selector.add_parser('clean', help="Remove artifacts folder.")
    # cron
    selector.add_parser('cron', help="Create a cronjob.")
    # test
    selector.add_parser('test', help="For test purpose.")
    args = parser.parse_args()

    if args.selector == 'start':
        start_args = parser.parse_args()
        # check suplemental args
        if start_args.sudo:
            sys.exit(manage_hook(get_root_dir(), sudo=True))       # Create the hook file
        else:
            sys.exit(manage_hook(get_root_dir()))       # Create the hook file

    elif args.selector == 'stop':
        sys.exit(manage_hook(get_root_dir(), False))# Delete the hook file

    elif args.selector == 'init':
        create_example_file(get_root_dir())         # Create the .simple-ci.yml file
        sys.exit(manage_hook(get_root_dir()))       # start

    elif args.selector == 'exec':
        exec_args = parser.parse_args()

        time_summary = "Execution times:\n----------------\n"
        sudo_prefix = ""

        # check suplemental args
        if exec_args.file:
            path_to_script = exec_args.file
            data = get_pipeline_data(get_root_dir(), str(path_to_script)) # Collect data from script
        else:
            data = get_pipeline_data(get_root_dir())    # Collect data from script

        if exec_args.sudo:
            pswd = getpass()
            sudo_prefix = f"echo {pswd} | sudo -S "

        log("\n>>>>>>\nStarting the pipeline execution\n", "green")
        ### Global scope ###

        try:
            # Variables
            if 'variables' in data:                     # if user declared variables in global scope
                global_env = data['variables']
            else:
                global_env = {}

            # Inside docker                             # if user declared a docker (global scope)
            if 'inside_docker' in data:
                global_docker = data['inside_docker']
            else:
                global_docker = {}

            # Artifacts
            if 'artifacts' in data:
                global_artifacts = data['artifacts']
            else:
                global_artifacts = {}

            # stages
            if 'stages' in data:                        # if user declared stages in global scope
                for stage in data['stages']:
                    stage_name = str(stage)
                    stage_start_time = time.time()
                    log("###### Stage \'" + stage_name + "\' ######\n", "green")

                    ### Stage scope ###
                    stage = data[stage]                 # get data from stage

                    # variables
                    if 'variables' in stage:        # if user declared variables in the stage scope
                        stage_env = global_env | stage['variables'] # merge dicts with overwrite
                    else:
                        stage_env = global_env

                    # Inside docker
                    if 'inside_docker' in stage:    # if user declared variables in the stage scope
                        # merge dicts + overwrite
                        stage_docker = stage['inside_docker']
                    else:
                        stage_docker = global_docker

                    # Jobs
                    if 'jobs' in stage:                 # Check if user declared jobs in this stage
                        job_time_summary = ""
                        for job in stage['jobs']:
                            job_time_summary = ""
                            job_name = str(job)
                            log("#### Job \'" + job_name + "\' ####", "green")

                            ### Job scope ###
                            job = data[job]             # get data from job

                            # variables
                            if 'variables' in job:  # if user declared variables in the job scope
                                job_env = stage_env | job['variables']
                            else:
                                job_env = stage_env

                            # Inside docker
                            if 'inside_docker' in job: # if user declared variables in the job scope
                                job_docker = job['inside_docker']
                            else:
                                job_docker = stage_docker

                            # Artifacts
                            if 'artifacts' in job:
                                job_artifacts = job['artifacts']
                            else:
                                job_artifacts = {}

                            # Script
                            if 'script' in job:         # Check if user defined script in this job
                                job_script = job['script']
                                script_parameters = [job_script, job_env, job_docker, \
                                        job_artifacts, get_root_dir(), sudo_prefix]
                                exec_time = run_script(script_parameters)
                                job_time_summary += \
                                        f"|-->\t{job_name} ({float(f'{exec_time:.2f}')}s)\n"

                            else:
                                log(f"No script found for the job \"{job_name}\".", "red")
                                end_of_pipeline()

                        stage_stop_time = time.time()
                        stage_exec_time = stage_stop_time - stage_start_time
                        time_summary += f"{stage_name} ({float(f'{stage_exec_time:.2f}')}s)\n"
                        time_summary += job_time_summary

                    else:
                        log(f"No jobs found fo the stage \"{stage_name}\".", "red")
                        end_of_pipeline()
            # Jobs
            else:
                if 'jobs' in data:                      # if user declared jobs in global scope
                    for job in data['jobs']:
                        job_time_summary = ""
                        job_name = str(job)
                        log("#### Job \'" + job_name + "\' ####", "green")

                        ### Job scope ###
                        job = data[job]

                        # variables                 # if user declared variables in the job scope
                        if 'variables' in job:
                            job_env = global_env | job['variables']
                        else:
                            job_env = global_env

                        # Inside docker             # if user declared a docker option (job scope)
                        if 'inside_docker' in job:  # if user declared variables in the job scope
                            job_docker = job['inside_docker']
                        else:
                            job_docker = global_docker

                        # Artifacts
                        if 'artifacts' in job:
                            job_artifacts = job['artifacts']
                        else:
                            job_artifacts = {}

                        # Script
                        if 'script' in job:         # Check if user defined script in this job
                            job_script = job['script']
                            script_parameters = [job_script, job_env, job_docker, \
                                    job_artifacts, get_root_dir(), sudo_prefix]
                            exec_time = run_script(script_parameters)
                            job_time_summary += f"{job_name} ({float(f'{exec_time:.2f}')}s)\n"
                        else:
                            log(f"No script found for the job \"{job_name}\".", "red")
                            end_of_pipeline()

                        time_summary += job_time_summary

            # Script
                else:
                    if 'script' in data:         # Check if user defined script in this job
                        global_script = data['script']
                        script_parameters = [global_script, global_env, global_docker, \
                                global_artifacts, get_root_dir(), sudo_prefix]
                        exec_time = run_script(script_parameters)
                        time_summary += f"Script ({float(f'{exec_time:.2f}')}s)\n"
                    else:
                        log("No script found.", "red")
                        end_of_pipeline()

        except TypeError:
            log("Failed to read pipeline script. Please check the syntax.", "red")
            end_of_pipeline()

        log(time_summary, "blue")
        log("<<<<<\nEnd of the pipeline", "green")

    elif args.selector == 'cron':
        # TODO Create cron job
        pass

    elif args.selector == 'clean':
        artifacts_dir = get_root_dir() + "-artifacts"
        if input(f"Delete {artifacts_dir} directory? (y/N)\n>") \
                in ('y', 'yes', 'Y', 'YES'):
            sys.exit(command_execution(f"rm -rf {artifacts_dir}"))

    elif args.selector == 'test':
        # For dev purpose only
        print("Test of simpleci install succeded!")

if __name__ == '__main__':
    main()
