import connexion
import logging

from connexion import NoContent
from models import orm


db_session = None
db_session = orm.init_db('sqlite:///test.db')


def get_evento(IDEvento, aclass=None):
    if aclass is None:
        aclass = orm.Evento
    evento = db_session.query(aclass).filter(
        aclass.IDEvento == IDEvento
    ).one_or_none()
    print(evento.dump() if evento is not None else 'None')
    return evento.dump() if evento is not None else ('Not found', 404)

def add_evento(aclass, evento):
    logging.info('Creating evento %s %s..' %
                 (aclass.__name__,
                  evento.get('IDEvento'))
                 )
    db_session.add(aclass(**evento))
    db_session.commit()
    return NoContent, 200

def posicaoconteiner(evento):
    return add_evento(orm.PosicaoConteiner, evento)

def get_posicaoconteiner(IDEvento):
    return get_evento(IDEvento, orm.PosicaoConteiner)


def get_acessoveiculo(IDEvento):
    return get_evento(IDEvento, orm.AcessoVeiculo)

def get_acessoveiculo(IDEvento):
    acessoveiculo = orm.AcessoVeiculo.query.filter(
        orm.AcessoVeiculo.IDEvento == IDEvento
    ).join(orm.ConteineresGate).one_or_none()
    if acessoveiculo is None:
        return {'message': 'Evento não encontrado.'}, 400
    acessoveiculo_schema = orm.AcessoVeiculoSchema()
    data = acessoveiculo_schema.dump(acessoveiculo).data

    # conteineresgate_result = orm.conteineresgate_schema.dump(acessoveiculo.conteineres)
    # acessoveiculo_result.conteineres = conteineresgate_result
    return data

def acessoveiculo(evento):
    logging.info('Creating acessoveiculo %s..', evento.get('IDEvento'))
    acessoveiculo = orm.AcessoVeiculo(**evento)
    db_session.add(orm.AcessoVeiculo(**evento))
    conteineres = evento.get('conteineres')
    for conteiner in conteineres:
        logging.info('Creating conteiner %s..', conteiner.get('numero'))
        conteinergate = orm.ConteineresGate(acessoveiculo, numero=conteiner.get('numero'))
        db_session.add(conteinergate)
    db_session.commit()
    return NoContent, 200



'''
def get_eventos(limit, animal_type=None):
    q = db_session.query(orm.Pet)
    if animal_type:
        q = q.filter(orm.Pet.animal_type == animal_type)
    return [p.dump() for p in q][:limit]
'''
# If we're running in stand alone mode, run the application

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app = connexion.FlaskApp(__name__)
    app.add_api('openapi.yaml')
    application = app.app
    app.run(debug=True, port=8000, threaded=False)
