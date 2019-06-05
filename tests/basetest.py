from datetime import datetime
import json
import os
from unittest import TestCase

from dateutil.parser import parse

from apiserver.models import orm

session = None
testes = None
engine = None

def create_session():
    global session
    global testes
    global engine
    if session is None:
        print('Creating memory database')
        session, engine = orm.init_db('sqlite:///:memory:')
        with open(os.path.join(os.path.dirname(__file__),
                               'testes.json'), 'r') as json_in:
            testes = json.load(json_in)
    return session, engine, testes

def extractDictAFromB(A, B):
    return dict([(k, B[k]) for k in A.keys() if k in B.keys()])



class BaseTestCase(TestCase):

    def setUp(self):
        self.session, self.engine, self.testes = create_session()
        orm.Base.metadata.create_all(bind=self.engine)

    def tearDown(self) -> None:
        orm.Base.metadata.drop_all(bind=self.engine)

    def compare_dict(self, adict, bdict):
        for k, v in adict.items():
            vb = bdict.get(k)
            if vb is not None:
                if isinstance(vb, list):
                    for itema, itemb in zip(v, vb):
                        self.compare_dict(itema, itemb)
                elif isinstance(vb, dict):
                    self.compare_dict(v, vb)
                else:
                    if isinstance(vb, datetime):
                        if not isinstance(v, datetime):
                            vadate = parse(v)
                            # self.assertEqual(vadate, vb)
                    else:
                        self.assertEqual(v, vb)

    def compara_eventos(self, teste, response_json):
        for data in ['dataevento', 'dataregistro', 'dataoperacao', 'dataliberacao', 'dataagendamento']:
            if teste.get(data) is not None:
                teste.pop(data)
            if response_json.get(data) is not None:
                response_json.pop(data)
        # sub_response = extractDictAFromB(teste, response_json)
        self.compare_dict(teste, response_json)
        # self.maxDiff = None
        # self.assertDictContainsSubset(teste, sub_response)
