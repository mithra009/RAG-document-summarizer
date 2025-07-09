#!/bin/sh

# Start FastAPI app in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for FastAPI to start
sleep 5

# Start ngrok tunnel to FastAPI
if [ -n "$NGROK_AUTHTOKEN" ]; then
    ngrok config add-authtoken "$NGROK_AUTHTOKEN"
fi

ngrok http 8000 --log=stdout &
# Wait forever (so container doesn't exit)
wait