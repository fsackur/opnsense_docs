#! /usr/bin/env python3

import json
import os
from typing import *

from lib import ApiController
from collect_api_endpoints import collect_api_modules
from parse_endpoints import Endpoint, Parameter

controllers_by_module = collect_api_modules("/gitroot/upstream/opnsense/core/src/opnsense/", debug=False)
controllers = [
    ctrl
    for controller_list in controllers_by_module.values()
    for ctrl in controller_list
]
from pprint import *
for ctrl in controllers[0:4]:
    pprint(ctrl)
# controllers_by_name = {ctrl["filename"][0:-4]: ctrl for ctrl in controllers}
# # print(controllers_by_name)
exit()

endpoints = []
for ctrl in controllers:
    for action in ctrl["actions"]:
        method = action["method"]
        method = "POST" if method == "GET,POST" else method

        params = []
        for param_str in action["parameters"].split(","):
            pargs = {}
            if "=" in param_str:
                param_name, param_default = param_str.split("=", maxsplit=1)
                pargs["has_default"] = True
                pargs["default"] = param_default
            else:
                param_name = param_str
                pargs["has_default"] = False
                pargs["default"] = None

            params.append(Parameter(
                name=param_name,
                type="string",
                description="",
                **pargs,
            ))

        model_schema_name = None
        model_filename = ctrl["model_filename"]
        if model_filename is None:
            if ctrl["base_class"] == "ApiControllerBase":
                pass
            else:
                print(ctrl["filename"], ctrl["base_class"])

        else:
            vendor, _, filename = model_filename.split("/")[-3:]
            model_schema_name = f"{vendor}.{ctrl["module"]}.{filename[0:-4]}".lower()


        endpoint = Endpoint(
            description="",
            module=ctrl["module"],
            controller=ctrl["controller"],
            name=action["command"],
            method=method,
            parameters=params,
            request_model=None,
            response_model=model_schema_name,
            requires_body=method == "POST" and ctrl["model_filename"] is not None,
            model_path_map=f":{action.get("model_path", "")}",
        )
        endpoints.append(endpoint)

exit()
module_json = json.dumps(endpoints, indent=4)

script_dir = os.path.dirname(__file__)
json_path = os.path.join(script_dir, "modules.json")

with open(json_path, "w") as file:
    file.write(module_json)
