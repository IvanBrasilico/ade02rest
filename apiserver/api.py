import logging

from dateutil.parser import parse
from flask import current_app, request, jsonify
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from apiserver.logconf import logger
from apiserver.models import maschemas, orm

RECINTO = '00001'


def dump_eventos(eventos):
    eventos_dump = []
    for evento in eventos:
        evento.hash = hash(evento)
        eventos_dump.append(evento.dump())
    return jsonify(eventos_dump)


def _commit(evento):
    db_session = current_app.config['db_session']
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
    db_session = current_app.config['db_session']
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
    db_session = current_app.config['db_session']
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




def posicaolote(evento):
    return add_evento(orm.PosicaoLote, evento)


def get_posicaolote(IDEvento):
    return get_evento(IDEvento, orm.PosicaoLote)


def avarialote(evento):
    return add_evento(orm.AvariaLote, evento)


def get_avarialote(IDEvento):
    return get_evento(IDEvento, orm.AvariaLote)


def DTSC(evento):
    return add_evento(orm.DTSC, evento)


def get_DTSC(IDEvento):
    return get_evento(IDEvento, orm.DTSC)


def pesagemmaritimo(evento):
    return add_evento(orm.PesagemMaritimo, evento)


def get_pesagemmaritimo(IDEvento):
    return get_evento(IDEvento, orm.PesagemMaritimo)


def inspecaonaoinvasiva(evento):
    return add_evento(orm.InspecaonaoInvasiva, evento)


def get_inspecaonaoinvasiva(IDEvento):
    return get_evento(IDEvento, orm.InspecaonaoInvasiva)


def operacaonavio(evento):
    return add_evento(orm.OperacaoNavio, evento)


def get_operacaonavio(IDEvento):
    return get_evento(IDEvento, orm.OperacaoNavio)


def ocorrencia(evento):
    return add_evento(orm.Ocorrencias, evento)


def get_ocorrencia(IDEvento):
    return get_evento(IDEvento, orm.Ocorrencias)


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
    db_session = current_app.config['db_session']
    logging.info('Creating acessoveiculo %s..', evento.get('IDEvento'))
    try:
        acessoveiculo = orm.AcessoVeiculo(**evento)
        db_session.add(acessoveiculo)
        conteineres = evento.get('conteineres')
        if conteineres:
            for conteiner in conteineres:
                logging.info('Creating conteiner %s..', conteiner.get('numero'))
                conteinergate = orm.ConteineresGate(acessoveiculo=acessoveiculo,
                                                    numero=conteiner.get('numero'),
                                                    avarias=conteiner.get('avarias'),
                                                    lacres=conteiner.get('lacres'),
                                                    vazio=conteiner.get('vazio'))
                db_session.add(conteinergate)
        reboques = evento.get('reboques')
        if reboques:
            for reboque in reboques:
                logging.info('Creating reboque %s..', reboque.get('placa'))
                reboquegate = orm.ReboquesGate(acessoveiculo=acessoveiculo,
                                               placa=reboque.get('placa'),
                                               avarias=reboque.get('avarias'),
                                               lacres=reboque.get('lacres'),
                                               vazio=reboque.get('vazio'))
            db_session.add(reboquegate)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(acessoveiculo)


def pesagemveiculovazio(evento):
    db_session = current_app.config['db_session']
    logging.info('Creating pesagemveiculovazio %s..', evento.get('IDEvento'))
    try:
        pesagemveiculovazio = orm.PesagemVeiculoVazio(**evento)
        db_session.add(pesagemveiculovazio)
        reboques = evento.get('reboques')
        if reboques:
            for reboque in reboques:
                logging.info('Creating lotepesagemveiculovazio %s..',
                             reboque.get('placa'))
                olote = orm.ReboquesPesagem(
                    pesagem=pesagemveiculovazio,
                    placa=reboque.get('placa')
                )
                db_session.add(olote)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(pesagemveiculovazio)


def get_pesagemveiculovazio(IDEvento):
    try:
        pesagemveiculovazio = orm.PesagemVeiculoVazio.query.filter(
            orm.PesagemVeiculoVazio.IDEvento == IDEvento
        ).outerjoin(
            orm.ReboquesPesagem
        ).one_or_none()
        if pesagemveiculovazio is None:
            return {'message': 'Evento não encontrado.'}, 404
        pesagemveiculovazio_schema = maschemas.PesagemVeiculoVazio()
        data = pesagemveiculovazio_schema.dump(pesagemveiculovazio).data
        data['hash'] = hash(pesagemveiculovazio)
        return data, 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400

