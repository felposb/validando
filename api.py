from flask import Flask, request, jsonify
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app)
app.json.sort_keys = False
def carregar(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)
def salvar(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
def proximo_id(lista):
    if not lista:
        return None
    else:
        return  lista[-1]['id'] + 1
@app.get("/")
def rodando():
    return "Rodando", 200

@app.get("/usuarios")
def listarUsuarios():
    usuarios = carregar('usuarios.json')
    return jsonify(usuarios), 200

@app.post("/usuarios")
def criarUsuario():
    dados = request.json
    usuarios = carregar('usuarios.json')
    campos = [
        ('nome', str, True),
        ('data_nascimento', str, True),
        ('cpf', str, True),
        ('biometria', str, True)
        ]
    for usuario in usuarios:
        mesmo_cpf = usuario.get('cpf') == dados.get('cpf')
        mesma_biometria = usuario.get('biometria') == dados.get('biometria')
        if mesmo_cpf:
            return jsonify({"erro": "Ja existe cadastro com esse cpf"}), 422
        if  mesma_biometria:
            return jsonify({"erro": "Ja existe cadastro com essa biometria"}), 422
    
    for campo, tipo, obrigatorio in campos:
        valor = dados.get(campo)
        if obrigatorio and (campo not in dados or valor == ""):
            return jsonify({"erro": f"{campo} é obrigatorio"}), 400
        if campo in dados and not isinstance(valor, tipo):
            return jsonify({"erro": f"{campo} não aceita esse tipo de valor!"}), 422
        
    resposta = {
        'id': proximo_id(usuarios),
        'nome': dados.get('nome'),
        'data_nascimento': dados.get('data_nascimento'),
        'cpf': dados.get('cpf'),
        'biometria': dados.get('biometria')
    }
    usuarios.append(resposta)
    salvar('usuarios.json', usuarios)
    return jsonify({"mensagem": f"criado com sucesso id: {resposta.get('id')} nome: {resposta.get('nome')}"}), 201
@app.get('/usuarios/<int:id>')
def listarUsuario(id): 
    usuarios = carregar('usuarios.json')
    for usuario in usuarios:
        if usuario.get('id') == id:
            return jsonify(usuario)
    return jsonify({"erro": "Usuario não encontrado"}), 404

app.run(debug=True)