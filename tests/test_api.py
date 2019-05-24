import pytest

from apiserver.main import create_app

app = create_app()

@pytest.fixture(scope='module')
def client():
    with app.app.test_client() as c:
        yield c


def test_health(client):
    response = client.get('/non_ecxiste')
    assert response.status_code == 404


