import collections
import logging
import mimetypes
import os
from base64 import b64decode, b64encode

from dateutil.parser import parse
from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy import Boolean, Column, DateTime, Integer, \
    String, create_engine, ForeignKey, Index, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.sql import func

Base = declarative_base()
db_session = None
engine = None


class EventoBase(Base):
    __abstract__ = True
    IDEvento = Column(Integer, index=True)
    dataevento = Column(DateTime(), index=True)
    operadorevento = Column(String(14), index=True)
    dataregistro = Column(DateTime(), index=True)
    operadorregistro = Column(String(14), index=True)
    time_created = Column(DateTime(timezone=True),
                          index=True,
                          server_default=func.now())
    recinto = Column(String(10), index=True)
    request_IP = Column(String(21), index=True)
    # TODO: Ver como tratar retificação (viola índice único)
    retificador = Column(Boolean)

    def __init__(self, IDEvento, dataevento, operadorevento, dataregistro,
                 operadorregistro, retificador,
                 time_created=None, recinto=None, request_IP=None):
        self.IDEvento = IDEvento
        # print(dataevento)
        # print(parse(dataevento))
        self.dataevento = parse(dataevento)
        self.operadorevento = operadorevento
        self.dataregistro = parse(dataregistro)
        self.operadorregistro = operadorregistro
        self.retificador = retificador
        if recinto is not None:
            self.recinto = recinto
        if request_IP is not None:
            self.request_IP = request_IP

    def dump(self):
        dump = dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])
        # dump.pop('ID')
        return dump

    def __hash__(self):
        dump = self.dump()
        clean_dump = {}
        for k, v in dump.items():
            if isinstance(v, collections.Hashable):
                clean_dump[k] = v
        _sorted = sorted([(k, v) for k, v in clean_dump.items()])
        # print('Sorted dump:', _sorted)
        ovalues = tuple([s[1] for s in _sorted])
        # print('Sorted ovalues:', ovalues)
        ohash = hash(ovalues)
        # print(ohash)
        return ohash


class PosicaoConteiner(EventoBase):
    __tablename__ = 'posicoesconteiner'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numero = Column(String(11))
    placa = Column(String(7))
    posicao = Column(String(20))
    altura = Column(Integer())
    emconferencia = Column(Boolean())
    solicitante = Column(String(10))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.numero = kwargs.get('numero')
        self.placa = kwargs.get('placa')
        self.posicao = kwargs.get('posicao')
        self.altura = kwargs.get('altura')
        self.emconferencia = kwargs.get('emconferencia')
        self.solicitante = kwargs.get('solicitante')


class AcessoPessoa(EventoBase):
    __tablename__ = 'acessospessoas'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    direcao = Column(String(10))
    formaidentificacao = Column(String(10))
    cpf = Column(String(11))
    identidade = Column(String(15))
    portaoacesso = Column(String(10))
    numerovoo = Column(String(20))
    reserva = Column(String(20))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.direcao = kwargs.get('direcao')
        self.formaidentificacao = kwargs.get('formaidentificacao')
        self.cpf = kwargs.get('cpf')
        self.identidade = kwargs.get('identidade')
        self.portaoacesso = kwargs.get('portaoacesso')
        self.numerovoo = kwargs.get('numerovoo')
        self.reserva = kwargs.get('reserva')


class PesagemTerrestre(EventoBase):
    __tablename__ = 'pesagensterrestres'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    documentotransporte = Column(String(20))
    tipodocumentotransporte = Column(String(10))
    placa = Column(String(7))
    tara = Column(Integer())
    pesobrutodeclarado = Column(Integer())
    pesobalanca = Column(Integer())
    capturaautomatica = Column(Boolean())
    # reboques = relationship('ReboquePesagemTerrestre')
    conteineres = relationship('ConteinerPesagemTerrestre')

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.documentotransporte = kwargs.get('documentotransporte')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')
        self.placa = kwargs.get('placa')
        self.tara = kwargs.get('tara')
        self.pesobrutodeclarado = kwargs.get('pesobrutodeclarado')
        self.pesobalanca = kwargs.get('pesobalanca')
        self.capturaautomatica = kwargs.get('capturaautomatica')


