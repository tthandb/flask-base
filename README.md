# Flask Project

## Develop 
```
	# Create file .env from .env.example
	pipenv install  # Install dependency
	pipenv shell 
	alembic upgrade head # migrate database
	python run.py # run app with port 5000
	check swagger at http://localhost:5000/swagger

```
### Folder Structure

```
├── apis # API 
│   ├── apps
│   │   ├── helpers # Method helper for api
│   │   ├── validators # Validator Input API 
│   │   └── views # API, routing, get input and return result 
│   ├── sessions
│   ├── __init__.py # Setup routing api
│   ├── example.py
├── background_jobs # Background Job
├── common # Common Library
├── database
│   ├── models # Define model 
│   │   ├── base.py # base method
│   │   ├── user.py # model table
│   ├── services # Business logic 
│   │   ├── base.py 
│   │   ├── user.py
├── workers # Workers for Faktory
├── swagger # Swagger API
├── app.py # App init
├── run.py # start app
├── .env # ENV Config
├── Pipfile # Dependency
├── Pipfile.lock # Pipefile lock dependency
└── test
``` 

## How many environments in this project?

There are 4 environments:
- production
- staging

## How are these environments deployed?

### Production (`production`)

The `.env.production` file will be saved in the server and only sys admin or
the men who can access production servers can edit it.

### Staging (`staging`)

Tools:  `gitlab-ci`
ENV file: `.env.staging`
ENV requirements:

```
ENVIRONMENT=staging
```