import sqlite3

def create_connection():
    conn = sqlite3.connect("database/scraper_data.db")
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraper_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_concorrente TEXT,
            titulo_concorrente TEXT,
            preco_sem_desconto_concorrente REAL,
            preco_com_desconto_concorrente REAL,
            preco_sem_desconto_nosso REAL,
            preco_com_desconto_nosso REAL,
            nota_avaliacao REAL,
            quantidade_venda INTEGER,
            quantidade_estoque INTEGER,
            nome_portal TEXT,
            prazo_entrega_concorrente TEXT,
            valor_frete_concorrente REAL,
            prazo_entrega_nosso TEXT,
            valor_frete_nosso REAL,
            data_hora
        );
    """)
    conn.commit()
    conn.close()
