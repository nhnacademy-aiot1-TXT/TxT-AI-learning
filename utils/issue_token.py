import requests

def get_token(auth_url, tenant_id, username, password):
    """
    주어진 인증 정보를 사용하여 NHN Cloud Object Storage에 접근할 수 있는 API 토큰을 발급받습니다.

    Args:
        auth_url (str): 토큰을 발급받기 위한 인증 서버의 URL.
        tenant_id (str): 테넌트 ID.
        username (str): 사용자 이름.
        password (str): 사용자 비밀번호.

    Returns:
        Response: 토큰 ID 데이터가 담긴 API 응답 객체.
    """
    token_url = auth_url + '/tokens'
    req_header = {'Content-Type': 'application/json'}
    req_body = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': username,
                'password': password
            }
        }
    }

    response = requests.post(token_url, headers=req_header, json=req_body)
    return response.json()