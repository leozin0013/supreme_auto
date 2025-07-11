import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
import time
from apiMP import verificar_pagamentos
import shutil
from config import load_env_var

# Importar módulos de UI
from ui.menu_principal import MenuPrincipal
from ui.cadastro_clientes import CadastroClientes
from ui.cadastro_categorias import CadastroCategorias
from ui.cadastro_produtos import CadastroProdutos
from ui.criacao_pedidos import CriacaoPedidos
from ui.financeiro import Financeiro
from ui.cobranca import Cobranca
from ui.pedidos_pagos import PedidosPagos
from ui.atrelamento_contratos import AtrelamentoContratos
from estoque import get_estoque_from_urls

# Configuração do banco de dados usando variável de ambiente
DB_PATH = load_env_var("DATABASE_PATH", "database.db")

class App(tk.Tk):
    """
    Classe principal da aplicação que gerencia a janela, o banco de dados e a navegação entre telas.
    """
    def __init__(self):
        super().__init__()
        self.title("Sistema de Automação Residencial")
        self.minsize(800, 600)

        # Limpar QR Codes ao iniciar
        self.clear_qr_codes()

        # Conectando ao banco de dados
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_tables()

        # Container para frames
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dicionário de telas
        self.frames = {}
        for F in (MenuPrincipal, CadastroClientes, CadastroCategorias, CadastroProdutos, CriacaoPedidos, Financeiro, Cobranca, PedidosPagos, AtrelamentoContratos):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Exibe tela inicial
        self.show_frame("MenuPrincipal")

        # Atalho para recarregar dados (F5)
        self.bind('<F5>', lambda e: self.reload_all())

        # Inicia a verificação periódica de pagamentos
        self.start_payment_verification()

    def _create_tables(self):
        """
        Cria as tabelas necessárias no banco de dados caso não existam.
        """
        try:
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE NOT NULL,
                    telefone NUMERIC NOT NULL,
                    email TEXT UNIQUE,
                    endereco TEXT
                )
                '''
            )
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL
                )
                '''
            )
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    valor REAL NOT NULL,
                    categoria_id INTEGER,
                    urls TEXT NOT NULL,
                    estoque INTEGER DEFAULT 0,
                    FOREIGN KEY(categoria_id) REFERENCES categorias(id)
                )
                '''
            )
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER,
                    simulacao INTEGER DEFAULT 0,
                    valor_total REAL,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    external_reference TEXT UNIQUE,
                    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
                )
                '''
            )
            self.cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS itens_pedido (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER NOT NULL,
                    produto_id INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL,
                    valor_unitario REAL NOT NULL,
                    FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
                    FOREIGN KEY(produto_id) REFERENCES produtos(id)
                )
                '''
            )
            self.cursor.execute(
                '''CREATE TABLE IF NOT EXISTS pagamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    external_reference TEXT NOT NULL,
                    preference_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    valor REAL NOT NULL,
                    comprovante_pdf BLOB,
                    contrato_pdf BLOB,
                    title TEXT NOT NULL,
                    data_criacao TEXT NOT NULL,
                    executado BOOLEAN NOT NULL
                    )'''
            )
            
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Falha ao criar tabelas: {e}")

    def show_frame(self, page_name):
        """
        Exibe o frame solicitado.
        """
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()
        else:
            messagebox.showerror("Erro", f"Tela {page_name} não encontrada.")

        if page_name == "MenuPrincipal": #fecha o app caso ja esteja no menu principal
            self.bind_all("<Escape>", lambda e: self.on_closing())
        elif page_name == "Cobranca" or page_name == "PedidosPagos" or page_name == "AtrelamentoContratos": #paginas de financiero para retornar para financeiro
            self.bind_all("<Escape>", lambda e: self.show_frame("Financeiro"))
        else: # qualquer outra pagina retorna para o menu principal (vulgo todas do proprio menu principal)
            self.bind_all("<Escape>", lambda e: self.show_frame("MenuPrincipal"))

    def reload_all(self):
        """
        Recarrega listas de clientes, categorias e produtos em todas as telas.
        """
        for frame in self.frames.values():
            if hasattr(frame, 'reload_data'):
                frame.reload_data()

    def on_closing(self):
        """
        Fecha a conexão com o banco antes de sair.
        """
        self.conn.close()
        self.destroy()

    def start_payment_verification(self):
        """
        Executa a função verificar_pagamentos a cada 60 segundos.
        """
        verificar_pagamentos()  # Chama a função de verificação
        self.after(60000, self.start_payment_verification)  # Agenda a próxima execução em 60 segundos

    def clear_qr_codes(self):
        """
        Remove todos os QR Codes da pasta assets/temp/QRs ao iniciar o programa.
        """
        qr_folder = os.path.join(os.path.dirname(__file__), 'assets', 'temp', 'QRs')
        if os.path.exists(qr_folder):
            shutil.rmtree(qr_folder)  # Remove a pasta e todo o conteúdo
            os.makedirs(qr_folder)  # Recria a pasta vazia



    def atualizar_estoque_produtos(self):
        """
        Atualiza o estoque de todos os produtos com base nas URLs (campo 'urls' em formato JSON).
        """
        self.cursor.execute("SELECT id, nome, urls FROM produtos")
        produtos = self.cursor.fetchall()
        for prod in produtos:
            prod_id, nome, urls_json = prod
            if not urls_json:
                print(f"Produto sem URL: {nome} (ID: {prod_id})")
                estoque = 0
            else:
                estoque = get_estoque_from_urls(urls_json)
            self.cursor.execute("UPDATE produtos SET estoque = ? WHERE id = ?", (estoque, prod_id))
        self.conn.commit()

if __name__ == '__main__':
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.atualizar_estoque_produtos()
    app.mainloop()
