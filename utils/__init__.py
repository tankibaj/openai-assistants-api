import json


def pretty_json(obj):
    # Convert the JSON string back to a Python dictionary
    data = json.loads(obj.model_dump_json())

    # Convert the dictionary back to a string, this time pretty-printed
    pretty_json = json.dumps(data, indent=4)

    # Print the pretty JSON string
    print(pretty_json)
