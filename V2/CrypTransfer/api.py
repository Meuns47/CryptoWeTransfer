from typing import Optional
from fastapi import FastAPI, Form, Request, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from cryptography.fernet import Fernet, InvalidToken
from urllib.parse import unquote
import os
import secrets
import shutil
import hashlib

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Clé pour le chiffrement
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Fonction pour chiffrer le nom de fichier
def encrypt_file_id(file_id):
    return cipher_suite.encrypt(file_id.encode()).decode()

# Fonction pour déchiffrer le nom de fichier
def decrypt_file_id(encrypted_file_id):
    return cipher_suite.decrypt(encrypted_file_id.encode()).decode()

# Fonction pour chiffrer le mot de passe
def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

# Fonction pour déchiffrer le mot de passe
def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

# Dictionnaire pour save le fichier upload et le mot de passe
file_storage = {}

# Affiche la page index.html
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Affiche la pahe upload.html
@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Fonction pour upload un fichier
@app.post("/upload/")
async def upload_file(request: Request, file: Optional[UploadFile] = File(...), password: str = Form(...)):
    # Récupère le nom du fichier
    filename = file.filename
 
    # Générer un identifiant unique pour le fichier
    file_id = secrets.token_urlsafe(8)
    
    # Chiffrer le nom de fichier
    encrypted_file_name = encrypt_file_id(filename)

    # Créer le chemin du dossier "uploads" s'il n'existe pas
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Créer le chemin du fichier
    file_path = os.path.join("uploads", encrypted_file_name)
    
    # Sauvegarde le fichier
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Chiffre le mot de passe
    encrypted_password = encrypt_password(password)

    # Stocke l'identifiant du fichier chiffré avec le mot de passe chiffré et le nom du fichier chiffré
    file_storage[file_id] = {"file_path": file_path, "password": encrypted_password}

    # Retourner l'identifiant du fichier pour être utilisé dans le modèle
    return templates.TemplateResponse("upload.html", {"request": request, "file_id": file_id})


# Affiche la page download.html
@app.get("/download/{file_id}/", response_class=HTMLResponse)
async def download_page(request: Request, file_id: str):
    return templates.TemplateResponse("download.html", {"request": request, "file_id": file_id})

# Fonction pour télécharger le fichier 
@app.post("/download/{file_id}/")
async def download_file(request: Request, file_id: str, password: str = Form(...)):

    try:
        # Vérifier si l'identifiant de fichier existe dans le stockage
        if file_id in file_storage:

            # Récupère les infos du fichier 
            file_info = file_storage[file_id]
            # Récupère le chemin du fichier
            file_path = file_info["file_path"]
            # Récupère le mot de passe lié au fichier
            stored_encrypted_password = file_info["password"]
            
            # Déchiffrement du mot de passe stocké
            stored_password = decrypt_password(stored_encrypted_password)

            # Vérification du mot de passe fourni par l'utilisateur
            if password == stored_password:

                # Extraire le nom de fichier original du chemin stocké
                stored_decrypted_filename = os.path.basename(unquote(file_path))
                file_name = decrypt_file_id(stored_decrypted_filename)
                
                # Retourner le fichier pour le téléchargement
                return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename={file_name}"})
            else:
                # Mot de passe incorrect
                return templates.TemplateResponse("download.html", {"request": request, "file_id": file_id, "error_message": "Invalid password."})
        else:
            # Fichier non trouvé
            return templates.TemplateResponse("download.html", {"request": request, "file_id": file_id, "error_message": "File not found."})
    except InvalidToken:
        # Token Fernet invalide
        raise HTTPException(status_code=400, detail="Invalid token")

