# Gerador de Relatórios Cadastrais: Sua Ferramenta Essencial para Análise de Dados

Este projeto oferece um aplicativo Python completo, desenvolvido para automatizar a extração de dados de cadastros de um banco de dados PostgreSQL, processar informações de diferentes tipos de cadastro e gerar relatórios detalhados em arquivos Excel.

## Funcionalidades:

- **Conexão com Banco de Dados PostgreSQL:** Conecta-se ao seu banco de dados PostgreSQL e extrai dados de tabelas específicas, simplificando o processo de obtenção de informações.
  
- **Interface Gráfica Intuitiva:** Uma interface gráfica amigável, construída com PyQt5, permite ao usuário configurar o aplicativo e iniciar o processo de extração de dados de forma fácil e intuitiva.
  
- **Processamento de Múltiplos Tipos de Cadastro:** Suporta o processamento de diferentes tipos de cadastro, incluindo PG, IP, CONSUMIDOR, USO MUTUO e ESTRUTURA, com a possibilidade de adicionar novos tipos facilmente, adaptando-se às suas necessidades específicas.
  
- **Agrupamento de Dados:** Agrupa dados por cadastrador e data para uma análise mais profunda, fornecendo insights valiosos sobre a produtividade e o desempenho dos cadastradores, ajudando a tomar decisões mais assertivas.
  
- **Relatórios Personalizáveis em Excel:** Gera relatórios detalhados em arquivos Excel, permitindo a personalização da saída para atender às suas necessidades específicas, como filtros e formatação.
  
- **Sistema de Log Completo:** Registra eventos e erros durante a execução do aplicativo, facilitando a depuração e a análise do comportamento do aplicativo, garantindo uma experiência mais suave e segura.
  
- **Modularização e Extensibilidade:** A estrutura modularizada do código facilita a manutenção e a adição de novas funcionalidades, permitindo que o aplicativo evolua de acordo com as suas necessidades.

## Como Usar:

### Requisitos:
- Python 3.x
- PyQt5
- psycopg2
- pandas
- xlrd
- openpyxl
- xlswriter
- numpy
- pyinstaller (opcional, para criar um executável)
- git


### Configuração:

1. Edite o arquivo `src/config.py` com as credenciais do seu banco de dados e defina o diretório de saída para os relatórios.


### Executando o Aplicativo:

1. Abra o aplicativo.
2. Selecione o banco de dados desejado no menu suspenso "Banco de Dados".
3. Selecione o projeto desejado no menu suspenso "Projeto".
4. Clique no botão "..." para selecionar o diretório de saída para os arquivos Excel.
5. Clique no botão "Extrair" para iniciar o processo de extração e processamento de dados.

   
## Benefícios:

- **Eficiência:** Automatiza o processo de extração, processamento e análise de dados, liberando tempo para tarefas mais estratégicas.
  
- **Precisão:** Garante a precisão dos dados extraídos e processados, oferecendo relatórios confiáveis e consistentes.
  
- **Insights:** Permite a análise profunda dos dados, revelando tendências e padrões que podem auxiliar na tomada de decisões estratégicas.
  
- **Flexibilidade:** Adapta-se facilmente às suas necessidades específicas, permitindo a personalização de relatórios e a adição de novos tipos de cadastro.
