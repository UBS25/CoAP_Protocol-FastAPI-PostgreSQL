import asyncio
import json
import asyncpg
from fastapi import FastAPI, HTTPException
from aiocoap import Context, Message, GET

app = FastAPI()

# PostgreSQL Connection Configuration
DATABASE_URL = "postgresql://postgres:Ushabs25@localhost:5432/COAP_IOT"

# ✅ Function to Store Data in PostgreSQL
# ✅ Function to Store or Update Data in PostgreSQL
async def store_data_in_db(ip_address, protocol_name, request_param, response_value):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # ✅ Check if entry exists (same IP & request_param)
        existing_row = await conn.fetchrow(
            "SELECT * FROM coap_server_data WHERE ip_address = $1 AND request_param = $2",
            ip_address, request_param
        )

        if existing_row:
            # ✅ Update existing row instead of inserting a new one
            await conn.execute(
                "UPDATE coap_server_data SET response_value = $1 WHERE ip_address = $2 AND request_param = $3",
                response_value, ip_address, request_param
            )
        else:
            # ✅ Insert new entry if IP & request_param do not exist
            await conn.execute(
                "INSERT INTO coap_server_data (ip_address, protocol_name, request_param, response_value) VALUES ($1, $2, $3, $4)",
                ip_address, protocol_name, request_param, response_value
            )

    finally:
        await conn.close()

# ✅ FastAPI Endpoint to Connect to CoAP Server & Store Data
@app.post("/connect_coap_server/")
async def connect_coap_server(ip_address: str, port: int, message: str):
    try:
        coap_url = f"coap://{ip_address}:{port}/sensor"
        request = Message(code=GET, uri=coap_url)

        protocol = await Context.create_client_context()
        response = await protocol.request(request).response
        response_data = json.loads(response.payload.decode())

        # ✅ Extract the requested value
        response_value = response_data.get(message, "Invalid Parameter")

        # ✅ Store or Update in PostgreSQL
        await store_data_in_db(ip_address, "CoAP", message, response_value)

        return {
            "status": "success",
            "message": message,
            "response_value": response_value
        }

    except Exception as e:
        print(f"❌ CoAP Connection Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect: {str(e)}")
