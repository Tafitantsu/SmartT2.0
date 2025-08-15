import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from petri_net import PetriNet

app = FastAPI()

# Allow CORS for the frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
petri_net = PetriNet()

async def simulation_loop():
    """Runs the simulation step and broadcasts the state periodically."""
    while True:
        petri_net.run_step()
        state = petri_net.get_state()
        await manager.broadcast(json.dumps(state))
        await asyncio.sleep(0.1) # Update rate: 10 times per second

@app.on_event("startup")
async def startup_event():
    """Starts the simulation loop when the server starts."""
    asyncio.create_task(simulation_loop())

@app.get("/")
async def get():
    return {"status": "running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            direction = message.get("direction")

            if action == "add_car" and direction in ["NS", "EW"]:
                petri_net.add_car(direction)
            elif action == "pedestrian_request" and direction in ["NS", "EW"]:
                petri_net.pedestrian_request(direction)
            elif action == "toggle_night_mode":
                petri_net.toggle_night_mode()

            # Immediately broadcast the change after a user action
            state = petri_net.get_state()
            await manager.broadcast(json.dumps(state))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
