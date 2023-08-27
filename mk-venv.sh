#!/bin/bash

python -mm venv venv
echo "Deny from all" > venv/.htaccess
touch config.py
echo 
echo "Environment created, edit config.py to add your settings"
