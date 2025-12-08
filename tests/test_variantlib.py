import json
import subprocess
from pathlib import Path


def test_plugins_list(tmp_path):
    with open(Path(tmp_path) / "plugins.list", "w") as outfile:
        subprocess.run(["variantlib", "plugins", "list"], stdout=outfile, text=True, check=True)

    subprocess.run(["grep", "intel", Path(tmp_path) / "plugins.list"], text=True, check=True)

def test_all_valid_configs(tmp_path):
    with open(Path(tmp_path) / "output.json", "w") as outfile:
        subprocess.run(["variantlib", "plugins", "get-configs", "-a", "-n", "intel"], stdout=outfile, text=True, check=True)

    with open(Path(tmp_path) / "output.json", 'r') as f:
        configs = json.load(f)

    assert "intel" in configs
    assert len(configs["intel"]) == 1
    for prop in configs["intel"]:
        assert prop["name"] == "device_ip"
        assert prop["values"]
        assert prop["multi_value"]

def test_supported_configs(tmp_path):
    with open(Path(tmp_path) / "output.json", "w") as outfile:
        subprocess.run(["variantlib", "plugins", "get-configs", "-s", "-n", "intel"], stdout=outfile, text=True, check=True)

    with open(Path(tmp_path) / "output.json", 'r') as f:
        configs = json.load(f)

    # configs might be empty if Intel stack was not detected
    if configs:
        assert "intel" in configs
        assert len(configs["intel"]) == 1
        for prop in configs["intel"]:
            assert prop["name"] == "device_ip"
            assert prop["values"]
            assert prop["multi_value"]
