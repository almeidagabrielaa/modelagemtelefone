import pandas as pd
import re
import glob
import os
import unicodedata

def verificar_nome_valido(nome):
    # Tenta decodificar o nome se ele estiver em formato de bytes
    try:
        if isinstance(nome, bytes):
            nome = nome.decode('utf-8')
    except UnicodeDecodeError:
        print(f"Erro de decodificação: {nome}")
        return False

    # Normaliza o nome para a forma NFKC
    nome = unicodedata.normalize('NFKC', nome)
    # Expressão regular para validar nomes (apenas letras e espaços)
    nome_valido_regex = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$")
    # Retorna True se o nome corresponder ao padrão, caso contrário, False
    return bool(nome_valido_regex.match(nome))

# Dicionário para corrigir nomes com caracteres especiais
correcoes_nomes = {
    "Cristiana da Conceiç?o": "Cristiana da Conceição",
    "Edivânia Conceiç?o Dos Santos": "Edivânia Conceição Dos Santos",
    "Nívea de Lucena Brand?o": "Nívea de Lucena Brandão",
    "Valdinete Maria da Conceiç?o Silva": "Valdinete Maria da Conceição Silva",
    "CONCEIÇ?O ELITA SILVA PINTO": "CONCEIÇÃO ELITA SILVA PINTO",
    "Andreia Rom?o da Silva": "Andreia Romão da Silva",
    "Adriana da Conceiç?o Cruz": "Adriana da Conceição Cruz",
    "Ver?nica da Silva": "Verônica da Silva",
    "Claudiceia da Conceiç?o Ramos": "Claudiceia da Conceição Ramos",
    "Solange Guimar?es Dos Santos": "Solange Guimarães Dos Santos",
    "Maria Elenilda Fraz?o Bezerra": "Maria Elenilda Frazão Bezerra"
}

def validar_formatar_telefone(telefone):
    # Verifica se o telefone é nulo ou uma string vazia
    if pd.isnull(telefone) or str(telefone).strip() == '':
        return None  # Retorna None se o telefone não for válido
    
    # Divide a string do telefone em números individuais
    numeros = re.split(r'[;, ]+', str(telefone))
    
    # Itera sobre cada número extraído
    for numero in numeros:
        # Remove todos os caracteres não numéricos
        numero = re.sub(r'\D', '', numero)
        # Adiciona o DDI '55' se o número não começar com ele
        if not numero.startswith('55'):
            numero = '55' + numero
        
        # Remove o DDI para validação
        numero_sem_ddi = numero[2:]
        
        # Valida o número de telefone baseado no DDD e na quantidade de dígitos
        if re.fullmatch(r'(82|71|73|74|75|77|85|88|98|99|83|81|87|86|89|84|79)\d{9}', numero_sem_ddi):
            # Verifica se não há mais de três dígitos iguais consecutivos
            # e se o terceiro dígito é 7, 8 ou 9
            if not re.search(r'(\d)\1{3,}', numero_sem_ddi) and numero_sem_ddi[2] in ['7', '8', '9']:
                return numero  # Retorna o número formatado se válido
                
    return None  # Retorna None se nenhum número for válido

def remover_ddi(whatsapp):
    # Verifica se o número do WhatsApp é nulo
    if pd.isnull(whatsapp):
        return None  # Retorna None se o número for nulo

    whatsapp = str(whatsapp)  # Converte o número para string
    # Verifica se o número começa com o DDI '55'
    if whatsapp.startswith('55'):
        return whatsapp[2:]  # Remove o DDI e retorna o número sem ele
    
    return whatsapp  # Retorna o número original se não tiver DDI

def validar_cns(cns):
    # Verifica se o CNS é nulo
    if pd.isnull(cns):
        return None  # Retorna None se o CNS for nulo

    cns = str(cns)  # Converte o CNS para string
    # Remove todos os caracteres não numéricos do CNS
    cns = re.sub(r'\D', '', cns)

    # Verifica se o CNS possui exatamente 15 dígitos
    if not re.fullmatch(r'\d{15}', cns):
        return None  # Retorna None se o CNS não for válido
    
    return cns  # Retorna o CNS validado

