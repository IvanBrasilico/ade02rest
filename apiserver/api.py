import logging

import connexion
from flask import request, jsonify
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from apiserver.logconf import logger
from apiserver.models import orm

RECINTO = '00001'


def dump_eventos(eventos):
    eventos_dump = []
    for evento in eventos:
        evento.hash = hash(evento)
        eventos_dump.append(evento.dump())
    return jsonify(eventos_dump)


def _commit(evento):
    try:
        evento.request_IP = request.environ.get('HTTP_X_REAL_IP',
                                                request.remote_addr)
        evento.recinto = RECINTO
        db_session.flush()
        db_session.refresh(evento)
        ohash = hash(evento)
        db_session.commit()
        logger.info('Recinto: %s IDEvento: %d ID: %d Token: %d' %
                    (evento.recinto, evento.IDEvento, evento.ID, ohash))
    except IntegrityError as err:
        db_session.rollback()
        logging.error(err, exc_info=True)
        return 'Evento repetido ou campo invalido: %s' % err, 405
    except Exception as err:
        db_session.rollback()
        logging.error(err, exc_info=True)
        return 'Erro inesperado: %s ' % err, 405
    return ohash, 201


def get_evento(IDEvento, aclass):
    try:
        evento = db_session.query(aclass).filter(
            aclass.IDEvento == IDEvento
        ).one_or_none()
        # print(evento.dump() if evento is not None else 'None')
        # print(hash(evento) if evento is not None else 'None')
        if evento is None:
            return 'Not found', 404
        evento.hash = hash(evento)
        return evento.dump(), 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def add_evento(aclass, evento):
    logging.info('Creating evento %s %s' %
                 (aclass.__name__,
                  evento.get('IDEvento'))
                 )
    try:
        novo_evento = aclass(**evento)
        db_session.add(novo_evento)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 405
    return _commit(novo_evento)


def posicaoconteiner(evento):
    return add_evento(orm.PosicaoConteiner, evento)


def get_posicaoconteiner(IDEvento):
    return get_evento(IDEvento, orm.PosicaoConteiner)


def acessopessoa(evento):
    return add_evento(orm.AcessoPessoa, evento)


def get_acessopessoa(IDEvento):
    return get_evento(IDEvento, orm.AcessoPessoa)


def posicaoveiculo(evento):
    return add_evento(orm.PosicaoVeiculo, evento)


def get_posicaoveiculo(IDEvento):
    return get_evento(IDEvento, orm.PosicaoVeiculo)


def posicaolote(evento):
    return add_evento(orm.PosicaoLote, evento)


def get_posicaolote(IDEvento):
    return get_evento(IDEvento, orm.PosicaoLote)


def avarialote(evento):
    return add_evento(orm.AvariaLote, evento)


def get_avarialote(IDEvento):
    return get_evento(IDEvento, orm.AvariaLote)


def unitizacao(evento):
    return add_evento(orm.Unitizacao, evento)


def get_unitizacao(IDEvento):
    return get_evento(IDEvento, orm.Unitizacao)




def DTSC(evento):
    return add_evento(orm.DTSC, evento)


def get_DTSC(IDEvento):
    return get_evento(IDEvento, orm.DTSC)


def pesagemveiculovazio(evento):
    return add_evento(orm.PesagemVeiculoVazio, evento)


def get_pesagemveiculovazio(IDEvento):
    return get_evento(IDEvento, orm.PesagemVeiculoVazio)


def pesagemmaritimo(evento):
    return add_evento(orm.PesagemMaritimo, evento)


def get_pesagemmaritimo(IDEvento):
    return get_evento(IDEvento, orm.PesagemMaritimo)


def inspecaonaoinvasiva(evento):
    return add_evento(orm.InspecaonaoInvasiva, evento)


def get_inspecaonaoinvasiva(IDEvento):
    return get_evento(IDEvento, orm.InspecaonaoInvasiva)


def get_acessoveiculo(IDEvento):
    try:
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
        data['hash'] = hash(acessoveiculo)
        return data, 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def acessoveiculo(evento):
    logging.info('Creating acessoveiculo %s..', evento.get('IDEvento'))
    try:
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
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(acessoveiculo)

def desunitizacao(evento):
    logging.info('Creating desunitizacao %s..', evento.get('IDEvento'))
    try:
        desunitizacao = orm.Desunitizacao(**evento)
        db_session.add(desunitizacao)
        lotes = evento.get('lotes')
        if lotes:
            for lote in lotes:
                logging.info('Creating lotedesunitizacao %s..', lote.get('numerolote'))
                campos = ['numerolote', 'acrescimo',
                'documentodesconsolidacao', 'documentopapel',
                'falta', 'marca', 'observacoes', 'pesolote', 'qtdefalta',
                'qtdevolumes', 'tipodocumentodesconsolidacao',
                'tipodocumentopapel', 'tipovolume']
                olote = orm.Lote(desunitizacao=desunitizacao, **lote)
                db_session.add(olote)
        imagensdesunitizacao = evento.get('imagensdesunitizacao')
        if imagensdesunitizacao:
            for imagemdesunitizacao in imagensdesunitizacao:
                logging.info('Creating imagemdesunitizacao %s..', imagemdesunitizacao.get('caminhoarquivo'))
                aimagemdesunitizacao = orm.ImagemDesunitizacao(desunitizacao=desunitizacao,
                                                       caminhoarquivo=imagemdesunitizacao.get('caminhoarquivo'))
            db_session.add(aimagemdesunitizacao)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(desunitizacao)


