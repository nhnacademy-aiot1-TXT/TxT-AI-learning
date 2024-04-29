from dotenv import load_dotenv
import os

def load_environment_variables():
    load_dotenv('.env')
    env_vars = {
        'db_url': os.getenv('DB_URL'),
        'token': os.getenv('DB_TOKEN'),
        'org': os.getenv('DB_ORG'),
        'bucket': os.getenv('DB_BUCKET'),
        'auth_url': os.getenv('AUTH_URL'),
        'tenant_id': os.getenv('TENANT_ID'),
        'user_email': os.getenv('USER_EMAIL'),
        'password': os.getenv('PASSWORD'),
        'storage_url': os.getenv('STORAGE_URL'),
        'container_name': os.getenv('CONTAINER_NAME')
    }
    return env_vars