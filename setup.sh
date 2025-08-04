#!/bin/bash

echo "Installing backend dependencies..."
cd backend && pip install -r requirements.txt

echo "Installing frontend dependencies..."
cd ../frontend && npm install

echo "Setup complete. You can now run 'npm run dev' in frontend and 'uvicorn main:app --reload' in backend to start the application."
