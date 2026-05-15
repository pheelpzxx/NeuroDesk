from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuração do Banco de Dados NeuroDesk
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'SUA_SENHA_AQUI',  # ← ALTERE PARA SUA SENHA DO MYSQL
    'database': 'neurodesk_db',
    'port': 3306
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def check_status():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            conn.close()
            return jsonify({"status": "NeuroDesk Online", "version": "1.0.0", "mysql": "conectado"}), 200
        return jsonify({"status": "NeuroDesk Online", "version": "1.0.0", "mysql": "desconectado"}), 200
    except:
        return jsonify({"status": "NeuroDesk Offline", "version": "1.0.0"}), 503

# Rota para registrar LOG DE PRODUTIVIDADE (seu foco principal)
@app.route('/registrar_log', methods=['POST'])
def registrar_log():
    data = request.json
    tarefa_nome = data.get('tarefa_nome')
    tempo_gasto = data.get('tempo_gasto_segundos', 0)
    
    if not tarefa_nome:
        return jsonify({"error": "Nome da tarefa é obrigatório"}), 400
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Erro de conexão com MySQL"}), 500
            
        cursor = conn.cursor()
        query = """
            INSERT INTO logs_produtividade (tarefa_nome, tempo_gasto_segundos) 
            VALUES (%s, %s)
        """
        cursor.execute(query, (tarefa_nome, tempo_gasto))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "✅ Log de produtividade registrado!",
            "tarefa": tarefa_nome,
            "tempo": f"{tempo_gasto}s"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para listar PRODUTOS CRÍTICOS (estoque baixo)
@app.route('/produtos/criticos', methods=['GET'])
def produtos_criticos():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([]), 500
            
        cursor = conn.cursor(dictionary=True)
        # Busca produtos com status CRÍTICO ou estoque abaixo do mínimo
        query = """
            SELECT id, nome, categoria, estoque_atual, estoque_minimo, preco, status_prioridade
            FROM produtos
            WHERE status_prioridade = 'CRÍTICO' OR estoque_atual <= estoque_minimo
            ORDER BY estoque_atual ASC, status_prioridade DESC
            LIMIT 20
        """
        cursor.execute(query)
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(produtos), 200
    except Exception as e:
        print(f"❌ Erro ao buscar produtos críticos: {e}")
        return jsonify([]), 500

# Rota para listar todos os produtos (com filtro opcional)
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([]), 500
            
        cursor = conn.cursor(dictionary=True)
        categoria = request.args.get('categoria')
        
        if categoria:
            query = "SELECT * FROM produtos WHERE categoria = %s ORDER BY nome"
            cursor.execute(query, (categoria,))
        else:
            query = "SELECT * FROM produtos ORDER BY nome LIMIT 50"
            cursor.execute(query)
            
        produtos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(produtos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para atualizar estoque (aciona o TRIGGER automaticamente)
@app.route('/produtos/<int:id>/atualizar_estoque', methods=['PUT'])
def atualizar_estoque(id):
    data = request.json
    novo_estoque = data.get('estoque_atual')
    
    if novo_estoque is None:
        return jsonify({"error": "Valor de estoque é obrigatório"}), 400
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Erro de conexão"}), 500
            
        cursor = conn.cursor()
        # O TRIGGER vai atualizar status_prioridade automaticamente!
        query = "UPDATE produtos SET estoque_atual = %s WHERE id = %s"
        cursor.execute(query, (novo_estoque, id))
        conn.commit()
        
        # Busca o produto atualizado para retornar
        cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
        produto_atualizado = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "✅ Estoque atualizado! Prioridade recalculada automaticamente.",
            "produto": {
                "id": produto_atualizado[0],
                "nome": produto_atualizado[1],
                "estoque_atual": produto_atualizado[3],
                "status_prioridade": produto_atualizado[6]
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
