#! /bin/python3
"""
SIMPLE CI: Dead simple CI/CD pipeline executor.
author: François Sevestre
email: francois.sevestre.35@gmail.com
"""

############## Imports   ##############
import sys
import os
import time

from simple_cicd.ci_files import *
from simple_cicd.functions import *
############## Main ##############

def main():
    args = sys.argv
    args.pop(0)                       # Remove script name from the list
    SELECTOR = args[0]
    if len(args) > 1:
        OPTIONS = args[1:]
    else:
        OPTIONS = [False]

    if SELECTOR == "start":
        sys.exit(manage_hook(get_root_dir()))       # Create the hook file

    elif SELECTOR == "stop":
        sys.exit(manage_hook(get_root_dir(), False))# Delete the hook file

    elif SELECTOR == "init":
        create_example_file(get_root_dir())         # Create the .simple-ci.yml file
        sys.exit(manage_hook(get_root_dir()))       # start

    elif SELECTOR == "exec":                        # Execution of the .simple-ci.yml script
        time_summary = "Execution times:\n----------------\n"

        # check suplemental args
        if OPTIONS[0] in ("--file", "-f"):
            path_to_script = OPTIONS[1]
            data = get_pipeline_data(get_root_dir(), str(path_to_script)) # Collect data from script
        else:
            data = get_pipeline_data(get_root_dir())    # Collect data from script

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
                    STAGE_NAME = str(stage)
                    stage_start_time = time.time()
                    log("###### Stage \'" + STAGE_NAME + "\' ######\n", "green")

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
                            JOB_NAME = str(job)
                            log("#### Job \'" + JOB_NAME + "\' ####", "green")

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
                                        job_artifacts, get_root_dir()]
                                exec_time = run_script(script_parameters)
                                job_time_summary += f"|-->\t{JOB_NAME} ({float(f'{exec_time:.2f}')}s)\n"
                                # log(f"Execution time: {float(f'{exec_time:.2f}')} secondes", "blue")

                            else:
                                log(f"No script found for the job \"{JOB_NAME}\".", "red")
                                end_of_pipeline()

                        stage_stop_time = time.time()
                        stage_exec_time = stage_stop_time - stage_start_time
                        time_summary += f"{STAGE_NAME} ({float(f'{stage_exec_time:.2f}')}s)\n"
                        time_summary += job_time_summary

                    else:
                        log(f"No jobs found fo the stage \"{STAGE_NAME}\".", "red")
                        end_of_pipeline()
            # Jobs
            else:
                if 'jobs' in data:                      # if user declared jobs in global scope
                    job_time_summary = ""
                    for job in data['jobs']:
                        JOB_NAME = str(job)
                        log("#### Job \'" + JOB_NAME + "\' ####", "green")

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
                                    job_artifacts, get_root_dir()]
                            exec_time = run_script(script_parameters)
                            job_time_summary += f"{JOB_NAME} ({float(f'{exec_time:.2f}')}s)\n"

                        else:
                            log(f"No script found for the job \"{JOB_NAME}\".", "red")
                            end_of_pipeline()

                        time_summary += job_time_summary

            # Script
                else:
                    if 'script' in data:         # Check if user defined script in this job
                        global_script = data['script']
                        script_parameters = [global_script, global_env, global_docker, \
                                global_artifacts, get_root_dir()]
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

    elif SELECTOR == "cron":
        # TODO Create cron job
        pass

    elif SELECTOR == "clean":
        artifacts_dir = get_root_dir() + "-artifacts"
        if input(f"Delete {artifacts_dir} directory? (y/N)\n>") \
                in ('y', 'yes', 'Y', 'YES'):
            os.system(f"rm -rf {artifacts_dir}")

    elif SELECTOR == "test":
        # For dev purpose only
        print("Test of simpleci install succeded!")

    else:
        print("Wrong argument")
        sys.exit(1)


if __name__ == '__main__':
    main()
