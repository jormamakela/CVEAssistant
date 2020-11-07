import json
import urllib.request
import gzip


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


def download_file_from_to(url, path_to):
    urllib.request.urlretrieve(url, path_to)


def extract_gzip_to_file(gzip_file, extract):
    gzip_file_handle = gzip.GzipFile(gzip_file, 'rb')
    s = gzip_file_handle.read()
    gzip_file_handle.close()
    output = open(extract, 'wb')
    output.write(s)
    output.close()


def remove_unwanted_characters(clean):
    clean = clean.replace('[', '')
    clean = clean.replace(']', '')
    clean = clean.replace('{', '')
    clean = clean.replace('}', '')
    clean = clean.replace("\t", '')
    clean = clean.replace("\n", '')
    return clean


def parse_json_file(from_file):
    f = open(from_file, 'r')
    data = f.read()
    f.close()
    return json.loads(data)


def replace_commas(in_str, replace_with="(comma)"):
    return in_str.replace(",", replace_with)
