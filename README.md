# CustomizedMeal_ObesityPrediction_ETL_Pipeline

A combined Django web application and Dagster ETL pipeline for personalized meal recommendations and obesity prediction. The Django app serves user interactions and recipe management, while the Dagster pipeline automates data ingestion, preprocessing, model training (obesity prediction), and diet plan generation. The core ETL logic resides in `food_recipe/assets.py`, and the obesity prediction complements the diet recommendation feature.

## Contents

- **myproject/**  
  - Django project folder containing global settings and URL configurations:
    - `settings.py`
    - `urls.py`
    - `wsgi.py`
    - `asgi.py`

- **my_recipes/**  
  - Django application handling recipe management and user views:
    - `views.py` (HTTP request handlers for recipes and obesity prediction)
    - `models.py` (data models for recipes and user health profiles)
    - `urls.py` (URL routing for the `my_recipes` app)
    - `templates/my_recipes/` (HTML templates for rendering diet plans and prediction results)
    - `static/` (CSS, JavaScript, and image assets)

- **meal_recommendation/**  
  - Django application (or submodule) containing logic for recommending diet plans based on predicted obesity levels and user preferences.

- **food_recipe/**  
  - Dagster ETL pipeline automating the extraction, transformation, and loading of data, model training, and generation of diet recommendations:
    - `assets.py` (main Dagster asset definitions, schedules, and partitions)
    - `pipelines/` (individual pipeline modules such as `etl_pipeline.py` and `model_training.py`)
    - `workspace.yaml` (Dagster workspace configuration)
    - `dagster.yaml` (optional DAG configuration or run settings)

- **manage.py**  
  - Django’s command-line utility for administrative tasks (migrations, running server, creating superuser).

- **requirements.txt**  
  - Python dependencies required by both Django and Dagster portions (Django, djangorestframework, psycopg2-binary, python-dotenv, dagster, dagit, pandas, celery, redis, scikit-learn, etc.).

- **.gitignore**  
  - Specifies files and folders to exclude from version control (virtual environments, SQLite database, compiled caches, environment files, etc.).

- **README.md**  
  - This file—project overview, setup instructions, and dependency listings.

## Repository Structure
```text
CustomizedMeal_ObesityPrediction_ETL_Pipeline/
├── .gitignore
├── README.md
├── requirements.txt
├── manage.py
├── db.sqlite3                     # Development SQLite database (ignored in .gitignore)
├── myproject/                     # Django project settings and configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── my_recipes/                    # Django app “my_recipes”
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── my_recipes/
│   │       ├── diet_plan.html
│   │       ├── obesity_predict.html
│   │       └── recipe_list.html
│   └── static/
│       ├── css/
│       └── js/
├── meal_recommendation/           # Django app for generating diet recommendations
│   ├── __init__.py
│   ├── recommendation.py          # Logic to convert model predictions into diet plans
│   └── utils.py                   # Helper functions for meal selection
└── food_recipe/                   # Dagster ETL pipeline for meal recommendation and obesity prediction
    ├── assets.py                  # Main Dagster asset definitions & schedules
    ├── pipelines/
    │   ├── etl_pipeline.py        # Data ingestion and cleansing steps
    │   ├── model_training.py      # Train obesity prediction model
    │   └── recommendation_pipeline.py  # Generate diet recommendations based on predictions
    ├── workspace.yaml             # Dagster workspace configuration
    └── dagster.yaml               # Optional run configuration
```

## Setup & Usage

### 1. Clone the Repository

```bash
git clone git@github.com:YourUsername/CustomizedMeal_ObesityPrediction_ETL_Pipeline.git
cd CustomizedMeal_ObesityPrediction_ETL_Pipeline
```

### 2. Create and Activate a Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
The requirements.txt should include (but is not limited to):
```bash
Django>=4.1.0
djangorestframework>=3.14.0
psycopg2-binary>=2.9.5
python-dotenv>=1.0.0
dagster>=1.0.0
dagit>=1.0.0
pandas>=2.1.0
scikit-learn>=1.2.0
celery>=5.3.0
redis>=4.5.0
sqlparse>=0.5.2
```
### 4. Django Web Application
   ### a. Apply Database Migrations

```bash
python manage.py migrate
This creates/updates the db.sqlite3 file according to models.py.
```
  ### b. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin user for Django’s admin interface.

###  c. Run the Development Server

```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000/recipes/ to browse recipes.

### d. Obesity Prediction & Diet Plan Flow

The my_recipes/views.py includes a view that collects user health metrics (age, weight, height, activity level, etc.), calls a trained machine learning model (implemented in food_recipe/model_training.py), and returns an obesity risk score.

### 5. Dagster ETL Pipeline (food_recipe/)
Configure Environment Variables

### a. Create a food_recipe/.env file (this file is excluded by .gitignore) with any required secrets, for example:

```bash
DATABASE_URL=sqlite:///../db.sqlite3
REDIS_URL=redis://localhost:6379/0
```
### b. Launch Dagster UI

```bash
cd food_recipe
dagit -w workspace.yaml
```
Visit http://127.0.0.1:3000/ in your browser.

You should see pipelines like “etl_pipeline”, “model_training”, and “recommendation_pipeline”.

### c. Run the ETL Pipelines

In the Dagster UI sidebar, select etl_pipeline and run the whole pipeline

### Dependencies
All required Python packages are listed in requirements.txt. At minimum, this project uses:

```bash
Django>=4.1.0
djangorestframework>=3.14.0
psycopg2-binary>=2.9.5
python-dotenv>=1.0.0
dagster>=1.0.0
dagit>=1.0.0
pandas>=2.1.0
scikit-learn>=1.2.0
celery>=5.3.0
redis>=4.5.0
sqlparse>=0.5.2
```
If you add any new dependencies (e.g., a different ML library for obesity classification), run 
```bash
pip freeze > requirements.txt to update.
```

### .gitignore
Use the following .gitignore to prevent committing local environment files, caches, and database artifacts:

```bash
# Byte-compiled Python files
__pycache__/
*.pyc

# Django migrations (optional)
*/migrations/*.py
*/migrations/__pycache__/

