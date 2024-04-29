from dotenv import load_dotenv
import os

def load_environment_variables():
    """
    환경 변수 파일('.env')로부터 환경 변수를 로드하고 이를 사전으로 반환합니다.

    이 함수는 '.env' 파일에서 필요한 환경 변수들을 로드하여 각각의 변수를 키로 갖는 사전을 생성합니다. 
    이 사전은 데이터베이스 접속 정보, 인증 정보 등의 구성 정보를 포함할 수 있습니다.

    Returns:
        dict: 로드된 환경 변수들을 포함하는 사전. 각 키는 환경 변수의 이름이며, 값은 해당 환경 변수의 값입니다.
    """
    load_dotenv('secret.env')
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