import asyncio
import websockets
import json
import random

# Store active WebSocket connections
active_connections = set()

# List of commands to trigger randomly
commands = [
	{"EventID": "all_buff_heal"},
	{"EventID": "all_buff_full_restore"},
	{"EventID": "all_debuff_hurt"},
	{"EventID": "all_debuff_hp_shuffle"},
	{"EventID": "all_buff_hp_average"},
	{"EventID": "all_goal_dec"},
	{"EventID": "all_goal_inc"},
	{"EventID": "all_teleport_shuffle"},
	{"EventID": "all_teleport_start"},
	{"EventID": "all_teleport_rand"},
	{"EventID": "all_cart_spread"},
	{"EventID": "all_stun_enemies"},
	{"EventID": "all_buff_resurrect_rand"},
	{"EventID": "all_buff_resurrect_all"},
	{"EventID": "all_debuff_kill_rand"},
	{"EventID": "item_health_small"},
    {"EventID": "item_health_med"},
    {"EventID": "item_health_big"},
    {"EventID": "item_crystal"},
    {"EventID": "item_nade_stun"},
    {"EventID": "item_nade_shock"},
    {"EventID": "item_nade_expl"},
    {"EventID": "item_nade_f1"},
    {"EventID": "item_nade_duck_f1"},
    {"EventID": "item_mine_stun"},
    {"EventID": "item_mine_shock"},
    {"EventID": "item_mine_expl"},
    {"EventID": "item_rubber_duck"},
    {"EventID": "item_book_roll"},
    {"EventID": "item_book_speed"},
    {"EventID": "item_book_energy"},
    {"EventID": "item_book_health"},
    {"EventID": "item_book_range"},
    {"EventID": "item_book_strength"},
    {"EventID": "item_book_jump"},
    {"EventID": "item_drone_roll"},
    {"EventID": "item_drone_gravity"},
    {"EventID": "item_drone_feather"},
    {"EventID": "item_drone_energy"},
    {"EventID": "item_drone_shield"},
    {"EventID": "item_sphere_gravity"},
    {"EventID": "item_frying_pan"},
    {"EventID": "item_inflatable_hammer"},
    {"EventID": "item_sword"},
    {"EventID": "item_baseball_bat"},
    {"EventID": "item_sledge_hammer"},
    {"EventID": "item_valuable_tracker"},
    {"EventID": "item_extraction_tracker"},
    {"EventID": "item_cart_small"},
    {"EventID": "item_cart_medium"},
    {"EventID": "item_tranq"},
    {"EventID": "item_handgun"},
    {"EventID": "item_shotgun"},
    {"EventID": "spawn_duck", "Args": []},
    {"EventID": "spawn_spewer", "Args": []},
    {"EventID": "spawn_upscream", "Args": []},
    {"EventID": "spawn_alien", "Args": []},
    {"EventID": "spawn_baby", "Args": []},
    {"EventID": "spawn_thinman", "Args": []},
    {"EventID": "spawn_hidden", "Args": []},
    {"EventID": "spawn_frog", "Args": []},
    {"EventID": "spawn_bowtie", "Args": []},
    {"EventID": "spawn_huntsman", "Args": []},
    {"EventID": "spawn_trudge", "Args": []},
    {"EventID": "spawn_clown", "Args": []},
    {"EventID": "spawn_robe", "Args": []},
    {"EventID": "spawn_reaper", "Args": []}
]

async def handle_connection(websocket):
        print("Client connected.")
        # Add the new connection to the set
        active_connections.add(websocket)
        config = {
                  "type": "config",
                  "data": json.dumps({"isAllPlayers": True})  # Properly escape nested JSON
        }
        await websocket.send(json.dumps(config))
        try:
            async for message in websocket:
                print(f"Received: {message}")
        finally:
            # Remove the connection when it closes
            active_connections.remove(websocket)

async def broadcast(message):
    """Broadcast a message to all connected clients."""
    if not active_connections:
        print("No active connections to broadcast to.")
        return
    # Send the message to all clients
    for websocket in list(active_connections):  # Use a copy to avoid runtime errors
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed while broadcasting.")
            active_connections.remove(websocket)

async def trigger_random_event():
    """Trigger a random event every minute."""
    while True:
        # Wait for 10 seconds
        await asyncio.sleep(60)

        # Select a random command
        command = random.choice(commands)
        event_id = command["EventID"]

        # Format the WebSocket payload
        payload = {
            "type": "event",
            "data": f"UserName=RandomBot&Cost=0&EventID={event_id}&Lang=RU&ExtraInfo=",
        }

        # Broadcast the payload
        print(f"Triggering random event: {event_id}")
        await broadcast(json.dumps(payload))

async def start_server():
    # Start the WebSocket server
    async with websockets.serve(handle_connection, "127.0.0.1", 13715):
        print("WebSocket server running on ws://127.0.0.1:13715")
        # Run the random event trigger in parallel
        await asyncio.gather(trigger_random_event())

# Start the server
asyncio.run(start_server())