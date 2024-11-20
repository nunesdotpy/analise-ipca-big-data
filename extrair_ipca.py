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
            # Ignorar linhas sem ano ou dados inválidos
            if not row[0].strip().isdigit():
                continue  # Pula linhas com dados inválidos no início
            
            # O ano está na primeira coluna
            ano = int(row[0])
            
            # Processando os meses (até a penúltima coluna)
            for i, mes in enumerate(header[1:-1]):  # Ignorar última coluna "Ano"
                indice = row[i + 1]  # Começa da segunda coluna (índices mensais)
                if indice != '--':  # Ignora os valores '--'
                    indice_float = convert_to_float(indice)
                    if indice_float is not None:
                        cursor.execute('''
                            INSERT INTO ipca (mes, ano, indice)
                            VALUES (?, ?, ?)
                        ''', (mes, ano, indice_float))
            
            # Processar o acumulado anual (última coluna)
            acumulado = row[-1]  # Última coluna contém o acumulado anual
            if acumulado != '--':  # Ignora os valores '--'
                acumulado_float = convert_to_float(acumulado)
                if acumulado_float is not None:
                    cursor.execute('''
                        INSERT INTO ipca (mes, ano, indice)
                        VALUES (?, ?, ?)
                    ''', ('Ano', ano, acumulado_float))  # "Ano" usado como identificador especial
    
    conn.commit()
    conn.close()

# Função principal
def main():
    create_db()  # Cria o banco de dados e a tabela (se não existir)
    load_csv_to_db('indice.csv')  # Substitua 'indice.csv' pelo caminho do seu arquivo CSV

if __name__ == '__main__':
    main()
