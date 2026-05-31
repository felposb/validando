from flask import Flask, request, jsonify
import json
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
CAMINHO_CLIENTES = 'dados/clientes.json'
CAMINHO_USUARIOS = 'dados/usuarios.json'
def proximo_id(lista, campo_id):
    maior = 0
    for item in lista:
        id_atual = item.get(campo_id, 0)
        if isinstance(id_atual, int) and id_atual > maior:
            maior = id_atual
    return maior + 1
def carregar(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def salvar(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def horario():
    return datetime.now().strftime("%d/%m/%y %H:%M:%S")


@app.get('/usuarios')
def getAllUsers():
    usuarios = carregar(CAMINHO_USUARIOS)
    return jsonify(usuarios), 200

@app.get('/listar/usuarios/id')
def getUserById(id):
    id = int(id)
    usuarios = carregar(CAMINHO_USUARIOS)
    for usuario in usuarios:
        if usuario.get('id') == id:
            return jsonify(usuario), 200
    return jsonify({'erro': 'Usuario não encontrado'}), 404

@app.get('/listar/clientes')
def getClientes():
    clientes = carregar(CAMINHO_CLIENTES)
    return jsonify(clientes),200
@app.get('/listar/cliente/<id>')
def getClienteById(id):
    id = int(id)
    clientes = carregar(CAMINHO_CLIENTES)
    for cliente in clientes:
        mesmo_id = cliente.get('id') == id
        if mesmo_id:
            return jsonify(cliente), 200
    return jsonify({'erro': "Usuario não  encontrado"}), 404

@app.post("/criar/usuario")
def createNewUser():
    dados = request.json
    usuarios = carregar(CAMINHO_USUARIOS)
    campos = [
        ('nome', str, True),
        ('cpf', str, True),
        ('data_nascimento', str, True),
        ('senha', str, True),
        ('endereco', dict, True)
        ]
    for usuario in usuarios:
        if usuario.get('cpf') == dados.get('cpf'):
            return jsonify({"erro": "Já existe um cadastro neste cpf"}),422
        
    for campo, tipo, obrigatorio in campos:
        valor = dados.get(campo)
        if obrigatorio and(campo not in dados or valor == ""):
            return jsonify({"erro": f"{campo} é obrigatório"}), 422
        if campo in dados and not isinstance(valor, tipo):
            return jsonify({"erro": f"{campo} precisa ser{tipo.__name__}"}), 422
        
    resposta = {
        'id_usuario': proximo_id(usuarios, 'id_usuario'),
        'nome': dados.get('nome'),
        'cpf': dados.get('cpf'),
        'data_nascimento': dados.get('data_nascimento'),
        'senha': dados.get('senha'),
        'endereco': dados.get('endereco')
    }
    usuarios.append(resposta)
    salvar(CAMINHO_USUARIOS, usuarios)
    return jsonify({"mensagem": "Usuario criado com sucesso"}), 201
@app.post("/clientes")
def dataClientes():
    dados = request.json
    clientes = carregar(CAMINHO_CLIENTES)
    campos = [
        ('data_nascimento', str, True),
        ('cpf', str, True),
        ('digital', dict, True)
        ]
    for cliente in clientes:
        mesmo_cpf = cliente.get('cpf') == dados.get('cpf')
        mesma_digital = cliente.get('digital') == dados.get('digital')
        if mesmo_cpf or mesma_digital:
            return jsonify({'erro': "cliente ja esta cadastrado"}), 422
    for campo, tipo, obrigatorio in campos:
        valor = dados.get(campo)
        if obrigatorio and(campo not in dados or valor == ""):
            return jsonify({'erro': f"{campo} é obrigatório"}),400
        if campo in dados and not isinstance(valor, tipo):
            return jsonify({"erro": f"{campo} apenas recebe {tipo.__name__}"}),422
    if dados.get('cpf') == 0 and dados.get('cpf') > 11:
        return jsonify({"erro" f"cpf esta inválido"}), 422
    resposta = {
        'id_cliente': proximo_id(cliente, 'id_clientes'),
        'data_nascimento': dados.get('data_nascimento'),
        'cpf': dados.get('cpf'),
        'digital': dados.get('digital')
    }
    clientes.append(resposta)
    salvar(CAMINHO_CLIENTES, clientes)
    return jsonify({'mensagem': "Cadastrado com sucesso"}), 201 

app.run(debug=True)
    