import connexion

from apiserver.models import orm
from apiserver.views import create_views


def create_app(session, engine):  # pragma: no cover
    app = connexion.FlaskApp(__name__)
    app.add_api('openapi.yaml')
    app.app.config['db_session'] = session
    app.app.config['engine'] = engine
    print('Configurou app')
    app = create_views(app)
    print('Configurou views')
    return app


def main():  # pragma: no cover
    # session, engine = orm.init_db('sqlite:///:memory:')
    # orm.Base.metadata.create_all(bind=engine)
    session, engine = orm.init_db()
    app = create_app(session, engine)
    print(app.app.config['db_session'])
    app.run(debug=True, port=8000, threaded=False)


if __name__ == '__main__':  # pragma: no cover
    main()


04.4 – Agendamento de Entrada/Saída de Veículos
	- Direção [Entrada / Saída]
	- Documento de Transporte
	- Tipo de Documento de Transporte
	- Placa Cavalo-trator/truck/automóvel ou chassi (veículo-mercadoria)
	- Dimensões que impeçam entrada pelo gate ou passagem pelo scaner (OOG) (S/N)
	- Peso que impeça entrada pelo gate ou passagem pelo scaner (OOG) (S/N)
	- Lista de chaves NFE
	- Lista semirreboques
		- Placa
		- Vazio [S/N]
		- Lacres
		- Lacre SIF
		- Local SIF
		- CNPJ Cliente Estadia
		- Nome Cliente Estadia
	- Lista de Contêineres
		- Número
		- Vazio [S/N]
		- Tipo
		- Lacre Armador
		- Lacre SIF
		- Local SIF
		- CNPJ Local estufagem
		- Porto de Descarga
		- Navio de Embarque
		- CNPJ Cliente Armazenagem
		- Nome Cliente Armazenagem
	- CNPJ Transportador
	- Nome Transportador
	- CPF Motorista
	- Nome Motorista
	- Data e Hora agendada
	- Modal [Rodoviário/Ferroviário]
	- ÀreasAcesso (Lista)
