# Supreme Food Industry — Full Site

**सुप्रिम खाद्य उद्योग** · Panchakanya-2, Nuwakot

Phones: **+977 9841043864** · **9840067681**

## Quick start

```bash
cd supreme-food-industry
.venv/bin/pip install -r requirements.txt   # first time
.venv/bin/python server.py
```

→ http://localhost:5173

## What’s included

- Landing + product + gallery + CSR + contact
- Login / signup (Flask + SQLite)
- Smart order calculator (calls **C++/C** via API, Python fallback)
- NE ↔ EN language toggle
- WhatsApp + call buttons
- Polyglot sources in `polyglot/` (HTML/CSS/JS/Python/PHP/Java/C/C++)
- Deploy guide: [DEPLOY.md](DEPLOY.md)

## Folders

```
supreme-food-industry/
  index.html, login.html, signup.html
  styles.css, script.js, auth.js
  server.py                 # main backend
  assets/facebook/          # packaging photos
  assets/rice/              # rice imagery
  polyglot/                 # php, java, c, cpp, python helpers
  bin/                      # compiled native calculators
  data/                     # sqlite db (created at runtime)
```
