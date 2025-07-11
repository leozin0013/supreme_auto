import os
import tkinter as tk
from tkinter import ttk, messagebox
from apiMP import create_payment
import qrcode
from PIL import Image, ImageTk

class Cobranca(tk.Frame):
    """
    Tela de cobrança com geração de links de pagamento e QR Codes.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.conn = controller.conn
        self.cursor = self.conn.cursor()

        self.configure(padx=20, pady=20)
        self.show_billing()

    def show_billing(self):
        """
        Exibe pedidos pendentes de pagamento e permite gerar links de pagamento.
        """
        for widget in self.winfo_children():
            widget.destroy()

        label = ttk.Label(self, text="Cobrança", font=("Helvetica", 16, "bold"))
        label.pack(pady=10)

        # TreeView para pedidos sem link de pagamento
        self.tree_pending = ttk.Treeview(self, columns=("id", "cliente", "valor_total"), show="headings")
        self.tree_pending.heading("id", text="Pedido")
        self.tree_pending.heading("cliente", text="Cliente")
        self.tree_pending.heading("valor_total", text="Valor Total")
        self.tree_pending.pack(pady=10, fill="both", expand=True)

        # TreeView para pedidos com link de pagamento
        self.tree_with_link = ttk.Treeview(self, columns=("id", "cliente", "valor_total", "link", "status"), show="headings")
        self.tree_with_link.heading("id", text="Pedido")
        self.tree_with_link.heading("cliente", text="Cliente")
        self.tree_with_link.heading("valor_total", text="Valor Total")
        self.tree_with_link.heading("link", text="Link de Pagamento")
        self.tree_with_link.heading("status", text="Status do Pagamento")
        self.tree_with_link.pack(pady=10, fill="both", expand=True)

        self.tree_with_link.column("id", width=40, anchor="center")
        self.tree_with_link.column("valor_total", width=50, anchor="center")
        self.tree_with_link.column("status", width=100, anchor="center")

        # Botões de ação
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        generate_button = ttk.Button(button_frame, text="Gerar Link de Pagamento", command=self.generate_payment_link)
        generate_button.grid(row=0, column=0, padx=5)

        copy_link_button = ttk.Button(button_frame, text="Copiar Link de Pagamento", command=self.copy_payment_link)
        copy_link_button.grid(row=0, column=1, padx=5)

        copy_link_button = ttk.Button(button_frame, text="Gerar QR Code", command=self.generate_qr_code)
        copy_link_button.grid(row=0, column=2, padx=5)

        btn_voltar = ttk.Button(self, text="Voltar", command=lambda: self.controller.show_frame("Financeiro"))
        btn_voltar.pack(pady=10)

        self.load_billing_data()

    def load_billing_data(self):
        """
        Carrega os pedidos pendentes de pagamento e os pedidos com link de pagamento.
        """
        self.tree_pending.delete(*self.tree_pending.get_children())
        self.tree_with_link.delete(*self.tree_with_link.get_children())

        # Pedidos sem link de pagamento
        self.cursor.execute("""
            SELECT p.id, COALESCE(c.nome, 'Desconhecido') AS cliente_nome, p.valor_total
            FROM pedidos p
            LEFT JOIN pagamentos pg ON p.id = pg.external_reference
            LEFT JOIN clientes c ON p.cliente_id = c.id
            WHERE pg.external_reference IS NULL
        """)
        for row in self.cursor.fetchall():
            cliente_nome = row[1]
            self.tree_pending.insert("", "end", values=(row[0], cliente_nome, f"R$ {row[2]:.2f}"))

        # Pedidos com link de pagamento (removendo duplicatas)
        self.cursor.execute("""
            SELECT DISTINCT p.id, COALESCE(c.nome, 'Desconhecido') AS cliente_nome, p.valor_total, pg.preference_id, pg.status
            FROM pedidos p
            JOIN pagamentos pg ON p.external_reference = pg.external_reference
            LEFT JOIN clientes c ON p.cliente_id = c.id
        """)
        for row in self.cursor.fetchall():
            cliente_nome = row[1]
            self.tree_with_link.insert("", "end", values=(row[0], cliente_nome, f"R$ {row[2]:.2f}", row[3], row[4]))

    def generate_payment_link(self):
        """
        Gera o link de pagamento ou QR code para o pedido selecionado.
        """
        selected_item = self.tree_pending.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um pedido para gerar o link de pagamento.")
            return

        pedido_id = self.tree_pending.item(selected_item, "values")[0]
        self.cursor.execute("SELECT external_reference FROM pedidos WHERE id = ?", (pedido_id,))
        result = self.cursor.fetchone()
        if not result:
            messagebox.showerror("Erro", "Pedido não encontrado.")
            return
        external_reference = result[0]

        valor_total = float(self.tree_pending.item(selected_item, "values")[2].replace("R$", "").strip())
        titulo = f"Pedido número {pedido_id}"

        try:
            payment_link = create_payment(external_reference, titulo, valor_total)
            self.clipboard_clear()
            self.clipboard_append(payment_link)
            messagebox.showinfo("Sucesso", "Link de pagamento copiado para a área de transferência.")
            self.load_billing_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar link de pagamento: {e}")

    def generate_qr_code(self):
        """
        Gera o QR code para o pedido selecionado e exibe em uma nova janela.
        """
        selected_item = self.tree_with_link.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um pedido para gerar o QR code.")
            return

        pedido_id = self.tree_with_link.item(selected_item, "values")[0]
        self.cursor.execute("SELECT preference_id FROM pagamentos WHERE external_reference = ?", (pedido_id,))
        result = self.cursor.fetchone()

        if not result:
            messagebox.showerror("Erro", "O pedido selecionado não possui um link de pagamento.")
            return

        preference_id = result[0]
        payment_link = f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id={preference_id}"

        # Criar o diretório se não existir
        qr_directory = os.path.join("assets", "temp", "QRs")
        os.makedirs(qr_directory, exist_ok=True)

        qr_filename = os.path.join(qr_directory, f"qrcode_pedido_{pedido_id}.png")

        qr = qrcode.make(payment_link)
        qr.save(qr_filename)

        # Exibir o QR Code em uma nova janela
        qr_window = tk.Toplevel(self)
        qr_window.title(f"QR Code - Pedido {pedido_id}")
        qr_window.geometry("320x320")

        img = Image.open(qr_filename)
        img = img.resize((250, 250), Image.Resampling.LANCZOS)  # Substituído por Image.Resampling.LANCZOS
        qr_image = ImageTk.PhotoImage(img)

        label = tk.Label(qr_window, image=qr_image)
        label.image = qr_image  # Manter referência para evitar garbage collection
        label.pack(pady=10)

        close_button = ttk.Button(qr_window, text="Fechar", command=lambda: self.close_qr_window(qr_window, qr_filename))
        close_button.pack(pady=10)

    def close_qr_window(self, window, qr_filename):
        """
        Fecha a janela do QR Code e exclui o arquivo gerado.
        """
        window.destroy()
        if os.path.exists(qr_filename):
            os.remove(qr_filename)

    def copy_payment_link(self):
        """
        Copia o link de pagamento completo do pedido selecionado na TreeView inferior.
        """
        selected_item = self.tree_with_link.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um pedido para copiar o link de pagamento.")
            return

        pedido_id = self.tree_with_link.item(selected_item, "values")[0]
        self.cursor.execute("SELECT preference_id FROM pagamentos WHERE external_reference = ?", (pedido_id,))
        result = self.cursor.fetchone()

        if not result:
            messagebox.showerror("Erro", "O pedido selecionado não possui um link de pagamento.")
            return

        preference_id = result[0]
        payment_link = f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id={preference_id}"

        self.clipboard_clear()
        self.clipboard_append(payment_link)
        messagebox.showinfo("Sucesso", "Link de pagamento copiado para a área de transferência.")

    def reload_data(self):
        """
        Recarrega os dados das TreeViews de pedidos pendentes e com link de pagamento.
        """
        self.load_billing_data()