import sys

from apiserver.models import orm

sys.path.insert(0, './apiserver')

from apiserver.main import create_app

session, engine = orm.init_db('sqlite:///:memory:')

try:
    orm.Base.metadata.drop_all(bind=engine)
except:
    pass
try:
    orm.Base.metadata.create_all(bind=engine)
except:
    pass
app = create_app(session, engine)

if __name__ == '__main__':
    app.run(port=8000)
