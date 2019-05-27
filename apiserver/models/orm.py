import collections
import logging

from dateutil.parser import parse
from marshmallow import Schema, fields, ValidationError
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy import Boolean, Column, DateTime, Integer, \
    String, create_engine, ForeignKey, Index, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.sql import func

Base = declarative_base()


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

    def __init__(self, IDEvento, dataevento, operadorevento, dataregistro, operadorregistro,
                 time_created=None, recinto=None, request_IP=None):
        self.IDEvento = IDEvento
        # print(dataevento)
        # print(parse(dataevento))
        self.dataevento = parse(dataevento)
        self.operadorevento = operadorevento
        self.dataregistro = parse(dataregistro)
        self.operadorregistro = operadorregistro

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
        print('Sorted dump:', _sorted)
        ovalues = tuple([s[1] for s in _sorted])
        print('Sorted ovalues:', ovalues)
        ohash = hash(ovalues)
        print(ohash)
        return ohash


class PosicaoConteiner(EventoBase):
    __tablename__ = 'posicoesconteiner'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numero = Column(String(11))
    placa = Column(String(11))
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
        self.emconferencia = kwargs.get('emconferencia') == 'True'
        self.solicitante = kwargs.get('solicitante')


class PesagemMaritimo(EventoBase):
    __tablename__ = 'pesagensmaritimo'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    documentotransporte = Column(String(20))
    tipodocumentotransporte = Column(String(10))
    numero = Column(String(11))
    placa = Column(String(11))
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
        # self.ID = kwargs.get('IDEvento')
        self.documentotransporte = kwargs.get('documentotransporte')
        self.tipodocumentotransporte = kwargs.get('tipodocumentotransporte')
        self.numero = kwargs.get('numero')
        self.placa = kwargs.get('placa')
        self.placasemireboque = kwargs.get('placasemireboque')
        self.pesobrutodeclarado = kwargs.get('pesobrutodeclarado')
        self.taraconjunto = kwargs.get('taraconjunto')
        self.pesobalanca = kwargs.get('pesobalanca')
        self.capturaautomatica = kwargs.get('capturaautomatica') == 'True'


class InspecaonaoInvasiva(EventoBase):
    __tablename__ = 'inspecoesnaoinvasivas'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    numero = Column(String(11))
    placa = Column(String(11))
    nomearquivo = Column(String(50))
    capturaautomatica = Column(Boolean())

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.numero = kwargs.get('numero')
        self.placa = kwargs.get('placa')
        self.capturaautomatica = kwargs.get('capturaautomatica') == 'True'


class AcessoVeiculo(EventoBase):
    __tablename__ = 'acessosveiculo'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    IDGate = Column(String(20))
    cpfmotorista = Column(String(11))
    conteineres = relationship('ConteineresGate')
    reboques = relationship('ReboquesGate')

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(EventoBase).keys()
        ])
        super().__init__(**superkwargs)
        self.placa = kwargs.get('placa')
        self.IDGate = kwargs.get('IDGate')
        self.cpfmotorista = kwargs.get('cpfmotorista')


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
    acessoveiculo_id = Column(Integer, ForeignKey('acessosveiculo.IDEvento'))
    acessoveiculo = relationship(
        'AcessoVeiculo'
    )

    def __init__(self, parent, numero, avarias, lacres, vazio):
        self.acessoveiculo_id = parent.IDEvento
        self.numero = numero
        self.avarias = avarias
        self.lacres = lacres
        self.vazio = vazio


class ReboquesGate(Gate):
    __tablename__ = 'reboquesgate'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    placa = Column(String(7))
    acessoveiculo_id = Column(Integer, ForeignKey('acessosveiculo.IDEvento'))
    acessoveiculo = relationship(
        'AcessoVeiculo'
    )

    def __init__(self, parent, placa, avarias, lacres, vazio):
        self.acessoveiculo_id = parent.IDEvento
        self.placa = placa
        self.avarias = avarias
        self.lacres = lacres
        self.vazio = vazio


# SCHEMAS

# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class GateSchema(Schema):
    ID = fields.Int(dump_only=True)
    avarias = fields.Str()
    lacres = fields.Str()
    vazio = fields.Boolean()


class ConteineresGateSchema(GateSchema):
    numero = fields.Str()


class ReboquesGateSchema(GateSchema):
    placa = fields.Str()


class AcessoVeiculoSchema(Schema):
    ID = fields.Int(dump_only=True)
    IDEvento = fields.Int()
    placa = fields.Str()
    IDGate = fields.Str()
    dataevento = fields.DateTime()
    operadorevento = fields.Str()
    dataregistro = fields.DateTime()
    operadorregistro = fields.Str()
    conteineres = fields.Nested('ConteineresGateSchema', many=True)
    reboques = fields.Nested('ReboquesGateSchema', many=True)


class AcessoVeiculoSchema2(ModelSchema):
    class Meta:
        model = AcessoVeiculo
        # sqla_session = session


# conteinergate_schema = ConteineresGateSchema()
# conteineresgate_schema = ConteineresGateSchema(many=True)
# acessoveiculo_schema = AcessoVeiculoSchema()
# acessosveiculo_schema = AcessoVeiculoSchema(many=True, only=('IDEvento'))

db_session = None
engine = None


def init_db(uri='sqlite:///test.db'):
    global db_session
    global engine
    if db_session is None:
        engine = create_engine(uri)
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
                                                 bind=engine))
        Base.query = db_session.query_property()
    return db_session, engine


if __name__ == '__main__':
    db, engine = init_db()
    try:
        Base.metadata.drop_all(bind=engine)
        # recinto_idevento_index.create(bind=engine)
        Table('acessosveiculo', Base.metadata,
              Index('acessosveiculo_ideventorecinto_idx',
                    'recinto', 'IDEvento',
                    unique=True,
                    ),
              extend_existing=True
              )
        Table('pesagensmaritimo', Base.metadata,
              Index('pesagensmaritimo_ideventorecinto_idx',
                    'recinto', 'IDEvento',
                    unique=True,
                    ),
              extend_existing=True
              )
        Table('posicoesconteiner', Base.metadata,
              Index('posicoesconteiner_ideventorecinto_idx',
                    'recinto', 'IDEvento',
                    unique=True,
                    ),
              extend_existing=True
              )
        Table('inspecoesnaoinvasivas', Base.metadata,
              Index('inspecoesnaoinvasivas_ideventorecinto_idx',
                    'recinto', 'IDEvento',
                    unique=True,
                    ),
              extend_existing=True
              )
        Base.metadata.create_all(bind=engine)
        print('Criou Banco!!!')
    except Exception as err:
        logging.error(err, exc_info=True)
