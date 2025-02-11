# Usage: python app.py
import os

from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from keras.models import Sequential, load_model
import numpy as np
import argparse
import imutils
import cv2
import time
import uuid
import base64

img_width, img_height = 150, 150
model_path = './models/model.h5'
model_weights_path = './models/weights.h5'
model = load_model(model_path)
# model.load_weights(model_weights_path)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])


def get_as_base64(url):
    return base64.b64encode(request.get(url).content)


def predict(file):
    x = load_img(file, target_size=(img_width, img_height))
    x = img_to_array(x)
    x = np.expand_dims(x, axis=0)
    array = model.predict(x)

    result = array[0]
    answer = np.argmax(result)
    if answer == 0:
        print("Label: Acne vulgaris")
    elif answer == 1:
        print("Label: Atopic Dermatitis")
    elif answer == 2:
        print("Label: Scabies ")
    return answer


def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def template_test():
    return render_template('template.html', label='', sym='', treat='', imagesource='../uploads/skin-bn.jpg')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        import time
        start_time = time.time()
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            result = predict(file_path)
        
            if result == 0:
                label = 'Acne vulgaris'
                sym = """Uninflamed blackheads to pus-filled pimples or large, red and tender bumps."""
                treat = """Prescription creams (eg: chemotherapy)
                or surgery(eg: electrosurgery) to remove the cancer."""
            elif result == 1:
                label = 'Atopic Dermatitis'
                sym = """Skin: rashes, dryness, flakiness, bumps, fissures, peeling, or redness."""
                treat = """Avoid the use of soap and other irritants. Certain creams or ointments may also provide relief from the itching."""
            elif result == 2:
                label = 'scabies'
                sym = """ Intense itching in the area where the mites burrow
                """
                treat = """Scabies can be treated by killing the mites and their eggs with medication that's applied from the neck down and left on for eight hours"""
            
          

            print(result)
            print(file_path)
            filename = my_random_string(6) + filename

            os.rename(file_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("--- %s seconds ---" % str(time.time() - start_time))
            return render_template('template.html', label=label, sym=sym, treat=treat,
                                   imagesource='../uploads/' + filename)


from flask import send_from_directory


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


from werkzeug import SharedDataMiddleware

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads': app.config['UPLOAD_FOLDER']
})

if __name__ == "__main__":
    app.debug = False
    app.run(host='127.0.0.1', port=3000)
