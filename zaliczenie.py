import cv2
import numpy as np
from flask import Flask, Response, request, render_template_string
from flask_restful import Resource, Api
import requests

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    return render_template_string('''
        <form action="/people-counter-url" method="get">
            Podaj adres URL zdjęcia: <input type="text" name="image_url">
            <input type="submit" value="wyślij">
        </form>>
    ''')

# Część pierwsza: API, które posiada 1 endpoint GET, który czyta z dysku zdjęcie i zwraca informację
# o tym ile znaleziono osób na zdjęciu.
class PeopleCounter(Resource):
    def get(self):
        # ładowanie zdjęcia
        image_path = 'G:/PyCharm/ProjektyPython/ludzie.jpg'
        image = cv2.imread(image_path)

        # sprawdzenie, czy zdjęcie zostało poprawnie załadowane
        if image is None:
            return {"error": "Nie można załadować obrazu"}, 404

        # wykrywanie ludzi na zdjęciu
        (rects, _) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

        # Liczenie osób na zdjęciu
        liczba_osob = len(rects)

        # wyświetlenie odpowiedzi
        return {"liczba_osob": liczba_osob}

api.add_resource(PeopleCounter, '/people-counter')

# Część druga: API, które posiada 2 endpointy, jeden z punktu a., drugi GET który w parametrze
# otrzymuje link do zdjęcia, które jest w Internecie, pobiera je, a następnie zwraca
# informację o tym ile znaleziono osób na zdjęciu.

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

            # Zwróć liczbę wykrytych osób
            return {'peopleCount': len(rects)}

        except Exception as e:
            return {"error": str(e)}, 500

api.add_resource(PeopleCounterURL, '/people-counter-url')

if __name__ == '__main__':
    app.run(debug=True)
