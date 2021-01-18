#!/bin/bash
cd /opt/project
python3 -m assistant download
python3 -m assistant parse_data_files
python3 -m assistant
