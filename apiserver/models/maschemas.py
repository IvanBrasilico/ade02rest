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
