import asyncio
import random
import json
from aiocoap import resource, Message, Context, Code

# Simulated sensor data storage
sensor_data = {
    "temperature": 0.0,
    "humidity": 0.0,
    "pressure": 0.0
}

# Function to generate random sensor values every few seconds
async def generate_sensor_data():
    while True:
        sensor_data["temperature"] = round(random.uniform(20, 35), 2)  # Simulated °C
        sensor_data["humidity"] = round(random.uniform(40, 80), 2)      # Simulated %
        sensor_data["pressure"] = round(random.uniform(950, 1050), 2)   # Simulated hPa

        print(f"📡 Generated Data -> Temperature: {sensor_data['temperature']}°C, "
              f"Humidity: {sensor_data['humidity']}%, Pressure: {sensor_data['pressure']} hPa")
        await asyncio.sleep(5)  # Generate new values every 5 seconds

# Define CoAP resource handler
class SensorResource(resource.Resource):
    async def render_get(self, request):
        try:
            parameter = request.payload.decode('utf-8').strip()

            if parameter in sensor_data:
                response_value = sensor_data[parameter]
                print(f"📩 CoAP Response Sent -> {parameter}: {response_value}")  # ✅ Print response in terminal
                return Message(payload=str(response_value).encode('utf-8'))
            else:
                error_message = "Invalid sensor parameter"
                print(f"❌ CoAP Error: {error_message}")
                return Message(code=Code.BAD_REQUEST, payload=error_message.encode('utf-8'))

        except Exception as e:
            error_message = f"Server Error: {str(e)}"
            print(f"❌ CoAP Server Error: {error_message}")
            return Message(code=Code.INTERNAL_SERVER_ERROR, payload=error_message.encode('utf-8'))

# Setup and start CoAP server
async def main():
    root = resource.Site()
    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('sensor',), SensorResource())

    asyncio.create_task(generate_sensor_data())  # Start data generation in the background

    print("🚀 CoAP Server Running on 192.168.137.243:5683...")
    await Context.create_server_context(root, bind=("192.168.137.243", 5683))

    await asyncio.sleep(1000000)  # Keep server running

if __name__ == "__main__":
    asyncio.run(main())