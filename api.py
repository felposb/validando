from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime


app = Flask(__name__)
CORS(app)
app.json.sort_keys = False
def carregar(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def salvar(arquivo, dados):
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
        
def proximo_id(lista, campo_id):
    if not lista:
        return 1
    return max(item[campo_id] for item in lista) +1

@app.get("/")
def rodando():
    return "Rodando", 200

def agora():
        return datetime.now().strftime("%d/%m/%y %H:%M:%S")

@app.get("/usuarios")
def listarUsuarios():
    usuarios = carregar('usuarios.json')
    return jsonify(usuarios), 200

@app.post("/criar/usuario")
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
        'digital': {"biometria": dados.get('biometria'), "img_biometria": dados.get('img_biometria')}
    }
    usuarios.append(resposta)
    salvar('usuarios.json', usuarios)
    return jsonify({"mensagem": f"criado com sucesso id: {resposta.get('id')} nome: {resposta.get('nome')}"}), 201

@app.get('/listar/usuario/<int:id>')
def listarUsuario(id): 
    usuarios = carregar('usuarios.json')
    for usuario in usuarios:
        if usuario.get('id') == id:
            return jsonify(usuario), 200
    return jsonify({"erro": "Usuario não encontrado"}), 404

@app.get('/listar/historicos')
def listarHistoricos():
    historicos = carregar('historicos.json')
    return jsonify(historicos),200

@app.get("/listar/historico/<int:id>")
def listarHistorico(id):
    historicos = carregar('historicos.json')
    for historico in historicos:
        if historico.get('id') == id:
            return jsonify(historico), 200
    return jsonify({"erro": "Historico não encontrado"}), 404

@app.post("/criar/historico")
def criarHistorico():
    historicos = carregar('historicos.json')
    dados = request.json
    campos = [
        ('id', int, False),
        ('id_empresa', int, False),
        ('cpf', str, True),
        ]
    validacao = [
        ('resultado', ["aprovado", "reprovado"], True),
        ('motivo', ["maior de idade", "menor de idade"], True),
        ('metodo', ["biometria", "cpf"], True)
    ]
    for campo, campos_validos, obrigatorio in validacao:
        valor = dados.get(campo)
        if obrigatorio and (campo not in dados or valor == ""):
            return jsonify({"erro": f"{campo} é obrigatorio"}), 400
        if valor not in campos_validos:
            return jsonify({"erro": f"{campo} apenas recebe {campos_validos}"}), 422
        
    for campo, tipo, obrigatorio in campos:
        valor = dados.get(campo)
        if obrigatorio and (campo not in dados or valor == ""):
            return jsonify({"erro": f"{campo} é obrigatorio"}), 422
        if campo in dados and not isinstance(valor, tipo):
            return jsonify({"erro": f"{campo} não recebe esse tipo de valor"}), 422
    
    resposta = {
        'id_historico': proximo_id(historicos, 'id_historico'),
        'id_empresa': dados.get('id_empresa'),
        'cpf': dados.get('cpf'),
        'resultado': dados.get('resultado'),
        'motivo': dados.get('motivo'),
        'metodo': dados.get('metodo'),
        'data': agora()
    }
    
    historicos.append(resposta)
    salvar('historicos.json', historicos)
    return jsonify({"mensagem": "criado com sucesso"}), 201

@app.put("/atualizar/usuario/<int:id>")
def updateUser(id):
    usuarios = carregar("usuarios.json")    
    dados = request.json
    for usuario in usuarios:
        if usuario.get('id') == id:
            campos = [
                ('nome', str ),
                ('data_nascimento', str),
                ('cpf', str,),
                ('biometria', str)
                ]
            
            for campo, tipo in campos:
                valor = dados.get(campo)
                if campo in dados and not isinstance(valor, tipo):
                    return jsonify({"erro": f"{campo} não deve receber esse valor"}), 422
            
            usuario.update(dados)
            usuario['id'] = id
            salvar('usuarios.json', usuarios)
            return jsonify({"mensagem": "atualizado com sucesso"}), 200
    return jsonify({"erro": "Usuario não encontrado"}), 404

app.run(debug=True)