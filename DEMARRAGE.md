# 🚀 DÉMARRAGE RAPIDE — CityReport

Suis ces étapes DANS L'ORDRE. Tape les commandes une par une.

## ⚠️ IMPORTANT — Remplace bien l'ancien dossier

Si tu avais déjà une ancienne version, SUPPRIME complètement l'ancien dossier
`cityreport` et remplace-le par celui-ci. Sinon tu garderas l'ancienne version.

---

## 1️⃣ BACKEND (première fenêtre PowerShell)

```powershell
cd C:\Users\taha1\Desktop\cityreport\backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install Flask Flask-Cors SQLAlchemy scikit-learn pandas numpy
py seed.py
py app.py
```

✅ Tu dois voir : `Running on http://127.0.0.1:5000`
👉 LAISSE cette fenêtre ouverte.

> Si `.\venv\Scripts\Activate.ps1` refuse (erreur de scripts), tape d'abord :
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

---

## 2️⃣ FRONTEND (DEUXIÈME fenêtre PowerShell)

Ouvre une NOUVELLE fenêtre (ne ferme pas la première).

```powershell
cd C:\Users\taha1\Desktop\cityreport\frontend
npm install
npm run dev
```

✅ Tu dois voir :
```
  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.137:5173/
```

---

## 3️⃣ OUVRIR L'APPLICATION

**Sur ton PC :** ouvre le navigateur → http://localhost:5173

**Sur ton iPhone (même Wi-Fi) :** Safari → http://192.168.1.137:5173
(remplace par ton adresse « Network » si elle est différente)

---

## 🔑 Connexions de démonstration

**Espace citoyen** (page d'accueil)
- Email : `citoyen@cityreport.ma`
- Mot de passe : `citoyen`

**Espace municipalité** (bouton 🔒 en bas à droite de l'accueil)
- Email : `admin@cityreport.ma`
- Mot de passe : `admin`

---

## ✨ Fonctionnalités à tester

- **Signaler un problème** → bouton « + Nouveau signalement »
- **📷 Photo** → bouton « Prendre / choisir une photo » (ouvre l'appareil photo sur iPhone)
- **🚓 Urgence** → choisir Police (19) ou Secours (15) → bouton d'appel après envoi
- **🤖 Assistant IA** → bouton 💬 en bas à gauche de l'accueil
- **📍 Carte** → clique sur la carte pour placer le point exact
- **Timeline** → « Voir le suivi » sur chaque signalement

---

## 📱 Pour ouvrir sur le téléphone : règles de pare-feu (une seule fois)

Ouvre PowerShell EN ADMINISTRATEUR (clic droit → Exécuter en tant qu'administrateur)
et colle :

```powershell
New-NetFirewallRule -DisplayName "Vite 5173" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Flask 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

Puis sur Safari (iPhone) : http://192.168.1.137:5173

---

## ❓ Problèmes fréquents

**« npm n'est pas reconnu »** → Node.js n'est pas installé. Télécharge-le sur
https://nodejs.org (version LTS), installe, ferme et rouvre PowerShell.

**Le formulaire montre encore « Photo (URL) »** → tu es sur l'ancienne version.
Vérifie que tu as bien remplacé le dossier par le nouveau, puis recharge la page
en forçant (Ctrl+Shift+R sur PC, ou ferme/rouvre l'onglet Safari).

**Page blanche/noire** → vérifie que les DEUX fenêtres (backend + frontend)
tournent bien en même temps.
