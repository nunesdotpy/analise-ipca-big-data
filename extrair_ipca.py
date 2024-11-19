import csv
import sqlite3

# Função para criar o banco de dados e a tabela
def create_db():
    conn = sqlite3.connect('inflacao.db')
    cursor = conn.cursor()
    
    # Criação da tabela para armazenar os dados do IPCA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ipca (
            mes TEXT,
            ano INTEGER,
            indice REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# Função para converter os índices de porcentagem para formato numérico
def convert_to_float(value):
    # Remove o símbolo '%' e converte para float
    try:
        return float(value.replace(',', '.')[:-1])  # Troca vírgula por ponto e remove '%'
    except ValueError:
        return None  # Para valores inválidos como '--'

# Função para ler o arquivo CSV e inserir os dados no banco de dados
def load_csv_to_db(csv_file):
    conn = sqlite3.connect('inflacao.db')
    cursor = conn.cursor()
    
    # Abrindo o arquivo CSV
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        
        # Lendo os cabeçalhos (meses)
        header = next(reader)
        
        # Processando cada linha do CSV
        for row in reader:
            # O ano está na primeira coluna
            ano = row[0]
            try:
                ano = int(ano)  # Convertendo o ano para inteiro
            except ValueError:
                continue  # Caso o valor não seja válido, ignora essa linha
            
            # Processando os meses, ignorando a última coluna (ano acumulado)
            for i, mes in enumerate(header[:-1]):  # Ignora a última coluna 'Ano'
                indice = row[i + 1]  # Começa da segunda coluna (índices mensais)
                if indice != '--':  # Ignora os valores '--'
                    indice_float = convert_to_float(indice)
                    if indice_float is not None:
                        cursor.execute('''
                            INSERT INTO ipca (mes, ano, indice)
                            VALUES (?, ?, ?)
                        ''', (mes, ano, indice_float))
    
    conn.commit()
    conn.close()

# Função principal
def main():
    create_db()  # Cria o banco de dados e a tabela (se não existir)
    load_csv_to_db('indice.csv')  # Substitua 'indice.csv' pelo caminho do seu arquivo CSV

if __name__ == '__main__':
    main()
