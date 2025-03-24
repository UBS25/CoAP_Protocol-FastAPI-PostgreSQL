from fastapi import FastAPI, HTTPException, Query, Depends
import asyncio
import aiocoap
import json
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

app = FastAPI()

# ✅ PostgreSQL Database Configuration
DATABASE_URL = "postgresql://postgres:Ushabs25@localhost:5432/COAP_IOT"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# ✅ Define Database Tables
class ConfigLog(Base):
    __tablename__ = "config_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

class CoapLog(Base):
    __tablename__ = "coap_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    response_value = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

# ✅ Create Tables
Base.metadata.create_all(bind=engine)

# ✅ Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Store Configurations in Memory
# ✅ Store Configurations in Memory (Define Before Usage)
config = {"ip_address": None, "port": None, "connected": False}

# ✅ Load the latest configuration from the database on startup
@app.on_event("startup")
def load_config_on_startup():
    db = SessionLocal()
    latest_config = db.query(ConfigLog).order_by(ConfigLog.id.desc()).first()
    if latest_config:
        config["ip_address"] = latest_config.ip_address
        config["port"] = latest_config.port
        config["connected"] = False  # Default not connected
    db.close()

# ✅ Set Config Endpoint (POST) - Stores in config_logs
@app.post("/coap_set_config/")
async def set_config(
    ip_address: str = Query(..., description="CoAP Server IP Address"),
    port: int = Query(..., description="CoAP Server Port"),
    db: Session = Depends(get_db)
):
    """
    Store configuration settings in the database.
    If the IP and Port exist, update the timestamp; otherwise, insert new.
    """
    existing_entry = db.query(ConfigLog).filter_by(ip_address=ip_address, port=port).first()

    if existing_entry:
        # ✅ Update existing entry timestamp
        existing_entry.timestamp = datetime.utcnow()
        db.commit()
        return {"status": "updated", "message": "Configuration already exists, timestamp updated!", "config": {
            "ip_address": existing_entry.ip_address,
            "port": existing_entry.port
        }}

    # ✅ Insert new entry
    new_config = ConfigLog(ip_address=ip_address, port=port)
    db.add(new_config)
    db.commit()

    return {"status": "success", "message": "New configuration stored!", "config": {
        "ip_address": new_config.ip_address,
        "port": new_config.port
    }}


# ✅ Updating ip address and port number
@app.put("/coap_update_config/")
async def update_config(
    id: int = Query(..., description="Row ID to update"),
    new_ip: str = Query(None, description="New CoAP Server IP Address"),
    new_port: int = Query(None, description="New CoAP Server Port"),
    db: Session = Depends(get_db)
):
    """
    Update an existing configuration entry based on ID.
    Allows updating IP and Port without checking for duplicates.
    Timestamp remains unchanged.
    """

    existing_entry = db.query(ConfigLog).filter(ConfigLog.id == id).first()

    if not existing_entry:
        raise HTTPException(status_code=404, detail="Configuration not found!")

    # ✅ Directly update IP and Port without checking for uniqueness
    if new_ip:
        existing_entry.ip_address = new_ip.strip()
    if new_port:
        existing_entry.port = new_port

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Database constraint error! Try removing the UNIQUE constraint from (ip_address, port)."
        )

    return {
        "status": "success",
        "message": "Configuration updated successfully without modifying the timestamp!",
        "config": {
            "id": existing_entry.id,
            "ip_address": existing_entry.ip_address,
            "port": existing_entry.port,
            "timestamp": existing_entry.timestamp  # Returning unchanged timestamp
        },
    }

# ✅ Connect to CoAP Server (POST)
@app.post("/coap_connect/")
async def connect_coap_server():
    """
    Establish a connection to the CoAP server only after clicking 'Connect'.
    """
    if not config["ip_address"] or not config["port"]:
        raise HTTPException(status_code=400, detail="CoAP Server configuration is not set!")

    config["connected"] = True  # ✅ Update status

    return {"status": "success", "message": "Connected to CoAP server!"}

# ✅ Read Sensor Data (POST)
@app.post("/coap_read_data/")
async def read_data(
    message: str = Query(..., description="Sensor data request (e.g., temperature, pressure)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve sensor data from the CoAP server and log it in PostgreSQL.
    """
    if not config["connected"]:
        raise HTTPException(status_code=400, detail="CoAP Server is not connected!")

    coap_url = f"coap://{config['ip_address']}:{config['port']}/sensor"
    request = aiocoap.Message(code=aiocoap.GET, uri=coap_url)
    request.payload = message.encode()

    try:
        protocol = await aiocoap.Context.create_client_context()
        response = await protocol.request(request).response
        response_text = response.payload.decode()

        print(f"📩 RAW CoAP Response: {response_text}")

        # ✅ Directly process float response instead of JSON parsing
        try:
            response_value = float(response_text)  # Convert to float
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid response format from CoAP server!")

        # ✅ Log Data into PostgreSQL
        new_entry = CoapLog(
            ip_address=config["ip_address"],
            port=config["port"],
            message=message,
            response_value=response_value
        )
        db.add(new_entry)
        db.commit()

        return {
            "status": "success",
            "message": message,
            "response": response_value
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect: {str(e)}")