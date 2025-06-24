import os
import json
import datetime
import smtplib
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify, flash, render_template, g
from flask_babel import Babel, gettext as _

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
DATA_FILE = 'academic_data.json'

@app.before_request
def set_global_lang_code():
    if request.view_args and 'lang_code' in request.view_args:
        g.lang_code = request.view_args['lang_code']
    else:
        g.lang_code = 'pt'

def get_locale():
    return g.lang_code

babel = Babel(app, locale_selector=get_locale)

@app.route('/')
def root():
    return redirect(url_for('index', lang_code='pt'))

@app.route('/<lang_code>/')
def index(lang_code):
    data = load_data()
    featured_pubs = [p for p in data.get('publicacoes', []) if p.get('is_featured')]
    recent_projects = sorted(
        [p for p in data.get('projetos', []) if p.get('data_inicio')],
        key=lambda x: x.get('data_inicio', datetime.date(1,1,1)),
        reverse=True
    )[:3]
    return render_template('index.html', 
                           professor=data.get('professor', {}),
                           featured_publications=featured_pubs,
                           recent_projects=recent_projects,
                           areas_pesquisa=data.get('areas_pesquisa', []),
                           lang_code=g.lang_code,
                           now=datetime.datetime.now())

@app.route('/<lang_code>/projetos')
def projetos(lang_code):
    data = load_data()
    return render_template('projetos.html', 
                           projetos=data.get('projetos', []),
                           professor=data.get('professor', {}),
                           areas=data.get('areas_pesquisa', []),
                           lang_code=g.lang_code,
                           now=datetime.datetime.now())

@app.route('/<lang_code>/publicacoes')
def publicacoes(lang_code):
    data = load_data()
    return render_template('publicacoes.html', 
                           publicacoes=data.get('publicacoes', []),
                           professor=data.get('professor', {}),
                           areas=data.get('areas_pesquisa', []),
                           lang_code=g.lang_code,
                           now=datetime.datetime.now())

@app.route('/<lang_code>/orientacoes')
def orientacoes(lang_code):
    data = load_data()
    return render_template('orientacoes.html', 
                           orientacoes=data.get('orientacoes', []),
                           professor=data.get('professor', {}),
                           areas=data.get('areas_pesquisa', []),
                           lang_code=g.lang_code,
                           now=datetime.datetime.now())

@app.route('/<lang_code>/contato')
def contato(lang_code):
    data = load_data()
    return render_template('contato.html',
                           professor=data.get('professor', {}),
                           areas=data.get('areas_pesquisa', []),
                           lang_code=g.lang_code,
                           now=datetime.datetime.now())

@app.route('/<lang_code>/sobre-mim')
def sobre_mim(lang_code):
    data = load_data()
    return render_template('sobre_mim.html',
                           professor=data.get('professor', {}),
                           areas=data.get('areas_pesquisa', []),
                           lang_code=g.lang_code,
                           now=datetime.datetime.now())

@app.route('/<lang_code>/areas-pesquisa')
def areas_pesquisa(lang_code):
    data = load_data()
    return render_template('areas_pesquisa.html',
                           areas=data.get('areas_pesquisa', []),
                           professor=data.get('professor', {}),
                           lang_code=g.lang_code,
                           now=datetime.datetime.now())
app.secret_key = os.environ.get('SECRET_KEY', 'um_fallback') # Mude o fallback!
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')  # Ler do ambiente
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # Ler do ambiente
ADMIN_RECEIVER_EMAIL = os.environ.get('ADMIN_RECEIVER_EMAIL') # Ler do ambiente

