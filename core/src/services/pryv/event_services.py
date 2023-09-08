from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from services.pryv.stream_services import Stream
import requests
import json
import logging
from http import HTTPStatus


class GetEventParameters(BaseModel):
    from_time: Optional[float] = Field(alias='fromTime')
    to_time: Optional[float] = Field(alias='toTime')
    streams: Optional[list[Stream]]
    types: Optional[list[str]]
    running: Optional[bool]
    sort_ascending: Optional[bool] = Field(alias='sortAscending')
    skip: Optional[int]
    limit: Optional[int]
    state: Optional[str]
    modified_since: Optional[float] = Field(alias='modifiedSince')
    include_deletions = Optional[bool] = Field(alias='includeDeletions')


class Attachment(BaseModel):
    id: str
    file_name: str = Field(alias='fileName')
    type: str
    size: int
    read_token: str = Field(alias='readToken')
    integrity: Optional[str]
    model_config = ConfigDict(
        # remove whitespaces in the beginning / end of strings
        str_strip_whitespace=True,
        # allows to use either variable name or alias to populate a field of the model
        populate_by_name=True,
        # allows to instantiate model from attribute of another class
        from_attributes=True,
    )


class Event(BaseModel):
    id: str
    stream_ids: list[str] = Field(alias='streamIds')
    time: float
    duration: Optional[float]
    type: str
    content: Optional[any]
    description: Optional[str]
    attachments: Optional[list[Attachment]]
    client_data: Optional[dict] = Field(alias='clientData')
    trashed: Optional[bool]
    integrity: Optional[str]
    created: float
    created_by: str = Field(alias='createdBy')
    modified: float
    modified_by: str = Field(alias='modifiedBy')
    model_config = ConfigDict(
        # remove whitespaces in the beginning / end of strings
        str_strip_whitespace=True,
        # allows to use either variable name or alias to populate a field of the model
        populate_by_name=True,
        # allows to instantiate model from attribute of another class
        from_attributes=True,
    )


class EventServices:
    def __init__(self, user_endpoint: str, token: str) -> None:
        self.logger = logging.getLogger('[EventServices]')
        self.url = f'{user_endpoint}/events'
        self.headers = {
            'Authorization': token
        }

    def get_events(self,
                   params: GetEventParameters = None) -> list[Event]:
        response = requests.get(url=self.url, params=params, headers=self.headers)
        if response.status_code != HTTPStatus.OK:
            self.logger.error(
                f'Unexpected error while trying to fetch Pryv events with params: {params}.'
                f' Status: {response.status_code}, content: {response.json()}')
            return None
        return [Event(event) for event in response.json().get('events', [])]

    def get_event(self, event_id: str, include_history: bool = False) -> Event:
        params = {'includeHistory': include_history}
        response = requests.get(url=self.url, params=params, headers=self.headers).json()
        event = Event(response['event'])
        if response.status_code != HTTPStatus.OK:
            self.logger.error(
                f'Unexpected error while trying to fetch Pryv event with id: {event_id}.'
                f' Status: {response.status_code}, content: {response.json()}')
            return None
        if include_history:
            history = [Event(event) for event in response['history']]
        return event, history

    def create_event(self, event: Event):
        response = requests.post(url=self.url, json=json.dumps(event), headers=self.headers)
        if response.status_code != HTTPStatus.CREATED:
            self.logger.error(
                f'Unexpected error while trying to create Pryv event: {event}.'
                f' Status: {response.status_code}, content: {response.json()}')
            return None
        return Event(response.json()['event'])
