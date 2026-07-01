from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise ImportError(
        "PyYAML is required to load config.yaml. Install it with `pip install pyyaml`."
    ) from exc


def load_config(config_path="config.yaml"):
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    return config or {}


def get_config(config, section, default=None):
    return config.get(section, default if default is not None else {})
