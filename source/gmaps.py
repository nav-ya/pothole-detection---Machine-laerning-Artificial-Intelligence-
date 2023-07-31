import io
import json
import torch
import requests
import numpy as np
import cv2
import googlemaps
from PIL import Image
from flask import Flask, request
from ultralytics import YOLO
from pigps import GPS

app = Flask(__name__)

model = YOLO("./best.pt")
gmaps = googlemaps.Client(key="API_KEY")
detected_pothole_locations = []
gmaps.add_layer(
    name="Potholes",
    type="marker",
    data=detected_pothole_locations,  # starts with no potholes
    options={
        "title": "Pothole Locations",
    },
)
apture = cv2.VideoCapture(0)

while True:
    ret, frame = capture.read()
    frame = cv2.resize(frame, (224, 224))
    frame = frame / 255.0

    predictions = model.predict(frame)

    # Check for potholes
    if predictions[0][0] > 0.5:
        gps = GPS()
  # Get the current location
        latitude = gps.lat
        longitude = gps.lon
        timestamp = gps.time

        coordinates = (latitude, longitude)
        detected_pothole_locations.append(coordinates)

        # Update the map
        gmaps.update_layer(
            name="Potholes",
            data=detected_pothole_locations,
        )

        # Show the map
        gmaps.display()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

@app.route("/", methods=["GET"])
def index():
    return json.dumps({"message": "Hello from rasp!"})


@app.route("/detect_pothole", methods=["POST"])
def detect_pothole():
    try:
        coordinates = request.form["data"]
        uploaded_image = request.files["image"]
        print(coordinates)
        print(uploaded_image)

        image_data = uploaded_image.read()
        image = np.asarray(bytearray(image_data), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        results = model(image)

        pothole_found = True if len(results[0].boxes) > 0 else False

        if pothole_found:
            # gmaps logic
            # If potholes are detected, send a POST request to the Google Maps API to add a marker to the map
            # lat = coordinates['lat']
            # lng = coordinates['lng']
            # url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=17&size=400x400&markers=color:red%7C{lat},{lng}&key=API_KEY"
            # response = requests.post(url)

            return json.dumps({"pothole_found": True})

        return json.dumps({"pothole_found": False})
    except Exception as e:
        return json.dumps({"error": str(e)})
