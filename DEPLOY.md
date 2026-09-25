# Deploy Supreme Food Industry

Project root: `supreme-food-industry/`

Official phones:
- **+977 9841043864**
- **9840067681**

## 1) Local (already works)

```bash
cd supreme-food-industry
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
gcc -O2 -o bin/rice_calc_c polyglot/c/rice_calc.c
g++ -O2 -o bin/rice_calc_cpp polyglot/cpp/rice_calc.cpp
.venv/bin/python server.py
```

Open http://localhost:5173

## 2) Docker (any VPS / cloud)

```bash
docker build -t supreme-food .
docker run -p 5173:5173 -e SFI_SECRET='change-me' supreme-food
```

## 3) Render.com

1. Push this folder to GitHub
2. New **Web Service** → connect repo
3. Build: `pip install -r requirements.txt && gcc -O2 -o bin/rice_calc_c polyglot/c/rice_calc.c && g++ -O2 -o bin/rice_calc_cpp polyglot/cpp/rice_calc.cpp`
4. Start: `FLASK_DEBUG=0 python server.py`
5. Set env `SFI_SECRET` and `PORT` (Render sets PORT automatically — server already reads it)

## 4) Railway / Fly.io

Same as Docker or Procfile. Set `FLASK_DEBUG=0`.

## 5) Shared hosting with PHP contact only

If you only have Apache + PHP:
- Upload the static HTML/CSS/JS/assets
- Point contact forms to `polyglot/php/contact.php`
- Login/order APIs need Python — use Render/Railway for the full stack

## Stack map

| Piece | Tech |
|-------|------|
| UI | HTML, CSS, JS |
| API / auth / orders | Python Flask + SQLite |
| Bag calculator | C / C++ binaries (+ Python fallback) |
| Alt contact | PHP |
| Extra source | Java `RiceCalc.java` |
