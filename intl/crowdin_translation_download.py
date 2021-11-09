#!/usr/bin/env python3

import re
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from core_option_translation import clean_file_name

# Check Crowdin API Token and core name
if len(sys.argv) < 3:
    print('Please provide Crowdin API Token and core name!')
    exit()

api_key = sys.argv[1]
core_name = clean_file_name(sys.argv[2])

# Apply Crowdin API Key
with open('crowdin.yaml', 'r') as crowdin_config_file:
    crowdin_config = crowdin_config_file.read()
crowdin_config = re.sub(r'"api_token": "_secret_"', f'"api_token": "{api_key}"', crowdin_config, 1)
crowdin_config = re.sub(r'"dest": "/_core_name_/%original_file_name%",', f'"dest": "/{core_name}/%original_file_name%",'
                        , crowdin_config, 1)
with open('crowdin.yaml', 'w') as crowdin_config_file:
    crowdin_config_file.write(crowdin_config)

try:
    # Download Crowdin CLI
    dir_path = os.path.dirname(os.path.realpath(__file__))

    jar_name = 'crowdin-cli.jar'

    if not os.path.isfile(jar_name):
        print('download crowdin-cli.jar')
        crowdin_cli_file = 'crowdin-cli.zip'
        crowdin_cli_url = 'https://downloads.crowdin.com/cli/v3/' + crowdin_cli_file
        urllib.request.urlretrieve(crowdin_cli_url, crowdin_cli_file)
        with zipfile.ZipFile(crowdin_cli_file, 'r') as zip_ref:
            jar_dir = zip_ref.namelist()[0]
            for file in zip_ref.namelist():
                if file.endswith(jar_name):
                    jar_file = file
                    break
            zip_ref.extract(jar_file)
            os.rename(jar_file, jar_name)
            os.remove(crowdin_cli_file)
            shutil.rmtree(jar_dir)

    print('download translation *.json')
    subprocess.run(['java', '-jar', 'crowdin-cli.jar', 'download'])

    # Reset Crowdin API Key
    with open('crowdin.yaml', 'r') as crowdin_config_file:
        crowdin_config = crowdin_config_file.read()
    crowdin_config = re.sub(r'"api_token": ".*?"', '"api_token": "_secret_"', crowdin_config, 1)
    with open('crowdin.yaml', 'w') as crowdin_config_file:
        crowdin_config_file.write(crowdin_config)

except Exception as e:
    # Try really hard to reset Crowdin API Key
    with open('crowdin.yaml', 'r') as crowdin_config_file:
        crowdin_config = crowdin_config_file.read()
    crowdin_config = re.sub(r'"api_token": ".*?"', '"api_token": "_secret_"', crowdin_config, 1)
    with open('crowdin.yaml', 'w') as crowdin_config_file:
        crowdin_config_file.write(crowdin_config)
    raise e
