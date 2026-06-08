# Running on Windows 🪟 (step by step)

Foolproof setup. You'll use **two terminals** at the end — one for the backend,
one for the frontend.

## 0. Install these first (one time)
- **Python 3.11+** → https://www.python.org/downloads/
  *On the installer's first screen, TICK "Add python.exe to PATH".*
- **Node.js 18+** → https://nodejs.org (the "LTS" button)

## 1. Get your two keys
- **MongoDB URI** — your Atlas connection string (already in `backend\.env`).
- **Gemini API key** (free, no card) — https://aistudio.google.com/apikey →
  "Create API key" → copy it (`AIza...`).

## 2. Fill in the keys
Open `backend\.env` in Notepad and make sure these two lines are filled:
```
GEMINI_API_KEY=AIza...your key...
MONGODB_URI=mongodb+srv://...your connection string...
```
(The MongoDB one is already filled in.)

## 3. Set up + run the BACKEND (first terminal)
In File Explorer, go into the `backend` folder and **double-click**:
1. **`setup.bat`**  → creates the environment + installs everything (takes a few minutes the first time).
2. **`seed.bat`**   → loads the 20 products into MongoDB + builds the search index (run once).
3. **`run.bat`**    → starts the API. Leave this window open. It should say it's running on `http://localhost:8000`.

✅ Test it: open http://localhost:8000/health in a browser — you should see `{"status":"ok"}`.

## 4. Set up + run the FRONTEND (second terminal / window)
Go into the `frontend` folder and **double-click**:
1. **`setup.bat`** → installs the website dependencies.
2. **`run.bat`**   → starts the website. Leave this open.

## 5. Open the app
Go to **http://localhost:3000** 🎉
Try a suggestion chip, or type *"safe car seat for a 3-month-old"*. Click the
**العربية** button (top-right) to flip the whole UI to Arabic.

---

### If something goes wrong
- **`python` not recognized** → reinstall Python with "Add to PATH" ticked, or use `py` instead of `python` in the scripts.
- **`npm` not recognized** → install Node.js, then reopen the terminal.
- **Backend can't connect to MongoDB** → in MongoDB Atlas → Network Access, make sure `0.0.0.0/0` is allowed.
- **Frontend says "couldn't reach the assistant"** → make sure the backend `run.bat` window is still open and running.
- **First answer is slow** → the embedding model downloads (~80MB) on the very first run; it's fast after that.

### Zipping it to share
Before zipping, you can delete these (they're rebuilt by the setup scripts and
just make the zip huge): `backend\.venv`, `backend\chroma_db`, `backend\__pycache__`,
`frontend\node_modules`, `frontend\.next`.
Keep `backend\.env` if you want it to work without re-entering keys.
