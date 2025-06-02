#!/bin/bash

echo "Starting MongoDB database, backend API, and frontend application."

if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker and Docker Compose are required but not installed."
    echo "Please install Docker and Docker Compose first."
    exit 1
fi

if [ ! -f ./backend/.env ]; then
    echo "Warning: No .env file found"
fi

echo "Building and starting containers..."
docker-compose up -d --build

echo "-------------------------------------------------------"
echo "Pametni paketnik"
echo "-------------------------------------------------------"
echo "Frontend: http://localhost:8080"
echo "Backend API: http://localhost:3000"
echo "MongoDB: localhost:27018"
echo "-------------------------------------------------------"
echo "To stop the application, run: docker-compose down"
echo "-------------------------------------------------------"