class ReboquePesagemTerrestre(Base):
    __tablename__ = 'reboquespesagemterrestre'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    tara = Column(Integer)
    pesagem_id = Column(Integer, ForeignKey('pesagensterrestres.ID'))
    pesagem = relationship(
        'PesagemTerrestre', backref=backref("reboques")
    )

    # def __init__(self, **kwargs):
    #    self.placa = kwargs.get('placa')
    #    self.tara = kwargs.get('tara')


class ConteinerPesagemTerrestre(Base):
    __tablename__ = 'conteinerespesagemterrestre'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numero = Column(String(11))
    tara = Column(Integer)
    pesagem_id = Column(Integer, ForeignKey('pesagensterrestres.ID'))
    pesagem = relationship(
        'PesagemTerrestre'
    )

    # def __init__(self, **kwargs):
    #    self.numero = kwargs.get('numero')
    #    self.tara = kwargs.get('tara')


class PesagemTerrestreSchema(ModelSchema):
    conteineres = fields.Nested('ConteinerPesagemTerrestreSchema', many=True,
                                exclude=('ID', 'pesagem_id', 'pesagem'))
    reboques = fields.Nested('ReboquePesagemTerrestreSchema', many=True,
                             exclude=('ID', 'pesagem_id', 'pesagem'))

    class Meta:
        model = PesagemTerrestre


class ConteinerPesagemTerrestreSchema(ModelSchema):
    class Meta:
        model = ConteinerPesagemTerrestre


class ReboquePesagemTerrestreSchema(ModelSchema):
    class Meta:
        model = ReboquePesagemTerrestre


class ArtefatoRecinto(EventoBase):
    __tablename__ = 'artefatosrecinto'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    tipoartefato = Column(String(10))
    codigo = Column(String(10))

    # coordenadas = relationship('CoordenadaArtefato')

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.recinto = kwargs.get('recinto')
        self.codigo = kwargs.get('codigo')
        self.tipoartefato = kwargs.get('tipoartefato')


class CoordenadaArtefato(Base):
    __tablename__ = 'coordenadasartefato'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    ordem = Column(Integer)
    long = Column(Float)
    lat = Column(Float)
    artefato_id = Column(Integer, ForeignKey('artefatosrecinto.ID'))
    artefato = relationship(
        'ArtefatoRecinto', backref=backref("coordenadasartefato")
    )


class ArtefatoRecintoSchema(ModelSchema):
    coordenadasartefato = fields.Nested('CoordenadaArtefatoSchema', many=True,
                                        exclude=('ID', 'artefato_id', 'artefato'))

    class Meta:
        model = ArtefatoRecinto


class CoordenadaArtefatoSchema(ModelSchema):
    class Meta:
        model = CoordenadaArtefato


class PesagemVeiculoVazio(EventoBase):
    __tablename__ = 'pesagensveiculosvazios'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    pesobalanca = Column(Integer())

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.placa = kwargs.get('placa')
        self.pesobalanca = kwargs.get('pesobalanca')


class ReboquesPesagem(Base):
    __tablename__ = 'reboquespesagem'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    pesagem_id = Column(Integer, ForeignKey('pesagensveiculosvazios.ID'))
    pesagem = relationship(
        'PesagemVeiculoVazio', backref=backref("reboques")
    )


class PesagemMaritimo(EventoBase):
    __tablename__ = 'pesagensmaritimo'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    documentotransporte = Column(String(20))
    tipodocumentotransporte = Column(String(10))
    numero = Column(String(11))
    placa = Column(String(7))
    placasemireboque = Column(String(11))
    pesobrutodeclarado = Column(Integer())
    taraconjunto = Column(Integer())
    pesobalanca = Column(Integer())
    capturaautomatica = Column(Boolean())

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.documentotransporte = kwargs.get('documentotransporte')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')
        self.numero = kwargs.get('numero')
        self.placa = kwargs.get('placa')
        self.placasemireboque = kwargs.get('placasemireboque')
        self.pesobrutodeclarado = kwargs.get('pesobrutodeclarado')
        self.taraconjunto = kwargs.get('taraconjunto')
        self.pesobalanca = kwargs.get('pesobalanca')
        self.capturaautomatica = kwargs.get('capturaautomatica')


