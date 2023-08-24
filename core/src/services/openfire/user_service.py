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

    def bot_user_exist(self, bot_user_name: str) -> bool:
        url = f'{self.url}/{bot_user_name}'
        response = requests.get(url, headers=self.headers)
        return response.status_code == status.HTTP_200_OK

    def create_bot_user(self, bot_user_name: str, password: str) -> bool:
        data = {'username': bot_user_name, 'password': password}
        response = requests.post(self.url, json=data, headers=self.headers)

        if response.status_code == status.HTTP_201_CREATED:
            self.logger.info(f'Bot user {bot_user_name} has been successfully created in XMPP server')
            return True

        self.logger.error(f'Unexpected error creating bot user {bot_user_name}. Request ended with code: {response.status_code}:')
        self.logger.error(f'Error message: {response.text}')
        return False

    def delete_bot_user(self, bot_user_name: str) -> bool:
        url = f'{self.url}/{bot_user_name}'
        response = requests.delete(url, headers=self.headers)
        if response.status_code == status.HTTP_200_OK:
            self.logger.info(f'Bot user {bot_user_name} has been successfully deleted from XMPP server')
            return True

        self.logger.error(f'Unexpected error deleting bot user {bot_user_name}. Request ended with code: {response.status_code}:')
        self.logger.error(f'Error message: {response.text}')
        return False