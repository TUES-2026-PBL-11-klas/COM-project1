#!/bin/bash

echo "Building images..."
docker build -t martin590/com-project1:api-gateway ./api-gateway
docker build -t martin590/com-project1:quiz-service ./quiz-service
docker build -t martin590/com-project1:user-service ./user-service
docker build -t martin590/com-project1:result-service ./result-service

echo "Pushing images (optional)..."

echo "Updating Helm..."
helm upgrade --install quiz-platform ./quiz-chart -n quiz-platform

echo "Starting Port-Forward..."
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80

echo "Restarting pods to apply changes..."
kubectl rollout restart deployment -n quiz-platform