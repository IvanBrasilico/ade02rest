from apiserver.api import app
from apiserver.views import create_views

def configure_app(session, engine):
    app.add_api('openapi.yaml')
    app.app.config['db_session'] = session
    app.app.config['engine'] = engine
    print('Configurou app')
    print(app.app.config['db_session'])
    app = create_views(app)
    print('Configurou views')
    print(app.app.config['db_session'])
    return app
