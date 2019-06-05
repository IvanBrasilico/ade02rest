from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from apiserver.models import orm


class Unitizacao(ModelSchema):
    lotes = fields.Nested('LoteUnitizacao', many=True,
                          exclude=('ID', 'unitizacao_id', 'unitizacao'))
    imagens = fields.Nested('ImagemUnitizacao', many=True,
                            exclude=('ID', 'unitizacao_id', 'unitizacao'))

    class Meta:
        model = orm.Unitizacao


class LoteUnitizacao(ModelSchema):
    class Meta:
        model = orm.LoteUnitizacao


class ImagemUnitizacao(ModelSchema):
    class Meta:
        model = orm.ImagemUnitizacao


class PesagemVeiculoVazio(ModelSchema):
    reboques = fields.Nested('ReboquesPesagem', many=True,
                             exclude=('ID', 'pesagem_id', 'pesagem'))

    class Meta:
        model = orm.PesagemVeiculoVazio


class ReboquesPesagem(ModelSchema):
    class Meta:
        model = orm.ReboquesPesagem


class PosicaoVeiculo(ModelSchema):
    conteineres = fields.Nested('ConteinerPosicao', many=True,
                                exclude=('ID', 'posicaoveiculo_id',
                                         'posicaoveiculo'))
    reboques = fields.Nested('ReboquePosicao', many=True,
                             exclude=('ID', 'posicaoveiculo_id',
                                      'posicaoveiculo'))

    class Meta:
        model = orm.PosicaoVeiculo


class ConteinerPosicao(ModelSchema):
    class Meta:
        model = orm.ConteinerPosicao


class ReboquePosicao(ModelSchema):
    class Meta:
        model = orm.ReboquePosicao


class DTSC(ModelSchema):
    cargas = fields.Nested('CargaDTSC', many=True,
                           exclude=('ID', 'DTSC_ID', 'DTSC'))

    class Meta:
        model = orm.DTSC


class CargaDTSC(ModelSchema):
    class Meta:
        model = orm.CargaDTSC


class InspecaonaoInvasiva(ModelSchema):
    identificadores = fields.Nested('IdentificadorInspecaoSchema', many=True,
                                    exclude=('ID', 'inspecao_id', 'inspecao'),
                                    unknown='EXCLUDE'
                                    )
    anexos = fields.Nested('AnexoInspecaoSchema', many=True,
                           exclude=('ID', 'inspecao_id', 'inspecao'),
                           unknown='EXCLUDE'
                           )

    class Meta:
        model = orm.InspecaonaoInvasiva


class IdentificadorInspecaoSchema(ModelSchema):
    class Meta:
        model = orm.IdentificadorInspecao


class AnexoInspecaoSchema(ModelSchema):
    class Meta:
        model = orm.AnexoInspecao


class AcessoVeiculo(ModelSchema):
    conteineres = fields.Nested('ConteineresGate', many=True,
                                exclude=('ID', 'acessoveiculo_id', 'acessoveiculo'))
    reboques = fields.Nested('ReboquesGate', many=True,
                             exclude=('ID', 'acessoveiculo_id', 'acessoveiculo'))
    listanfe = fields.Nested('ListaNfeGate', many=True,
                             exclude=('ID', 'acessoveiculo_id', 'acessoveiculo'))

    class Meta:
        model = orm.AcessoVeiculo


class ConteineresGate(ModelSchema):
    class Meta:
        model = orm.ConteineresGate


class ReboquesGate(ModelSchema):
    class Meta:
        model = orm.ReboquesGate


class ListaNfeGate(ModelSchema):
    class Meta:
        model = orm.ListaNfeGate


class ArtefatoRecinto(ModelSchema):
    coordenadasartefato = fields.Nested('CoordenadaArtefato', many=True,
                                        exclude=('ID', 'artefato_id', 'artefato'))

    class Meta:
        model = orm.ArtefatoRecinto


class CoordenadaArtefato(ModelSchema):
    class Meta:
        model = orm.CoordenadaArtefato
