#!/bin/bash

# Navigate to backend folder
cd backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask backend
echo "Starting Flask backend..."
python app.py &

# Navigate back to project root
cd ..

# If a frontend exists in the future, add its startup command here
# cd frontend && npm install && npm start

echo "🚀 Server is running at: http://127.0.0.1:5000"