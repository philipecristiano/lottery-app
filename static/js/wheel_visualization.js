/**
 * Visualização do volante de loteria
 * Este script cria uma representação visual do volante de loteria
 * mostrando graficamente a estratégia usada para seleção de números
 */

class LotteryWheel {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with ID ${containerId} not found`);
            return;
        }
        
        // Configurações padrão
        this.options = {
            lotteryType: 'megasena',
            width: 320,
            height: 320,
            margin: 40,
            numberSize: 30,
            highlightedNumbers: [],
            strategy: 'random',
            ...options
        };
        
        // Configurações específicas para cada tipo de loteria
        this.lotteryConfig = {
            megasena: { range: [1, 60], rows: 6, cols: 10 },
            lotofacil: { range: [1, 25], rows: 5, cols: 5 },
            quina: { range: [1, 80], rows: 8, cols: 10 },
            timemania: { range: [1, 80], rows: 8, cols: 10 },
            maismilionaria: { range: [1, 50], rows: 5, cols: 10 }
        };
        
        // Cores para diferentes estratégias
        this.strategyColors = {
            random: { fill: '#6c757d', stroke: '#495057' },
            hot_numbers: { fill: '#dc3545', stroke: '#c82333' },
            cold_numbers: { fill: '#0d6efd', stroke: '#0a58ca' },
            balanced: { fill: '#fd7e14', stroke: '#e76102' },
            ai_suggested: { fill: '#6f42c1', stroke: '#5e37a6' },
            last_5_avg: { fill: '#20c997', stroke: '#1ba87e' }
        };
        
        this.init();
    }
    
    init() {
        // Limpar o container
        this.container.innerHTML = '';
        
        // Criar o canvas SVG
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', this.options.width);
        this.svg.setAttribute('height', this.options.height);
        this.svg.setAttribute('viewBox', `0 0 ${this.options.width} ${this.options.height}`);
        this.svg.setAttribute('class', 'lottery-wheel');
        
        this.container.appendChild(this.svg);
        
        // Desenhar o volante
        this.drawWheel();
    }
    
    drawWheel() {
        const config = this.lotteryConfig[this.options.lotteryType];
        if (!config) {
            console.error(`Lottery type ${this.options.lotteryType} not supported`);
            return;
        }
        
        const { range, rows, cols } = config;
        const [min, max] = range;
        const totalNumbers = max - min + 1;
        
        // Calcular tamanho e espaçamento
        const availableWidth = this.options.width - 2 * this.options.margin;
        const availableHeight = this.options.height - 2 * this.options.margin;
        
        const cellWidth = availableWidth / cols;
        const cellHeight = availableHeight / rows;
        
        const radius = Math.min(cellWidth, cellHeight) * 0.4;
        
        // Desenhar cada número
        for (let i = 0; i < totalNumbers; i++) {
            const number = min + i;
            const row = Math.floor(i / cols);
            const col = i % cols;
            
            const cx = this.options.margin + col * cellWidth + cellWidth / 2;
            const cy = this.options.margin + row * cellHeight + cellHeight / 2;
            
            // Verificar se o número está destacado
            const isHighlighted = this.options.highlightedNumbers.includes(number);
            
            // Definir cores com base na estratégia e se está destacado
            let fillColor, strokeColor;
            if (isHighlighted) {
                const strategyColor = this.strategyColors[this.options.strategy] || this.strategyColors.random;
                fillColor = strategyColor.fill;
                strokeColor = strategyColor.stroke;
            } else {
                fillColor = '#f8f9fa';
                strokeColor = '#dee2e6';
            }
            
            // Criar círculo para o número
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', cx);
            circle.setAttribute('cy', cy);
            circle.setAttribute('r', radius);
            circle.setAttribute('fill', fillColor);
            circle.setAttribute('stroke', strokeColor);
            circle.setAttribute('stroke-width', '2');
            
            if (isHighlighted) {
                // Adicionar efeito de brilho para números destacados
                circle.setAttribute('filter', 'url(#glow)');
            }
            
            this.svg.appendChild(circle);
            
            // Adicionar texto do número
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', cx);
            text.setAttribute('y', cy);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'central');
            text.setAttribute('font-size', `${radius * 1.2}px`);
            text.setAttribute('font-weight', isHighlighted ? 'bold' : 'normal');
            text.setAttribute('fill', isHighlighted ? 'white' : '#212529');
            text.textContent = number;
            
            this.svg.appendChild(text);
        }
        
        // Adicionar filtro de brilho para números destacados
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
        filter.setAttribute('id', 'glow');
        
        const feGaussianBlur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
        feGaussianBlur.setAttribute('stdDeviation', '2.5');
        feGaussianBlur.setAttribute('result', 'coloredBlur');
        
        const feMerge = document.createElementNS('http://www.w3.org/2000/svg', 'feMerge');
        const feMergeNode1 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode1.setAttribute('in', 'coloredBlur');
        const feMergeNode2 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode2.setAttribute('in', 'SourceGraphic');
        
        feMerge.appendChild(feMergeNode1);
        feMerge.appendChild(feMergeNode2);
        filter.appendChild(feGaussianBlur);
        filter.appendChild(feMerge);
        defs.appendChild(filter);
        
        this.svg.appendChild(defs);
        
        // Adicionar legenda
        this.addLegend();
    }
    
    addLegend() {
        const legendGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        legendGroup.setAttribute('class', 'legend');
        legendGroup.setAttribute('transform', `translate(${this.options.margin}, ${this.options.height - 20})`);
        
        const strategyName = {
            random: 'Aleatória',
            hot_numbers: 'Números Quentes',
            cold_numbers: 'Números Frios',
            balanced: 'Balanceada',
            ai_suggested: 'Sugestão IA',
            last_5_avg: 'Média Últimos 5'
        };
        
        const strategyColor = this.strategyColors[this.options.strategy] || this.strategyColors.random;
        
        // Círculo da legenda
        const legendCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        legendCircle.setAttribute('cx', 10);
        legendCircle.setAttribute('cy', -10);
        legendCircle.setAttribute('r', 8);
        legendCircle.setAttribute('fill', strategyColor.fill);
        legendCircle.setAttribute('stroke', strategyColor.stroke);
        legendCircle.setAttribute('stroke-width', '1');
        
        // Texto da legenda
        const legendText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        legendText.setAttribute('x', 25);
        legendText.setAttribute('y', -7);
        legendText.setAttribute('font-size', '12px');
        legendText.setAttribute('fill', '#212529');
        legendText.textContent = `Estratégia: ${strategyName[this.options.strategy] || 'Desconhecida'}`;
        
        legendGroup.appendChild(legendCircle);
        legendGroup.appendChild(legendText);
        
        this.svg.appendChild(legendGroup);
    }
    
    // Método para atualizar os números destacados
    updateHighlightedNumbers(numbers, strategy = null) {
        this.options.highlightedNumbers = numbers;
        if (strategy) {
            this.options.strategy = strategy;
        }
        this.init();
    }
}

// Função para inicializar a visualização do volante
function initWheelVisualization(containerId, lotteryType, highlightedNumbers, strategy) {
    return new LotteryWheel(containerId, {
        lotteryType: lotteryType,
        highlightedNumbers: highlightedNumbers,
        strategy: strategy
    });
}
