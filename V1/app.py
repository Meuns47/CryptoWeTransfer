from msilib.schema import File
from flask import Flask, make_response, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from tempfile import NamedTemporaryFile, gettempdir
import mimetypes
from utils import encrypt_file, generate_key, decrypt_file
from io import BytesIO
import os
import uuid


app = Flask(__name__)
# Get the current directory of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create a directory named 'uploads' within the current directory
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Check if the directory exists, if not, create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create a dictionary to store the file extensions
file_extensions = {}

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        password = request.form['password']
        file_id, filename, random_link = encrypt_file(file, password, app.config['UPLOAD_FOLDER'])

        _, file_extension = os.path.splitext(filename)
        file_extensions[random_link] = file_extension

        return redirect(url_for('download_file', link_id=random_link))

    return render_template('upload.html')


@app.route('/download/<link_id>', methods=['GET', 'POST'])
def download_file(link_id):
    if request.method == 'POST':
        password = request.form['password']
        decrypted_data, _ = decrypt_file(link_id, password, app.config['UPLOAD_FOLDER'])

        if not decrypted_data:
            return 'Invalid password or link', 403

        file_extension = file_extensions.get(link_id, '')
        mime_type, _ = mimetypes.guess_type("dummy" + file_extension)  # Déduire le type MIME
        file_name = f"{link_id}{file_extension}"  # Nom du fichier original reconstruit

        response = make_response(decrypted_data)
        response.headers.set('Content-Type', mime_type or 'application/octet-stream')
        response.headers.set('Content-Disposition', f'attachment; filename="{file_name}"')
        return response

    else:
        return render_template('download.html', link_id=link_id)
    
if __name__ == '__main__':
    app.run(debug=True)