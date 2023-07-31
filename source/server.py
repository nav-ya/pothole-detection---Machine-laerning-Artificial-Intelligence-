import json
import numpy as np
import cv2

# send requests
import requests

# image pre processing
from PIL import Image

# used to run the server
from flask import Flask, request, render_template_string

# used for pothole detection
from ultralytics import YOLO

# used for visualization
import folium

#app = Flask(name)
app = Flask(__name__)


model = YOLO("./best.pt")

GMAPS_API_KEY="API_KEY"
detected_pothole_locations = []

# initial location is set to hyderabad
map_center = ("17.3850", "78.4867")
m = folium.Map(location=map_center, zoom_start=12)

@app.route("/", methods=["GET"])
def index():
    return json.dumps({"message": "Hello from rasp!"})

@app.route("/detect_pothole", methods=["POST"])
def detect_pothole():
    try:
        coordinates = request.form["data"]
        #coordinates = json.loads(coordinates)
        
        uploaded_image = request.files["image"]
        print("coordinates",coordinates)
        print(uploaded_image)
        print(coordinates['lat'])


        image_data = uploaded_image.read()
        image = np.asarray(bytearray(image_data), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        results = model(image)

        pothole_found = True if len(results[0].boxes) > 0 else False

        if pothole_found:
            lat = coordinates['lat']
            lng = coordinates['lng']
            print(coordinates['lat'])
            print(coordinates['lng'])
            marker = folium.Marker(location=(lat, lng))
            marker.add_to(m)

            return json.dumps({"pothole_found": True})

        return json.dumps({"pothole_found": False})
    except Exception as e:
        return json.dumps({"error": str(e)})
    
@app.route("/show_pothole", methods=["GET"])
def show_pothole():
    try:
       html = m._repr_html_()
       return render_template_string(html)
    except Exception as e:
        return json.dumps({"error": str(e)})
