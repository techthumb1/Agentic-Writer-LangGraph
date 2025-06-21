#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="${PWD}:${PYTHONPATH}"
python langgraph_app/server.py
