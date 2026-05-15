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
    'password': 'sua_senha',  # ALTERE SUA SENHA AQUI
    'database': 'neurodesk_db'
}

def get_db_connection():
    try:
        return mysql.connector.connect(**db_config)
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def check_status():
    return jsonify({"status": "NeuroDesk Online", "version": "1.0.0"}), 200

@app.route('/processar_tarefa', methods=['POST'])
def processar_tarefa():
    data = request.json
    tarefa_descricao = data.get('descricao')
    prioridade = data.get('prioridade', 2)
    
    if not tarefa_descricao:
        return jsonify({"error": "Descrição da tarefa é obrigatória"}), 400
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Erro de conexão com o banco de dados"}), 500
            
        cursor = conn.cursor()
        query = "INSERT INTO tarefas (descricao, prioridade_ia, status) VALUES (%s, %s, %s)"
        cursor.execute(query, (tarefa_descricao, prioridade, 'pendente'))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Tarefa registrada no NeuroDesk!",
            "descricao": tarefa_descricao,
            "prioridade": prioridade
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/listar_tarefas', methods=['GET'])
def listar_tarefas():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([]), 500
            
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT t.id, t.descricao, t.prioridade_ia as prioridade, t.criado_em
            FROM tarefas t
            ORDER BY t.criado_em DESC
            LIMIT 10
        """
        cursor.execute(query)
        tarefas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Converter datetime para string
        for tarefa in tarefas:
            if isinstance(tarefa.get('criado_em'), datetime):
                tarefa['criado_em'] = tarefa['criado_em'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(tarefas), 200
    except Exception as e:
        print(f"Erro ao listar tarefas: {e}")
        return jsonify([]), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
