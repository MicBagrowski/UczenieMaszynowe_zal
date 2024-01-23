import cv2
import numpy as np
from flask import Flask, Response, request
from flask_restful import Resource, Api
import requests

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

app = Flask(__name__)
api = Api(app)


class PeopleCounter(Resource):
    def get(self):
        # ładowanie zdjęcia
        image_path = 'G:/projects/GitTutorial/UczMasz/ludzie.jpg'
        image = cv2.imread(image_path)

        # sprawdzenie, czy obraz został poprawnie załadowany
        if image is None:
            return {"error": "Nie można załadować obrazu"}, 404
        image = cv2.resize(image, (700, 400))

        # wykrywanie ludzi na zdjęciu
        (rects, weights) = hog.detectMultiScale(image, winStride=(2, 2), padding=(16, 16), scale=1.01)

        # Rysowanie kwadratów
        policzono_ludzi = len(rects)
        for (x, y, w, h) in rects:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Zamiana zdjęcia na jpeg
        _, jpeg = cv2.imencode('.jpg', image)

        # Wyświetlenie zdjęcia w odpowiedzi
        return Response(jpeg.tobytes(), mimetype='image/jpeg')


api.add_resource(PeopleCounter, '/')


class PeopleCounterURL(Resource):
    def get(self):
        # pobranie url obrazu
        image_url = request.args.get('image_url')

        if not image_url:
            return {"error": "Brak URL obrazu"}, 400

        try:
            # Pobierz obraz z internetu
            response = requests.get(image_url)
            image = np.array(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image, -1)

            # sprawdzenie czy obraz został poprawnie załadowany
            if image is None:
                return {"error": "Nie można załadować obrazu z URL"}, 404

            # wykrywanie ludzi na zdjęciu
            (rects, weights) = hog.detectMultiScale(image, winStride=(2, 2), padding=(16, 16), scale=1.01)

            # Rysowanie kwadratów
            policzono_ludzi = len(rects)
            for (x, y, w, h) in rects:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Zwróć liczbę wykrytych osób
            return {'peopleCount': len(rects)}

        except Exception as e:
            return {"error": str(e)}, 500


api.add_resource(PeopleCounterURL, '/url')

if __name__ == '__main__':
    app.run(debug=True)
