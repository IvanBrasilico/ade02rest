import pytest

from api_server.app import create_app

flask_app = create_app()

@pytest.fixture(scope='module')
def client():
    with flask_app.test_client() as c:
        yield c


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200


