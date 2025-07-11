import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class AtrelamentoContratos(tk.Frame):
    """
    Tela para atrelamento e download de contratos em PDF.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.conn = controller.conn
        self.cursor = self.conn.cursor()

        self.configure(padx=20, pady=20)

        # Título
        label = ttk.Label(self, text="Atrelamento de Contratos", font=("Helvetica", 16, "bold"))
        label.pack(pady=10)

        # TreeView para pedidos sem contrato
        self.tree_no_contract = ttk.Treeview(self, columns=("id", "cliente", "valor_total"), show="headings")
        self.tree_no_contract.heading("id", text="ID")
        self.tree_no_contract.heading("cliente", text="Cliente")
        self.tree_no_contract.heading("valor_total", text="Valor Total")
        self.tree_no_contract.pack(pady=10, fill="both", expand=True)

        # TreeView para pedidos com contrato
        self.tree_with_contract = ttk.Treeview(self, columns=("id", "cliente", "valor_total"), show="headings")
        self.tree_with_contract.heading("id", text="ID")
        self.tree_with_contract.heading("cliente", text="Cliente")
        self.tree_with_contract.heading("valor_total", text="Valor Total")
        self.tree_with_contract.pack(pady=10, fill="both", expand=True)

        # Botões de ação
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        attach_button = ttk.Button(button_frame, text="Atrelar Contrato", command=self.attach_contract)
        attach_button.grid(row=0, column=0, padx=5)

        download_button = ttk.Button(button_frame, text="Download Contrato", command=self.download_contract)
        download_button.grid(row=0, column=1, padx=5)

        btn_voltar = ttk.Button(self, text="Voltar", command=lambda: controller.show_frame("Financeiro"))
        btn_voltar.pack(pady=10)

        self.load_data()

    def load_data(self):
        """
        Carrega os pedidos sem contrato e com contrato.
        """
        self.tree_no_contract.delete(*self.tree_no_contract.get_children())
        self.tree_with_contract.delete(*self.tree_with_contract.get_children())

        # Pedidos sem contrato
        self.cursor.execute("""
            SELECT p.id, COALESCE(c.nome, 'Desconhecido') AS cliente_nome, p.valor_total
            FROM pedidos p
            JOIN pagamentos pg ON p.id = pg.external_reference
            LEFT JOIN clientes c ON p.cliente_id = c.id
            WHERE pg.contrato_pdf IS NULL AND pg.status = 'approved'
        """)
        for row in self.cursor.fetchall():
            cliente_nome = row[1]
            self.tree_no_contract.insert("", "end", values=(row[0], cliente_nome, f"R$ {row[2]:.2f}"))

        # Pedidos com contrato
        self.cursor.execute("""
            SELECT p.id, COALESCE(c.nome, 'Desconhecido') AS cliente_nome, p.valor_total
            FROM pedidos p
            JOIN pagamentos pg ON p.id = pg.external_reference
            LEFT JOIN clientes c ON p.cliente_id = c.id
            WHERE pg.contrato_pdf IS NOT NULL
        """)
        for row in self.cursor.fetchall():
            cliente_nome = row[1]
            self.tree_with_contract.insert("", "end", values=(row[0], cliente_nome, f"R$ {row[2]:.2f}"))

    def attach_contract(self):
        """
        Atrela um arquivo PDF ao pedido selecionado na TreeView superior.
        """
        selected_item = self.tree_no_contract.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um pedido para atrelar o contrato.")
            return

        pedido_id = self.tree_no_contract.item(selected_item, "values")[0]
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "rb") as pdf_file:
                pdf_blob = pdf_file.read()

            self.cursor.execute("""
                UPDATE pagamentos
                SET contrato_pdf = ?
                WHERE external_reference = ?
            """, (pdf_blob, pedido_id))
            self.conn.commit()

            messagebox.showinfo("Sucesso", f"Contrato atrelado ao pedido #{pedido_id}.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atrelar contrato: {e}")

    def download_contract(self):
        """
        Realiza o download do contrato do pedido selecionado na TreeView inferior.
        """
        selected_item = self.tree_with_contract.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um pedido para baixar o contrato.")
            return

        pedido_id = self.tree_with_contract.item(selected_item, "values")[0]
        self.cursor.execute("""
            SELECT contrato_pdf FROM pagamentos WHERE external_reference = ?
        """, (pedido_id,))
        result = self.cursor.fetchone()

        if not result or not result[0]:
            messagebox.showerror("Erro", "Contrato não encontrado para o pedido selecionado.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Salvar contrato como",
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            initialfile=f"contrato_pedido_{pedido_id}.pdf"
        )
        if not file_path:
            return

        try:
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(result[0])

            messagebox.showinfo("Sucesso", f"Contrato do pedido #{pedido_id} salvo com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar contrato: {e}")

    def reload_data(self):
        """
        Recarrega os dados das treeviews de pedidos com e sem contrato.
        """
        self.load_data()