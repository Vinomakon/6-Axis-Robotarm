import json
def load_json_config() -> dict:
    with open('../data/user_config.json') as f:
        d = json.load(f)
        f.close()
        return d
