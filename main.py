import os
import sys

sys.dont_write_bytecode = True

if os.name != "nt":
    exit("This OS is not supported. Please use Windows OS.")

if sys.version_info < (3, 10):
    exit("This version of Python is not supported. Please use Python 3.10 at least.")

import importlib
import importlib.metadata
import importlib.util
import logging
import subprocess


def install_packages() -> None:
    print(" * Verifying packages", end="\n\n")

    packages = open("data/requirements.txt").readlines()

    for package in packages:
        if package.startswith("#") or "==" not in package:
            continue

        (package, version) = package.strip().split("==")
        redo = importlib.util.find_spec(package.replace("-", "_")) is None

        if not redo and importlib.metadata.version(package) != version:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package], capture_output=True)
            redo = True

        if redo:
            print(f" * Installing {package} .......... ", end="", flush=True)
            stdout = subprocess.run([sys.executable, "-m", "pip", "install", f"{package}=={version}"], capture_output=True, text=True).stdout

            if "Successfully installed" not in stdout:
                exit("FAIL")
            print("OK")


install_packages()

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from core.classes.exceptions import InvalidProcess
from core.common.utils import check_version, run_server


def main() -> None:
    logging.disable()
    disable_warnings(InsecureRequestWarning)

    check_version()

    try:
        run_server()
    except InvalidProcess:
        exit(' * You must have GTA open before running this script')


if __name__ == "__main__":
    main()
