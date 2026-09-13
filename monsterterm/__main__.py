"""Main entry point for MonsterTerm."""

from __future__ import annotations

import sys

from monsterterm.app import MonsterTermApp


def main() -> None:
    app = MonsterTermApp()
    app.run()


if __name__ == "__main__":
    sys.exit(main())
