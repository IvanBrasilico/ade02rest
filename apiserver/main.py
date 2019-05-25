import logging
import sys

import connexion
from flask import render_template

from apiserver.models import orm

sys.path.insert(0, './apiserver/')
logging.basicConfig(level=logging.INFO)

TOKEN = 'Evento incluido'


def get_token(evento):
    # TODO: Calcular TOKEN (recibo) do Evento
    return TOKEN


def get_evento(IDEvento, aclass):
    try:
        evento = db_session.query(aclass).filter(
            aclass.IDEvento == IDEvento
        ).one_or_none()
        # print(evento.dump() if evento is not None else 'None')
        return evento.dump(), 200 if evento is not None else ('Not found', 404)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def _commit(object):
    try:
        db_session.commit()
    except Exception as err:
        db_session.rollback()
        logging.error(err, exc_info=True)
        return str(err), 405
    return get_token(object), 200


def add_evento(aclass, evento):
    logging.info('Creating evento %s %s..' %
                 (aclass.__name__,
                  evento.get('IDEvento'))
                 )
    novo_evento = aclass(**evento)
    db_session.add(novo_evento)
    return _commit(novo_evento)


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
    ).outerjoin(
        orm.ConteineresGate
    ).outerjoin(
        orm.ReboquesGate).one_or_none()
    if acessoveiculo is None:
        return {'message': 'Evento não encontrado.'}, 404
    acessoveiculo_schema = orm.AcessoVeiculoSchema()
    data = acessoveiculo_schema.dump(acessoveiculo).data
    return data


def acessoveiculo(evento):
    logging.info('Creating acessoveiculo %s..', evento.get('IDEvento'))
    acessoveiculo = orm.AcessoVeiculo(**evento)
    db_session.add(acessoveiculo)
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
    return _commit(acessoveiculo)


# If we're running in stand alone mode, run the application


def create_app():
    app = connexion.FlaskApp(__name__)
    app.add_api('openapi.yaml')
    return app


def main():
    app.run(debug=True, port=8000, threaded=False)


app = create_app()
db_session, engine = orm.init_db()


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    main()
