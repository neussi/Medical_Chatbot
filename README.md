<div style="text-align: center;">
  <img src="./image.png" alt="Logo de l'École Nationale Supérieure Polytechnique de Yaoundé" style="border-radius: 15px; width: 150px; height: auto;">
</div>
<div style="text-align: center;">

## École Nationale Supérieure Polytechnique de Yaoundé
</div>
<div style="text-align: center;">

# Documentation du Projet Chatbot WhatsApp pour le Diagnostic Médical 🤖💻📱
</div>

## Introduction
Ce projet vise à développer un chatbot intégré à WhatsApp pour aider les utilisateurs à déterminer leur état de santé en posant des questions sur leurs symptômes et en recommandant des médecins ou des traitements appropriés. Le chatbot utilisera un moteur d'inférence pour interpréter les symptômes des patients et fournir des suggestions de diagnostic.

## Objectifs
- Fournir une interface conviviale via WhatsApp pour interagir avec les utilisateurs.
- Poser des questions sur les symptômes pour aider à déterminer un diagnostic probable.
- Recommander des médecins ou des traitements en fonction du diagnostic.
- Permettre à l'utilisateur d'accéder à son dernier bilan de santé.
- Intégrer le moteur d'inférence pour une prise de décision automatique.

## Fonctionnalités
1. **Communication via WhatsApp** 📲 :
   - Envoi et réception de messages via l'API WhatsApp (Twilio).
   - Multi-langues : Français et Anglais.
2. **Diagnostic médical basé sur les symptômes** 🩺 :
   - Analyse des symptômes fournis par l'utilisateur.
   - Génération d'un diagnostic probable.
3. **Recommandations personnalisées** 🏥 :
   - Suggestions de médecins ou de traitements.
4. **Accès aux bilans de santé** 📋 :
   - Récupération des informations depuis une plateforme de gestion des patients.

## Outils et Technologies
1. **Framework Backend** : Django 🐍
   - Gestion des utilisateurs et des patients.
   - Intégration avec le moteur d'inférence.
2. **API de Communication** : Twilio WhatsApp API 🔗
   - Envoi et réception de messages WhatsApp.
   - Notifications pour les utilisateurs.
3. **Base de Données** : PostgreSQL 🛢️
   - Stockage des utilisateurs, patients et historiques de diagnostic.
4. **Moteur d'inférence** :
   - Implémentation d’une logique d’analyse des symptômes pour déterminer un diagnostic.

## Architecture du Projet
1. **Frontend (WhatsApp)** :
   - Interface utilisateur pour l’interaction avec le chatbot.
2. **Backend (Django)** :
   - Réception des messages et traitement des données.
   - Gestion des réponses du moteur d'inférence.
3. **API de Communication (Twilio)** :
   - Interface entre WhatsApp et le backend.

## Workflow du Chatbot
1. L'utilisateur envoie un message au chatbot via WhatsApp.
2. Le backend Django reçoit le message via l'API Twilio.
3. Le moteur d'inférence analyse les symptômes envoyés par l'utilisateur.
4. Une réponse est générée :
   - Diagnostic probable.
   - Recommandations (médecins, traitements, etc.).
5. Le chatbot envoie la réponse à l'utilisateur via WhatsApp.

## Déploiement
1. **Serveur** :
   - Déploiement du backend Django sur un serveur cloud (Heroku, AWS, etc.).
2. **API Twilio** :
   - Configuration de l’API pour gérer les messages WhatsApp.
3. **Base de Données** :
   - Configuration et connexion à une base PostgreSQL.

## Instructions pour l’Installation
1. Clonez le dépôt GitHub :
   ```bash
   git clone https://github.com/neussi/Medical_Chatbot.git
   ```
2. Installez les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```
3. Configurez les variables d'environnement :
   - **TWILIO_ACCOUNT_SID** : SID du compte Twilio.
   - **TWILIO_AUTH_TOKEN** : Token d'authentification Twilio.
   - **TWILIO_WHATSAPP_NUMBER** : Numéro WhatsApp Twilio.
4. Exécutez le serveur Django :
   ```bash
   python manage.py runserver
   ```

## Structure des Fichiers
- **chatbot/** : Contient les applications Django.
- **templates/** : Templates HTML pour les vues administratives (le cas échéant).
- **static/** : Fichiers statiques comme les CSS et JS.
- **requirements.txt** : Liste des dépendances Python.

## Améliorations Futures
- Intégration de recommandations basées sur l’historique des diagnostics.
- Amélioration de l’interface utilisateur sur WhatsApp avec des boutons interactifs.
- Génération de rapports PDF pour les diagnostics et bilans.

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---


Pour toute question ou contribution, veuillez contacter l’équipe de développement à patriceneussi9@gmai.com .

