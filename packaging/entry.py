"""Ponto de entrada do executavel: roda o mesmo `main()` de `python -m filepilot`."""

import sys

from filepilot.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
