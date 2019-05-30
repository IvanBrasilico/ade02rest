import sqlalchemy as sa
from marshmallow import fields
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref

engine = sa.create_engine("sqlite:///:memory:")
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    def __repr__(self):
        return "<Author(name={self.name!r})>".format(self=self)


class Book(Base):
    __tablename__ = "books"
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("authors.id"))
    author = relationship("Author", backref=backref("books"))


class ArtefatoRecinto(Base):
    __tablename__ = 'artefatosrecinto'
    ID = sa.Column(sa.Integer, primary_key=True)
    codigo = sa.Column(sa.String(10))


class CoordenadaArtefato(Base):
    __tablename__ = 'coordenadasartefato'
    ID = sa.Column(sa.Integer, primary_key=True)
    long = sa.Column(sa.Float)
    lat = sa.Column(sa.Float)
    artefato_id = sa.Column(sa.Integer, sa.ForeignKey('artefatosrecinto.ID'))
    artefato = relationship(
        'ArtefatoRecinto', backref=backref("coordenadasartefato")
    )



Base.metadata.create_all(engine)
from marshmallow_sqlalchemy import ModelSchema


class AuthorSchema(ModelSchema):
    class Meta:
        model = Author


class BookSchema(ModelSchema):
    class Meta:
        model = Book
        # optionally attach a Session
        # to use for deserialization
        sqla_session = session


class SmartNested(fields.Nested):
    def serialize(self, attr, obj, accessor=None):
        if attr not in obj.__dict__:
            return {"id": int(getattr(obj, attr + "_id"))}
        return super(SmartNested, self).serialize(attr, obj, accessor)


class SmartNested2(fields.Nested):
    def serialize(self, attr, obj, accessor=None):
        if attr not in obj.__dict__:
            print('%%%%%%%%', attr)
        return super(SmartNested, self).serialize(attr, obj, accessor)


class CoordenadaArtefatoSchema(ModelSchema):
    # artefato = SmartNested(ArtefatoRecintoSchema)
    class Meta:
        model = CoordenadaArtefato

class ArtefatoRecintoSchema(ModelSchema):
    coordenadasartefato = fields.Nested('CoordenadaArtefatoSchema', many=True, exclude=('artefato'))
    class Meta:
        model = ArtefatoRecinto
        sqla_session = session






author_schema = AuthorSchema()

author = Author(name="Chuck Paluhniuk")
author_schema = AuthorSchema()
book = Book(title="Fight Club", author=author)
session.add(author)
session.add(book)
session.commit()

print(author)
print(author.books)

dump_data = author_schema.dump(author).data
print(dump_data)
# {'books': [123], 'id': 321, 'name': 'Chuck Paluhniuk'}

data = author_schema.load(dump_data, session=session).data
print(data)
# <Author(name='Chuck Paluhniuk')>

artefato = ArtefatoRecinto(codigo='1')
                               #IDEvento=1000, dataevento='2019-01-01', operadorevento='ivan',
                               #dataregistro='2019-01-01', operadorregistro='ivan', retificador=False)
coordenada_artefato = CoordenadaArtefato(artefato=artefato, lat=1.0, long=2.0)
session.add(artefato)
session.add(coordenada_artefato)
session.commit()
# session.refresh(artefato)
print(artefato)
print(coordenada_artefato)
print(hash(artefato))
# print(artefato.coordenadas)
print(artefato.coordenadasartefato)

artefato_schema = ArtefatoRecintoSchema()
coordenada_artefato_schema = CoordenadaArtefatoSchema()

dump_data = artefato_schema.dump(artefato).data
print(dump_data)
dump_data = coordenada_artefato_schema.dump(coordenada_artefato).data
print(dump_data)
artefato = artefato_schema.load(dump_data, session=session).data
print(artefato)
print(hash(artefato))


# from apiserver.models.orm import ArtefatoRecinto, ArtefatoRecintoSchema, \
#     CoordenadaArtefato, CoordenadaArtefatoSchema, db_session, init_db
#
# session, engine = init_db()
#
# artefato = ArtefatoRecinto(codigo='1')
#                                #IDEvento=1000, dataevento='2019-01-01', operadorevento='ivan',
#                                #dataregistro='2019-01-01', operadorregistro='ivan', retificador=False)
# coordenada_artefato = CoordenadaArtefato(artefato=artefato, lat=1.0, long=2.0)
# session.add(artefato)
# session.add(coordenada_artefato)
# session.commit()
# # orm.db_session.refresh(artefato)
# print(artefato)
# print(coordenada_artefato)
# print(hash(artefato))
# # print(artefato.coordenadas)
# print(artefato.coordenadasartefato)
#
# artefato_schema = ArtefatoRecintoSchema()
# coordenada_artefato_schema = CoordenadaArtefatoSchema()
#
# dump_data = artefato_schema.dump(artefato).data
# print(dump_data)
# dump_data = coordenada_artefato_schema.dump(coordenada_artefato).data
# print(dump_data)
# artefato = artefato_schema.load(dump_data, session=session).data
# print(artefato)
# print(hash(artefato))
