// Verificar status do sistema
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        const statusDot = document.getElementById('system-status');
        const statusMsg = document.getElementById('status-msg');
        
        if (data.mysql === 'conectado') {
            statusDot.classList.add('online');
            statusDot.textContent = 'Online';
            statusMsg.textContent = `✅ ${data.status} v${data.version} - MySQL conectado`;
        } else {
            statusDot.textContent = '⚠️';
            statusMsg.textContent = `⚠️ ${data.status} - MySQL desconectado`;
        }
    } catch (error) {
        document.getElementById('system-status').textContent = '❌';
        document.getElementById('status-msg').textContent = 'Erro de conexão com o backend';
    }
}

// Registrar log de produtividade
document.getElementById('tarefa-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const descricao = document.getElementById('descricao').value;
    const tempoEstimado = document.getElementById('tempo_estimado')?.value || 0;
    const feedback = document.getElementById('form-feedback');
    
    try {
        const response = await fetch('/registrar_log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                tarefa_nome: descricao,
                tempo_gasto_segundos: parseInt(tempoEstimado) * 60 // converte minutos para segundos
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            feedback.className = 'feedback-msg success';
            feedback.textContent = data.message;
            document.getElementById('tarefa-form').reset();
            carregarAlertas(); // Atualiza a lista de críticos
        } else {
            throw new Error(data.error || 'Erro ao registrar');
        }
    } catch (error) {
        feedback.className = 'feedback-msg error';
        feedback.textContent = `❌ Erro: ${error.message}`;
    }
    
    setTimeout(() => {
        feedback.className = 'feedback-msg';
        feedback.textContent = '';
    }, 5000);
});

// Carregar produtos críticos (alertas de estoque)
async function carregarAlertas() {
    try {
        const response = await fetch('/produtos/criticos');
        let produtos = [];
        
        if (response.ok) {
            produtos = await response.json();
        }
        
        const alertList = document.getElementById('alert-list');
        if (!alertList) return;
        
        alertList.innerHTML = '';
        
        if (produtos.length === 0) {
            alertList.innerHTML = '<li style="text-align:center;color:var(--text-light);padding:2rem">✅ Nenhum produto crítico no momento</li>';
            document.getElementById('alert-count').textContent = '0';
            return;
        }
        
        produtos.forEach(produto => {
            const li = document.createElement('li');
            const isCritico = produto.status_prioridade === 'CRÍTICO' || produto.estoque_atual <= produto.estoque_minimo;
            
            li.className = `alert-item ${isCritico ? 'high' : 'medium'}`;
            li.innerHTML = `
                <span class="tag ${isCritico ? 'alta' : 'media'}">${isCritico ? 'CRÍTICO' : 'Atenção'}</span>
                <p><strong>${produto.nome}</strong><br>
                <small>Estoque: ${produto.estoque_atual} | Mínimo: ${produto.estoque_minimo}</small></p>
                <small>${produto.categoria} • R$ ${parseFloat(produto.preco).toFixed(2)}</small>
            `;
            alertList.appendChild(li);
        });
        
        // Atualiza contador de alertas
        document.getElementById('alert-count').textContent = produtos.length;
        
    } catch (error) {
        console.error('Erro ao carregar alertas:', error);
    }
}

// Carregar lista de produtos recentes
async function carregarProdutos() {
    try {
        const response = await fetch('/produtos');
        let produtos = [];
        
        if (response.ok) {
            produtos = await response.json();
        }
        
        const taskList = document.getElementById('task-list');
        if (!taskList) return;
        
        taskList.innerHTML = '';
        
        if (produtos.length === 0) {
            taskList.innerHTML = '<li style="text-align:center;color:var(--text-light);padding:2rem">Nenhum produto cadastrado</li>';
            return;
        }
        
        // Mostra apenas os 10 primeiros
        produtos.slice(0, 10).forEach(produto => {
            const li = document.createElement('li');
            const prioridadeCor = produto.status_prioridade === 'CRÍTICO' 
                ? 'var(--alert-high)' 
                : produto.estoque_atual <= produto.estoque_minimo 
                    ? 'var(--alert-med)' 
                    : 'var(--alert-low)';
            
            li.innerHTML = `
                <div class="task-info">
                    <h4>${produto.nome}</h4>
                    <small>${produto.categoria} • Estoque: ${produto.estoque_atual}</small>
                </div>
                <span class="tag" style="background:${prioridadeCor};color:white">
                    ${produto.status_prioridade}
                </span>
            `;
            taskList.appendChild(li);
        });
        
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    carregarAlertas();
    carregarProdutos();
    
    // Atualiza a cada 30 segundos
    setInterval(checkStatus, 30000);
    setInterval(carregarAlertas, 30000);
});

// Navegação suave
document.querySelectorAll('.nav a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.nav a').forEach(l => l.classList.remove('active'));
        e.target.classList.add('active');
        
        const target = e.target.getAttribute('href');
        document.querySelector(target)?.scrollIntoView({ behavior: 'smooth' });
    });
});
// Funções do modal (adicione ao final do main.js)
function abrirModal(id, nome, estoqueAtual) {
    document.getElementById('modal-produto-id').value = id;
    document.getElementById('modal-produto-nome').textContent = nome;
    document.getElementById('modal-novo-estoque').value = estoqueAtual;
    document.getElementById('modal-estoque').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('modal-estoque').style.display = 'none';
}

async function salvarEstoque() {
    const id = document.getElementById('modal-produto-id').value;
    const novoEstoque = document.getElementById('modal-novo-estoque').value;
    
    try {
        const response = await fetch(`/produtos/${id}/atualizar_estoque`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estoque_atual: parseInt(novoEstoque) })
        });
        
        const data = await response.json();
        if (response.ok) {
            alert(data.message);
            fecharModal();
            carregarAlertas();
            carregarProdutos();
        } else {
            alert('Erro: ' + data.error);
        }
    } catch (error) {
        alert('Erro de conexão: ' + error.message);
    }
}

// Fechar modal ao clicar fora
document.getElementById('modal-estoque')?.addEventListener('click', (e) => {
    if (e.target.id === 'modal-estoque') fecharModal();
});

// Fechar com ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') fecharModal();
});