class InspecaonaoInvasiva(EventoBase):
    __tablename__ = 'inspecoesnaoinvasivas'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    documentotransporte = Column(String(20))
    tipodocumentotransporte = Column(String(20))
    numero = Column(String(11))
    placa = Column(String(8))
    placasemireboque = Column(String(8))
    capturaautomatica = Column(Boolean)

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.documentotransporte = kwargs.get('documentotransporte')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')
        self.numero = kwargs.get('numero')
        self.placa = kwargs.get('placa')
        self.placasemireboque = kwargs.get('placasemireboque')
        self.capturaautomatica = kwargs.get('capturaautomatica')


class AnexoBase(Base):
    __abstract__ = True
    content = Column(String(1), default='')
    nomearquivo = Column(String(100), default='')
    contentType = Column(String(40), default='')

    def monta_caminho_arquivo(self, basepath, eventobase):
        filepath = basepath
        for caminho in [eventobase.recinto,
                        eventobase.dataevento.year,
                        eventobase.dataevento.month,
                        eventobase.dataevento.day]:
            filepath = os.path.join(filepath, str(caminho))
            if not os.path.exists(basepath):
                os.mkdir(filepath)
        return filepath

    def save_file(self, basepath, file, filename, evento) -> (str, bool):
        '''

        :param basepath: diretorio onde guardar arquivos
        :param file: objeto arquivo
        :return:
            mensagem de sucesso ou mensagem de erro
            True se sucesso, False se houve erro
        '''
        if not file or not filename:
            return None
        filepath = self.monta_caminho_arquivo(
            basepath, evento)
        with open(os.path.join(filepath, filename), 'wb') as file_out:
            file = b64decode(file.encode())
            file_out.write(file)
        self.contentType = mimetypes.guess_type(filename)[0]
        self.nomearquivo = filename
        return 'Arquivo salvo'

    def load_file(self, basepath, evento):
        if not self.nomearquivo:
            return ''
        filepath = self.monta_caminho_arquivo(basepath, evento)
        content = open(os.path.join(filepath, self.nomearquivo), 'rb')
        base64_bytes = b64encode(content.read())
        base64_string = base64_bytes.decode('utf-8')
        return base64_string


class AnexoInspecao(AnexoBase):
    __tablename__ = 'anexosinspecao'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    datacriacao = Column(DateTime())
    datamodificacao = Column(DateTime())
    inspecao_id = Column(Integer, ForeignKey('inspecoesnaoinvasivas.ID'))
    inspecao = relationship(
        'InspecaonaoInvasiva', backref=backref('anexos')
    )

    def save_file(self, basepath, file, filename) -> (str, bool):
        return super().save_file(basepath, file, filename, self.inspecao)

    def load_file(self, basepath):
        return super().load_file(basepath, self.inspecao)


class IdentificadorInspecao(Base):
    __tablename__ = 'identificadoresinspecao'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    identificador = Column(String(100))
    inspecao_id = Column(Integer, ForeignKey('inspecoesnaoinvasivas.ID'))
    inspecao = relationship(
        'InspecaonaoInvasiva', backref=backref('identificadores')
    )


class PosicaoLote(EventoBase):
    __tablename__ = 'posicoeslote'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numerolote = Column(Integer)
    posicao = Column(String(10))
    qtdevolumes = Column(Integer)

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.numerolote = kwargs.get('numerolote')
        self.posicao = kwargs.get('posicao')
        self.qtdevolumes = kwargs.get('qtdevolumes')


class Unitizacao(EventoBase):
    __tablename__ = 'unitizacoes'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    documentotransporte = Column(String(20))
    tipodocumentotransporte = Column(String(10))
    numero = Column(String(11))
    placa = Column(String(7))
    placasemireboque = Column(String(11))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        # self.ID = kwargs.get('IDEvento')
        self.documentotransporte = kwargs.get('documentotransporte')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')
        self.numero = kwargs.get('numero')
        self.placa = kwargs.get('placa')
        self.placasemireboque = kwargs.get('placasemireboque')


class ImagemUnitizacao(Base):
    __tablename__ = 'imagensunitizacao'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    caminhoarquivo = Column(String(100))
    content = Column(String(1))
    contentType = Column(String(40))
    datacriacao = Column(DateTime())
    datamodificacao = Column(DateTime())
    unitizacao_id = Column(Integer, ForeignKey('unitizacoes.ID'))
    unitizacao = relationship(
        'Unitizacao', backref=backref('imagens')
    )


