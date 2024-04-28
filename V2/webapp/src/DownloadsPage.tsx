import { useParams } from "react-router-dom";
import { useState } from "react";
import CryptoJS from "crypto-js";

function DownloadsPage() {
  const { id } = useParams();
  const [password, setPassword] = useState("");

  const handleSubmit = (event: { preventDefault: () => void }) => {
    event.preventDefault();
    const hashedPassword = CryptoJS.SHA256(password).toString();
    const formData = new FormData();
    formData.append("file_id", id!);
    formData.append("password", hashedPassword);

    fetch("http://localhost:8000/download", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        console.log(response);
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const hashedFileName = response.headers.get("Content-Disposition");

        if (!hashedFileName) {
          throw new Error("No Content-Disposition header found");
        }

        return response.blob();
      })
      .then(async (blob) => {
        console.log(blob);
        const arrayBuffer = await blobToArrayBuffer(blob);
        console.log(arrayBuffer);
        const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
        console.log(wordArray);
        const encryptedData = wordArray.toString(CryptoJS.enc.Base64); // Convertir le WordArray en chaîne Base64 pour le décryptage
        const decrypted = CryptoJS.AES.decrypt(
          encryptedData, // Passer la chaîne chiffrée
          hashedPassword,
          {
            mode: CryptoJS.mode.CFB,
            padding: CryptoJS.pad.Pkcs7,
          }
        );

        console.log(decrypted);

        const decryptedText = decrypted.toString(CryptoJS.enc.Utf8); // Convertir le résultat décrypté en texte UTF-8

        const decryptedBlob = new Blob([decryptedText], {
          type: "application/octet-stream",
        });
        const url = window.URL.createObjectURL(decryptedBlob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = "decrypted_file.png"; // Utiliser le nom de fichier original ou extrait du Content-Disposition
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        console.log("Success:", decryptedText);
      })
      .catch((error) => {
        console.error("Error downloading the file:", error);
      });
  };

  return (
    <div>
      <h1>Download ID: {id}</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
        />
        <button type="submit">Download</button>
      </form>
    </div>
  );
}

export default DownloadsPage;

function blobToArrayBuffer(blob: Blob): Promise<ArrayBuffer> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      resolve(reader.result as ArrayBuffer);
    };
    reader.onerror = (e) => {
      reject(new Error("Failed to read blob to arrayBuffer"));
    };
    reader.readAsArrayBuffer(blob);
  });
}
