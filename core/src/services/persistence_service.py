from abc import ABC, abstractmethod
from enums.environment import Environment
from http import HTTPStatus
import requests
import os

from mas.enums.message import MessageMetadata


class AbstractPersistenceService(ABC):
    """ Singleton aiming to be an interface for the persistence layer in Erebots 3.

       The purpose of this class is to be an interface between the persistence layer and the rest of Erebots 3.
       In other terms, Erebots 3 core as well as the modules should call this class each time some data should be
       persisted. The persistenceService is then responsible to handle the persistence in a way that fit the database
       used.
    """

    @abstractmethod
    def save_message_to_history(self, message: str):
        """ Save the given message to history to keep track of conversation historic"""
        pass

    @abstractmethod
    def save_data(self, data, table: str):
        """ Save the given data to the given table"""
        pass

    @abstractmethod
    def deploy_model(self, model):
        """Deploy the provided database model"""
        pass


# Todo - check bug that token does not give right permissions the first time we receive it.
class PryvPersistenceService(AbstractPersistenceService):

    def __init__(self, username: str, module_name: str, token: str):
        super().__init__()
        self.username = username
        self.module_name = module_name
        self.token = token
        self.url = os.environ.get(Environment.PRYV_SERVER_URL.value).replace('https://', f'https://{username}.')
        self.headers = {'authorization': self.token}

    def deploy_model(self, model):
        url = f'{self.url}/streams'
        for stream in model:
            json = {
                'name': stream.default_name,
                'parentId': stream.parent,
                'id': stream.stream_id
            }
            response = requests.post(url, json=json, headers=self.headers)
            if response.status_code == HTTPStatus.BAD_REQUEST:
                raise ValueError(f'Pryv Create Stream with Invalid input: {response.status_code}/{response.text}')
            if response.status_code != HTTPStatus.CREATED:
                raise Exception(f'Stream not created: {response.status_code}/{response.text}')

    def save_data(self, data, table: str):
        pass

    def save_message_to_history(self, message):
        url = f'{self.url}/events'
        pryv_type = message.get_metadata(MessageMetadata.CONTEXT.value)
        event = {
            'streamIds': [f'{self.module_name}_messages'],
            'type': f'{pryv_type}/json',
            'content': message.__dict__
        }

        response = requests.post(url, json=event, headers=self.headers)

        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ValueError(f'Pryv Create Event with Invalid input: {response.status_code}/{response.text}')
        if response.status_code != HTTPStatus.CREATED:
            raise Exception(f'Message Event not created: {response.status_code}/{response.text}')