class LoteUnitizacao(Base):
    __tablename__ = 'lotesunitizacao'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numerolote = Column(String(10))
    qtdevolumes = Column(Integer)
    unitizacao_id = Column(Integer, ForeignKey('unitizacoes.ID'))
    unitizacao = relationship(
        'Unitizacao', backref=backref('lotes')
    )


class AvariaLote(EventoBase):
    __tablename__ = 'avariaslote'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numerolote = Column(Integer)
    descricaoavaria = Column(String(50))
    qtdevolumes = Column(Integer)

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.numerolote = kwargs.get('numerolote')
        self.descricaoavaria = kwargs.get('descricaoavaria')
        self.qtdevolumes = kwargs.get('qtdevolumes')


class OperacaoNavio(EventoBase):
    __tablename__ = 'operacoesnavios'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    direcao = Column(String(10), index=True)
    imonavio = Column(String(7), index=True)
    viagem = Column(String(7))
    numero = Column(String(11))
    peso = Column(Integer)
    porto = Column(String(5))
    posicao = Column(String(10))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.direcao = kwargs.get('direcao')
        self.imonavio = kwargs.get('imonavio')
        self.viagem = kwargs.get('viagem')
        self.numero = kwargs.get('numero')
        self.peso = kwargs.get('peso')
        self.imonavio = kwargs.get('imonavio')
        self.porto = kwargs.get('porto')
        self.posicao = kwargs.get('posicao')


class Ocorrencias(EventoBase):
    __tablename__ = 'ocorrencias'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    tipoartefato = Column(String(10), index=True)
    codigo = Column(String(10), index=True)
    disponivel = Column(Boolean, index=True)
    motivo = Column(String(100))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.tipoartefato = kwargs.get('tipoartefato')
        self.codigo = kwargs.get('codigo')
        self.disponivel = kwargs.get('disponivel')
        self.motivo = kwargs.get('motivo')


class DTSC(EventoBase):
    __tablename__ = 'DTSC'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    imonavio = Column(String(7), index=True)
    viagem = Column(String(7))
    dataoperacao = Column(DateTime(), index=True)

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.imonavio = kwargs.get('imonavio')
        self.viagem = kwargs.get('viagem')
        self.dataoperacao = parse(kwargs.get('dataoperacao'))


class CargaDTSC(Base):
    __tablename__ = 'cargasDTSC'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    numero = Column(String(11))
    codigorecinto = Column(String(7))
    cpfcnpjproprietario = Column(String(15))
    cpfcnpjtransportador = Column(String(15))
    documentotransporte = Column(String(10))
    placasemireboque = Column(String(7))
    tipodocumentotransporte = Column(String(10))
    DTSC_id = Column(Integer, ForeignKey('DTSC.ID'))
    DTSC = relationship(
        'DTSC', backref=backref("cargas")
    )


class AcessoVeiculo(EventoBase):
    __tablename__ = 'acessosveiculo'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    IDAgendamento = Column(Integer)
    IDGate = Column(String(20))
    tipodocumentotransporte = Column(String(20))
    documentotransporte = Column(String(20))
    placa = Column(String(7))
    ocr = Column(Boolean)
    chassi = Column(String(30))
    cpfmotorista = Column(String(11))
    nomemotorista = Column(String(50))
    cpfcnpjtransportador = Column(String(14))
    nometransportador = Column(String(50))
    modal = Column(String(20))
    pesoespecial = Column(Boolean)
    dimensaoespecial = Column(Boolean)
    tipooperacao = Column(String(10))
    dataliberacao = Column(DateTime)
    dataagendamento = Column(DateTime)

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.IDAgendamento = kwargs.get('IDAgendamento')
        self.IDGate = kwargs.get('IDGate')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')
        self.documentotransporte = kwargs.get('documentotransporte')
        self.placa = kwargs.get('placa')
        self.ocr = kwargs.get('ocr')
        self.chassi = kwargs.get('chassi')
        self.cpfmotorista = kwargs.get('cpfmotorista')
        self.nomemotorista = kwargs.get('nomemotorista')
        self.cpfcnpjtransportador = kwargs.get('cpfcnpjtransportador')
        self.nometransportador = kwargs.get('nometransportador')
        self.modal = kwargs.get('modal')
        self.pesoespecial = kwargs.get('pesoespecial')
        self.dimensaoespecial = kwargs.get('dimensaoespecial')
        self.tipooperacao = kwargs.get('tipooperacao')
        self.dataliberacao = parse(kwargs.get('dataliberacao'))
        self.dataagendamento = parse(kwargs.get('dataagendamento'))


