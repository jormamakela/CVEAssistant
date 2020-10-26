#!/bin/bash
cd /opt/project
python3 -m assistant download
python3 -m assistant refresh_database
python3 -m assistant gui

