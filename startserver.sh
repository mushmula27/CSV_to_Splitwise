#!/usr/bin/env bash
export FLASK_APP=CSV_to_Splitwise.py
export FLASK_DEBUG=1

flask run

# if creating a new sh file, always run "chmod 777 startserver.sh" in terminal to make this executable!
