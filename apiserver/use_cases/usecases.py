import logging

from apiserver.models import orm


def insert_evento(db_session, aclass, evento: dict,
                  recinto='', request_IP='') -> orm.EventoBase:
    novo_evento = aclass(**evento)
    if recinto:
        novo_evento.recinto = recinto
    if request_IP:
        novo_evento.request_IP = request_IP
    db_session.add(novo_evento)
    db_session.commit()
    db_session.refresh(novo_evento)
    novo_evento.hash = hash(novo_evento)
    return novo_evento


def load_evento(db_session, aclass,
                recinto: str, IDEvento: int) -> orm.EventoBase:
    """
    Retorna Evento classe aclass encontrado único com recinto E IDEvento.

    Levanta exceção NoResultFound(não encontrado) ou MultipleResultsFound.

    :param db_session:
    :param recinto: codigo do recinto
    :param IDEvento: ID do Evento informado pelo recinto
    :return: objeto
    """

    evento = db_session.query(aclass).filter(
        aclass.IDEvento == IDEvento,
        aclass.recinto == recinto
    ).one()
    return evento


def insert_inspecaonaoinvasiva(
        db_session, evento: dict,
        recinto: str, request_IP: str) -> orm.InspecaonaoInvasiva:
    inspecaonaoinvasiva = insert_evento(
        db_session, orm.InspecaonaoInvasiva, evento,
        recinto, request_IP)
    anexos = evento.get('anexos', [])
    for anexo in anexos:
        anexo['inspecao_id'] = inspecaonaoinvasiva.ID
        logging.info('Creating anexoinspecaonaoinvasiva %s..',
                     anexo.get('datamodificacao'))
        anexoinspecao = orm.AnexoInspecao(inspecao=inspecaonaoinvasiva,
                                          **anexo)
        db_session.add(anexoinspecao)
    identificadores = evento.get('identificadores', [])
    for identificador in identificadores:
        logging.info('Creating identificadorinspecaonaoinvasiva %s..',
                     identificador.get('identificador'))
        oidentificador = orm.IdentificadorInspecao(
            inspecao=inspecaonaoinvasiva,
            **identificador)
        db_session.add(oidentificador)
    db_session.commit()
    return inspecaonaoinvasiva


def load_inspecaonaoinvasiva(recinto: str, IDEvento: int,
                             basepath: str) -> orm.InspecaonaoInvasiva:
    """
    Retorna InspecaonaoInvasiva encontrada única no filtro recinto E IDEvento.

    :param recinto: codigo do recinto
    :param IDEvento: ID do Evento informado pelo recinto
    :param basepath: diretorio dos anexos
    :return: instância objeto orm.InspecaonaoInvasiva
    """
    inspecaonaoinvasiva = orm.InspecaonaoInvasiva.query.filter(
        orm.InspecaonaoInvasiva.IDEvento == IDEvento,
        orm.InspecaonaoInvasiva.recinto == recinto
    ).outerjoin(
        orm.AnexoInspecao
    ).outerjoin(
        orm.IdentificadorInspecao
    ).one()
    inspecaonaoinvasiva_dump = inspecaonaoinvasiva.dump()
    inspecaonaoinvasiva_dump['hash'] = hash(inspecaonaoinvasiva)
    if inspecaonaoinvasiva.anexos and len(inspecaonaoinvasiva.anexos) > 0:
        inspecaonaoinvasiva_dump['anexos'] = []
        for anexo in inspecaonaoinvasiva.anexos:
            inspecaonaoinvasiva_dump['anexos'].append(anexo.dump())
    if inspecaonaoinvasiva.identificadores and len(inspecaonaoinvasiva.identificadores) > 0:
        inspecaonaoinvasiva_dump['identificadores'] = []
        for identificador in inspecaonaoinvasiva.identificadores:
            inspecaonaoinvasiva_dump['identificadores'].append(identificador.dump())
    return inspecaonaoinvasiva_dump