def get_desunitizacao(IDEvento):
    try:
        desunitizacao = orm.desunitizacao.query.filter(
            orm.desunitizacao.IDEvento == IDEvento
        ).outerjoin(
            orm.Lote
        ).outerjoin(
            orm.ImagemDesunitizacao
        ).one_or_none()
        if desunitizacao is None:
            return {'message': 'Evento não encontrado.'}, 404
        desunitizacao_schema = orm.DesunitizacaoSchema()
        data = desunitizacao_schema.dump(desunitizacao).data
        data['hash'] = hash(desunitizacao)
        return data, 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400

def pesagemterrestre(evento):
    logging.info('Creating pesagemterrestre %s..', evento.get('IDEvento'))
    try:
        pesagemterrestre = orm.PesagemTerrestre(**evento)
        db_session.add(pesagemterrestre)
        conteineres = evento.get('conteineres')
        if conteineres:
            for conteiner in conteineres:
                logging.info('Creating conteinerpesagemterrestre %s..', conteiner.get('numero'))
                oconteiner = orm.ConteinerPesagemTerrestre(pesagem=pesagemterrestre,
                                                 numero=conteiner.get('numero'),
                                                 tara=conteiner.get('tara'))
                db_session.add(oconteiner)
        reboques = evento.get('reboques')
        if reboques:
            for reboque in reboques:
                logging.info('Creating reboque %s..', reboque.get('placa'))
                oreboque = orm.ReboquePesagemTerrestre(pesagem=pesagemterrestre,
                                                       placa=reboque.get('placa'),
                                                       tara=reboque.get('tara'))
            db_session.add(oreboque)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(pesagemterrestre)


def get_pesagemterrestre(IDEvento):
    try:
        pesagemterrestre = orm.PesagemTerrestre.query.filter(
            orm.PesagemTerrestre.IDEvento == IDEvento
        ).outerjoin(
            orm.ReboquePesagemTerrestre
        ).outerjoin(
            orm.ConteinerPesagemTerrestre
        ).one_or_none()
        if pesagemterrestre is None:
            return {'message': 'Evento não encontrado.'}, 404
        pesagemterrestre_schema = orm.PesagemTerrestreSchema()
        data = pesagemterrestre_schema.dump(pesagemterrestre).data
        data['hash'] = hash(pesagemterrestre)
        return data, 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def get_artefatorecinto(IDEvento):
    try:
        artefatorecinto = orm.ArtefatoRecinto.query.filter(
            orm.ArtefatoRecinto.IDEvento == IDEvento
        ).outerjoin(
            orm.CoordenadaArtefato).one_or_none()
        if artefatorecinto is None:
            return {'message': 'Evento não encontrado.'}, 404
        artefatorecinto_schema = orm.ArtefatoRecintoSchema()
        data = artefatorecinto_schema.dump(artefatorecinto).data
        data['hash'] = hash(artefatorecinto)
        return data, 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def artefatorecinto(evento):
    logging.info('Creating artefatorecinto %s..', evento.get('IDEvento'))
    try:
        artefatorecinto = orm.ArtefatoRecinto(**evento)
        db_session.add(artefatorecinto)
        coordenadas = evento.get('coordenadasartefato')
        if coordenadas:
            for coordenada in coordenadas:
                logging.info('Creating coordenada %s..', coordenada.get('ordem'))
                coordenadaarteafato = orm.CoordenadaArtefato(artefato=artefatorecinto,
                                                             ordem=coordenada.get('ordem'),
                                                             lat=coordenada.get('lat'),
                                                             long=coordenada.get('long')
                                                             )
                db_session.add(coordenadaarteafato)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(artefatorecinto)


def list_posicaoconteiner(filtro):
    try:
        try:
            recinto = filtro.get('recinto')
            datainicial = filtro.get('datainicial')
            datafinal = filtro.get('datafinal')
            altura = filtro.get('altura')
            filters = [orm.PosicaoConteiner.dataevento.between(datainicial, datafinal),
                       orm.PosicaoConteiner.recinto.like(recinto)]
            if altura is not None:
                filters.append(orm.PosicaoConteiner.altura.__eq__(int(altura)))
        except  Exception as err:
            logging.error(err, exc_info=True)
            return 'Erro nos filtros passados: %s' % str(err), 400
        eventos = db_session.query(
            orm.PosicaoConteiner
        ).filter(and_(*filters)).all()
        if eventos is None or len(eventos) == 0:
            return 'Sem eventos posicaoconteiner entre datas %s a %s.' % \
                   (datainicial, datafinal), 404
        return dump_eventos(eventos)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 405


def get_eventosnovos(filtro):
    try:
        print(filtro)
        IDEvento = filtro.get('IDEvento')
        dataevento = filtro.get('dataevento')
        tipoevento = filtro.get('tipoevento')
        aclass = getattr(orm, tipoevento)
        if dataevento is None:
            eventos = db_session.query(aclass).filter(
                aclass.IDEvento > IDEvento
            ).all()
        else:
            eventos = db_session.query(aclass).filter(
                aclass.dataevento > dataevento
            ).all()
        if eventos is None or len(eventos) == 0:
            if dataevento is None:
                return 'Sem eventos com ID maior que %d.' % IDEvento, 404
            return 'Sem eventos com dataevento maior que %s.' % dataevento, 404
        return dump_eventos(eventos)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 405


def create_app():
    app = connexion.FlaskApp(__name__)
    app.add_api('openapi.yaml')
    return app


app = create_app()
db_session, engine = orm.init_db()
