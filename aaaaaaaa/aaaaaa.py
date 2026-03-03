import subprocess
import sys

try:
    # standard‑library metadata API (Python 3.8+)
    from importlib.metadata import distributions
except ImportError:  # older Python / no stdlib support
    import pkg_resources
    def distributions():
        return pkg_resources.working_set

def check_dependencies(requirements_file="requirements.txt"):
    """Check if all dependencies in requirements.txt are installed."""
    try:
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Error: {requirements_file} not found")
        return False

    missing = []
    installed_pkgs = {pkg.name.lower() for pkg in distributions()}

    for req in requirements:
        pkg_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('!=')[0].lower()
        if pkg_name not in installed_pkgs:
            missing.append(req)

    if missing:
        print("Missing dependencies:")
        for pkg in missing:
            print(f"  - {pkg}")
        return False
    else:
        print("All dependencies are installed!")
        return True

if __name__ == "__main__":
    check_dependencies()