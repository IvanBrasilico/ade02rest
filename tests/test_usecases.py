from sqlalchemy.exc import IntegrityError

import assinador
from apiserver.models import orm
from apiserver.use_cases.usecases import UseCases
from tests.basetest import BaseTestCase

RECINTO = '00001'
REQUEST_IP = '10.10.10.10'


class UseCaseTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.usecase = UseCases(self.db_session, RECINTO, REQUEST_IP, '')

    def _insert(self, classe_evento):
        evento = self.testes[classe_evento.__name__]
        return self.usecase.insert_evento(classe_evento,
                                          evento)

    def _load(self, classe_evento, IDEvento):
        return self.usecase.load_evento(classe_evento,
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
        evento_banco = self.usecase.insert_inspecaonaoinvasiva(evento)

        self.compara_eventos(evento, evento_banco.dump())
        evento_banco_load = self.usecase.load_inspecaonaoinvasiva(evento['IDEvento'])
        self.compara_eventos(evento, evento_banco_load)

    def test_DTSC(self):
        self._insert_and_load(orm.DTSC)

    def test_ChavePublicaRecinto(self):
        """Adiciona dois recintos de numero diferente e checa chaves"""
        chave_recinto1 = orm.ChavePublicaRecinto('00001', b'MIIBIjANBgkqhkiG9w0B')
        chave_recinto2 = orm.ChavePublicaRecinto('00002', b'TESTE123')
        self.db_session.add(chave_recinto1)
        self.db_session.add(chave_recinto2)
        self.db_session.commit()
        assert chave_recinto1.public_key == \
               orm.ChavePublicaRecinto.get_public_key(self.db_session,
                                                      chave_recinto1.recinto)
        assert chave_recinto2.public_key == \
               orm.ChavePublicaRecinto.get_public_key(self.db_session,
                                                      chave_recinto2.recinto)
        assert chave_recinto1.public_key != \
               orm.ChavePublicaRecinto.get_public_key(self.db_session,
                                                      chave_recinto2.recinto)

    def test_ChavePublicaRecinto_change(self):
        """Adiciona dois recintos de numero igual.
        Usando classe, dará erro de integridade.
        Usando set_public_key, chave deve ser editada."""
        chave_recinto1 = orm.ChavePublicaRecinto('00001', b'MIIBIjANBgkqhkiG9w0B')
        chave_recinto2 = orm.ChavePublicaRecinto('00001', b'TESTE123')
        self.db_session.add(chave_recinto1)
        self.db_session.add(chave_recinto2)
        try:
            self.db_session.commit()
            assert False  # Deveria ter dado exceção
        except IntegrityError:
            self.db_session.rollback()
        chave_recinto1 = orm.ChavePublicaRecinto.set_public_key(
            self.db_session,
            '00001', b'MIIBIjANBgkqhkiG9w0B')
        assert chave_recinto1.public_key == \
               orm.ChavePublicaRecinto.get_public_key(self.db_session,
                                                      chave_recinto1.recinto)
        chave_recinto2 = orm.ChavePublicaRecinto.set_public_key(
            self.db_session,
            '00001', b'TESTE123')
        assert chave_recinto2.public_key == \
               orm.ChavePublicaRecinto.get_public_key(self.db_session,
                                                      chave_recinto2.recinto)

    def test_gerachaverecinto_and_sign(self):
        recinto = '00001'
        private_key_pem = UseCases.gera_chaves_recinto(self.db_session, recinto)
        public_key_pem = UseCases.get_public_key(self.db_session, recinto)
        private_key = assinador.load_private_key(private_key_pem)
        public_key = assinador.load_public_key(public_key_pem)
        message = b'TESTE'
        signed = assinador.sign(message, private_key)
        assinador.verify(signed, message, public_key)
