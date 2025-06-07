if [ ! -f ./backend/.env ]; then
    echo "Warning: No .env file found"
fi

if [ ! -f ../ORV/model/face_embedding_model_dim128.keras ]; then
    echo "Error: Face recognition model not found at ../ORV/model/face_embedding_model_dim128.keras"
    echo "Please train the model first by running:"
    echo "  cd ../ORV/src && python train_face_recognition_model.py"
    exit 1
fi

echo "Building and starting containers..."
docker-compose up -d --build

echo "Waiting for services to start..."
sleep 10

echo "Checking service health..."

    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "Face Recognition API is ready"
        break
    fi
    echo "  Waiting for Face Recognition API... ($timeout seconds remaining)"
    sleep 2
    timeout=$((timeout-2))


echo "Waiting for Backend API..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        echo "✓ Backend API is ready"
        break
    fi
    echo "  Waiting for Backend API... ($timeout seconds remaining)"
    sleep 2
    timeout=$((timeout-2))
done

echo "-------------------------------------------------------"
echo "Frontend: http://localhost:8080"
echo "Backend API: http://localhost:3000"
echo "Face Recognition API: http://localhost:5000"
echo "MongoDB: localhost:27018"
echo "-------------------------------------------------------"
echo "To stop the application, run: docker-compose down"
echo "-------------------------------------------------------"
