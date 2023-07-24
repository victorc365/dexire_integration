from fastapi import status
from fastapi.testclient import TestClient
from src.setup import _init_app

app = _init_app()
client = TestClient(app)
bots_url = 'v1/bots/'


class TestBotsAPI():
    def test_get_bots(self):
        test_dev_bot = {'name': 'testDevBot',
                        'url': 'http://testDevBot.com', 'isDev': True}
        test_bot = {'name': 'testBot',
                    'url': 'http://testBot.com', 'isDev': False}
        expected = sorted([test_bot, test_dev_bot], key=lambda x: x['name'])

        response = client.get(bots_url)
        assert response.status_code == status.HTTP_200_OK

        result = response.json()
        result = sorted(result, key=lambda x: x['name'])
        assert expected == result
