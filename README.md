# Aplicativo de Loteria Inteligente

Este é um aplicativo web para análise estatística e geração de jogos para as principais loterias brasileiras. O sistema utiliza dados históricos e algoritmos de inteligência artificial para fornecer análises detalhadas e sugestões de jogos com maior probabilidade estatística de acertos.

## Funcionalidades

- **Análise estatística avançada** de jogos de loteria (frequência, atraso, padrões)
- **Geração inteligente de jogos** com diferentes estratégias
- **Visualização gráfica do volante** mostrando a estratégia aplicada
- **Verificação automática** de acertos com resultados oficiais
- **Histórico completo** de jogos e acertos
- **Informações sobre prêmio acumulado** e próximo sorteio
- **Análise de probabilidade com IA** para cada jogo gerado

## Loterias Suportadas

- Mega-Sena
- Quina
- +Milionária
- Time Mania
- Lotofácil

## Requisitos Técnicos

- Python 3.8+
- Flask
- SQLite
- HTML/CSS/JavaScript
- Bootstrap 5

## Instalação Local

1. Clone este repositório:
```
git clone https://github.com/seu-usuario/lottery-app.git
cd lottery-app
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Execute o aplicativo:
```
python -m src.main
```

5. Acesse o aplicativo em seu navegador:
```
http://localhost:5000
```

## Implantação no Vercel

### Pré-requisitos

- Conta no GitHub
- Conta no Vercel

### Passos para Implantação

1. Faça upload deste projeto para um repositório GitHub:
   - Crie um novo repositório no GitHub
   - Faça upload de todos os arquivos deste projeto para o repositório

2. Conecte-se ao Vercel:
   - Acesse https://vercel.com/ e faça login com sua conta
   - Clique em "New Project"
   - Importe o repositório GitHub que você acabou de criar

3. Configure o projeto no Vercel:
   - Framework Preset: Selecione "Other"
   - Build Command: `pip install -r requirements.txt && python -m src.main`
   - Output Directory: `public`
   - Environment Variables: Não são necessárias para a configuração básica

4. Clique em "Deploy" e aguarde a conclusão da implantação

5. Acesse seu aplicativo através da URL fornecida pelo Vercel

## Estrutura do Projeto

```
lottery-app/
├── venv/                  # Ambiente virtual Python
├── src/                   # Código-fonte do aplicativo
│   ├── models/            # Modelos de dados
│   ├── routes/            # Rotas e controladores
│   │   ├── api.py         # API para comunicação com o frontend
│   │   └── views.py       # Rotas para renderização de páginas
│   ├── services/          # Serviços e lógica de negócio
│   │   ├── analyzer.py    # Análise básica de loterias
│   │   ├── advanced_analyzer.py  # Análise avançada
│   │   └── probability_optimizer.py  # Otimização de probabilidade
│   ├── static/            # Arquivos estáticos
│   │   ├── css/           # Estilos CSS
│   │   ├── js/            # Scripts JavaScript
│   │   └── img/           # Imagens
│   ├── templates/         # Templates HTML
│   │   ├── base.html      # Template base
│   │   ├── index.html     # Página inicial
│   │   ├── analyze.html   # Página de análise
│   │   ├── generate.html  # Página de geração de jogos
│   │   ├── check.html     # Página de verificação
│   │   └── history.html   # Página de histórico
│   └── main.py            # Ponto de entrada do aplicativo
└── requirements.txt       # Dependências do projeto
```

## Uso do Aplicativo

### Página Inicial

A página inicial exibe os últimos resultados das loterias suportadas e permite acesso rápido às principais funcionalidades.

### Análise Estatística

1. Acesse a página "Análise" no menu principal
2. Selecione a loteria desejada no canto superior direito
3. Navegue pelas três abas disponíveis:
   - **Análise Básica**: Para visualização de frequência e atraso
   - **Análise Avançada**: Para estatísticas detalhadas e padrões
   - **Estratégias Recomendadas**: Para sugestões personalizadas

### Geração de Jogos

1. Acesse a página "Gerar Jogos" no menu principal
2. Selecione a loteria desejada
3. Escolha a estratégia de geração:
   - **Aleatória**: Para jogos completamente aleatórios
   - **Números Quentes**: Para priorizar números frequentes
   - **Números Frios**: Para priorizar números atrasados
   - **Média dos Últimos 5 Jogos**: Para jogos baseados em padrões recentes
   - **Personalizada (Pares/Ímpares)**: Para definir manualmente a quantidade de pares e ímpares
   - **Otimizada por IA**: Para jogos com maior probabilidade estatística
4. Defina a quantidade de jogos desejada
5. Clique em "Visualizar Antes de Gerar" para ver uma prévia
6. Verifique a análise de probabilidade exibida
7. Clique em "Gerar Jogos" para confirmar

### Verificação de Jogos

1. Acesse a página "Verificar" no menu principal
2. Selecione a loteria e o concurso desejado
3. Insira os números do seu jogo ou selecione do histórico
4. Clique em "Verificar" para conferir os acertos

### Histórico de Jogos

1. Acesse a página "Histórico" no menu principal
2. Visualize todos os seus jogos anteriores
3. Filtre por loteria, período ou quantidade de acertos
4. Analise seu desempenho histórico e padrões de acertos

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Aviso Legal

Este aplicativo utiliza análise estatística e não pode garantir prêmios, pois a loteria é fundamentalmente um jogo de azar. Use com responsabilidade.
