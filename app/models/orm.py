from dateutil.parser import parse
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import Boolean, Column, DateTime, Integer, \
    String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship

Base = declarative_base()


class EventoBase(Base):
    __abstract__ = True
    IDEvento = Column(Integer, primary_key=True)
    dataevento = Column(DateTime())
    operadorevento = Column(String(14))
    dataregistro = Column(DateTime())
    operadorregistro = Column(String(14))

    def __init__(self, IDEvento, dataevento, operadorevento, dataregistro, operadorregistro):
        self.IDEvento = IDEvento
        print(dataevento)
        print(parse(dataevento))
        self.dataevento = parse(dataevento)
        self.operadorevento = operadorevento
        self.dataregistro = parse(dataregistro)
        self.operadorregistro = operadorregistro

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])


class Evento(EventoBase):
    __tablename__ = 'eventos'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)

    def __init__(self, IDEvento, dataevento, operadorevento,
                 dataregistro, operadorregistro):
        super().__init__(IDEvento, dataevento, operadorevento,
                         dataregistro, operadorregistro)
        self.ID = IDEvento


class PosicaoConteiner(EventoBase):
    __tablename__ = 'posicoesconteiner'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    conteiner = Column(String(11))
    placa = Column(String(11))
    posicao = Column(String(20))
    altura = Column(Integer())
    emconferencia = Column(Boolean())
    solicitante = Column(String(10))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(Evento).keys()
        ])
        super().__init__(**superkwargs)
        self.ID = kwargs.get('IDEvento')
        self.conteiner = kwargs.get('conteiner')
        self.placa = kwargs.get('placa')
        self.posicao = kwargs.get('posicao')
        self.altura = kwargs.get('altura')
        self.emconferencia = kwargs.get('emconferencia') == 'True'
        self.solicitante = kwargs.get('solicitante')


class AcessoVeiculo(EventoBase):
    __tablename__ = 'acessosveiculo'
    __table_args__ = {'sqlite_autoincrement': True}
    ID = Column(Integer, primary_key=True)
    conteineres = relationship('ConteineresGate')
    placa = Column(String(7))
    IDGate = Column(String(20))

    def __init__(self, **kwargs):
        superkwargs = dict([
            (k, v) for k, v in kwargs.items() if k in vars(Evento).keys()
        ])
        super().__init__(**superkwargs)
        self.ID = kwargs.get('IDEvento')
        self.placa = kwargs.get('placa')
        self.IDGate = kwargs.get('IDGate')


class ConteineresGate(Base):
    __tablename__ = 'conteineresgate'
    id = Column(Integer, primary_key=True)
    numero = Column(String(11))
    acessoveiculo_id = Column(Integer, ForeignKey('acessosveiculo.ID'))
    acessoveiculo = relationship(
        'AcessoVeiculo'
    )

    def __init__(self, parent, numero):
        self.acessoveiculo_id = parent.ID
        self.numero = numero


# SCHEMAS

# Custom validator
def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class ConteineresGateSchema(Schema):
    ID = fields.Int(dump_only=True)
    numero = fields.Str()


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


# conteinergate_schema = ConteineresGateSchema()
# conteineresgate_schema = ConteineresGateSchema(many=True)
# acessoveiculo_schema = AcessoVeiculoSchema()
# acessosveiculo_schema = AcessoVeiculoSchema(many=True, only=('IDEvento'))

db_session = None


def init_db(uri):
    global db_session
    if db_session is None:
        engine = create_engine(uri, convert_unicode=True)
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        Base.query = db_session.query_property()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print('Criou Banco!!!')
    return db_session
