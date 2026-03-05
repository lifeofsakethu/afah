import os
import sys
import subprocess
from pathlib import Path

def install_package_to_folder(package_name, custom_folder):
    """
    Install a Python package to a custom folder for code inspection.
    
    Args:
        package_name (str): Name of the package to install
        custom_folder (str): Target folder path
    """
    custom_folder = Path(custom_folder).resolve()
    custom_folder.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"Installing {package_name} to {custom_folder}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "--target", str(custom_folder),
            package_name
        ])
        print(f"✓ Successfully installed {package_name}")
        print(f"Package location: {custom_folder}")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 2.py <package_name> [custom_folder]")
        sys.exit(1)
    
    package = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else f"./packages/{package}"
    
    install_package_to_folder(package, folder)