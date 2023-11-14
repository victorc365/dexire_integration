import json
from abc import ABC, abstractmethod
from enums.environment import Environment
from http import HTTPStatus
import requests
import os
from spade.message import Message
from mas.enums.message import MessageMetadata, MessageBodyFormat


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

    @abstractmethod
    def get_history(self, skip: int = 0, limit: int = 10) -> list[Message]:
        """ Get the history of the messages in the conversation.

            Get the history of messages in the conversation from your database.
            The returned array of messages is sorted from newest to oldest.

            skip: The number of items to skip in the results.
            limit: The number of items to return in the results
        """
        pass

    @abstractmethod
    def get_profile(self) -> dict:
        pass


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
        url = f'{self.url}/events'
        event = {
            'streamIds': [f'{self.module_name}_{table}'],
            'type': 'profile/json',
            'content': json.dumps(data)
        }

        response = requests.post(url, json=event, headers=self.headers)

        if response.status_code == HTTPStatus.BAD_REQUEST:
            raise ValueError(f'Pryv Create Event with Invalid input: {response.status_code}/{response.text}')
        if response.status_code != HTTPStatus.CREATED:
            raise Exception(f'Event not created: {response.status_code}/{response.text}')

    def save_message_to_history(self, message: Message) -> None:
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

    def get_history(self, skip: int = 0, limit: int = 10) -> list[Message]:
        url = f'{self.url}/events'
        params = {
            'streams': f'{self.module_name}_messages',
            'skip': skip,
            'limit': limit,
            'sortAscending': True
        }
        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != HTTPStatus.OK:
            raise Exception(f'Exception while getting history of conversation: {response.status_code}/{response.text}')

        data = response.json()
        messages = []
        bot_name = f'{self.module_name}_{self.username}'
        for event in data['events']:
            content = event['content']
            to = bot_name if bot_name in content['_to'] else self.username
            sender = bot_name if bot_name in content['_sender'] else self.username
            body = content['_body']
            message = {
                'to': str(to),
                'sender': str(sender),
                'body': body,
                'metadata': {
                    MessageMetadata.BODY_FORMAT.value: MessageBodyFormat.TEXT.value
                }
            }
            messages.append(message)
        return messages

    def get_profile(self) -> dict:
        url = f'{self.url}/events'
        params = {
            'streams': f'{self.module_name}_profiling'
        }

        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code != HTTPStatus.OK:
            raise Exception(f'Exception while getting profile: {response.status_code}/{response.text}')
        data = response.json()
        events = data['events']
        if len(events) == 0:
            return {}

        return events[0]['content']
