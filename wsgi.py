
import sys
from apiserver.models import orm

sys.path.insert(0, './apiserver')

from apiserver.main import create_app

if __name__ == '__main__':
    session, engine = orm.init_db()
    orm.Base.metadata.drop_all(bind=engine)
    orm.Base.metadata.create_all(bind=engine)
    app = create_app(session, engine)
    app.run(port=8000)
