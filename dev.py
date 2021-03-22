import os
import subprocess
import sys
import time


def print_header(msg):
    print(f"\n######################## {msg} ########################")


def run_flask(name, runner, port, expose=False):
    print_header(f'Starting {name}')

    webapp_command = f'pipenv run python {runner}.py -p {port}'
    if expose:
        webapp_command += ' --expose'

    proc = subprocess.Popen(
        webapp_command,  # shell=True,
        stdout=sys.stdout, stderr=sys.stderr
    )
    wait_for_output(proc, 10)
    return proc


def run_webapp():
    return run_flask('WebApp', 'run_webapp', 5000)


def wait_for_output(subproc, timeout=2):
    while True:
        try:
            outs, errs = subproc.communicate(timeout=timeout)
            if not outs and not errs:
                break
            if outs:
                print(outs)
            if errs:
                print(errs)
        except subprocess.TimeoutExpired:
            break


def all_live(procs):
    for proc in procs:
        if proc is None:
            continue
        if proc.poll() is not None:
            return False
    return True


def check_proc(proc):
    return (proc is not None and proc.poll() is None)


DEV_PROCESSES = {
    run_webapp: run_webapp()
}


def run_procs(processes, is_main):
    try:
        while True:
            while all_live(list(processes.values())):
                time.sleep(1)

            for runner, proc in processes.items():
                if not check_proc(proc):
                    processes[runner] = runner()
    finally:
        print_header("Terminating Flask Applications ...")
        for proc in processes.values():
            if proc is not None:
                proc.terminate()


if __name__ == '__main__':
    is_main = os.environ.get('WERKZEUG_RUN_MAIN') != 'true'

    if is_main:
        print_header("Running Dev Environment")

    try:
        run_procs(DEV_PROCESSES, is_main)
    except KeyboardInterrupt:
        pass
