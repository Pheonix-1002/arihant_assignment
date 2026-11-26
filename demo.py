"""Run all three CLI demos sequentially."""

import subprocess
import sys


for mod in ["project1_options.cli",
            "project2_portfolio.cli",
            "project3_charts.cli"]:
    print(f"\n{'#' * 68}\n#  {mod}\n{'#' * 68}\n")
    r = subprocess.run([sys.executable, "-m", mod])
    if r.returncode != 0:
        print(f"[{mod}] exited with code {r.returncode}")
