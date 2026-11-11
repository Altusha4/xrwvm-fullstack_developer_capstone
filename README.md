# fullstack_developer_capstone

Best Cars dealership review portal. Django authentication and car models, React interface, Express/MongoDB dealer API and a separate sentiment service.

## Local development
Run `docker compose up --build` and visit http://localhost:8000.
The demo uses fictional customers and dealership seed data from the course template.
Create an admin with `docker compose exec web python manage.py createsuperuser`.

## Validation
`cd server && python manage.py test djangoapp` tests authentication, CSRF, validation and upstream failures.
`npm --prefix server/frontend run build` validates the React production build.
CI runs backend tests, Python lint, JavaScript syntax checks and React build.

## Scope
Local Docker/Kubernetes evidence is collected separately. IBM Code Engine deployment is pending and is not claimed as completed. No assessment is submitted automatically.
