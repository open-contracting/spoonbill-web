import json
import os

ocds_lite_config_path = os.path.dirname(__file__) + "/data/ocds_lite_config.json"
with open(ocds_lite_config_path) as fd:
    OCDS_LITE_CONFIG = json.loads(fd.read())
