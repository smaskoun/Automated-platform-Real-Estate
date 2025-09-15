web: bash -c 'set -e; : "${DATABASE_URL:?DATABASE_URL environment variable is required}"; flask --app src.main:create_app db upgrade && exec gunicorn src.main:app'

