import os
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load local .env if present
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except Exception:
        # Fallback line-by-line parser if dotenv is not imported
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

# Render / cloud environment persistent directory (optional)
DATA_DIR = os.environ.get('DATA_DIR', BASE_DIR)

# Handle Render / Heroku / Neon Postgres dialect fix and options
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Remove unsupported channel_binding parameter if present
    if 'channel_binding=' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('&channel_binding=require', '').replace('?channel_binding=require&', '?').replace('?channel_binding=require', '')
        DATABASE_URL = DATABASE_URL.replace('&channel_binding=prefer', '').replace('?channel_binding=prefer&', '?').replace('?channel_binding=prefer', '')
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "+psycopg2" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'exam-allocation-super-secret-key-2025-token')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{os.path.join(DATA_DIR, 'exam_seat.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configure pooling appropriately for SQLite vs Neon PostgreSQL
    is_postgres = bool(DATABASE_URL and DATABASE_URL.startswith('postgresql'))
    if is_postgres:
        pg_connect_args = {}
        # Ensure connection reliability on local Windows machines with restrictive DNS
        if 'ep-holy-recipe-b3teux3m-pooler.c-4.ap-southeast-1.aws.neon.tech' in (DATABASE_URL or ''):
            pg_connect_args['hostaddr'] = '52.76.246.190'
            
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,  # Recycle every 5 mins for Neon PgBouncer pooler
            'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
            'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 5)),
            'connect_args': pg_connect_args
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'connect_args': {
                'check_same_thread': False,
                'timeout': 30
            }
        }

    # Backblaze B2 Private Cloud Storage Configuration
    B2_KEY_ID = os.environ.get('B2_KEY_ID', '005c2f9f65018190000000001')
    B2_APPLICATION_KEY = os.environ.get('B2_APPLICATION_KEY', 'K0053m0DJPfAlUzwKrWv9F4YtFjr8zY')
    B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME', 'allocera-storage')
    B2_ENDPOINT = os.environ.get('B2_ENDPOINT', 's3.us-east-005.backblazeb2.com')
    B2_REGION = os.environ.get('B2_REGION', 'us-east-005')

    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