class Gate(Base):
    __abstract__ = True
    avarias = Column(String(50))
    lacres = Column(String(50))
    vazio = Column(Boolean())


class ConteineresGate(Gate):
    __tablename__ = 'conteineresgate'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numero = Column(String(11))
    vazio = Column(Boolean)
    lacres = Column(String(30))
    lacresverificados = Column(String(30))
    localsif = Column(String(20))
    lacressif = Column(String(30))
    lacressifverificados = Column(String(30))
    portodescarga = Column(String(30))
    paisdestino = Column(String(30))
    navioembarque = Column(String(30))
    numerobooking = Column(String(30))
    avarias = Column(String(100))
    cpfcnpjcliente = Column(String(14))
    nomecliente = Column(String(30))
    acessoveiculo_id = Column(Integer, ForeignKey('acessosveiculo.ID'))
    acessoveiculo = relationship(
        'AcessoVeiculo', backref=backref("conteineres")
    )


class ReboquesGate(Gate):
    __tablename__ = 'reboquesgate'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    vazio = Column(Boolean)
    lacres = Column(String(30))
    lacresverificados = Column(String(30))
    localsif = Column(String(20))
    lacressif = Column(String(30))
    lacressifverificados = Column(String(30))
    cnpjestadia = Column(String(14))
    nomeestadia = Column(String(50))
    avarias = Column(String(100))
    acessoveiculo_id = Column(Integer, ForeignKey('acessosveiculo.ID'))
    acessoveiculo = relationship(
        'AcessoVeiculo', backref=backref("reboques")
    )


class ListaNfeGate(Base):
    __tablename__ = 'listanfegate'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    chavenfe = Column(String(30))
    acessoveiculo_id = Column(Integer, ForeignKey('acessosveiculo.ID'))
    acessoveiculo = relationship(
        'AcessoVeiculo', backref=backref("listanfe")
    )


class PosicaoVeiculo(EventoBase):
    __tablename__ = 'posicoesveiculo'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    box = Column(String(20))
    camera = Column(String(20))
    divergencia = Column(Boolean)
    emconferencia = Column(Boolean)
    observacaodivergencia = Column(String(100))
    solicitante = Column(String(20))
    documentotransporte = Column(String(20))
    tipodocumentotransporte = Column(String(20))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.placa = kwargs.get('placa')
        self.box = kwargs.get('box')
        self.camera = kwargs.get('camera')
        self.divergencia = kwargs.get('divergencia')
        self.emconferencia = kwargs.get('emconferencia')
        self.observacaodivergencia = kwargs.get('observacaodivergencia')
        self.solicitante = kwargs.get('solicitante')
        self.documentotransporte = kwargs.get('documentotransporte')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')


class ConteinerPosicao(Base):
    __tablename__ = 'conteineresposicao'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numero = Column(String(11))
    vazio = Column(Boolean)
    posicaoveiculo_id = Column(Integer, ForeignKey('posicoesveiculo.ID'))
    posicaoveiculo = relationship(
        'PosicaoVeiculo', backref=backref('conteineres')
    )


class ReboquePosicao(Base):
    __tablename__ = 'reboquesposicao'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    vazio = Column(Boolean)
    posicaoveiculo_id = Column(Integer, ForeignKey('posicoesveiculo.ID'))
    posicaoveiculo = relationship(
        'PosicaoVeiculo', backref=backref('reboques')
    )


class Desunitizacao(EventoBase):
    __tablename__ = 'desunitizacoes'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    documentotransporte = Column(String(20))
    tipodocumentotransporte = Column(String(10))
    numero = Column(String(11))
    placa = Column(String(7))
    placasemireboque = Column(String(11))

    # imagens = relationship('ImagemDesunitizacao')
    # lotes = relationship('Lote')

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.documentotransporte = kwargs.get('documentotransporte')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')
        self.numero = kwargs.get('numero')
        self.placa = kwargs.get('placa')
        self.placasemireboque = kwargs.get('placasemireboque')


