import requests
import json
import os

class IssueToken:
    def get_token(self, auth_url, tenant_id, username, password):
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