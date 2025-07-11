import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pyotp
import requests
from config import load_env_var, load_bool_env_var

# Configuração do TOTP
# IMPORTANTE: Configure suas chaves em um arquivo .env ou variáveis de ambiente
# Nunca commite chaves reais no repositório
SECRET_KEY = load_env_var("TOTP_SECRET_KEY", "YOUR_TOTP_SECRET_KEY_HERE")
totp = pyotp.TOTP(SECRET_KEY)

# Configuração de debug
DEBUG_MODE = load_bool_env_var("DEBUG_MODE", False)

# IMPORTANTE: Configure seu webhook do Discord em um arquivo .env
# Nunca commite URLs de webhook reais no repositório  
DISCORD_WEBHOOK_URL = load_env_var("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_URL_HERE")

class Financeiro(tk.Frame):
    """
    Tela de gerenciamento financeiro com autenticação TOTP e layout similar ao menu principal.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.last_auth_time = None

        self.configure(padx=30, pady=30)
        self.show_auth_screen()

    def show_auth_screen(self):
        """
        Tela de autenticação TOTP.
        """
        for widget in self.winfo_children():
            widget.destroy()

        label = ttk.Label(self, text="Digite o código TOTP para acessar o Financeiro:", font=("Helvetica", 14))
        label.pack(pady=10)
        
        # Aviso de modo debug
        if DEBUG_MODE:
            debug_label = ttk.Label(
                self, 
                text="⚠️ MODO DEBUG ATIVO\nDigite 'debug', 'bypass' ou 'dev' para pular autenticação", 
                font=("Helvetica", 10),
                foreground="orange"
            )
            debug_label.pack(pady=5)

        self.totp_entry = ttk.Entry(self, font=("Helvetica", 14))
        self.totp_entry.pack(pady=10)

        self.totp_entry.bind("<Return>", lambda event: self.authenticate())
        auth_button = ttk.Button(self, text="Autenticar", command=self.authenticate)
        auth_button.pack(pady=10)

    def authenticate(self):
        """
        Valida o código TOTP e concede acesso temporário.
        No modo debug, permite bypass da autenticação.
        """
        code = self.totp_entry.get()
        try:
            # Bypass para modo debug
            if DEBUG_MODE and code.lower() in ['debug', 'bypass', 'dev']:
                print("⚠️  AVISO: Bypass de autenticação ativado (modo debug)")
                self.last_auth_time = datetime.now()
                self.send_discord_notification(f"{code} (DEBUG MODE)")
                self.show_finance_menu()
                return
                
            # Autenticação normal
            if totp.verify(code):
                self.last_auth_time = datetime.now()
                self.send_discord_notification(code)
                self.show_finance_menu()
            else:
                messagebox.showerror("Erro de Autenticação", "Código TOTP inválido. Por favor, tente novamente.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar o código TOTP: {e}")

    def send_discord_notification(self, otp_code):
        """
        Envia uma mensagem ao webhook do Discord informando que o painel financeiro foi acessado.
        """
        try:
            data = {
                "content": f"🔒 O painel financeiro foi acessado com sucesso.\nCódigo OTP utilizado: `{otp_code}`\nHorário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            requests.post(DISCORD_WEBHOOK_URL, json=data)
        except Exception as e:
            print(f"Erro ao enviar mensagem ao Discord: {e}")

    def show_finance_menu(self):
        """
        Exibe o menu principal do módulo financeiro com layout similar ao menu principal.
        """
        for widget in self.winfo_children():
            widget.destroy()

        # Estilos
        style = ttk.Style()
        style.configure('FinanceTitle.TLabel', font=('Helvetica', 20, 'bold'))
        style.configure('FinanceButton.TButton', font=('Helvetica', 14), padding=(10, 10))

        # Título
        title = ttk.Label(self, text="Central Financeira", style='FinanceTitle.TLabel')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 40))

        # Frame para botões principais
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        # Configurar grid interno para expansão uniforme
        btn_frame.columnconfigure((0, 1), weight=1, uniform='col')
        btn_frame.rowconfigure((0, 1), weight=1, uniform='row')

        # Botões principais
        btn_cobranca = ttk.Button(
            btn_frame,
            text="Cobrança",
            style='FinanceButton.TButton',
            command=lambda: self.controller.show_frame("Cobranca")
        )
        btn_atrelamento = ttk.Button(
            btn_frame,
            text="Atrelamento de Contratos",
            style='FinanceButton.TButton',
            command=lambda: self.controller.show_frame("AtrelamentoContratos")
        )
        btn_pedidos_pagos = ttk.Button(
            btn_frame,
            text="Pedidos Pagos",
            style='FinanceButton.TButton',
            command=lambda: self.controller.show_frame("PedidosPagos")
        )

        # Posicionamento em grade
        btn_cobranca.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        btn_atrelamento.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        btn_pedidos_pagos.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # Botão de saída centralizado na parte inferior
        btn_voltar = ttk.Button(
            self,
            text="Voltar",
            style='FinanceButton.TButton',
            command=lambda: self.controller.show_frame("MenuPrincipal")
        )
        btn_voltar.grid(row=2, column=0, columnspan=2, pady=(40, 0), ipadx=10, ipady=5)

        # Responsividade do frame principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)