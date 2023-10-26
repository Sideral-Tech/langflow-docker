#!/usr/bin/env python3

import argparse
import urllib.request
import json

try:
    import tomli
except ImportError:
    from pip._vendor import tomli


def get_latest_version():
    url = "https://api.github.com/repos/logspace-ai/langflow/releases/latest"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data["name"]


def get_latest_pyproject():
    # TODO: Use latest version
    #
    # Temporarily disabling this as it's missing langflow dependencies
    #
    # url = f"https://raw.githubusercontent.com/logspace-ai/langflow/{get_latest_version()}/pyproject.toml"
    #
    # Use dev branch for now
    url = "https://raw.githubusercontent.com/logspace-ai/langflow/dev/pyproject.toml"
    response = urllib.request.urlopen(url)
    data = response.read()
    return data.decode("utf-8")


def load_toml():
    return tomli.loads(get_latest_pyproject())


def write_requirements(dependencies, output_path):
    with open(output_path, "w") as file:
        for dep, version in dependencies.items():
            file.write(f"{dep}{version}\n")


def convert_dependency_version(version):
    if isinstance(version, dict):
        version = version.get("version", "")
    if "^" in version:
        # Caret requirements
        parts = version.replace("^", "").split(".")
        if parts[0] == "0":
            if parts[1] == "0":
                return f">={version.replace('^', '')},<0.0.{str(int(parts[2])+1)}"
            return f">={version.replace('^', '')},<0.{str(int(parts[1])+1)}.0"
        return f">={version.replace('^', '')},<{str(int(parts[0])+1)}.0.0"
    elif "~" in version:
        # Tilde requirements
        parts = version.replace("~", "").split(".")
        if len(parts) == 3:
            return f">={version.replace('~', '')},<{parts[0]}.{str(int(parts[1])+1)}.0"
        elif len(parts) == 2:
            return f">={version.replace('~', '')},<{parts[0]}.{str(int(parts[1])+1)}"
        else:
            return f">={version.replace('~', '')},<{str(int(parts[0])+1)}.0.0"
    elif "*" in version:
        # Wildcard requirements
        parts = version.split(".")
        if len(parts) == 2:
            return f">={parts[0]}.0.0,<{str(int(parts[0])+1)}.0.0"
        elif len(parts) == 3:
            return f">={version.replace('*', '0')},<{parts[0]}.{str(int(parts[1])+1)}.0"
        else:
            return ">=0.0.0"
    elif "," in version:
        # Multiple requirements
        return ",".join(
            [convert_dependency_version(v.strip()) for v in version.split(",")]
        )
    elif any(op in version for op in [">=", "<=", ">", "<", "!=", "=="]):
        # Inequality and Exact requirements
        return version
    else:
        # Assume exact version if none of the above
        return f"=={version}"


def convert_pyproject_to_requirements(output_path):
    pyproject = load_toml()

    dependencies = pyproject["tool"]["poetry"]["dependencies"]
    extras = pyproject["tool"]["poetry"]["extras"]

    dep_lines = {}

    for name, dep in dependencies.items():
        if "pywin32" in name:
            continue
        if name != "python" and not isinstance(dep, dict):
            version = convert_dependency_version(dep)
            dep_lines[name] = version
        elif isinstance(dep, dict):
            version = convert_dependency_version(dep.get("version", ""))
            dep_lines[name] = version

    for _, deps in extras.items():
        for dep in deps:
            if dep not in dep_lines:  # avoid duplicate entries
                dep_version = dependencies.get(dep, "")
                if dep_version:
                    version = convert_dependency_version(dep_version)
                    dep_lines[dep] = version

    write_requirements(dep_lines, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert pyproject.toml to requirements.txt."
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        default="requirements.txt",
        help="Path to the output requirements.txt file.",
    )
    args = parser.parse_args()

    convert_pyproject_to_requirements(args.output_path)
