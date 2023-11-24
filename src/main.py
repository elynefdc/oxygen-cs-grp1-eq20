import logging
import os
import time
import json
import requests
from dotenv import load_dotenv
from signalrcore.hub_connection_builder import HubConnectionBuilder
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from src.db_map import UserEvent, SystemEvent, Base

load_dotenv()

class Main:
    def __init__(self):
        """Setup environment variables and default values."""
        self._hub_connection = None
        self.HOST = os.environ.get("HOST", "https://hvac-simulator-a23-y2kpq.ondigitalocean.app")  # Setup your host here
        self.TOKEN = os.environ.get("TOKEN", "t3ivYx3wZ5")  # Setup your token here

        self.TICKETS = 2  # Setup your tickets here
        self.T_MAX = os.environ.get("T_MAX", 50)  # Setup your max temperature here
        self.T_MIN = os.environ.get("T_MIN", 0) # Setup your min temperature here
        self.DATABASE = os.environ.get("DATABASE", "postgres")  # Setup your database here

        self.engine = create_engine(f"postgresql+psycopg2://postgres:postgres@{os.environ.get.POSTGRES_HOST}:5432/{self.DATABASE}")
        Base.metadata.create_all(self.engine)

    def __del__(self):
        if self._hub_connection != None:
            self._hub_connection.stop()

    def setup(self):
        """Setup Oxygen CS."""
        self.set_sensorhub()

    def start(self):
        """Start Oxygen CS."""
        self.setup()
        self._hub_connection.start()

        print("Press CTRL+C to exit.", flush=True)
        while True:
            time.sleep(2)

    def set_sensorhub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )

        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened.", flush=True))
        self._hub_connection.on_close(lambda: print("||| Connection closed.", flush=True))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}", flush=True)
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            date = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)

            self.send_event_to_database(date, temperature)

        except Exception as err:
            print(err, flush=True)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKETS}")
        details = json.loads(r.text)
        print(details, flush=True)
        self.send_event_to_database(datetime.now(timezone.utc), details["Response"])

    def send_event_to_database(self, timestamp, event):
        """Save sensor data into database."""
        try:
            with Session(self.engine) as session:
                if type(event) is str:
                    data_event = SystemEvent(
                        name=event,
                        timestamp=timestamp
                    )

                elif type(event) is float:
                    data_event = UserEvent(
                        temperature=event,
                        timestamp=timestamp
                    )
                session.add_all([data_event])
                session.commit()

            pass
        except requests.exceptions.RequestException as e:
            print(e)
            pass


if __name__ == "__main__":
    main = Main()
    main.start()
