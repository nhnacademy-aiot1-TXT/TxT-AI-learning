from dotenv import load_dotenv
import os

def load_environment_variables():
    """
    환경 변수 파일('.env')로부터 환경 변수를 로드하고 이를 dictionary로 반환합니다.

    이 함수는 '.env' 파일에서 필요한 환경 변수들을 로드하여 각각의 변수를 키로 갖는 dictionary을 생성합니다. 
    이 dictionary는 데이터베이스 접속, 인증에 필요한 정보를 포함합니다.

    Returns:
        dict: 로드된 환경 변수들을 포함하는 dictionary. 각 키는 환경 변수의 이름이며, 값은 해당 환경 변수의 값입니다.
    """
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

    for key, value in env_vars.items():
        print(f"{key}: {value}")
            
    return env_vars
