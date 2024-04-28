import os
import uuid
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet, InvalidToken
from werkzeug.utils import secure_filename

def generate_key(password, salt):
    password = password.encode()  # Convert the password to bytes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key  # Retourne seulement la clé



def encrypt_file(file, password, upload_folder):
    salt = os.urandom(16)  # Generate a random salt
    key = generate_key(password, salt)  # Only the key is returned
    cipher = Fernet(key)

    data = file.read()
    encrypted_data = cipher.encrypt(data)

    file_id = str(uuid.uuid4())  # Generate a truly unique ID
    random_link = str(uuid.uuid4())
    encrypted_path = os.path.join(upload_folder, random_link)

    with open(encrypted_path, 'wb') as f:
        f.write(salt)  # Write the salt to the file
        f.write(encrypted_data)  # Write the encrypted data to the file

    return file_id, file.filename, random_link


def decrypt_file(link_id, password, upload_folder):
    file_path = os.path.join(upload_folder, link_id)

    if not os.path.exists(file_path):
        return '', ''  # Return two empty strings if the file doesn't exist

    with open(file_path, 'rb') as file:
        salt = file.read(16)  # The salt is the first 16 bytes of the file
        encrypted_data = file.read()

    key = generate_key(password, salt)
    cipher = Fernet(key)

    try:
        decrypted_data = cipher.decrypt(encrypted_data)
    except InvalidToken:
        return '', ''  # Return two empty strings if the password is incorrect

    return decrypted_data, ''  # Return the decrypted data and an empty string for the file extension