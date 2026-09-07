"""
Real-Time WebSocket for Packing Stations
Broadcasting scan triggers, live status updates, and audio alerts.
"""
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSockets"])

class ConnectionManager:
    def __init__(self):
        # station_id -> list of active websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, station_id: str):
        await websocket.accept()
        if station_id not in self.active_connections:
            self.active_connections[station_id] = []
        self.active_connections[station_id].append(websocket)

    def disconnect(self, websocket: WebSocket, station_id: str):
        if station_id in self.active_connections:
            if websocket in self.active_connections[station_id]:
                self.active_connections[station_id].remove(websocket)

    async def broadcast_to_station(self, station_id: str, message: dict):
        if station_id in self.active_connections:
            for connection in self.active_connections[station_id]:
                await connection.send_json(message)

ws_manager = ConnectionManager()

@router.websocket("/ws/operator/{station_id}")
async def operator_websocket_endpoint(websocket: WebSocket, station_id: str):
    await ws_manager.connect(websocket, station_id)
    try:
        # Send initial connection greeting
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "station_id": station_id,
            "status": "ONLINE",
            "message": f"Connected to PharmaPack QV Real-Time Stream for Station {station_id}"
        })

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "PING")
            
            if msg_type == "PING":
                await websocket.send_json({"type": "PONG", "station_id": station_id})
            elif msg_type == "TRIGGER_SCAN":
                # Acknowledge barcode trigger from physical scanner
                await websocket.send_json({
                    "type": "SCAN_ACKNOWLEDGED",
                    "order_number": data.get("order_number"),
                    "station_id": station_id
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, station_id)
