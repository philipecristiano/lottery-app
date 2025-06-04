// Funções utilitárias e comportamentos comuns para todas as páginas
document.addEventListener('DOMContentLoaded', function() {
    // Disponibilizar informações sobre jogos globalmente
    window.games = {
        "megasena": {"name": "Mega-Sena", "numbers": 6, "range": [1, 60]},
        "quina": {"name": "Quina", "numbers": 5, "range": [1, 80]},
        "lotofacil": {"name": "Lotofácil", "numbers": 15, "range": [1, 25]},
        "maismilionaria": {"name": "Mais Milionária", "numbers": 6, "range": [1, 50], "trevos": 2, "trevos_range": [1, 6]},
        "timemania": {"name": "Timemania", "numbers": 10, "range": [1, 80], "time_coracao": true}
    };
    
    // Configurar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Configurar popovers do Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Função para formatar números como moeda brasileira
    window.formatCurrency = function(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    };
    
    // Função para formatar data no padrão brasileiro
    window.formatDate = function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    };
    
    // Função para gerar cores aleatórias para gráficos
    window.getRandomColors = function(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            const r = Math.floor(Math.random() * 200);
            const g = Math.floor(Math.random() * 200);
            const b = Math.floor(Math.random() * 200);
            colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
        }
        return colors;
    };
    
    // Função para mostrar mensagens de alerta
    window.showAlert = function(message, type = 'info') {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertContainer.style.zIndex = '9999';
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        document.body.appendChild(alertContainer);
        
        // Remover automaticamente após 5 segundos
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.parentNode.removeChild(alertContainer);
            }
        }, 5000);
    };
    
    // Função para validar formulários
    window.validateForm = function(form) {
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return false;
        }
        return true;
    };
    
    // Função para copiar texto para a área de transferência
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text)
            .then(() => {
                window.showAlert('Texto copiado para a área de transferência!', 'success');
            })
            .catch(err => {
                console.error('Erro ao copiar texto:', err);
                window.showAlert('Não foi possível copiar o texto. Por favor, tente novamente.', 'danger');
            });
    };
    
    // Função para verificar se o dispositivo é móvel
    window.isMobile = function() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    };
    
    // Ajustar interface para dispositivos móveis
    if (window.isMobile()) {
        document.body.classList.add('mobile-device');
    }
});
