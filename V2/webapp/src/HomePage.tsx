import React, { useState } from "react";
import CryptoJS from "crypto-js";

function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [password, setPassword] = useState("");
  const [expiryTime, setExpiryTime] = useState(0);
  const [singleUseLink, setSingleUseLink] = useState(false);
  const [email, setEmail] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFile(event.target.files?.[0] || null);
  };

  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(event.target.value);
  };

  const handleExpiryTimeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setExpiryTime(new Date(event.target.value).getTime());
  };

  const handleSingleUseLinkChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setSingleUseLink(event.target.checked);
  };

  const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value);
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (file) {
      const reader = new FileReader();

      reader.onload = function (event) {
        if (event.target) {
          const hashedPassword = CryptoJS.SHA256(password).toString();
          
          const arrayBuffer = (event.target.result as ArrayBuffer).slice(0);
          const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
          const encrypted = CryptoJS.AES.encrypt(
            wordArray,
            hashedPassword
          ).toString();
          
          const encryptedFileName = CryptoJS.AES.encrypt(
            file.name,
            hashedPassword
          ).toString();
          
          // const unencryptedFileName = CryptoJS.AES.decrypt(
          //   encryptedFileName,
          //   hashedPassword
          // ).toString(CryptoJS.enc.Utf8);

          // Create a new FormData instance
          const formData = new FormData();

          // Create a blob from the encrypted file string
          const blob = new Blob([encrypted], { type: "text/plain" });

          // Append the blob to the FormData instance
          formData.append("file", blob, encryptedFileName);

          formData.append("password", hashedPassword);

          formData.append("expiryTime", expiryTime.toString());

          formData.append("singleUseLink", singleUseLink.toString());

          formData.append("email", email);

          // console.log({ formData });

          // Send encrypted file to your server

          fetch("http://localhost:8000/upload", {
            method: "POST",
            body: formData,
          })
            .then((response) => response.json())
            .then((data) => {
              console.log("Success:", data);
              // Here you can handle the unique link returned by the server
            })
            .catch((error) => {
              console.error("Error:", error);
            });
        }
      };

      reader.readAsArrayBuffer(file);
    }
  };

  return (
    <div>
      <h1>Plateforme de stockage de fichiers sécurisée</h1>

      <form
        id="uploadForm"
        encType="multipart/form-data"
        onSubmit={handleSubmit}
      >
        <h2>Téléverser un fichier</h2>
        <input
          type="file"
          id="file"
          name="file"
          onChange={handleFileChange}
          required
        />
        <br />

        <input
          type="password"
          id="encryptionPassword"
          name="encryptionPassword"
          placeholder="Mot de passe de chiffrement"
          onChange={handlePasswordChange}
          required
        />
        <br />
        <input
          type="date"
          id="expiryTime"
          min={
            new Date(new Date().getTime() + 24 * 60 * 60 * 1000)
              .toISOString()
              .split("T")[0]
          }
          name="expiryTime"
          placeholder="Délai d'expiration"
          onChange={handleExpiryTimeChange}
        />
        <br />

        <label htmlFor="singleUseLink">Lien à usage unique</label>
        <input
          type="checkbox"
          id="singleUseLink"
          name="singleUseLink"
          onChange={handleSingleUseLinkChange}
        />
        <br />

        <input
          type="email"
          id="email"
          name="email"
          placeholder="Email pour envoyer le lien"
          onChange={handleEmailChange}
          required
        />
        <br />

        <input type="submit" value="Téléverser" />
      </form>

      {/* Here you can add the download form */}
    </div>
  );
}

export default HomePage;
