up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose exec backend python manage.py seed_data
