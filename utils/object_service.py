import requests

class ObjectService:
    """
    NHN Cloud Object storage 서비스에 접근하여 객체를 업로드하거나 관리하는 클래스입니다.

    Attributes:
        storage_url (str): Object storage의 URL.
        token_id (str): 인증 토큰 ID.
    """
    
    def __init__(self, storage_url, token_id):
        """
        객체 저장 서비스에 대한 접근을 관리하기 위해 초기화합니다.

        Args:
            storage_url (str): 객체 저장소의 URL.
            token_id (str): 접근을 위한 인증 토큰 ID.
        """
        self.storage_url = storage_url
        self.token_id = token_id

    def _get_url(self, container, object):
        """
        저장소 URL을 생성합니다.

        Args:
            container (str): 업로드할 컨테이너 이름.
            object (str): 객체의 이름.

        Returns:
            str: 완성된 객체 접근 URL.
        """
        return '/'.join([self.storage_url, container, object])

    def _get_request_header(self):
        """
        요청 헤더를 생성합니다. 인증 토큰을 헤더에 포함시킵니다.

        Returns:
            dict: 요청에 사용할 헤더.
        """
        return {'X-Auth-Token': self.token_id}

    def upload(self, container, object, object_path):
        """
        지정된 경로의 객체를 저장소에 업로드합니다.

        Args:
            container (str): 업로드할 컨테이너 이름.
            object (str): 객체의 이름.
            object_path (str): 로컬에 저장된 객체 파일 경로.

        Returns:
            Response: 요청의 HTTP 응답 객체.
        """
        req_url = self._get_url(container, object)
        req_header = self._get_request_header()

        path = '/'.join([object_path, object])
        with open(path, 'rb') as f:
            return requests.put(req_url, headers=req_header, data=f.read())