from admin_template import get_admin_template

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'professor' not in data or 'id' not in data['professor']:
                    data['professor'] = create_default_data()['professor']
                for key in ["publicacoes", "projetos", "orientacoes", "contatos", "areas_pesquisa", "admin_users"]:
                    if key not in data:
                        data[key] = []
                
                for pub in data.get('publicacoes', []):
                    if isinstance(pub.get('data_publicacao'), str):
                        try:
                            pub['data_publicacao'] = datetime.datetime.strptime(pub['data_publicacao'], '%Y-%m-%d').date()
                        except ValueError:
                            print(f"Aviso: data_publicacao '{pub.get('data_publicacao')}' em publicação {pub.get('id')} não está no formato AAAA-MM-DD.")
                            pass 

                for proj in data.get('projetos', []):
                    if isinstance(proj.get('data_inicio'), str):
                        try:
                            proj['data_inicio'] = datetime.datetime.strptime(proj['data_inicio'], '%Y-%m-%d').date()
                        except ValueError:
                            print(f"Aviso: data_inicio '{proj.get('data_inicio')}' em projeto {proj.get('id')} não está no formato AAAA-MM-DD.")
                            pass
                    if isinstance(proj.get('data_termino'), str):
                        try:
                            proj['data_termino'] = datetime.datetime.strptime(proj['data_termino'], '%Y-%m-%d').date()
                        except ValueError:
                            print(f"Aviso: data_termino '{proj.get('data_termino')}' em projeto {proj.get('id')} não está no formato AAAA-MM-DD.")
                            pass

                for ori in data.get('orientacoes', []):
                    if isinstance(ori.get('data_inicio'), str):
                        try:
                            ori['data_inicio'] = datetime.datetime.strptime(ori['data_inicio'], '%Y-%m-%d').date()
                        except ValueError:
                            print(f"Aviso: data_inicio '{ori.get('data_inicio')}' em orientação {ori.get('id')} não está no formato AAAA-MM-DD.")
                            pass
                    if isinstance(ori.get('data_defesa'), str):
                        try:
                            ori['data_defesa'] = datetime.datetime.strptime(ori['data_defesa'], '%Y-%m-%d').date()
                        except ValueError:
                            print(f"Aviso: data_defesa '{ori.get('data_defesa')}' em orientação {ori.get('id')} não está no formato AAAA-MM-DD.")
                            pass

                return data
        else:
            return create_default_data()
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return create_default_data()

def create_default_data():
    return {
        "professor": {
            "id": 1,
            "nome": "Professor Raul Benites Paradeda",
            "email": "professor@universidade.edu",
            "titulacao": "Doutorado em Ciência da Computação",
            "lattes_url": "http://lattes.cnpq.br/exemplo",
            "foto_path": "/static/img/professor.jpg",
            "orcid": "0000-0000-0000-0000",
            "bio_pt": "Professor universitário com foco em inteligência artificial e redes de computadores. Possui vasta experiência em pesquisa e orientação acadêmica.",
            "bio_en": "University professor focused on artificial intelligence and computer networks. Has extensive experience in research and academic advising.",
            "updated_at": datetime.datetime.now().isoformat() + 'Z'
        },
        "areas_pesquisa": [
            {
                "id": 1,
                "nome_pt": "Inteligência Artificial",
                "nome_en": "Artificial Intelligence",
                "descricao_pt": "Estudo de IA e aprendizado de máquina.",
                "descricao_en": "Study of AI and machine learning."
            }
        ],
        "publicacoes": [
            {
                "id": 1,
                "titulo_pt": "Um Estudo Sobre Redes Neurais Convolucionais",
                "titulo_en": "A Study on Convolutional Neural Networks",
                "abstract_pt": "Resumo da publicação em português sobre CNNs.",
                "abstract_en": "Abstract of the publication in English about CNNs.",
                "data_publicacao": "2023-10-26",
                "revista": "Journal of AI Research",
                "doi": "10.1234/jair.2023.1",
                "lattes_url": "http://lattes.cnpq.br/publicacao/1",
                "is_featured": True,
                "professor_id": 1,
                "area_id": 1
            }
        ],
        "projetos": [
            {
                "id": 1,
                "titulo_pt": "Desenvolvimento de um Sistema de Visão Computacional para Drones",
                "titulo_en": "Development of a Computer Vision System for Drones",
                "descricao_pt": "Descrição detalhada do projeto de pesquisa em visão computacional.",
                "descricao_en": "Detailed description of the research project on computer vision.",
                "tipo": "pesquisa",
                "status": "em_andamento",
                "data_inicio": "2022-01-01",
                "data_termino": None,
                "professor_id": 1
            },
            {
                "id": 2,
                "titulo_pt": "Aplicação de IA na Análise de Dados Clínicos",
                "titulo_en": "AI Application in Clinical Data Analysis",
                "descricao_pt": "Projeto de extensão focado na análise de dados de saúde.",
                "descricao_en": "Extension project focused on health data analysis.",
                "tipo": "extensao",
                "status": "concluido",
                "data_inicio": "2021-05-10",
                "data_termino": "2023-12-15",
                "professor_id": 1
            }
        ],
        "orientacoes": [
            {
                "id": 1,
                "aluno_nome": "Ana Clara Silva",
                "nivel": "mestrado",
                "status": "concluida",
                "titulo_tese_pt": "Otimização de Algoritmos de Machine Learning",
                "titulo_tese_en": "Optimization of Machine Learning Algorithms",
                "data_inicio": "2022-03-01",
                "data_defesa": "2024-08-10",
                "professor_id": 1
            }
        ],
        "contatos": [
            {
                "id": 1,
                "nome": "Visitante 1",
                "email": "visitante1@email.com",
                "assunto": "Dúvida sobre Publicação",
                "mensagem": "Gostaria de mais detalhes sobre sua publicação mais recente.",
                "data_envio": datetime.datetime.now().isoformat() + 'Z',
                "lido": False,
                "professor_id": 1
            }
        ],
        "admin_users": []
    }

