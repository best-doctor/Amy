import subprocess

from config import BASE_CORE_DIR


def run_shell_command(raw_command: str) -> bytes:
    return subprocess.check_output(
        raw_command.split(' '),
        cwd=BASE_CORE_DIR,
    )
