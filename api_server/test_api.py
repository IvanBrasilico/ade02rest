import pytest

from api_server.main import create_app

app = create_app()

@pytest.fixture(scope='module')
def client():
    with app.test_client() as c:
        yield c


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200


