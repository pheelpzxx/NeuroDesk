from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import mysql.connector
import csv
import os

app = FastAPI(title="NeuroDesk - Sistema de Foco Extremo")

# Configuração de conexão
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "sua_senha", # [AJUSTE AQUI]
    "database": "neurodesk_db"
}

# [MUDANÇA: Validação de Dados Pydantic]
# Impede o retrabalho garantindo que os dados inseridos sejam válidos
class ProdutoSchema(BaseModel):
    nome: str = Field(..., min_length=2)
    categoria: str
    estoque_atual: int = Field(..., ge=0)
    estoque_minimo: int = Field(10, ge=0)
    preco: float = Field(..., gt=0)

# 1. Rota para Listar Produtos
@app.get("/produtos")
def listar_produtos():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos ORDER BY status_prioridade DESC")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados

# 2. Rota de Inteligência (Sugestão de Foco)
# [MUDANÇA: IA Preditiva para produtividade]
@app.get("/neurodesk/foco-do-dia")
def obter_foco():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nome, estoque_atual FROM produtos WHERE status_prioridade = 'CRÍTICO'")
    alertas = cursor.fetchall()
    cursor.close()
    conn.close()
    return {
        "mensagem": "NeuroDesk: Reduza o retrabalho focando nestes itens",
        "prioridade_maxima": alertas
    }

# 3. Rota de Exportação para Planilha
# [MUDANÇA: Conexão direta para alimentar seu Dashboard externo]
@app.get("/neurodesk/exportar")
def exportar_dados():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    rows = cursor.fetchall()
    
    filename = "dados_dashboard_neurodesk.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Nome', 'Categoria', 'Estoque', 'Mínimo', 'Preço', 'Status'])
        writer.writerows(rows)
    
    cursor.close()
    conn.close()
    return FileResponse(filename, media_type='text/csv', filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
