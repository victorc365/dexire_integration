import os
import logging
import requests
from fastapi import status
from enums.environment import Environment

class UserService:
    def __init__(self) -> None:
        self.logger = logging.getLogger('[UserService]')
        secret_key = os.environ.get(Environment.XMPP_SECRET_KEY.value)
        url = os.environ.get(Environment.XMPP_SERVER_URL.value)
        admin_port = os.environ.get(Environment.XMPP_ADMIN_PORT.value)
        self.url = f'http://{url}:{admin_port}/plugins/restapi/v1/users'
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': '*/*',
            'Authorization': secret_key
        }

    def create_bot_user(self, username: str, password: str) -> bool:
        data = {'username': username, 'password': password}
        r = requests.post(self.url, json=data, headers=self.headers)

        if r.status_code == status.HTTP_201_CREATED:
            self.logger.info(f'User {username} has been successfully created in XMPP server')
            return True

        self.logger.error(f'Unexpected error creating user {username}. Request ended with code: {r.status_code}:')
        self.logger.error(f'Error message: {r.text}')
        return False

    def delete_bot_user(self, username: str) -> bool:
        url = f'{self.url}/{username}'
        r = requests.delete(url, headers=self.headers)
        if r.status_code == status.HTTP_200_OK:
            self.logger.info(f'User {username} has been successfully deleted from XMPP server')
            return True

        self.logger.error(f'Unexpected error deleting user {username}. Request ended with code: {r.status_code}:')
        self.logger.error(f'Error message: {r.text}')
        return False