def save_data(data):
    try:
        serializable_data = json.loads(json.dumps(data, default=str))
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        return False

def create_admin_user(data, username, password):
    hashed_pw = generate_password_hash(password, method='scrypt')
    admin_user = {
        "username": username,
        "password_hash": hashed_pw
    }
    data["admin_users"] = [admin_user]
    save_data(data)
    return admin_user

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Faça login para acessar o painel administrativo'}), 401
            flash('Faça login para acessar o painel administrativo', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.after_request
def add_security_headers(response):
    csp = (
        "default-src 'self';"
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-eval' 'unsafe-inline';"
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline' https://cdnjs.cloudflare.com;"
        "img-src 'self' data:;"
        "connect-src 'self';"
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com;"
    )
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

def send_email(subject, body, sender_email, receiver_email):
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    data_db = load_data()
    admin_users = data_db.get('admin_users', [])
    user = next((u for u in admin_users if u['username'] == username), None)
    if user and check_password_hash(user['password_hash'], password):
        session['admin_logged_in'] = True
        session['admin_username'] = username
        return jsonify({'success': True, 'user': {'email': username}})
    return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401

@app.route('/api/admin/logout', methods=['POST'])
def api_admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return jsonify({'success': True})

@app.route('/api/admin/check-auth', methods=['GET'])
def api_admin_check_auth():
    return jsonify({
        'authenticated': session.get('admin_logged_in', False),
        'user': session.get('admin_username', '')
    })

@app.route('/api/admin/professor', methods=['GET'])
@admin_required
def api_admin_get_professor():
    data = load_data()
    return jsonify(data.get('professor', {}))

@app.route('/api/admin/professor/<int:professor_id>', methods=['PUT'])
@admin_required
def api_admin_update_professor(professor_id):
    updated_fields = request.get_json()
    if not updated_fields:
        return jsonify({'success': False, 'error': 'Dados para atualização inválidos'}), 400
    
    updated_fields = clean_data_for_save(updated_fields)
    
    data = load_data()
    professor_data = data.get('professor', {})
    
    if professor_data.get('id') == professor_id:
        professor_data.update(updated_fields)
        professor_data['updated_at'] = datetime.datetime.now().isoformat() + 'Z'
        data['professor'] = professor_data
        save_data(data)
        return jsonify({'success': True, 'professor': professor_data})
    
    return jsonify({'success': False, 'error': 'Professor não encontrado ou ID incorreto'}), 404

@app.route('/api/admin/publicacoes', methods=['GET'])
@admin_required
def api_admin_publicacoes():
    data = load_data()
    publicacoes_serializable = json.loads(json.dumps(data.get('publicacoes', []), default=str))
    return jsonify(publicacoes_serializable)

@app.route('/api/admin/projetos', methods=['GET'])
@admin_required
def api_admin_projetos():
    data = load_data()
    projetos_serializable = json.loads(json.dumps(data.get('projetos', []), default=str))
    return jsonify(projetos_serializable)

@app.route('/api/admin/orientacoes', methods=['GET'])
@admin_required
def api_admin_orientacoes():
    data = load_data()
    orientacoes_serializable = json.loads(json.dumps(data.get('orientacoes', []), default=str))
    return jsonify(orientacoes_serializable)

@app.route('/api/admin/contatos', methods=['GET'])
@admin_required
def api_admin_contatos():
    data = load_data()
    contatos = sorted(data.get('contatos', []), key=lambda x: x.get('data_envio', ''), reverse=True)
    contatos_serializable = json.loads(json.dumps(contatos, default=str))
    return jsonify(contatos_serializable)

def clean_data_for_save(item_data):
    cleaned_item = {}
    for key, value in item_data.items():
        if isinstance(value, str):
            if value == '':
                cleaned_item[key] = None
            else:
                cleaned_item[key] = value
        elif isinstance(value, bool):
             cleaned_item[key] = value
        elif isinstance(value, list):
             cleaned_item[key] = value
        else:
            cleaned_item[key] = value
    return cleaned_item

@app.route('/api/admin/publicacoes', methods=['POST'])
@admin_required
def api_admin_add_publicacao():
    nova_publicacao = request.get_json()
    if not nova_publicacao:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    nova_publicacao = clean_data_for_save(nova_publicacao)
    
    data = load_data()
    publicacoes = data.get('publicacoes', [])

    next_id = max([p.get('id', 0) for p in publicacoes] + [0]) + 1
    nova_publicacao['id'] = next_id
    
    nova_publicacao['professor_id'] = data['professor']['id'] if data.get('professor') else None
    
    if 'data_publicacao' not in nova_publicacao or nova_publicacao['data_publicacao'] is None:
        nova_publicacao['data_publicacao'] = datetime.date.today()
    else:
        try:
            nova_publicacao['data_publicacao'] = datetime.datetime.strptime(nova_publicacao['data_publicacao'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de publicação inválido. Use AAAA-MM-DD.'}), 400

    publicacoes.append(nova_publicacao)
    data['publicacoes'] = publicacoes
    save_data(data)
    return jsonify({'success': True, 'publicacao': json.loads(json.dumps(nova_publicacao, default=str))}), 201

@app.route('/api/admin/publicacoes/<int:publicacao_id>', methods=['PUT'])
@admin_required
def api_admin_update_publicacao(publicacao_id):
    updated_fields = request.get_json()
    if not updated_fields:
        return jsonify({'success': False, 'error': 'Dados para atualização inválidos'}), 400
    
    if 'data_publicacao' in updated_fields and updated_fields['data_publicacao'] is not None:
        try:
            updated_fields['data_publicacao'] = datetime.datetime.strptime(updated_fields['data_publicacao'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de publicação inválido. Use AAAA-MM-DD.'}), 400
    
    updated_fields = clean_data_for_save(updated_fields)
    
    data = load_data()
    publicacoes = data.get('publicacoes', [])
    
    found = False
    for i, pub in enumerate(publicacoes):
        if pub.get('id') == publicacao_id:
            pub.update(updated_fields)
            found = True
            break
    if found:
        data['publicacoes'] = publicacoes
        save_data(data)
        return jsonify({'success': True, 'publicacao': json.loads(json.dumps(pub, default=str))})
    return jsonify({'success': False, 'error': 'Publicação não encontrada'}), 404

@app.route('/api/admin/publicacoes/<int:publicacao_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_publicacao(publicacao_id):
    data = load_data()
    publicacoes_antes = len(data.get('publicacoes', []))
    data['publicacoes'] = [p for p in data.get('publicacoes', []) if p.get('id') != publicacao_id]
    if len(data['publicacoes']) < publicacoes_antes:
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Publicação não encontrada'}), 404

@app.route('/api/admin/projetos', methods=['POST'])
@admin_required
def api_admin_add_projeto():
    novo_projeto = request.get_json()
    if not novo_projeto:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    if 'data_inicio' in novo_projeto and novo_projeto['data_inicio'] is not None:
        try:
            novo_projeto['data_inicio'] = datetime.datetime.strptime(novo_projeto['data_inicio'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de início inválido. Use AAAA-MM-DD.'}), 400
    if 'data_termino' in novo_projeto and novo_projeto['data_termino'] is not None:
        try:
            novo_projeto['data_termino'] = datetime.datetime.strptime(novo_projeto['data_termino'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de término inválido. Use AAAA-MM-DD.'}), 400

    novo_projeto = clean_data_for_save(novo_projeto)
    
    data = load_data()
    projetos = data.get('projetos', [])

    next_id = max([p.get('id', 0) for p in projetos] + [0]) + 1
    novo_projeto['id'] = next_id
    novo_projeto['professor_id'] = data['professor']['id'] if data.get('professor') else None

    projetos.append(novo_projeto)
    data['projetos'] = projetos
    save_data(data)
    return jsonify({'success': True, 'projeto': json.loads(json.dumps(novo_projeto, default=str))}), 201

@app.route('/api/admin/projetos/<int:projeto_id>', methods=['PUT'])
@admin_required
def api_admin_update_projeto(projeto_id):
    updated_fields = request.get_json()
    if not updated_fields:
        return jsonify({'success': False, 'error': 'Dados para atualização inválidos'}), 400
    
    if 'data_inicio' in updated_fields and updated_fields['data_inicio'] is not None:
        try:
            updated_fields['data_inicio'] = datetime.datetime.strptime(updated_fields['data_inicio'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de início inválido. Use AAAA-MM-DD.'}), 400
    if 'data_termino' in updated_fields and updated_fields['data_termino'] is not None:
        try:
            updated_fields['data_termino'] = datetime.datetime.strptime(updated_fields['data_termino'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de término inválido. Use AAAA-MM-DD.'}), 400

    updated_fields = clean_data_for_save(updated_fields)
    
    data = load_data()
    projetos = data.get('projetos', [])

    found = False
    for i, proj in enumerate(projetos):
        if proj.get('id') == projeto_id:
            proj.update(updated_fields)
            found = True
            break
    if found:
        data['projetos'] = projetos
        save_data(data)
        return jsonify({'success': True, 'projeto': json.loads(json.dumps(proj, default=str))})
    return jsonify({'success': False, 'error': 'Projeto não encontrado'}), 404

@app.route('/api/admin/projetos/<int:projeto_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_projeto(projeto_id):
    data = load_data()
    projetos_antes = len(data.get('projetos', []))
    data['projetos'] = [p for p in data.get('projetos', []) if p.get('id') != projeto_id]
    if len(data['projetos']) < projetos_antes:
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Projeto não encontrado'}), 404

@app.route('/api/admin/orientacoes', methods=['POST'])
@admin_required
def api_admin_add_orientacao():
    nova_orientacao = request.get_json()
    if not nova_orientacao:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    if 'data_inicio' in nova_orientacao and nova_orientacao['data_inicio'] is not None:
        try:
            nova_orientacao['data_inicio'] = datetime.datetime.strptime(nova_orientacao['data_inicio'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de início inválido. Use AAAA-MM-DD.'}), 400
    if 'data_defesa' in nova_orientacao and nova_orientacao['data_defesa'] is not None:
        try:
            nova_orientacao['data_defesa'] = datetime.datetime.strptime(nova_orientacao['data_defesa'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de defesa inválido. Use AAAA-MM-DD.'}), 400

    nova_orientacao = clean_data_for_save(nova_orientacao)
    
    data = load_data()
    orientacoes = data.get('orientacoes', [])

    next_id = max([o.get('id', 0) for o in orientacoes] + [0]) + 1
    nova_orientacao['id'] = next_id
    nova_orientacao['professor_id'] = data['professor']['id'] if data.get('professor') else None
    
    orientacoes.append(nova_orientacao)
    data['orientacoes'] = orientacoes
    save_data(data)
    return jsonify({'success': True, 'orientacao': json.loads(json.dumps(nova_orientacao, default=str))}), 201

@app.route('/api/admin/orientacoes/<int:orientacao_id>', methods=['PUT'])
@admin_required
def api_admin_update_orientacao(orientacao_id):
    updated_fields = request.get_json()
    if not updated_fields:
        return jsonify({'success': False, 'error': 'Dados para atualização inválidos'}), 400
    
    if 'data_inicio' in updated_fields and updated_fields['data_inicio'] is not None:
        try:
            updated_fields['data_inicio'] = datetime.datetime.strptime(updated_fields['data_inicio'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de início inválido. Use AAAA-MM-DD.'}), 400
    if 'data_defesa' in updated_fields and updated_fields['data_defesa'] is not None:
        try:
            updated_fields['data_defesa'] = datetime.datetime.strptime(updated_fields['data_defesa'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Formato de data de defesa inválido. Use AAAA-MM-DD.'}), 400

    updated_fields = clean_data_for_save(updated_fields)
    
    data = load_data()
    orientacoes = data.get('orientacoes', [])

    found = False
    for i, ori in enumerate(orientacoes):
        if ori.get('id') == orientacao_id:
            ori.update(updated_fields)
            found = True
            break
    if found:
        data['orientacoes'] = orientacoes
        save_data(data)
        return jsonify({'success': True, 'orientacao': json.loads(json.dumps(ori, default=str))})
    return jsonify({'success': False, 'error': 'Orientação não encontrada'}), 404

@app.route('/api/admin/orientacoes/<int:orientacao_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_orientacao(orientacao_id):
    data = load_data()
    orientacoes_antes = len(data.get('orientacoes', []))
    data['orientacoes'] = [o for o in data.get('orientacoes', []) if o.get('id') != orientacao_id]
    if len(data['orientacoes']) < orientacoes_antes:
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Orientação não encontrada'}), 404

@app.route('/api/admin/contatos/<int:contato_id>/read', methods=['POST'])
@admin_required
def api_admin_contato_read(contato_id):
    data = load_data()
    contatos = data.get('contatos', [])
    found = False
    for contato in contatos:
        if contato.get('id') == contato_id:
            contato['lido'] = not contato.get('lido', False)
            found = True
            break
    if found:
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Contato não encontrado'}), 404

@app.route('/api/admin/contatos/<int:contato_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_contato(contato_id):
    data = load_data()
    contatos_antes = len(data.get('contatos', []))
    data['contatos'] = [c for c in data.get('contatos', []) if c.get('id') != contato_id]
    if len(data['contatos']) < contatos_antes:
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Contato não encontrado'}), 404

@app.route('/api/areas_pesquisa', methods=['GET'])
def api_public_areas_pesquisa():
    data = load_data()
    areas_serializable = json.loads(json.dumps(data.get('areas_pesquisa', []), default=str))
    return jsonify(areas_serializable)

@app.route('/api/professor', methods=['GET'])
def api_public_get_professor():
    data = load_data()
    professor_serializable = json.loads(json.dumps(data.get('professor', {}), default=str))
    return jsonify(professor_serializable)

@app.route('/api/publicacoes', methods=['GET'])
def api_public_publicacoes():
    data = load_data()
    publicacoes_serializable = json.loads(json.dumps(data.get('publicacoes', []), default=str))
    return jsonify(publicacoes_serializable)

@app.route('/api/projetos', methods=['GET'])
def api_public_projetos():
    data = load_data()
    projetos_serializable = json.loads(json.dumps(data.get('projetos', []), default=str))
    return jsonify(projetos_serializable)

@app.route('/api/orientacoes', methods=['GET'])
def api_public_orientacoes():
    data = load_data()
    orientacoes_serializable = json.loads(json.dumps(data.get('orientacoes', []), default=str))
    return jsonify(orientacoes_serializable)

@app.route('/api/contato', methods=['POST'])
def api_public_send_contact_message():
    message_data = request.get_json()
    if not message_data:
        return jsonify({'success': False, 'error': 'Dados da mensagem inválidos'}), 400

    required_fields = ['nome', 'email', 'assunto', 'mensagem']
    if not all(field in message_data and message_data[field] for field in required_fields):
        return jsonify({'success': False, 'error': 'Campos obrigatórios (nome, email, assunto, mensagem) são necessários'}), 400

    data = load_data()
    contatos = data.get('contatos', [])

    next_id = max([c.get('id', 0) for c in contatos] + [0]) + 1
    
    new_message = {
        "id": next_id,
        "nome": message_data['nome'],
        "email": message_data['email'],
        "assunto": message_data['assunto'],
        "mensagem": message_data['mensagem'],
        "data_envio": datetime.datetime.now().isoformat() + 'Z',
        "lido": False,
        "professor_id": data['professor']['id'] if data.get('professor') else None
    }
    
    contatos.append(new_message)
    data['contatos'] = contatos
    
    if save_data(data):
        email_subject = f"Nova Mensagem de Contato: {new_message['assunto']}"
        email_body = f"""
        <html>
            <body>
                <p>Você recebeu uma nova mensagem de contato através do seu site:</p>
                <ul>
                    <li><strong>Nome:</strong> {new_message['nome']}</li>
                    <li><strong>Email:</strong> {new_message['email']}</li>
                    <li><strong>Assunto:</strong> {new_message['assunto']}</li>
                </ul>
                <p><strong>Mensagem:</strong></p>
                <p>{new_message['mensagem'].replace('\\n', '<br>')}</p>
                <p><i>Esta é uma mensagem automática. Por favor, não responda a este email.</i></p>
            </body>
        </html>
        """
        if EMAIL_USERNAME and ADMIN_RECEIVER_EMAIL:
            try:
                send_email(email_subject, email_body, EMAIL_USERNAME, ADMIN_RECEIVER_EMAIL)
            except Exception as e:
                print(f"Erro ao tentar enviar e-mail de notificação: {e}")
                pass 
        else:
            print("Configurações de e-mail incompletas. E-mail de notificação não enviado.")

        return jsonify({'success': True, 'message': 'Mensagem enviada com sucesso!'}), 201
    else:
        return jsonify({'success': False, 'error': 'Erro ao salvar a mensagem'}), 500

@app.route('/admin')
@admin_required
def admin_dashboard():
    data = load_data()
    return render_template_string(
        get_admin_template(),
        professor=data.get('professor', {})
    )

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    data = load_data()
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin_users = data.get('admin_users', [])
        user = next((u for u in admin_users if u['username'] == username), None)
        if not user:
            error = 'Usuário não encontrado'
        else:
            if check_password_hash(user['password_hash'], password):
                session['admin_logged_in'] = True
                session['admin_username'] = username
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Senha incorreta'
        flash(error, 'error')
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login Administrativo</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }
                .login-container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    width: 100%;
                    max-width: 400px;
                    text-align: center;
                }
                .login-container h1 {
                    color: #34495e;
                    margin-bottom: 20px;
                }
                .login-container label {
                    display: block;
                    text-align: left;
                    margin-bottom: 8px;
                    font-weight: bold;
                }
                .login-container input[type="text"],
                .login-container input[type="password"] {
                    width: calc(100% - 20px);
                    padding: 10px;
                    margin-bottom: 15px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .login-container button {
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 1em;
                    transition: background-color 0.3s ease;
                }
                .login-container button:hover {
                    background-color: #2980b9;
                }
                .message {
                    padding: 10px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    text-align: center;
                }
                .message.error {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                .message.success {
                    background-color: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>Login Administrativo</h1>
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="message {{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <form method="POST">
                    <label>Usuário: <input type="text" name="username" required></label>
                    <label>Senha: <input type="password" name="password" required></label>
                    <button type="submit">Entrar</button>
                </form>
            </div>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    data = load_data()
    if not data.get('admin_users'):
        create_admin_user(data, 'admin', 'admin123')
        print("Usuário administrativo padrão criado: admin / admin123")
    app.run(port=3001, debug=True)