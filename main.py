from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Neurodesk API - Produtividade Farmacêutica")

# Configuração da conexão com o banco de dados
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "sua_senha",
    "database": "neurodesk_db"
}

# Modelo de Dados para validação
class Produto(BaseModel):
    nome: str
    categoria: str
    estoque_atual: int
    preco: float

# Rota para Listar Produtos (Onde a IA pode atuar prevendo falta de estoque)
@app.get("/produtos", response_model=List[dict])
def listar_produtos():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return produtos

# Rota para Registrar Produtividade (O cérebro da Neurodesk)
@app.post("/log-produtividade")
def registrar_foco(tarefa: str, segundos: int):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "INSERT INTO logs_produtividade (tarefa_nome, tempo_gasto_segundos) VALUES (%s, %s)"
        cursor.execute(sql, (tarefa, segundos))
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "sucesso", "mensagem": "Dados de foco registrados!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Simulação de IA para sugerir foco ao farmacêutico
@app.get("/neurodesk/sugestao-foco")
def sugerir_foco():
    # Aqui a IA analisaria o estoque e as vendas
    # Para a demo, vamos simular uma análise real
    sugestoes = [
        {"prioridade": "ALTA", "acao": "Repor Dipirona (Estoque abaixo do mínimo)"},
        {"prioridade": "MÉDIA", "acao": "Validar receitas pendentes de Amoxicilina"},
        {"prioridade": "BAIXA", "acao": "Organizar prateleira de Dermocosméticos"}
    ]
    return {"status": "Modo Foco Ativo", "sugestoes": sugestoes}
