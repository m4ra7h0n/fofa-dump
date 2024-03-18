import subprocess
import json

def execute_command(command) -> []:
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        output = result.stdout.decode('utf-8').splitlines()
        return output
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return None

def parse_json(json_string):
    try:
        parsed_json = json.loads(json_string)
        return parsed_json
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
        return None