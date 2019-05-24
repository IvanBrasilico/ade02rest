import logging
import sys

import connexion
from connexion import NoContent
from flask import render_template

from apiserver.models import orm

sys.path.insert(0, './apiserver/')
db_session = None
db_session = orm.init_db('sqlite:///test.db')
logging.basicConfig(level=logging.INFO)


def get_evento(IDEvento, aclass):
    try:
        evento = db_session.query(aclass).filter(
            aclass.IDEvento == IDEvento
        ).one_or_none()
        # print(evento.dump() if evento is not None else 'None')
        return evento.dump() if evento is not None else ('Not found', 404)
    except Exception as err:
        logging.error(err, exc_info=True)
        return err.msg, 400


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


def pesagemmaritimo(evento):
    return add_evento(orm.PesagemMaritimo, evento)


def get_pesagemmaritimo(IDEvento):
    return get_evento(IDEvento, orm.PesagemMaritimo)


def get_acessoveiculo(IDEvento):
    return get_evento(IDEvento, orm.AcessoVeiculo)


def get_acessoveiculo(IDEvento):
    acessoveiculo = orm.AcessoVeiculo.query.filter(
        orm.AcessoVeiculo.IDEvento == IDEvento
    ).join(orm.ConteineresGate).one_or_none()
    if acessoveiculo is None:
        return {'message': 'Evento não encontrado.'}, 404
    acessoveiculo_schema = orm.AcessoVeiculoSchema()
    data = acessoveiculo_schema.dump(acessoveiculo)

    # conteineresgate_result = orm.conteineresgate_schema.dump(acessoveiculo.conteineres)
    # acessoveiculo_result.conteineres = conteineresgate_result
    return data


def acessoveiculo(evento):
    logging.info('Creating acessoveiculo %s..', evento.get('IDEvento'))
    acessoveiculo = orm.AcessoVeiculo(**evento)
    db_session.add(orm.AcessoVeiculo(**evento))
    conteineres = evento.get('conteineres')
    if conteineres:
        for conteiner in conteineres:
            logging.info('Creating conteiner %s..', conteiner.get('numero'))
            conteinergate = orm.ConteineresGate(acessoveiculo,
                                                numero=conteiner.get('numero'),
                                                avarias=conteiner.get('avarias'),
                                                lacres=conteiner.get('lacres'),
                                                vazio=conteiner.get('vazio'))
            db_session.add(conteinergate)
    reboques = evento.get('reboques')
    if reboques:
        for reboque in reboques:
            logging.info('Creating reboque %s..', reboque.get('placa'))
            reboquegate = orm.ReboquesGate(acessoveiculo,
                                           placa=reboque.get('placa'),
                                           avarias=reboque.get('avarias'),
                                           lacres=reboque.get('lacres'),
                                           vazio=reboque.get('vazio'))
            db_session.add(reboquegate)
    db_session.commit()
    return 'Evento incluido', 200


'''
def get_eventos(limit, animal_type=None):
    q = db_session.query(orm.Pet)
    if animal_type:
        q = q.filter(orm.Pet.animal_type == animal_type)
    return [p.dump() for p in q][:limit]
'''


# If we're running in stand alone mode, run the application


def create_app():
    app = connexion.FlaskApp(__name__)
    app.add_api('openapi.yaml')
    return app


def main():
    app.run(debug=True, port=8000, threaded=False)


app = create_app()


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    main()
