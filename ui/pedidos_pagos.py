import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class PedidosPagos(tk.Frame):
    """
    Tela para exibir pagamentos aprovados e finalizados.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.conn = controller.conn
        self.cursor = self.conn.cursor()

        self.configure(padx=20, pady=20)

        label = ttk.Label(self, text="Pedidos Pagos", font=("Helvetica", 16, "bold"))
        label.pack(pady=10)

        # TreeView para pagamentos aprovados
        self.tree_approved = ttk.Treeview(self, columns=("id", "cliente", "valor_total"), show="headings")
        self.tree_approved.heading("id", text="Pedido")
        self.tree_approved.heading("cliente", text="Cliente")
        self.tree_approved.heading("valor_total", text="Valor Total")
        self.tree_approved.pack(pady=10, fill="both", expand=True)

        # TreeView para pagamentos finalizados
        self.tree_finalized = ttk.Treeview(self, columns=("id", "cliente", "valor_total"), show="headings")
        self.tree_finalized.heading("id", text="Pedido")
        self.tree_finalized.heading("cliente", text="Cliente")
        self.tree_finalized.heading("valor_total", text="Valor Total")
        self.tree_finalized.pack(pady=10, fill="both", expand=True)

        # Botões de ação
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        finalize_button = ttk.Button(button_frame, text="Marcar como Finalizado", command=self.finalize_payment)
        finalize_button.grid(row=0, column=0, padx=5)

        download_button = ttk.Button(button_frame, text="Baixar Comprovante", command=self.download_receipt)
        download_button.grid(row=0, column=1, padx=5)

        btn_voltar = ttk.Button(self, text="Voltar", command=lambda: controller.show_frame("Financeiro"))
        btn_voltar.pack(pady=10)

        self.load_payments()

    def load_payments(self):
        """
        Carrega os pagamentos aprovados e finalizados.
        """
        self.tree_approved.delete(*self.tree_approved.get_children())
        self.tree_finalized.delete(*self.tree_finalized.get_children())

        # Pagamentos aprovados
        self.cursor.execute("""
            SELECT pg.external_reference, COALESCE(c.nome, 'Desconhecido') AS cliente_nome, pg.valor
            FROM pagamentos pg
            LEFT JOIN pedidos p ON pg.external_reference = p.id
            LEFT JOIN clientes c ON p.cliente_id = c.id
            WHERE pg.status = 'approved'
        """)
        for row in self.cursor.fetchall():
            self.tree_approved.insert("", "end", values=(row[0], row[1], f"R$ {row[2]:.2f}"))

        # Pagamentos finalizados
        self.cursor.execute("""
            SELECT pg.external_reference, COALESCE(c.nome, 'Desconhecido') AS cliente_nome, pg.valor
            FROM pagamentos pg
            LEFT JOIN pedidos p ON pg.external_reference = p.id
            LEFT JOIN clientes c ON p.cliente_id = c.id
            WHERE pg.status = 'Finalizado'
        """)
        for row in self.cursor.fetchall():
            self.tree_finalized.insert("", "end", values=(row[0], row[1], f"R$ {row[2]:.2f}"))

    def finalize_payment(self):
        """
        Marca o pagamento selecionado na TreeView superior como finalizado.
        """
        selected_item = self.tree_approved.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um pagamento para finalizar.")
            return

        payment_id = self.tree_approved.item(selected_item, "values")[1]
        self.cursor.execute("UPDATE pagamentos SET status = 'Finalizado' WHERE id = ?", (payment_id,))
        self.conn.commit()
        messagebox.showinfo("Sucesso", f"Pagamento #{payment_id} marcado como finalizado.")
        self.load_payments()

    def download_receipt(self):
        """
        Faz o download do comprovante do pagamento selecionado.
        """
        selected_item = self.tree_approved.selection() or self.tree_finalized.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um pagamento para baixar o comprovante.")
            return

        # Corrigir para buscar pelo external_reference
        payment_id = self.tree_approved.item(selected_item, "values")[0] if self.tree_approved.selection() else self.tree_finalized.item(selected_item, "values")[0]
        self.cursor.execute("SELECT comprovante_pdf FROM pagamentos WHERE external_reference = ?", (payment_id,))
        result = self.cursor.fetchone()

        if not result or not result[0]:
            messagebox.showerror("Erro", "Comprovante não encontrado para o pagamento selecionado.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Salvar comprovante como",
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            initialfile=f"comprovante_pagamento_{payment_id}.pdf"
        )
        if not file_path:
            return

        try:
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(result[0])

            messagebox.showinfo("Sucesso", f"Comprovante do pagamento #{payment_id} salvo com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar comprovante: {e}")

    def reload_data(self):
        """
        Recarrega os dados das treeviews de pagamentos aprovados e finalizados.
        """
        self.load_payments()