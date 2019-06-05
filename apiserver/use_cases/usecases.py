import logging

from apiserver.models import orm


class UseCases():
    def __init__(self, db_session, recinto: str, request_IP: str, basepath: str):
        """Init

        :param db_session: Conexao ao Banco
        :param recinto: codigo do recinto
        :param request_IP: IP de origem
        :param basepath: Diretório raiz para gravar arquivos
        """
        self.db_session = db_session
        self.recinto = recinto
        self.request_IP = request_IP
        self.basepath = basepath

    def insert_evento(self, aclass, evento: dict, commit=True) -> orm.EventoBase:
        logging.info('Creating evento %s %s' %
                     (aclass.__name__,
                      evento.get('IDEvento'))
                     )
        novo_evento = aclass(**evento)
        novo_evento.recinto = self.recinto
        novo_evento.request_IP = self.request_IP
        self.db_session.add(novo_evento)
        if commit:
            self.db_session.commit()
        else:
            self.db_session.flush()
        self.db_session.refresh(novo_evento)
        novo_evento.hash = hash(novo_evento)
        return novo_evento

    def load_evento(self, aclass, IDEvento: int) -> orm.EventoBase:
        """
        Retorna Evento classe aclass encontrado único com recinto E IDEvento.

        Levanta exceção NoResultFound(não encontrado) ou MultipleResultsFound.

        :param IDEvento: ID do Evento informado pelo recinto
        :return: objeto
        """

        evento = self.db_session.query(aclass).filter(
            aclass.IDEvento == IDEvento,
            aclass.recinto == self.recinto
        ).one()
        return evento

    def insert_inspecaonaoinvasiva(self, evento: dict) -> orm.InspecaonaoInvasiva:
        logging.info('Creating inspecaonaoinvasiva %s..', evento.get('IDEvento'))
        inspecaonaoinvasiva = self.insert_evento(orm.InspecaonaoInvasiva, evento,
                                                 commit=False)
        anexos = evento.get('anexos', [])
        for anexo in anexos:
            anexo['inspecao_id'] = inspecaonaoinvasiva.ID
            logging.info('Creating anexoinspecaonaoinvasiva %s..',
                         anexo.get('datamodificacao'))
            anexoinspecao = orm.AnexoInspecao(inspecao=inspecaonaoinvasiva,
                                              **anexo)
            content = anexo.get('content')
            if anexo.get('content'):
                anexoinspecao.save_file(self.basepath, content)
            self.db_session.add(anexoinspecao)
        identificadores = evento.get('identificadores', [])
        for identificador in identificadores:
            logging.info('Creating identificadorinspecaonaoinvasiva %s..',
                         identificador.get('identificador'))
            oidentificador = orm.IdentificadorInspecao(
                inspecao=inspecaonaoinvasiva,
                **identificador)
            self.db_session.add(oidentificador)
        self.db_session.commit()
        return inspecaonaoinvasiva

    def load_inspecaonaoinvasiva(self, IDEvento: int) -> orm.InspecaonaoInvasiva:
        """
        Retorna InspecaonaoInvasiva encontrada única no filtro recinto E IDEvento.

        :param IDEvento: ID do Evento informado pelo recinto
        :return: instância objeto orm.InspecaonaoInvasiva
        """
        inspecaonaoinvasiva = orm.InspecaonaoInvasiva.query.filter(
            orm.InspecaonaoInvasiva.IDEvento == IDEvento,
            orm.InspecaonaoInvasiva.recinto == self.recinto
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
                anexo.load_file(self.basepath)
                inspecaonaoinvasiva_dump['anexos'].append(
                    anexo.dump(exclude=['ID', 'inspecao', 'inspecao_id'])
                )
        if inspecaonaoinvasiva.identificadores and len(inspecaonaoinvasiva.identificadores) > 0:
            inspecaonaoinvasiva_dump['identificadores'] = []
            for identificador in inspecaonaoinvasiva.identificadores:
                inspecaonaoinvasiva_dump['identificadores'].append(
                    identificador.dump(exclude=['ID', 'inspecao', 'inspecao_id'])
                )
        return inspecaonaoinvasiva_dump
