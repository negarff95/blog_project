# blog project
The backend project for simple rating system using Python and Django

### Stack
Following applications must be installed and configured:

- python3.11
- Postgresql

### Run
- Open a terminal in root folder of blog_project.
- Create a virtual environment with `virtualenv` and activate it:
```
python -m venv _env  && source _env/bin/activate
```
- Copy `env.sample` as `.env` in root folder:
```
cp env.sample .env
```
#### If running Docker:

```
docker-compose build
docker-compose up
```
- In .env file set DATABASE__HOST to db.
- And for celery set redis instead of localhost.

#### If not running Docker

- Install requirements:
```
pip install -r requirements.txt
```

- Configure settings in `.env` file with your stack data.
- Export environment variables:
```
export $(grep -v "^#" .env)
```
- Migrate database:
```
python manage.py migrate
```
- Run project:
```
python manage.py runserver
```

- Run async tasks:
```
celery -A blog_project worker -l INFO -B -Q periodic_queue
```
