# 🚀 Déployer CityReport en ligne (Vercel + Render)

Ton projet a un **frontend** (React) et un **backend** (Python + IA + base de données).
Vercel ne peut héberger que le frontend. On déploie donc :

- **Backend + base PostgreSQL → Render** (gratuit)
- **Frontend → Vercel** (gratuit)

Les deux communiquent via internet. Suis les étapes DANS L'ORDRE.

---

## ⚙️ PRÉREQUIS — Mettre le projet sur GitHub

Vercel et Render déploient depuis GitHub. Il faut donc d'abord y mettre ton projet.

1. Crée un compte sur https://github.com (si pas déjà fait)
2. Crée un nouveau dépôt (repository) : bouton **New** → nomme-le `cityreport` → **Create**
3. Sur ton PC, dans le dossier `cityreport`, ouvre un terminal et tape :

```bash
git init
git add .
git commit -m "CityReport"
git branch -M main
git remote add origin https://github.com/TON_PSEUDO/cityreport.git
git push -u origin main
```

(remplace `TON_PSEUDO` par ton nom d'utilisateur GitHub)

> Si `git` n'est pas installé : télécharge-le sur https://git-scm.com

---

## 1️⃣ BACKEND — Déployer sur Render

1. Va sur https://render.com et connecte-toi **avec GitHub**
2. Clique **New +** → **Blueprint**
3. Sélectionne ton dépôt `cityreport`
4. Render détecte le fichier `render.yaml` → clique **Apply**
5. Render crée automatiquement :
   - une base de données PostgreSQL
   - le service web backend
6. Attends la fin du déploiement (5-10 min la première fois — l'entraînement du modèle IA prend un peu de temps)
7. Une fois fini, Render te donne une URL du type :
   **`https://cityreport-backend.onrender.com`**
   
   👉 **COPIE cette URL**, tu en as besoin pour Vercel.

> Teste que ça marche : ouvre `https://cityreport-backend.onrender.com/api/health`
> Tu dois voir : `{"status": "ok", "service": "CityReport API"}`

---

## 2️⃣ FRONTEND — Déployer sur Vercel

1. Va sur https://vercel.com et connecte-toi **avec GitHub**
2. Clique **Add New...** → **Project**
3. Importe ton dépôt `cityreport`
4. **IMPORTANT** — configure ces réglages :
   - **Root Directory** : clique *Edit* et choisis le dossier **`frontend`**
   - **Framework Preset** : Vite (détecté automatiquement)
5. Déplie **Environment Variables** et ajoute :
   - **Name** : `VITE_API_URL`
   - **Value** : l'URL de ton backend Render (ex: `https://cityreport-backend.onrender.com`)
     ⚠️ SANS `/api` à la fin, SANS slash final
6. Clique **Deploy**
7. Après 1-2 min, Vercel te donne ton lien public :
   **`https://cityreport-xxx.vercel.app`** 🎉

---

## ✅ C'est en ligne !

Ouvre ton lien Vercel. L'app est accessible partout, sur n'importe quel téléphone
ou ordinateur.

**Comptes de démo :**
- Citoyen : `citoyen@cityreport.ma` / `citoyen`
- Admin : `admin@cityreport.ma` / `admin`

---

## ⚠️ Points importants à savoir

**Le plan gratuit de Render "s'endort".** Après 15 min sans visite, le backend se met
en veille. La première requête suivante prend ~30-50 secondes à réveiller le serveur
(l'app semble lente, puis redevient normale). Pour une soutenance : ouvre l'app
2 minutes avant pour la "réveiller".

**La base est réinitialisée à chaque déploiement.** Le script `start.sh` relance le
seed à chaque redéploiement, donc les comptes créés manuellement sont perdus si tu
redéploies. Les comptes de démo, eux, sont toujours recréés.

**Pour mettre à jour l'app en ligne :** modifie ton code, puis :
```bash
git add .
git commit -m "mise à jour"
git push
```
Vercel et Render redéploient automatiquement.

---

## 🎓 Pour la soutenance

Avoir un lien public est un vrai plus. Tu peux :
- Montrer l'app depuis n'importe quel appareil, sans rien lancer
- Donner le lien au jury pour qu'ils testent eux-mêmes
- Le mettre dans ton rapport

Mais **garde aussi la version locale prête** (sur ton PC) en secours, au cas où le
wifi de la salle serait mauvais ou le serveur Render endormi.
