import tkinter as tk
from tkinter import ttk, messagebox

class CadastroClientes(tk.Frame):
    """
    Tela de cadastro, listagem, edição e exclusão de clientes com layout organizado.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_id = None
        self.configure(padx=20, pady=20)

        # Título
        titulo = tk.Label(self, text="Cadastro de Clientes", font=("Helvetica", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=4, pady=(0, 15))

        # Formulário de Dados do Cliente
        form = ttk.LabelFrame(self, text="Dados do Cliente")
        form.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 15))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Linha 1: Nome
        tk.Label(form, text="Nome:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome = tk.Entry(form)
        self.entry_nome.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # Linha 2: CPF e Telefone
        tk.Label(form, text="CPF:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_cpf = tk.Entry(form)
        self.entry_cpf.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form, text="Telefone:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_telefone = tk.Entry(form)
        self.entry_telefone.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

        # Linha 3: Email e Endereço
        tk.Label(form, text="Email:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_email = tk.Entry(form)
        self.entry_email.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        tk.Label(form, text="Endereço:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_adress = tk.Entry(form)
        self.entry_adress.grid(row=2, column=3, sticky="ew", padx=5, pady=5)

        # Botões de Ação
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(0, 15))
        btn_novo = ttk.Button(btn_frame, text="Novo", command=self.clear_form)
        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self.save_client)
        btn_excluir = ttk.Button(btn_frame, text="Excluir", command=self.delete_client)
        btn_voltar = ttk.Button(btn_frame, text="Voltar", command=lambda: controller.show_frame("MenuPrincipal"))
        btn_novo.grid(row=0, column=0, padx=10)
        btn_salvar.grid(row=0, column=1, padx=10)
        btn_excluir.grid(row=0, column=2, padx=10)
        btn_voltar.grid(row=0, column=3, padx=10)

        self.bind("<Escape>", lambda e: controller.show_frame("MenuPrincipal"))

        # Treeview de Listagem
        cols = ("ID", "Nome", "CPF", "Telefone", "E-mail", "Endereço")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center")
        self.tree.grid(row=3, column=0, columnspan=5, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Responsividade
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure((0,1,2,3), weight=1)

        self.tree.column("ID", width=40, minwidth=40, stretch=True)
        self.tree.column("CPF", width=90, minwidth=90, stretch=True)
        self.tree.column("Telefone", width=90, minwidth=90, stretch=True)

        # Carregar dados
        self.reload_data()

    def reload_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            self.controller.cursor.execute(
                "SELECT id, nome, cpf, telefone, email, endereco FROM clientes ORDER BY nome"
            )
            for cli in self.controller.cursor.fetchall():
                self.tree.insert('', 'end', values=cli)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar clientes: {e}")

    def clear_form(self):
        self.selected_id = None
        self.entry_nome.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_adress.delete(0, tk.END)

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            self.selected_id = values[0]
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, values[1])
            self.entry_cpf.delete(0, tk.END)
            self.entry_cpf.insert(0, values[2])
            self.entry_telefone.delete(0, tk.END)
            self.entry_telefone.insert(0, values[3])
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, values[4])
            self.entry_adress.delete(0, tk.END)
            self.entry_adress.insert(0, values[5])

    def save_client(self):
        nome = self.entry_nome.get().strip()
        cpf = self.entry_cpf.get().strip()
        telefone = self.entry_telefone.get().strip()
        email = self.entry_email.get().strip()
        adress = self.entry_adress.get().strip()
        if not nome or not cpf:
            messagebox.showwarning("Atenção", "Nome e CPF são obrigatórios.")
            return
        try:
            if self.selected_id:
                self.controller.cursor.execute(
                    "UPDATE clientes SET nome=?, cpf=?, telefone=?, email=?, endereco=? WHERE id=?",
                    (nome, cpf, telefone, email, adress, self.selected_id)
                )
            else:
                self.controller.cursor.execute(
                    "INSERT INTO clientes (nome, cpf, telefone, email, endereco) VALUES (?, ?, ?, ?, ?)",
                    (nome, cpf, telefone, email, adress)
                )
            self.controller.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente salvo com sucesso.")
            self.clear_form()
            self.reload_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar cliente: {e}")

    def delete_client(self):
        if not self.selected_id:
            messagebox.showwarning("Atenção", "Selecione um cliente para excluir.")
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este cliente?"):
            try:
                self.controller.cursor.execute(
                    "DELETE FROM clientes WHERE id=?", (self.selected_id,)
                )
                self.controller.conn.commit()
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso.")
                self.clear_form()
                self.reload_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir cliente: {e}")
