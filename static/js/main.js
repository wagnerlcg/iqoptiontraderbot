// ========== FUNÇÕES DE MODAL MODERNAS ==========

// Função para mostrar alerta customizado
function showAlert(message, type = 'info', title = null) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        
        const iconMap = {
            'success': { icon: '✓', title: title || 'Sucesso' },
            'error': { icon: '✕', title: title || 'Erro' },
            'warning': { icon: '⚠', title: title || 'Atenção' },
            'info': { icon: 'ℹ', title: title || 'Informação' }
        };
        
        const config = iconMap[type] || iconMap['info'];
        
        const dialog = document.createElement('div');
        dialog.className = 'modal-dialog';
        
        dialog.innerHTML = `
            <div class="modal-dialog-header">
                <div class="icon ${type}">${config.icon}</div>
                <h3>${config.title}</h3>
            </div>
            <div class="modal-dialog-body">
                ${message}
            </div>
            <div class="modal-dialog-footer">
                <button class="btn btn-primary" id="okBtn">OK</button>
            </div>
        `;
        
        modal.appendChild(dialog);
        document.body.appendChild(modal);
        
        const okBtn = dialog.querySelector('#okBtn');
        
        const closeModal = () => {
            modal.remove();
            document.removeEventListener('keydown', escHandler);
            resolve(true);
        };
        
        okBtn.addEventListener('click', closeModal);
        
        // Fechar ao clicar fora do modal
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
        
        // Fechar com ESC
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal();
            }
        };
        document.addEventListener('keydown', escHandler);
    });
}

// Função para mostrar confirmação customizada
function showConfirm(message, title = 'Confirmar', details = null) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        
        const dialog = document.createElement('div');
        dialog.className = 'modal-dialog';
        
        dialog.innerHTML = `
            <div class="modal-dialog-header">
                <div class="icon warning">⚠</div>
                <h3>${title}</h3>
            </div>
            <div class="modal-dialog-body">
                ${message}
                ${details ? `<div class="details">${details}</div>` : ''}
            </div>
            <div class="modal-dialog-footer">
                <button class="btn btn-secondary" id="cancelBtn">Cancelar</button>
                <button class="btn btn-primary" id="confirmBtn">Confirmar</button>
            </div>
        `;
        
        modal.appendChild(dialog);
        document.body.appendChild(modal);
        
        // Handlers
        const cancelBtn = dialog.querySelector('#cancelBtn');
        const confirmBtn = dialog.querySelector('#confirmBtn');
        
        const closeModal = (result) => {
            modal.remove();
            document.removeEventListener('keydown', escHandler);
            resolve(result);
        };
        
        cancelBtn.addEventListener('click', () => closeModal(false));
        confirmBtn.addEventListener('click', () => closeModal(true));
        
        // Fechar ao clicar fora do modal (cancela)
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal(false);
            }
        });
        
        // Fechar com ESC (cancela)
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                closeModal(false);
            }
        };
        document.addEventListener('keydown', escHandler);
    });
}

// Sobrescrever alert e confirm nativos (opcional, mas mantemos compatibilidade)
window.customAlert = showAlert;
window.customConfirm = showConfirm;

// Função de logout
async function logout() {
    const result = await showConfirm('Tem certeza que deseja sair?', 'Confirmar Logout');
    if (result) {
        try {
            const response = await fetch('/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
            // Redirecionar mesmo em caso de erro
            window.location.href = '/';
        }
    }
}

// Função para mostrar notificações (pode ser expandida)
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Verificar conexão periodicamente
if (window.IS_LOGGED_IN === true || window.IS_LOGGED_IN === 'true') {
    setInterval(async () => {
        try {
            const response = await fetch('/api/balance', {
                credentials: 'same-origin'
            });
            if (!response.ok && response.status === 401) {
                // Não autenticado, redirecionar para login
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Erro ao verificar conexão:', error);
        }
    }, 30000); // Verificar a cada 30 segundos
}

