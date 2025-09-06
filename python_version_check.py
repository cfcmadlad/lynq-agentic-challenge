# python_version_check.py
import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        "Python 3.10+ is required. Upgrade your Python or change type hints to typing.Optional."
    )
