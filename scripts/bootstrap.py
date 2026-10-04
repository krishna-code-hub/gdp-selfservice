"""Cross-platform bootstrap without shell activation. Requires Python 3.11–3.13."""

import argparse
import subprocess
import sys
import venv
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dev", action="store_true")
    p.add_argument("--ingest", action="store_true")
    args = p.parse_args()
    if not (3, 11) <= sys.version_info[:2] < (3, 14):
        p.error("Use Python 3.11, 3.12 or 3.13; Python 3.14 is not supported by this kit")
    root = Path(__file__).resolve().parents[1]
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    # Prefer the committed full dependency lock when uv is available.
    import shutil

    uv = shutil.which("uv")
    if uv:
        command = [uv, "sync", "--frozen", "--python", str(python)]
        if args.dev:
            command += ["--extra", "dev"]
        subprocess.run(command, cwd=root, check=True)
    else:
        subprocess.run([str(python), "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        target = str(root) + ("[dev]" if args.dev else "")
        subprocess.run([str(python), "-m", "pip", "install", "-e", target], check=True)
        print("Installed compatible dependency ranges. Use uv sync --frozen for the tested lock.")
    if args.ingest:
        subprocess.run([str(python), str(root / "scripts/ingest.py")], cwd=root, check=True)
    print(f"Ready. Interpreter: {python}")


if __name__ == "__main__":
    main()
