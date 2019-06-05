from apiserver.models import orm
from apiserver.use_cases.usecases import insert_evento, load_evento, load_inspecaonaoinvasiva, \
    insert_inspecaonaoinvasiva
from tests.basetest import BaseTestCase

RECINTO = '00001'
REQUEST_IP = '10.10.10.10'


class UseCaseTestCase(BaseTestCase):

    def _insert(self, classe_evento):
        evento = self.testes[classe_evento.__name__]
        return insert_evento(self.session,
                             classe_evento,
                             evento,
                             RECINTO,
                             REQUEST_IP
                             )

    def _load(self, classe_evento, IDEvento):
        return load_evento(self.session,
                           classe_evento,
                           RECINTO,
                           IDEvento)

    def _insert_and_load(self, classe_evento):
        evento = self.testes[classe_evento.__name__]
        evento_banco = self._insert(classe_evento)
        evento_banco_load = self._load(classe_evento, evento['IDEvento'])
        self.compara_eventos(evento, evento_banco.dump())
        self.compara_eventos(evento, evento_banco_load.dump())

    def test_AcessoPessoa(self):
        self._insert_and_load(orm.AcessoPessoa)

    def test_PesagemMaritimo(self):
        self._insert_and_load(orm.PesagemMaritimo)

    def test_PosicaoConteiner(self):
        self._insert_and_load(orm.PosicaoConteiner)

    def test_AvariaLote(self):
        self._insert_and_load(orm.AvariaLote)

    def test_PosicaoLote(self):
        self._insert_and_load(orm.PosicaoLote)

    def test_Ocorrencia(self):
        self._insert_and_load(orm.Ocorrencia)

    def test_OperacaoNavio(self):
        self._insert_and_load(orm.OperacaoNavio)

    def test_InspecaonaoInvasiva(self):
        evento = self.testes['InspecaonaoInvasiva']
        evento_banco = insert_inspecaonaoinvasiva(self.session,
                                                  evento,
                                                  RECINTO,
                                                  REQUEST_IP
                                                  )
        self.compara_eventos(evento, evento_banco.dump())
        evento_banco_load = load_inspecaonaoinvasiva(
            RECINTO, evento['IDEvento'], '')
        self.compara_eventos(evento, evento_banco_load)

    def test_DTSC(self):
        self._insert_and_load(orm.DTSC)
