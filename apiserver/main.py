import connexion

from apiserver.models import orm
from views import create_views


def create_app(session, engine):
    app = connexion.FlaskApp(__name__)
    app.add_api('openapi.yaml')
    app.app.config['db_session'] = session
    app.app.config['engine'] = engine
    print('Configurou app')
    app = create_views(app)
    print('Configurou views')
    return app




def main():
    # session, engine = orm.init_db('sqlite:///:memory:')
    # orm.Base.metadata.create_all(bind=engine)
    session, engine = orm.init_db()
    app = create_app(session, engine)
    print(app.app.config['db_session'])
    app.run(debug=True, port=8000, threaded=False)


if __name__ == '__main__':
    main()
