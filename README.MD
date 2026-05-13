# Coletador do Governo

## Objetivo

Salvar em um arquivo de texto, automaticamente, a quantidade de servidores federais, média de remuneração desses servidores e os 10 servidores com a maior remuneração.

## Tecnologias utilizadas

- Python 3.9+
- pandas
- requests
- argparse
- logging

## Referências e processo de pesquisa

Diversos métodos para aprender e pesquisar sobre as tecnologias e metodologia estavam disponíveis, desde agentes de IA até fórums e projetos anteriores. Dentre os que foram usados, destaca-se:

### Documentação oficial Python

A documentação oficial Python está apresentada quase que como um tutorial para o leitor, muito bem escrita e didática. A documentação oficial é ostensiva sobre as bibliotecas argparse e logging que foram utilizadas, explicando muito bem suas funcionalidades e funcionamento.

### Documentação oficial Requests

Tal qual a documentação do Python, a documentação da Requests também é simples e muito objetiva, contando com diversos exemplos. Nota-se que a própria biblioteca vai além e mostra casos de uso, como salvar bytes usando `open` em modo `wb` (escrever binário/bytes).

### ChatGPT

O agente de IA ChatGPT foi usado extensivamente, em específico comumente em ocasiões para introduzir novos conceitos, sugerir melhorias em código - tanto em performance mas principalmente em legibilidade.

O ChatGPT teve papel importante principalmente nas etapas iniciais de investigação do funcionamento do portal. Para definir como coletar os dados do portal da transparência, o bot mostrou meios de como descobrir a origem dos dados, o que levou ao link do servidor com as planilhas.

Ademais, o ChatGPT auxiliou na discussão de boas práticas e estruturação e correção do README.

### Stack Overflow

Foi utilizado minimamente, principalmente para pesquisas rápidas sobre métodos e abordagens mais idiomáticas da biblioteca pandas, sem a necessidade de navegar extensivamente pela documentação.

Como exemplo, originalmente o código responsável por coletar os 10 servidores com maior remuneração utilizava:

`df.sort_values('RENDIMENTOS_TOTAIS', ascending=False)[['NOME', 'RENDIMENTOS_TOTAIS']].head(10).reset_index(drop=True)`

Após pesquisa sobre formas mais apropriadas de resolver o problema, foi encontrado o método `nlargest`, resultando em uma solução mais clara e legível.

## Decisões técnicas

### Bibliotecas

#### Pandas

Biblioteca usada para lidar com CSVs e análise de dados. O projeto a usa para carregar CSVs e realizar operações como soma de colunas, média, contagem, ordenação...

#### Requests

Biblioteca usada para fazer requisições HTTP. Foi percebido que o site onde estavam disponíveis as planilhas (https://portaldatransparencia.gov.br/download-de-dados/servidores) fazia um request GET para outro servidor, onde o arquivo estava localizado. Tendo essa informação em mente, podemos replicar essa ação no projeto e fazer um GET para esse servidor e coletar o arquivo.

#### Argparse

Foi usado a biblioteca argparse para interface CLI. A biblioteca é notória por sua simplicidade e facilidade de uso, permitindo diversas funcionalidades com pouco código, como help section automática. Também é uma biblioteca nativa do Python.

#### Logging

A biblioteca escolhida para fazer logs foi a logging. Esta biblioteca é simples e foi escolhida também porque é nativa do Python. A principal funcionalidade, além da formatação, inclusão de níveis, datas e horários, é a possibilidade de fazer logs para diversos meios. O projeto escreve logs em console e em arquivos de logs.

## Estrutura do projeto

### Estrutura de arquivos e pastas

```
Coletador do Governo/
├── main.py
├── README.MD
└── requirements.txt
```

### Resumo

O projeto foi estruturado de forma modular, utilizando funções pequenas e com responsabilidades bem definidas. O projeto evita o uso de estado global mutável. Todas as informações necessárias são passadas entre funções como parâmetros ou retornados.

Sobre as funções: todas encapsulam tarefas relativamente e auto explicativas - exceto pela gerar_relatorio e main. Essas duas são importantes a se notar pois:

- main: é a função principal, não executa tarefas ou operações diretamente. A única operação realizada em main é passar dados entre funções, fazendo pequenos ajustes ou preparações entre funções.
- gerar_relatorio: não é muito óbvio o que essa função faz pelo nome, mas em suma, ela extrai a quantidade de servidores, média de remuneração e os 10 servidores com a maior remuneração.

## Instalação

Clone o projeto para sua máquina local, crie uma venv python 3.9+ (mandatório) e instale as dependências do projeto através do requirements.txt:

`python -m venv .venv`

`python -m pip install -r requirements.txt`

## Execução

O programa contém uma seção de ajuda que pode ser acessada com o argumento `-h`. Esta seção mostra os parâmetros exigidos e um exemplo de uso.

## Exemplo de uso

`python main.py -m 1 -a 2026 -t Servidores_SIAPE`

## Funcionalidades

O programa é capaz de coletar dados do portal da transparência e realizar análise de dados básica.

## Tratamento de erros e robustez

A grande maioria dos tratamentos de erros é simplesmente abortar o programa, infelizmente. Isso se deve à natureza do projeto, pois este depende de muitos fatores externos, como um site governamental. Independente da situação, todo o erro, fatal ou não, é logado junto com traceback completo.

Pontos a se notarem:

- O programa tenta se conectar ao servidor desejado 3 vezes antes de subir o erro de Timeout e abortar. Cada tentativa é loggada.
- O programa também logga possíveis erros ao extrair ZIP e carregar CSV.

## Limitações

O programa é extremamente limitado em questão de parametrização. Há muito espaço para o usuário parametrizar muito mais variáveis, mas o programa não o faz.

## Melhorias futuras

A parametrização de variáveis através da CLI é o caminho mais óbvio. Seguem sugestões de parâmetros:

- Nome do arquivo final
- Onde salvar log
- Manter ZIP
- Descartar CSVs