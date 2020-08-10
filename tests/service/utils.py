import json
from pathlib import Path


def load_responses(folder="resp"):
    test_dir = Path(__file__).parent / f"{folder}/"
    resp_list = []
    for test_file in test_dir.glob("*.txt"):
        with open(test_file, "r") as f:
            json_data = ""
            params = f.readline().strip()
            params = json.loads(params)["params"]
            for line in f:
                json_data += line
            json_data = json.loads(json_data)
        resp_list.append([params, json_data])
    return resp_list
