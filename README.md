# CoAP_Protocol-FastAPI-PostgreSQL
IoT data storage using CoAP, FastAPI, and PostgreSQL

1. Introduction
With the rapid growth of the Internet of Things (IoT), efficient data transmission and storage methods are critical. This project focuses on storing sensor data received via the CoAP protocol into a PostgreSQL database using FastAPI as the backend framework.
1.1 Project Goals
•	Develop a CoAP-based IoT data collection system.
•	Store the received sensor data into a PostgreSQL database.
•	Provide FastAPI endpoints to retrieve stored data.
•	Use pgAdmin for database management.
1.2 Technologies Used
Technology	Purpose
FastAPI	Web framework for creating APIs
PostgreSQL	Relational database for storing sensor data
pgAdmin	GUI-based PostgreSQL management tool
SQLAlchemy	ORM for database interactions
aiocoap	Python CoAP library for communication
Uvicorn	ASGI server for running FastAPI

2. Project Setup & Configuration
This section explains how the project was set up, including database creation, API development, and CoAP integration.
2.1 Setting Up PostgreSQL
1.	Installed PostgreSQL and pgAdmin.
2.	Created a new database named coap_data in pgAdmin.
3.	Created a table named sensor_data using the following SQL command:
4.	Inserted sample data to verify table functionality:
2.2 FastAPI Project Structure
The project is structured as follows:


pgsql

/new
│── coap_server.py   # Handles CoAP communication
│── database.py      # Database connection & setup
│── main.py          # FastAPI server setup
│── models.py        # Defines database schema
2.3 Database Connection in FastAPI
•	Established a connection to PostgreSQL using SQLAlchemy in database.py:
python
CopyEdit
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:yourpassword@localhost:5432/IOT_DATA"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
•	This ensures that FastAPI interacts with the PostgreSQL database efficiently.

3. API Endpoints
FastAPI provides endpoints to interact with the database and the CoAP server.
3.1 Checking API Status
•	Endpoint: /
•	Method: GET
•	Description: Returns API status.
•	Response Example
{"message": "API is running"}
3.2 Fetching Sensor Data from CoAP Server
•	Endpoint: /coap_read_data/
•	Method: POST
•	Description: Connects to the CoAP server and retrieves temperature and humidity data.
•	Response Example:
{
  "status": "success",
  "temperature": 26.5,
  "humidity": 60
}
3.3 Storing Sensor Data into PostgreSQL
•	Endpoint: /store_sensor_data/
•	Method: POST
•	Description: Saves CoAP sensor data into the database.
•	Request Body:
{
  "temperature": 26.5,
  "humidity": 60
}
•	Response Example:
{
  "status": "success",
  "message": "Sensor data stored successfully!"
}
3.4 Retrieving Stored Sensor Data
•	Endpoint: /get_sensor_data/
•	Method: GET
•	Description: Retrieves all sensor data stored in the database.
•	Response Example:
[
  {
    "id": 1,
    "temperature": 26.5,
    "humidity": 60,
    "timestamp": "2025-03-17T10:22:05.565919+05:30"
  }
]

4. pgAdmin Operations
4.1 Executing Queries in pgAdmin
•	Verified database insertion using:
sql
SELECT * FROM coap_logs ORDER BY id ASC;
•	Confirmed that sensor data is stored correctly.
4.2 Managing Data
•	Inserted sample data manually for testing.
•	Checked live updates from the FastAPI endpoints.

5. Debugging & Troubleshooting
5.1 API Not Loading (/docs Swagger UI)
•	Issue: "Failed to load API definition. Internal Server Error /openapi.json"
•	Solution:
o	Ran FastAPI with debug mode:
uvicorn main:app --reload --log-level debug
o	Checked logs for missing dependencies.
5.2 Connection Issues Between FastAPI & PostgreSQL
•	Issue: FastAPI failing to fetch data from PostgreSQL.
•	Solution:
o	Verified that PostgreSQL service was running:
sudo service postgresql start
o	Checked credentials in DATABASE_URL.
o	Tested connection manually using:
psql -U postgres -d coap_data
5.3 CoAP Server Not Responding
•	Issue: No response from the CoAP server.
•	Solution:
o	Ensured the CoAP server was running properly.
o	Checked the firewall settings for UDP port 5683.

6. Conclusion
This project successfully integrates CoAP, FastAPI, and PostgreSQL to create a complete IoT data storage and retrieval system.
6.1 Key Achievements
✅ Set up PostgreSQL and pgAdmin for managing sensor data.
✅ Developed a CoAP client to communicate with IoT devices.
✅ Implemented FastAPI endpoints for storing and retrieving sensor data.
✅ Debugged common issues related to API failure and database connectivity.
