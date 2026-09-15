.PHONY: flask npm dev init-db test prod

init-db:
	flask --app agrogasm init-db

flask:
	flask --app agrogasm run

npm:
	npm run dev

dev:
	npm run dev

test:
	pytest -q
	npm run build

prod:
	gunicorn -w 2 -b 127.0.0.1:5000 agrogasm:app
