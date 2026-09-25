# Free Google deploy → www.supremefoodindustries.web.app style URL

Google does **not** give a free custom `.com` domain. Free Google URLs look like:

- `https://supremefoodindustries.web.app` (Firebase Hosting)
- `https://supremefoodindustries.firebaseapp.com`
- `https://supreme-food-industry-xxxxx-as.a.run.app` (Cloud Run)

You can later buy `supremefoodindustries.com` (~$10/yr) and point it at Firebase.

## Admin access (built-in)

| Phone | Password |
|-------|----------|
| `9841043864` | `supreme@2000@` |
| `9840067681` | `supreme@2000@` |

After login → `/admin.html` shows **all orders** + contact messages.

---

## Path A — Google Cloud Run (recommended for this Flask app)

### Needs
1. Free Google account
2. [Google Cloud Console](https://console.cloud.google.com/) — enable billing for free tier (Cloud Run free quota; card required by Google, $0 if traffic is low)
3. [Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install) on your PC

### Steps
```bash
cd supreme-food-industry
chmod +x deploy-google.sh

# Create project ID (must be globally unique), e.g. supremefoodindustries
gcloud projects create supremefoodindustries --name="Supreme Food Industry"
gcloud billing accounts list
gcloud billing projects link supremefoodindustries --billing-account=YOUR_BILLING_ACCOUNT_ID

./deploy-google.sh
```

Open the printed `*.run.app` URL.

### Firebase pretty URL (same project)
```bash
npm install -g firebase-tools
firebase login
firebase use supremefoodindustries
# Connect Hosting to the Cloud Run service in Firebase console (Hosting → Add integration)
firebase deploy --only hosting
```

Then use:
- **https://supremefoodindustries.web.app**
- **https://www.supremefoodindustries.web.app** (add `www` in Firebase Hosting domains)

---

## Path B — Easiest free (no Google card): Render.com

1. Push this folder to GitHub
2. [Render](https://render.com) → New Web Service → connect repo
3. Build: `pip install -r requirements.txt && mkdir -p bin && gcc -O2 -o bin/rice_calc_c polyglot/c/rice_calc.c && g++ -O2 -o bin/rice_calc_cpp polyglot/cpp/rice_calc.cpp`
4. Start: `FLASK_DEBUG=0 python server.py`
5. Free URL: `https://supreme-food-industry.onrender.com`

You can still use a custom domain later.

---

## Local test of admin

```bash
.venv/bin/python server.py
```

1. Open http://localhost:5173/login.html  
2. Phone `9841043864` · Password `supreme@2000@`  
3. You land on **Admin panel** with every order
