#!/bin/bash
# IMPORTANT: You must run this using 'source' for it to work.
# Command: source activate_env.sh

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated."
    echo "Python path: $(which python)"
else
    echo "❌ Error: .venv/bin/activate not found."
    echo "Please ensure the virtual environment exists."
fi
