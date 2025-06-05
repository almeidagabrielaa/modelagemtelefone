# Projeto: Processamento de Dados de Pacientes

Este projeto fornece ferramentas para processar e validar dados de pacientes, especificamente focando na validação de nomes, CPFs, CNS, e números de telefone. Ele está projetado para ler arquivos CSV e XLSX e gerar saídas validadas em arquivos CSV.

## Funcionalidades

- **Validação de Nomes**: Verifica se os nomes dos pacientes são válidos, garantindo que contenham apenas letras e espaços.
- **Correção de Nomes**: Aplica correções a nomes com caracteres especiais conhecidos.
- **Validação e Formatação de Telefones**: Valida números de telefone, adicionando o DDI do Brasil (`55`) quando necessário, e verifica a conformidade com formatos esperados.
- **Remoção de DDI de Telefones**: Remove o DDI dos números de telefone formatados para facilitar o uso.
- **Validação de CNS**: Verifica se os números do Cartão Nacional de Saúde possuem exatamente 15 dígitos.
- **Validação de CPF**: Valida CPFs, garantindo que tenham 11 dígitos, incluindo zeros à esquerda, e calcula os dígitos verificadores.
- **Geração de Arquivos de Saída**: Filtra registros válidos e inválidos, gerando arquivos CSV separados para cada tipo.

## Uso

### Pré-requisitos

- Python 3.x
- Bibliotecas: `pandas`, `re`, `glob`, `os`, `unicodedata`

### Como Executar

1. **Preparar o Ambiente**:
   - Certifique-se de que todas as bibliotecas necessárias estão instaladas. Você pode instalá-las usando `pip`:
     ```bash
     pip install pandas
     ```

2. **Colocar Arquivos na Pasta**:
   - Coloque os arquivos CSV e XLSX que deseja processar no mesmo diretório que o script Python.

3. **Executar o Script**:
   - Execute o script Python. Ele processará todos os arquivos CSV e XLSX no diretório atual.
   - No terminal ou prompt de comando, execute:
     ```bash
     python nome_do_seu_script.py
     ```

4. **Verificar Resultados**:
   - Após a execução, verifique os arquivos gerados com sufixos `_validos.csv` e `_invalidos.csv` para registros válidos e inválidos, respectivamente.

## Estrutura do Código

- **Funções de Validação e Formatação**:
  - `verificar_nome_valido(nome)`: Valida nomes.
  - `validar_formatar_telefone(telefone)`: Formata e valida números de telefone.
  - `remover_ddi(whatsapp)`: Remove DDI dos números de telefone.
  - `validar_cns(cns)`: Valida números de CNS.
  - `verificar_cpf(cpf)`: Valida CPFs e verifica dígitos.

- **Processamento de Arquivos**:
  - `processar_dataframe(df, arquivo, aba)`: Processa as abas de um DataFrame, aplica validações e gera saídas.
  - `processar_arquivo(arquivo)`: Lê arquivos CSV e XLSX, chamando `processar_dataframe` para cada aba ou arquivo.

## Observações

- Certifique-se de que os arquivos de entrada estão bem formatados e que as colunas necessárias (`cpf`, `cns`, `telefone`, etc.) estão presentes.
- O código foi projetado para ser robusto, mas erros podem ocorrer se os dados de entrada estiverem muito fora do padrão esperado.
