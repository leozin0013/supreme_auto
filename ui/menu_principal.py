import tkinter as tk
from tkinter import ttk

class MenuPrincipal(tk.Frame):
    """
    Tela inicial do sistema com layout aprimorado para melhor aproveitamento de espaço.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=30, pady=30)

        # Estilos
        style = ttk.Style()
        style.configure('MenuTitle.TLabel', font=('Helvetica', 20, 'bold'))
        style.configure('MenuButton.TButton', font=('Helvetica', 14), padding=(10, 10))

        # Título
        title = ttk.Label(self, text="Supreme Automações Residenciais", style='MenuTitle.TLabel')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 40))

        # Frame para botões principais
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # Configurar grid interno para expansão uniforme
        btn_frame.columnconfigure((0, 1), weight=1, uniform='col')
        btn_frame.rowconfigure((0, 1, 2), weight=1, uniform='row')

        # Botões principais
        btn_cliente = ttk.Button(
            btn_frame,
            text="Cadastro de Clientes",
            style='MenuButton.TButton',
            command=lambda: controller.show_frame("CadastroClientes")
        )
        btn_categoria = ttk.Button(
            btn_frame,
            text="Cadastro de Categorias",
            style='MenuButton.TButton',
            command=lambda: controller.show_frame("CadastroCategorias")
        )
        btn_produto = ttk.Button(
            btn_frame,
            text="Cadastro de Produtos",
            style='MenuButton.TButton',
            command=lambda: controller.show_frame("CadastroProdutos")
        )
        btn_pedido = ttk.Button(
            btn_frame,
            text="Criação de Pedidos",
            style='MenuButton.TButton',
            command=lambda: controller.show_frame("CriacaoPedidos")
        )
        btn_financeiro = ttk.Button(
            btn_frame,
            text="Financeiro",
            style='MenuButton.TButton',
            command=lambda: controller.show_frame("Financeiro")
        )

        # Posicionamento em grade
        btn_cliente.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        btn_categoria.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        btn_produto.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        btn_pedido.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        btn_financeiro.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Botão de saída centralizado na parte inferior
        btn_voltar = ttk.Button(
            self,
            text="Sair",
            style='MenuButton.TButton',
            command=controller.on_closing
        )
        btn_voltar.grid(row=3, column=0, columnspan=2, pady=(40, 0), ipadx=10, ipady=5)

        # Responsividade do frame principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)