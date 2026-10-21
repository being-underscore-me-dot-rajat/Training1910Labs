"""Small helpers shared by the pipeline stages."""
import json
from pathlib import Path

import yaml


def load_params():
    """Read every setting from params.yaml into a dictionary."""
    with open("params.yaml") as f:
        return yaml.safe_load(f)


def write_json(data, path):
    """Write a dictionary to a JSON file, creating the folder if needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" keeps the file byte-identical on Windows, macOS and Linux, so DVC sees no change
    with open(path, "w", newline="\n") as f:
        f.write(json.dumps(data, indent=2) + "\n")
