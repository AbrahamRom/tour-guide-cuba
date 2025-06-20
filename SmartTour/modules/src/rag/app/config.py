import yaml

def load_config(path="modules/src/rag/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Debug: print config to verify keys
    # print(config)
    return config