def posicaoveiculo(evento):
    db_session = current_app.config['db_session']
    logging.info('Creating posicaoveiculo %s..', evento.get('IDEvento'))
    try:
        posicaoveiculo = orm.PosicaoVeiculo(**evento)
        db_session.add(posicaoveiculo)
        conteineres = evento.get('conteineres')
        if conteineres:
            for conteiner in conteineres:
                logging.info('Creating conteinerpesagemterrestre %s..', conteiner.get('numero'))
                oconteiner = orm.ConteinerPosicao(posicaoveiculo=posicaoveiculo,
                                                           numero=conteiner.get('numero'),
                                                           vazio=conteiner.get('vazio'))
                db_session.add(oconteiner)
        reboques = evento.get('reboques')
        if reboques:
            for reboque in reboques:
                logging.info('Creating reboque %s..', reboque.get('placa'))
                oreboque = orm.ReboquePosicao(posicaoveiculo=posicaoveiculo,
                                                       placa=reboque.get('placa'),
                                                       vazio=reboque.get('vazio'))
            db_session.add(oreboque)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(posicaoveiculo)


def get_posicaoveiculo(IDEvento):
    try:
        posicaoveiculo = orm.PosicaoVeiculo.query.filter(
            orm.PosicaoVeiculo.IDEvento == IDEvento
        ).outerjoin(
            orm.ConteinerPosicao
        ).outerjoin(
            orm.ReboquePosicao
        ).one_or_none()
        if posicaoveiculo is None:
            return {'message': 'Evento não encontrado.'}, 404
        posicaoveiculo_schema = maschemas.PosicaoVeiculo()
        data = posicaoveiculo_schema.dump(posicaoveiculo).data
        data['hash'] = hash(posicaoveiculo)
        return data, 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400



def unitizacao(evento):
    db_session = current_app.config['db_session']
    logging.info('Creating unitizacao %s..', evento.get('IDEvento'))
    try:
        unitizacao = orm.Unitizacao(**evento)
        db_session.add(unitizacao)
        lotes = evento.get('lotes')
        if lotes:
            for lote in lotes:
                logging.info('Creating loteunitizacao %s..',
                             lote.get('numerolote'))
                olote = orm.LoteUnitizacao(unitizacao=unitizacao, **lote)
                db_session.add(olote)
        imagensunitizacao = evento.get('imagens')
        if imagensunitizacao:
            for imagemunitizacao in imagensunitizacao:
                logging.info('Creating imagemunitizacao %s..',
                             imagemunitizacao.get('caminhoarquivo'))
                aimagemunitizacao = orm.ImagemUnitizacao(
                    unitizacao=unitizacao,
                    caminhoarquivo=imagemunitizacao.get('caminhoarquivo'),
                    content=imagemunitizacao.get('content'),
                    contentType=imagemunitizacao.get('contentType'),
                    datacriacao=parse(imagemunitizacao.get('datacriacao')),
                    datamodificacao=parse(imagemunitizacao.get('datamodificacao'))
                )
            db_session.add(aimagemunitizacao)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(unitizacao)


def get_unitizacao(IDEvento):
    try:
        unitizacao = orm.Unitizacao.query.filter(
            orm.Unitizacao.IDEvento == IDEvento
        ).outerjoin(
            orm.LoteUnitizacao
        ).outerjoin(
            orm.ImagemUnitizacao
        ).one_or_none()
        if unitizacao is None:
            return {'message': 'Evento não encontrado.'}, 404
        unitizacao_schema = maschemas.Unitizacao()
        data = unitizacao_schema.dump(unitizacao).data
        data['hash'] = hash(unitizacao)
        return data, 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def desunitizacao(evento):
    db_session = current_app.config['db_session']
    logging.info('Creating desunitizacao %s..', evento.get('IDEvento'))
    try:
        desunitizacao = orm.Desunitizacao(**evento)
        db_session.add(desunitizacao)
        lotes = evento.get('lotes')
        if lotes:
            for lote in lotes:
                logging.info('Creating lotedesunitizacao %s..',
                             lote.get('numerolote'))
                olote = orm.Lote(desunitizacao=desunitizacao, **lote)
                db_session.add(olote)
        imagensdesunitizacao = evento.get('imagens')
        if imagensdesunitizacao:
            for imagemdesunitizacao in imagensdesunitizacao:
                logging.info('Creating imagemdesunitizacao %s..',
                             imagemdesunitizacao.get('caminhoarquivo'))
                aimagemdesunitizacao = orm.ImagemDesunitizacao(
                    desunitizacao=desunitizacao,
                    caminhoarquivo=imagemdesunitizacao.get('caminhoarquivo'),
                    content=imagemdesunitizacao.get('content'),
                    contentType=imagemdesunitizacao.get('contentType'),
                    datacriacao=parse(imagemdesunitizacao.get('datacriacao')),
                    datamodificacao=parse(imagemdesunitizacao.get('datamodificacao'))
                )
                db_session.add(aimagemdesunitizacao)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400
    return _commit(desunitizacao)


def get_desunitizacao(IDEvento):
    try:
        desunitizacao = orm.Desunitizacao.query.filter(
            orm.Desunitizacao.IDEvento == IDEvento
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
    db_session = current_app.config['db_session']
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
    db_session = current_app.config['db_session']
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
    db_session = current_app.config['db_session']
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
    db_session = current_app.config['db_session']
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
