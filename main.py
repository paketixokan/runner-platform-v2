from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import json

app = FastAPI(
    title="Runner V2 - Port 8001",
    description="AI Operating System running on port 8001",
    version="2.0"
)

# Static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_personal(websocket, {"type": "welcome", "message": "Connected to V2 on port 8001"})
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {
        "platform": "Runner V2",
        "port": 8001,
        "status": "active",
        "agents": ["Abacus", "GitBot", "ScriptRunner", "Memory", "Emergent", "Cursor", "Orchestrator"]
    }

@app.get("/api/status")
async def status():
    return {
        "platform": "V2",
        "port": 8001,
        "message": "V2 is running separately from V1 (which runs on port 8000)"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            print(f"[V2] Received: {message}")
            
            # Echo back with V2 prefix
            response = {
                "type": "response",
                "from": "V2-8001",
                "original": message,
                "timestamp": str(datetime.now())
            }
            await manager.broadcast(response)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        print("[V2] Client disconnected")

if __name__ == "__main__":
    import uvicorn
    print("="*50)
    print("🚀 Runner V2 Starting on PORT 8001")
    print("="*50)
    print("V1 runs on: http://localhost:8000")
    print("V2 runs on: http://localhost:8001")
    print("="*50)
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
