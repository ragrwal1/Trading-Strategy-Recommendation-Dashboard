#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Variables
LOG_DIR="$SCRIPT_DIR/logs"
FRONTEND_DIR="$SCRIPT_DIR/FinanceDashboard"
BACKEND_DIR="$SCRIPT_DIR/Bull_Call_Spread_API"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_LOG="$LOG_DIR/backend.log"
SCRIPT_LOG="$LOG_DIR/deployment.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$SCRIPT_LOG"
}

# Function to handle cleanup on exit
cleanup() {
    log "Cleanup initiated..."
    if [[ -n "$FRONTEND_PID" ]]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        log "Frontend process (PID: $FRONTEND_PID) terminated."
    fi
    if [[ -n "$BACKEND_PID" ]]; then
        kill "$BACKEND_PID" 2>/dev/null || true
        log "Backend process (PID: $BACKEND_PID) terminated."
    fi
    log "Cleanup completed."
    exit
}

# Trap signals to ensure cleanup is done
trap cleanup SIGINT SIGTERM

# Start of the deployment script
log "=== Deployment Script Started ==="

# Pull the latest changes from the repository
log "Pulling latest changes from git..."
if git pull >> "$SCRIPT_LOG" 2>&1; then
    log "Git pull successful."
else
    log "Git pull failed. Exiting."
    exit 1
fi

# Start the frontend
log "Starting frontend..."
cd "$FRONTEND_DIR"
if npm install >> "$SCRIPT_LOG" 2>&1; then
    log "Frontend dependencies installed successfully."
else
    log "Frontend dependencies installation failed. Exiting."
    exit 1
fi

# Run frontend in the background and redirect output to log
npm run dev >> "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
log "Frontend started with PID: $FRONTEND_PID."
cd "$SCRIPT_DIR"  # Return to the script directory

# Start the backend
log "Starting backend..."
cd "$BACKEND_DIR"

# Run backend in the background and redirect output to log
uvicorn BCS_API:app --reload >> "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
log "Backend started with PID: $BACKEND_PID."
cd "$SCRIPT_DIR"  # Return to the script directory

log "Waiting for services to start..."

# Allow a few seconds for logs to populate
sleep 5

# Extract frontend and backend links from logs
FRONTEND_LINK=$(grep -o "http://localhost:[0-9]*" "$FRONTEND_LOG" | head -n 1)
BACKEND_LINK=$(grep -o "http://127.0.0.1:[0-9]*" "$BACKEND_LOG" | head -n 1)

if [[ -n "$FRONTEND_LINK" ]]; then
    log "Frontend link: $FRONTEND_LINK"
    xdg-open "$FRONTEND_LINK" 2>/dev/null || open "$FRONTEND_LINK" 2>/dev/null || log "Failed to open frontend link in browser."
else
    log "Frontend link not found."
fi

if [[ -n "$BACKEND_LINK" ]]; then
    log "Backend link: $BACKEND_LINK"
    xdg-open "$BACKEND_LINK" 2>/dev/null || open "$BACKEND_LINK" 2>/dev/null || log "Failed to open backend link in browser."
else
    log "Backend link not found."
fi

log "=== Deployment Completed Successfully ==="

# Wait for background processes to keep the script running
wait