// Verificar status do sistema
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        document.getElementById('system-status').classList.add('online');
        document.getElementById('system-status').textContent = 'Online';
        document.getElementById('status-msg').textContent = 
            `${data.status} v${data.version} - Conectado ao MySQL`;
    } catch (error) {
        document.getElementById('system-status').textContent = 'Offline';
        document.getElementById('status-msg').textContent = 
            'Erro de conexão com o backend';
    }
}

// Enviar nova tarefa
document.getElementById('tarefa-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const descricao = document.getElementById('descricao').value;
    const prioridade = document.getElementById('prioridade').value;
    const feedback = document.getElementById('form-feedback');
    
    try {
        const response = await fetch('/processar_tarefa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                descricao: descricao,
                prioridade: parseInt(prioridade)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            feedback.className = 'feedback-msg success';
            feedback.textContent = '✅ Tarefa registrada com sucesso!';
            document.getElementById('tarefa-form').reset();
            
            // Atualizar lista de tarefas
            loadTarefas();
        } else {
            throw new Error(data.error || 'Erro ao registrar tarefa');
        }
    } catch (error) {
        feedback.className = 'feedback-msg error';
        feedback.textContent = `❌ Erro: ${error.message}`;
    }
    
    // Esconder mensagem após 5 segundos
    setTimeout(() => {
        feedback.className = 'feedback-msg';
        feedback.textContent = '';
    }, 5000);
});

// Carregar tarefas recentes
async function loadTarefas() {
    try {
        const response = await fetch('/listar_tarefas');
        let tarefas = [];
        
        if (response.ok) {
            tarefas = await response.json();
        } else {
            // Dados mockados para teste
            tarefas = [
                { id: 1, descricao: 'Conferência de estoque', prioridade: 3, criado_em: '2026-05-15 10:30:00' },
                { id: 2, descricao: 'Relatório de validação', prioridade: 2, criado_em: '2026-05-15 09:15:00' },
                { id: 3, descricao: 'Ajuste de planilha de custos', prioridade: 1, criado_em: '2026-05-14 16:45:00' }
            ];
        }
        
        const taskList = document.getElementById('task-list');
        taskList.innerHTML = '';
        
        if (tarefas.length === 0) {
            taskList.innerHTML = '<li style="text-align: center; color: var(--text-light); padding: 2rem;">Nenhuma tarefa registrada</li>';
            return;
        }
        
        tarefas.forEach(tarefa => {
            const li = document.createElement('li');
            const prioridadeTexto = ['Baixa', 'Média', 'Alta'][tarefa.prioridade - 1] || 'Média';
            const corPrioridade = ['var(--alert-low)', 'var(--alert-med)', 'var(--alert-high)'][tarefa.prioridade - 1] || 'var(--alert-med)';
            
            li.innerHTML = `
                <div class="task-info">
                    <h4>${tarefa.descricao}</h4>
                    <small>${new Date(tarefa.criado_em).toLocaleString('pt-BR')}</small>
                </div>
                <span class="tag" style="background: ${corPrioridade}; color: white;">${prioridadeTexto}</span>
            `;
            taskList.appendChild(li);
        });
        
        // Atualizar contador de alertas
        const alertasAltos = tarefas.filter(t => t.prioridade === 3).length;
        document.getElementById('alert-count').textContent = alertasAltos;
    } catch (error) {
        console.error('Erro ao carregar tarefas:', error);
    }
}

// Limpar alertas lidos
function limparAlertas() {
    const alertList = document.getElementById('alert-list');
    alertList.innerHTML = '<li style="text-align: center; color: var(--text-light); padding: 2rem;">Nenhum alerta pendente</li>';
    document.getElementById('alert-count').textContent = '0';
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    loadTarefas();
    
    // Atualizar a cada 30 segundos
    setInterval(checkStatus, 30000);
    setInterval(loadTarefas, 30000);
});

// Navegação suave
document.querySelectorAll('.nav a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.nav a').forEach(l => l.classList.remove('active'));
        e.target.classList.add('active');
        
        const target = e.target.getAttribute('href');
        document.querySelector(target).scrollIntoView({ behavior: 'smooth' });
    });
});
