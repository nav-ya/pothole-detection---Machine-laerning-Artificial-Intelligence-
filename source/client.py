import requests
import cv2
import time
import geocoder

cap = cv2.VideoCapture(0)
# TODO: Update <server-ip> should be the ip of the device that runs the server inside a network
url = "http://<server-ip>:5000/detect_pothole"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    _, img_encoded = cv2.imencode('.jpg', frame)

    headers = {}
    location = geocoder.ip('me').latlng
    latlng = {'lat': location[0], 'lng': location[1]}
    payload={'data': latlng}
    files=[
      ('image',('image.jpg', img_encoded.tostring(),'image/jpeg'))
    ]

    response = requests.post(url, headers=headers, data=payload, files=files)

    print(response.json())

    time.sleep(5)

cap.release()
cv2.destroyAllWindows()