class ImagemDesunitizacao(Base):
    __tablename__ = 'imagensdesunitizacao'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    caminhoarquivo = Column(String(100))
    content = Column(String(1))
    contentType = Column(String(40))
    datacriacao = Column(DateTime())
    datamodificacao = Column(DateTime())
    desunitizacao_id = Column(Integer, ForeignKey('desunitizacoes.ID'))
    desunitizacao = relationship(
        'Desunitizacao', backref=backref('imagens')
    )


class Lote(Base):
    __tablename__ = 'lotes'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numerolote = Column(String(10))
    acrescimo = Column(Boolean)
    documentodesconsolidacao = Column(String(20))
    tipodocumentodesconsolidacao = Column(String(20))
    documentopapel = Column(String(20))
    tipodocumentopapel = Column(String(20))
    falta = Column(Boolean)
    marca = Column(String(100))
    observacoes = Column(String(100))
    pesolote = Column(Integer)
    qtdefalta = Column(Integer)
    qtdevolumes = Column(Integer)
    tipovolume = Column(String(20))
    desunitizacao_id = Column(Integer, ForeignKey('desunitizacoes.ID'))
    desunitizacao = relationship(
        'Desunitizacao', backref=backref("lotes")
    )


'''
    def __init__(self, parent, numerolote, acrescimo,
                 documentodesconsolidacao, documentopapel,
                 falta, marca, observacoes, pesolote, qtdefalta,
                 qtdevolumes, tipodocumentodesconsolidacao,
                 tipodocumentopapel, tipovolume):
        self.desunitizacao_id = parent.ID
        self.numerolote = numerolote
        self.acrescimo = acrescimo
        self.documentodesconsolidacao = documentodesconsolidacao
        self.documentopapel = documentopapel
        self.falta = falta
        self.marca = marca
        self.observacoes = observacoes
        self.pesolote = pesolote
        self.qtdefalta = qtdefalta
        self.qtdevolumes = qtdevolumes
        self.tipodocumentodesconsolidacao = tipodocumentodesconsolidacao
        self.tipodocumentopapel = tipodocumentopapel
        self.tipovolume = tipovolume
'''


class DesunitizacaoSchema(ModelSchema):
    lotes = fields.Nested('LoteSchema', many=True,
                          exclude=('ID', 'desunitizacao_id', 'desunitizacao'))
    imagens = fields.Nested('ImagemDesunitizacaoSchema', many=True,
                            exclude=('ID', 'desunitizacao_id', 'desunitizacao'))

    class Meta:
        model = Desunitizacao


class LoteSchema(ModelSchema):
    class Meta:
        model = Lote


class ImagemDesunitizacaoSchema(ModelSchema):
    class Meta:
        model = ImagemDesunitizacao


# SCHEMAS

# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


def init_db(uri='sqlite:///test.db'):
    global db_session
    global engine
    if db_session is None:
        print('Conectando banco %s' % uri)
        engine = create_engine(uri)
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                                 bind=engine))
        Base.query = db_session.query_property()
        for table in ['DTSC', 'acessospessoas', 'avariaslote', 'desunitizacoes', 'pesagensterrestres',
                      'pesagensveiculosvazios', 'posicoeslote', 'posicoesveiculo', 'unitizacoes',
                      'acessosveiculo', 'pesagensmaritimo', 'posicoesconteiner', 'inspecoesnaoinvasivas',
                      'artefatosrecinto', 'ocorrencias', 'operacoesnavios']:
            # print(table)
            Table(table, Base.metadata,
                  Index(table + '_ideventorecinto_idx',
                        'recinto', 'IDEvento',
                        unique=True,
                        ),
                  extend_existing=True
                  )
    return db_session, engine


if __name__ == '__main__':
    db, engine = init_db()
    try:
        print('Apagando Banco!!!')
        Base.metadata.drop_all(bind=engine)
        print('Criando Banco novo!!!')
        Base.metadata.create_all(bind=engine)
    except Exception as err:
        logging.error(err, exc_info=True)
