import cv2
import numpy as np
from flask import Flask, request, render_template_string
from flask_restful import Resource, Api
import requests
from werkzeug.utils import secure_filename
import os


hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

app = Flask(__name__)
api = Api(app)


@app.route('/')
def index():
    return ('Witaj w Wielkim Liczniku Ludzi!<br>'
            'Wybierz jedną z opcji:<br>'
            '<a href="http://127.0.0.1:5000/people-counter">http://127.0.0.1:5000/people-counter</a><br>'
            '<a href="http://127.0.0.1:5000/url-form">http://127.0.0.1:5000/people-counter-url</a><br>'
            '<a href="http://127.0.0.1:5000/upload-form">http://127.0.0.1:5000/upload-form</a>')


def create_upload_folder():
    folder = 'pliki_z_posta'
    if not os.path.exists(folder):
        os.makedirs(folder)


create_upload_folder()


@app.route('/upload-form')
def upload_form():
    return render_template_string('''
        <h1>Prześlij obraz do analizy</h1>
        <form action="/people-counter-upload" method="post" enctype="multipart/form-data">
            Wybierz obraz do przesłania:
            <input type="file" name="file">
            <input type="submit" value="Wyślij">
        </form>
    ''')


@app.route('/url-form')
def url_form():
    return render_template_string('''
        <form action="/people-counter-url" method="get">
            Podaj adres URL zdjęcia: <input type="text" name="image_url">
            <input type="submit" value="Wyślij">
        </form>
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


# Część druga: GET który w parametrze otrzymuje link do zdjęcia, które jest w Internecie, pobiera je, a następnie zwraca
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


# Część trzecia: API, które posiada endpoint POST, na który można przesłać zdjęcie,
# a następnie zwraca informację o tym ile znaleziono osób na zdjęciu.
class PeopleCounterUpload(Resource):
    def post(self):
        # Sprawdzanie, czy plik został przesłany
        if 'file' not in request.files:
            return {"error": "Nie znaleziono pliku"}, 400

        file = request.files['file']

        # Sprawdzanie, czy nazwa pliku nie jest pusta
        if file.filename == '':
            return {"error": "Brak wybranego pliku"}, 400

        if file:
            # Zapisanie pliku w bezpiecznej lokalizacji
            filename = secure_filename(file.filename)
            file_path = os.path.join('pliki_z_posta', filename)
            file.save(file_path)

            # Ładowanie i przetwarzanie obrazu
            image = cv2.imread(file_path)

            # Usuwanie zapisanego pliku (opcjonalnie, zależy od wymagań)
            os.remove(file_path)

            if image is None:
                return {"error": "Nie można załadować obrazu"}, 404

            # Wykrywanie ludzi na zdjęciu
            (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

            # Zwrócenie liczby wykrytych osób
            return {"peopleCount": len(rects)}


api.add_resource(PeopleCounter, '/people-counter')
api.add_resource(PeopleCounterURL, '/people-counter-url')
api.add_resource(PeopleCounterUpload, '/people-counter-upload')

if __name__ == '__main__':
    app.run(debug=True)
