import datetime
import uuid
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import smtplib
from email.message import EmailMessage
import json


app = FastAPI()

# SMTP
email = "foratoenzo91@gmail.com"
password = "uefnlmxflokqzmdd"
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(email, password)


# BDD
# files = []
json_db_path = 'files_db.json'


app.add_middleware(
    CORSMiddleware,
    # Vous pouvez remplacer "*" par l'URL de votre application React
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)
# Initialiser le fichier JSON s'il n'existe pas


def init_json_db():
    try:
        with open(json_db_path, 'x') as f:
            json.dump([], f)
    except FileExistsError:
        pass


init_json_db()


def read_json_db():
    with open(json_db_path, 'r') as f:
        return json.load(f)


def write_json_db(data):
    with open(json_db_path, 'w') as f:
        json.dump(data, f)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    expiryTime: datetime.datetime = Form(...),
    singleUseLink: bool = Form(...),
    email: str = Form(...)
):
    # Générer un ID unique pour le fichier
    file_id = uuid.uuid4()

    upload_folder = Path('uploads')
    upload_folder.mkdir(exist_ok=True)

    # Encode the filename to a safe format
    file_path = upload_folder.joinpath(str(file_id))

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Envoi de l'email
    send_email(file_id, email)

    # Ajout du fichier à la liste
    files = read_json_db()
    files.append({
        "file_id": str(file_id),
        "file_name": file.filename,
        "password": password,
        "expiration": expiryTime.isoformat(),
        "is_unique": singleUseLink,
    })
    write_json_db(files)

    return {"file_id": str(file_id)}


def send_email(file_id, receiver_email):
    file_link = f"http://localhost:3000/download/{file_id}"
    msg = EmailMessage()
    msg.set_content(
        f"nAccédez au fichier ici: {file_link}", subtype='html')
    msg['Subject'] = 'Nouveau fichier uploadé'
    msg['From'] = email
    msg['To'] = receiver_email

    server.send_message(msg)
    print("Email envoyé")


# Fonction pour télécharger le fichier
@app.post("/download/")
async def download_file(file_id: str = Form(...), password: str = Form(...)):
    files = read_json_db()
    print(files)
    print(file_id)

    try:
        file = next(file for file in files if file["file_id"] == file_id)
        print(file)
        if file["password"] != password:
            raise HTTPException(
                status_code=401, detail="Mot de passe incorrect")
        print("zizi")
        file_path = Path('uploads').joinpath(file["file_id"])
        print(file_path)

        return FileResponse(file_path, filename=file["file_name"])
    except Exception as e:
        print(e)
    raise HTTPException(status_code=500, detail=str(e))
