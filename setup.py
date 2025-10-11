# assumes u have github setup
# for setting up venv or conda env and activating it, then
# installing dependencies from requirements.txt
# and lastly restructuring the dataset folder if not already done


import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, env=None, shell=True, should_exit=True):
    """Run a shell command."""
    try:
        subprocess.run(cmd, check=True, shell=shell, env=env)
    except subprocess.CalledProcessError:
        print(f"❌ Command failed: {cmd}")
        if should_exit:
            sys.exit(1)

def add_to_gitignore(venv_name):
    gitignore = Path(".gitignore")
    entry = f"{venv_name}/"
    if gitignore.exists():
        with open(gitignore, "r+") as f:
            lines = f.read().splitlines()
            if entry not in lines:
                f.write(f"\n{entry}")
                print(f"✅ Added {entry} to .gitignore")
            else:
                print(f"✅ {entry} already added to .gitignore")
    else:
        with open(gitignore, "w") as f:
            f.write(entry + "\n")
            print("✅ Created .gitignore and added venv entry")

def setup_venv(venv_name="venv"):
    print("Creating virtual environment...")
    run_cmd(f"{sys.executable} -m venv {venv_name}", shell=False)
    add_to_gitignore(venv_name)
    pip_path = Path(venv_name) / "Scripts" / "pip" if os.name == "nt" else Path(venv_name) / "bin" / "pip"
    print("Installing dependencies...")
    # run_cmd(f"{pip_path} install --upgrade pip", shell=False)
    try:
        pkgs = []
        with open("requirements.txt", "r", encoding="utf-16") as f: 
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Remove any version specifiers and clean invisible chars
                    clean = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0].strip()
                    pkgs.append(clean)

        failed_pkgs = []
        for pkg in pkgs:
            print(f"Installing {pkg} ...")
            result = run_cmd([str(pip_path), "install", pkg], shell=False, should_exit=False)
            if result != 0:
                print(f"⚠️ Skipped {pkg} (install failed)")
                failed_pkgs.append(pkg)
        if failed_pkgs:
            print("\n❌ The following packages could not be installed:")
            for pkg in failed_pkgs:
                print(f" - {pkg}")
            print("\n✅ Still double check and verify manually.")
        else:
            print("\n✅ All packages installed successfully!")

    except Exception as e:
        print(f"❌ Failed to install dependencies. \nError=> {e}. \nInstalling")
        sys.exit(1)
    print("✅ Virtual environment setup complete!")

def setup_conda(env_name="myenv"):
    print("Creating Conda environment...")
    run_cmd(f"conda create -y -n {env_name} python={sys.version_info.major}.{sys.version_info.minor}")
    print("Installing dependencies...")
    run_cmd(f"conda run -n {env_name} pip install -r requirements.txt")
    print("✅ Conda environment setup complete!")

if __name__ == "__main__":
    print("Select environment type:")
    print("1) venv (default)")
    print("2) conda")
    choice = input("Enter choice [1/2]: ").strip()

    if choice == "2":
        if subprocess.call("conda --version", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            env_name = input("Enter your conda env name: ")
            setup_conda(env_name)
        else:
            print("❌ Conda not found on this system.")
            sys.exit(1)
    else:
        if subprocess.call([sys.executable, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            setup_venv()
        else:
            print("❌ Python not found on this system.")
            sys.exit(1)
