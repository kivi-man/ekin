#!/usr/bin/env python3
"""Ekin programlama dili - komut satırı girişi.

    python ekin.py çalıştır ornekler/01_merhaba.ekin
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ekin.arac import ana  # noqa: E402

if __name__ == "__main__":
    sys.exit(ana())