def verificar_cpf(cpf):
    # Remove todos os caracteres não numéricos do CPF
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se o CPF tem menos de 11 dígitos e preenche com um zero à esquerda se necessário
    if len(cpf) < 11:
        cpf = cpf.zfill(11)
    
    # Verifica se o CPF tem exatamente 11 dígitos e não é uma sequência repetida
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return None

    # Função para calcular o dígito verificador
    def calcular_digito(cpf_part, peso_inicial):
        soma = sum(int(cpf_part[i]) * (peso_inicial - i) for i in range(len(cpf_part)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)
    
    # Calcula os dois dígitos verificadores
    primeiro_digito = calcular_digito(cpf[:9], 10)
    segundo_digito = calcular_digito(cpf[:9] + primeiro_digito, 11)

    # Verifica se os dígitos calculados são iguais aos do CPF
    if cpf[-2:] == primeiro_digito + segundo_digito:
        return cpf  # Retorna o CPF limpo se for válido
    
    return None  # Retorna None se o CPF for inválido
def processar_dataframe(df, arquivo, aba):
    try:
        print(f"📄 Processando: {arquivo} - Aba: {aba}")

        # Normaliza os nomes das colunas para minúsculas
        df.columns = df.columns.str.lower()

        # Identifica as colunas relevantes no DataFrame
        col_titulo = 'título'
        col_cpf = 'cpf' if 'cpf' in df.columns else None
        col_CNS = 'cns' if 'cns' in df.columns else None
        col_telefone = 'telefone' if 'telefone' in df.columns else None

        # Verifica se as colunas necessárias estão presentes
        if col_cpf is None or col_CNS is None or col_telefone is None:
            print(f"⚠️ Uma ou mais colunas necessárias não foram encontradas na aba {aba} do arquivo {arquivo}.")
            return

        # Aplica correções nos nomes com caracteres especiais
        df[col_titulo] = df[col_titulo].replace(correcoes_nomes)

        # Valida e normaliza os nomes dos pacientes
        df['nome paciente'] = df[col_titulo].apply(lambda nome: verificar_nome_valido(unicodedata.normalize('NFKC', nome)))

        # Valida o CPF
        df['cpf_validado'] = df[col_cpf].apply(verificar_cpf)
        # Cria uma coluna booleana para indicar validade do CPF
        df['cpf_valido'] = df['cpf_validado'].notnull()

        # Valida o CNS (Cartão Nacional de Saúde)
        df['cns'] = df[col_CNS].apply(validar_cns)

        # Valida e formata o número do telefone
        df['telefone_formatado'] = df[col_telefone].apply(validar_formatar_telefone)

        # Remove o DDI do número do telefone formatado
        df['telefone_sem_ddi'] = df['telefone_formatado'].apply(remover_ddi)

        # Define as colunas finais a serem salvas
        colunas_final = [col_titulo, 'cpf_validado', 'cns', 'telefone_formatado', 'telefone_sem_ddi']

        # Filtra os registros válidos
        df_validos = df[df['cpf_valido'] & df['cns'].notnull() & df['telefone_formatado'].notnull()][colunas_final].copy()
        df_validos.columns = ['Título', 'CPF Válido', 'CNS', 'Telefone Formatado', 'Telefone Sem DDI']

        # Armazena CPFs válidos em uma lista
        cpfs_validos = df_validos['CPF Válido'].tolist()

        # Filtra os registros inválidos
        df_invalidos = df[~df['cpf_valido'] | df['cns'].isnull() | df['telefone_formatado'].isnull()][colunas_final].copy()
        df_invalidos.columns = df_validos.columns

        # Armazena CPFs inválidos em uma lista
        cpfs_invalidos = df_invalidos['CPF Válido'].tolist()

        # Define o nome base do arquivo para salvar os resultados
        nome_base = arquivo.replace('.xlsx', '').replace('.csv', '')
        output_file_validos = f"{nome_base}_{aba}_validos.csv"
        df_validos.to_csv(output_file_validos, index=False, sep=';')

        print(f"✅ Arquivo salvo (válidos):\n - {output_file_validos}")

        if not df_invalidos.empty:
            output_file_invalidos = f"{nome_base}_{aba}_invalidos.csv"
            df_invalidos.to_csv(output_file_invalidos, index=False, sep=';')
            print(f"⚠️ Arquivo salvo (inválidos):\n - {output_file_invalidos}")
        else:
            print("✅ Nenhum registro inválido encontrado.")

        # Retorna listas de CPFs válidos e inválidos
        return cpfs_validos, cpfs_invalidos

    except Exception as e:
        print(f"❌ Erro ao processar aba {aba} do arquivo {arquivo}: {e}")
        return [], []

def processar_arquivo(arquivo):
    try:
        # Obtém a extensão do arquivo e converte para minúsculas
        ext = os.path.splitext(arquivo)[1].lower()

        if ext == '.csv':
            # Lê o arquivo CSV em um DataFrame, ignorando linhas problemáticas e definindo o tipo como string
            df = pd.read_csv(arquivo, encoding='utf-8', delimiter=';', on_bad_lines='skip', dtype=str)
            processar_dataframe(df, arquivo, 'especialidade')
        
        elif ext == '.xlsx':
            # Lê todas as planilhas do arquivo Excel em um dicionário de DataFrames
            sheets = pd.read_excel(arquivo, sheet_name=None, dtype=str)
            # Itera sobre cada aba e processa o DataFrame correspondente
            for aba, df in sheets.items():
                processar_dataframe(df, arquivo, aba)
        
        else:
            print(f"❌ Extensão não suportada: {ext}")
    
    except Exception as e:
        print(f"❌ Erro ao processar o arquivo {arquivo}: {e}")

# Busca todos os arquivos CSV e XLSX no diretório atual
arquivos = glob.glob("*.csv") + glob.glob("*.xlsx")

# Itera sobre cada arquivo encontrado e chama a função para processá-lo
for arquivo in arquivos:
    processar_arquivo(arquivo)