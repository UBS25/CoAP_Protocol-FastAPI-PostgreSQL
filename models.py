from sqlalchemy import Column, Integer, String, Numeric
from database import Base

class CoAPServerData(Base):
    _tablename_ = "coap_server_data"

    Server_ID = Column(Integer, primary_key=True, index=True)
    Protocol_name = Column(String, index=True)
    IP_Address = Column(String, index=True)  # Store IPv4 address
    Message = Column(String, index=True)
    Value = Column(Numeric)  # Store sensor value (temperature, etc.)