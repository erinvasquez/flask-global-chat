#!/bin/bash

# Print a message indicating that we're killing Gunicorn process
echo "Killing all Gunicorn processes..."

# Kill all processes named gunicorn
pkill -f gunicorn

# Check if pkill succeeded
if [ $? -eq 0 ]; then
    echo "All Gunicorn processes have been successfully killed."
else
    echo "Failed to kill Gunicorn processes or no Gunicorn processes found."
fi

echo "Script execution complete."
