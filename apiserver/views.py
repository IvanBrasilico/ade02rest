import json
import logging
import os

from dateutil.parser import parse
from flask import current_app, request, render_template, Response, jsonify

from apiserver.api import dump_eventos, RECINTO
from apiserver.logconf import logger
from apiserver.models import orm


def home():
    return render_template('home.html')


def get_caminho_arquivo(evento):
    filepath = current_app.config.get('UPLOAD_FOLDER')
    # print(filepath)
    for caminho in [evento.recinto,
                    evento.dataevento.year,
                    evento.dataevento.month,
                    evento.dataevento.day]:
        filepath = os.path.join(filepath, str(caminho))
        if not os.path.exists(filepath):
            os.mkdir(filepath)
    return filepath


def save_file_evento(file, IDEvento, tipoevento, campoevento):
    db_session = current_app.config['db_session']
    try:
        aclass = getattr(orm, tipoevento)
        evento = db_session.query(aclass).filter(
            aclass.IDEvento == IDEvento
        ).one_or_none()
        if evento is None:
            return 'Evento não encontrado.', 404
        setattr(evento, campoevento, file.filename)
        db_session.add(evento)
        filepath = get_caminho_arquivo(evento)
        file.save(os.path.join(filepath, file.filename))
        db_session.commit()
        return 'Arquivo salvo', 201
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def allowed_file(filename, extensions):
    """Checa extensões permitidas."""
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in extensions


def valid_file(file, extensions=['jpg', 'xml', 'json']):
    """Valida arquivo passado e retorna validade e mensagem."""
    if not file or file.filename == '' or not allowed_file(file.filename, extensions):
        if not file:
            mensagem = 'Arquivo nao informado'
        elif not file.filename:
            mensagem = 'Nome do arquivo vazio'
        else:
            mensagem = 'Nome de arquivo não permitido: ' + \
                       file.filename
            # print(file)
        return False, mensagem
    return True, None


def getfile():
    db_session = current_app.config['db_session']
    try:
        IDEvento = request.form.get('IDEvento')
        tipoevento = request.form.get('tipoevento')
        campoevento = request.form.get('campoevento')
        aclass = getattr(orm, tipoevento)
        evento = db_session.query(aclass).filter(
            aclass.IDEvento == IDEvento
        ).one_or_none()
        if evento is None:
            return 'Evento não encontrado.', 404
        filepath = get_caminho_arquivo(evento)
        file = open(os.path.join(filepath, getattr(evento, campoevento)), 'rb').read()
        return Response(response=file, mimetype='image/jpeg'), 200
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def uploadfile():
    """Função simplificada para upload de arquivo para um Evento."""
    # check if the post request has the file part
    try:
        file = request.files.get('file')
        IDEvento = request.form.get('IDEvento')
        tipoevento = request.form.get('tipoevento')
        campoevento = request.form.get('campoevento')
        validfile, mensagem = valid_file(file)
        if not validfile:
            return 'Arquivo invalido', 405
        return save_file_evento(file, IDEvento, tipoevento, campoevento)
    except Exception as err:
        logger.error(err, exc_info=True)
        return err, 405


def geteventosnovos():
    db_session = current_app.config['db_session']
    try:
        try:
            IDEvento = int(request.form.get('IDEvento'))
        except TypeError:
            IDEvento = None
        try:
            dataevento = parse(request.form.get('dataevento'))
        except Exception as err:
            if IDEvento is None:
                return 'IDEvento e dataevento invalidos, ' + \
                       'ao menos um dos dois e necessario'
            dataevento = None
        tipoevento = request.form.get('tipoevento')
        aclass = getattr(orm, tipoevento)
        if dataevento is None:
            eventos = db_session.query(aclass).filter(
                aclass.IDEvento > IDEvento
            ).all()
        else:
            eventos = db_session.query(aclass).filter(
                aclass.dataevento > dataevento
            ).all()
        if eventos is None:
            if dataevento is None:
                return 'Sem eventos com ID maior que %d.' % IDEvento, 404
            return 'Sem eventos com dataevento maior que %s.' % dataevento, 404
        return dump_eventos(eventos)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def geteventosintervalo():
    db_session = current_app.config['db_session']
    try:
        tipoevento = request.form.get('tipoevento')
        datainicial = parse(request.form.get('datainicial'))
        datafinal = parse(request.form.get('datafinal'))
        aclass = getattr(orm, tipoevento)
        eventos = db_session.query(aclass).filter(
            aclass.dataevento.between(datainicial, datafinal)
        ).all()
        if eventos is None:
            return 'Sem eventos no intervalo de datas %s a %s.' % \
                   (datainicial, datafinal), 404
        return dump_eventos(eventos)
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 400


def seteventosnovos():
    db_session = current_app.config['db_session']
    try:
        file = request.files.get('file')
        validfile, mensagem = valid_file(file,
                                         extensions=['json', 'bson', 'zip'])
        if not validfile:
            return mensagem, 405
        content = file.read()
        content = content.decode('utf-8')
        eventos = json.loads(content)
        for tipoevento, eventos in eventos.items():
            aclass = getattr(orm, tipoevento)
            for evento in eventos:
                try:
                    evento['request_IP'] = request.environ.get('HTTP_X_REAL_IP',
                                                               request.remote_addr)
                    evento['recinto'] = RECINTO
                    novo_evento = aclass(**evento)
                    db_session.add(novo_evento)
                except Exception as err:  # Ignora exceções porque vai comparar no Banco de Dados
                    logging.error(str(err))
            db_session.commit()
            result = []
            for evento in eventos:
                try:
                    IDEvento = evento.get('IDEvento')
                    evento_recuperado = db_session.query(aclass).filter(
                        aclass.IDEvento == IDEvento
                    ).one_or_none()
                    if evento_recuperado is None:
                        ohash = 'ERRO!!!'
                    else:
                        ohash = hash(evento_recuperado)
                    result.append({'IDEvento': IDEvento, 'hash': ohash})
                    logger.info('Recinto: %s IDEvento: %d ID: %d Token: %d' %
                                (evento_recuperado.recinto, IDEvento,
                                 evento_recuperado.ID, ohash))
                except Exception as err:
                    result.append({'IDEvento': IDEvento, 'hash': str(err)})
                    logger.error('Evento ID:  %d erro: %s' %
                                 (IDEvento,
                                  str(err)))
    except Exception as err:
        logging.error(err, exc_info=True)
        return str(err), 405
    return jsonify(result), 201


def recriatedb():
    db_session = current_app.config['db_session']
    try:
        orm.Base.metadata.drop_all(bind=engine)
        orm.Base.metadata.create_all(bind=engine)
    except Exception as err:
        return err, 405
    return 'Banco recriado!!!'


def create_views(app):
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'files')
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    app.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.add_url_rule('/', 'home', home)
    app.add_url_rule('/upload_file', 'uploadfile', uploadfile, methods=['POST'])
    app.add_url_rule('/get_file', 'getfile', getfile)
    app.add_url_rule('/get_eventos_novos', 'geteventosnovos', geteventosnovos)
    app.add_url_rule('/set_eventos_novos', 'seteventosnovos',
                     seteventosnovos, methods=['POST'])
    app.add_url_rule('/recriatedb', 'recriatedb', recriatedb)
    return app
