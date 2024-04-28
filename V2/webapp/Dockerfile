# Utilisez l'image officielle de Node.js comme base
FROM node:14


# Créez un répertoire de travail
WORKDIR /app

# Copiez le fichier package.json et package-lock.json dans le répertoire de travail
COPY package*.json ./

# Installez les dépendances
RUN npm install

# Copiez le reste des fichiers dans le répertoire de travail
COPY . .

# Exposez le port 3000
EXPOSE 3000

# Démarrez l'application
CMD ["npm", "run", "dev"]