import json


def read_file_as_string(file_path):
    f = open(file_path, "r")
    data = f.read()
    f.close()
    return data


def write_append_strings_to_file(file_path, new_data):
    f = open(file_path, "a")
    f.write(new_data)
    f.close()


def write_overwrite_file(file_path, overwrite_data):
    f = open(file_path, "w")
    f.write(overwrite_data)
    f.close()


def parse_any_dict_from_string(data):
    rv = dict()
    for lines in data.split("\n"):
        if "=" in lines:
            parsed = lines.split("=")
            rv[parsed[0]] = parsed[1]
    return rv
