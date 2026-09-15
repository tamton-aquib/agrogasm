# agrogasm
For Onehack 3.0. (WIP)

Farmer-first community + weather app. Vite + React frontend, Flask + SQLite backend.

### Members
- @[mhdafh7](https://github.com/mhdafh7)
- @[codeklada](https://github.com/codeklada)
- @[nishoyan](https://github.com/nishoyan)
- @[tamton-aquib](https://github.com/tamton-aquib)

### Setup
```sh
cp .env.example .env
# edit .env, set VITE_OWM_KEY from https://openweathermap.org/api

npm install
pip install -r requirements.txt
flask --app agrogasm init-db
```

### Usage
Run backend and frontend in two terminals:
```sh
flask --app agrogasm run
npm run dev
```
Or with honcho/foreman:
```sh
honcho -f Procfile.dev start
```
Production backend (2 workers to avoid SQLite lock contention):
```sh
gunicorn -w 2 -b 127.0.0.1:5000 agrogasm:app
```
Docker:
```sh
docker compose up --build
```

Frontend reads `VITE_API_URL`, `VITE_OWM_KEY`, `VITE_OWM_CITY` from `.env`.
City and theme can also be changed in Settings, stored in `localStorage`.
Backend reads `AGROGASM_DB`, `AGROGASM_THRESHOLD`, `FRONTEND_ORIGIN` from `.env`.

### Tests
```sh
pytest -q
npm run build
```

### API
- `GET /?limit=20&offset=0&q=&sort=new|old|top&reliability=` -> `{data: {posts, global}, meta: {total, limit, offset}}`
- `GET /community/<pid>` -> `{post}`
- `POST /community/new` `{author, title, description}` -> `201 {post}`
- `POST /community/<pid>/vote` `{direction: "up"|"down"}` -> updated counts (rate limited)
- `POST /community/<pid>/comment` `{author, description}` -> `201 {comment}`
- `DELETE /community/<pid>` -> `{message: Deleted}`
- `GET /health` -> `{status: "ok"}`

Each post includes computed `reliability` (`new`/`reliable`/`unsure`/`unreliable`), `created_at`, and `comments: []`.

### Security notes
- Old OpenWeather key was committed in history. Rotate it at openweathermap.org and do not reuse.
- To purge history: `git filter-repo --path src/components/Weather.tsx --invert-paths` is destructive, coordinate with team first.
- Backend sets `nosniff`, `DENY` framing, `no-referrer` headers. Vote/create/comment are rate limited.
