# config/environ.py

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def set_thread_env_vars():
    os.environ["OMP_NUM_THREADS"] = "1"  # OpenMP / BLAS threads
    os.environ["MKL_NUM_THREADS"] = "1"  # Intel MKL
    os.environ["OPENBLAS_NUM_THREADS"] = "1"  # OpenBLAS
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"  # Apple vecLib
    os.environ["NUMEXPR_NUM_THREADS"] = "1"  # numexpr


def set_secret_key():
    secret_key = os.getenv("DJANGO_SECRET_KEY")
    if not secret_key:
        raise ValueError("DJANGO_SECRET_KEY environment variable is not set")
    return secret_key


def get_debug_state():
    return False if os.getenv("DEBUG", "False") == "False" else True


def app_log_to_console(debug: bool = False):
    return (
        os.getenv("APP_LOG_TO_CONSOLE", "True" if debug else "False") == "True"
    )


def active_log_modules():
    return os.getenv("ACTIVE_LOG_MODULES", "").split(",")


APP_LOG_TO_CONSOLE = app_log_to_console()
ACTIVE_LOG_MODULES = active_log_modules()