# SQLite database
db.sqlite3

# Virtual environment folders
venv/
env/
.venv/

# Environment variable files
.env

# Dagster run history and logs
*.db
*.log

# OS or editor-specific files
.DS_Store
.vscode/
.idea/
```

### Notes & Best Practices
Environment Variables: Never commit API keys, database credentials, or your Django SECRET_KEY. Use a .env file (excluded via .gitignore) or a secrets manager.

Database Configuration: By default, Django uses SQLite (db.sqlite3). For production, update myproject/settings.py to use PostgreSQL or MySQL.

Static & Media Files: In production, run python manage.py collectstatic and configure a web server (e.g., Nginx) or use WhiteNoise to serve static assets.

Dagster Scheduling: If you want to run ETL pipelines on a schedule, define schedules or sensors in food_recipe/assets.py, then run the Dagster daemon:

```bash
dagster-daemon run
```
### Testing: 
Implement unit tests for Django views (my_recipes/tests.py) and Dagster assets (food_recipe/tests/). Configure a CI workflow (GitHub Actions) to run tests on push.

### Deployment: For deployment, containerize the application with Docker. Example steps:

1. Create a Dockerfile that installs dependencies and copies source code.

2. Build and publish images for both Django (Gunicorn + WhiteNoise) and Dagster (Dagit + Celery).

3. Deploy to a cloud provider (AWS, GCP, Azure) or use Docker Compose to orchestrate services (PostgreSQL, Redis, Django, Dagit, Celery).

Contact
For questions or feedback, please reach out to:
```bash
narensinghchilwal@gmail.com
```
