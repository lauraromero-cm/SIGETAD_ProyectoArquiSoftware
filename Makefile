up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose exec backend python manage.py seed_data

export-users:
	docker compose exec backend python manage.py export_datos

import-users:
	docker compose exec backend python manage.py import_datos

export-data:
	docker compose exec backend python manage.py export_datos

import-data:
	docker compose exec backend python manage.py import_datos
