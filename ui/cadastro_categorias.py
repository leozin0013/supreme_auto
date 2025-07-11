import tkinter as tk
from tkinter import ttk, messagebox

class CadastroCategorias(tk.Frame):
    """
    Tela de cadastro, edição e exclusão de categorias de produtos com layout organizado.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_id = None
        self.configure(padx=20, pady=20)

        # Título
        titulo = tk.Label(self, text="Cadastro de Categorias", font=("Helvetica", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=4, pady=(0, 15))

        # Formulário de Dados
        form = ttk.LabelFrame(self, text="Dados da Categoria")
        form.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 15))
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Nome da Categoria:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome = tk.Entry(form)
        self.entry_nome.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # Botões de Ação
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(0, 15))
        btn_novo = ttk.Button(btn_frame, text="Novo", command=self.clear_form)
        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self.save_category)
        btn_excluir = ttk.Button(btn_frame, text="Excluir", command=self.delete_category)
        btn_voltar = ttk.Button(btn_frame, text="Voltar", command=lambda: controller.show_frame("MenuPrincipal"))
        btn_novo.grid(row=0, column=0, padx=10)
        btn_salvar.grid(row=0, column=1, padx=10)
        btn_excluir.grid(row=0, column=2, padx=10)
        btn_voltar.grid(row=0, column=3, padx=10)

        # Treeview de Listagem
        cols = ("id", "nome")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center")
        self.tree.grid(row=3, column=0, columnspan=4, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Responsividade
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure((0,1,2,3), weight=1)

        # Carregar dados
        self.reload_data()

    def reload_data(self):
        """
        Recarrega a lista de categorias.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            self.controller.cursor.execute("SELECT id, nome FROM categorias ORDER BY nome")
            for cat in self.controller.cursor.fetchall():
                self.tree.insert('', 'end', values=cat)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar categorias: {e}")

    def clear_form(self):
        """
        Limpa o formulário para novo cadastro.
        """
        self.selected_id = None
        self.entry_nome.delete(0, tk.END)

    def on_select(self, event):
        """
        Ao selecionar categoria, popula o campo de edição.
        """
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            self.selected_id = values[0]
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, values[1])

    def save_category(self):
        """
        Salva ou atualiza a categoria no banco.
        """
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Nome da categoria é obrigatório.")
            return
        try:
            if self.selected_id:
                self.controller.cursor.execute(
                    "UPDATE categorias SET nome=? WHERE id=?",
                    (nome, self.selected_id)
                )
            else:
                self.controller.cursor.execute(
                    "INSERT INTO categorias (nome) VALUES (?)",
                    (nome,)
                )
            self.controller.conn.commit()
            messagebox.showinfo("Sucesso", "Categoria salva com sucesso.")
            self.clear_form()
            self.reload_data()
            # Atualiza produtos
            if hasattr(self.controller.frames.get('CadastroProdutos'), 'reload_data'):
                self.controller.frames['CadastroProdutos'].reload_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar categoria: {e}")

    def delete_category(self):
        """
        Exclui a categoria selecionada.
        """
        if not self.selected_id:
            messagebox.showwarning("Atenção", "Selecione uma categoria para excluir.")
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta categoria? Todos os produtos vinculados perderão a categoria."):
            try:
                self.controller.cursor.execute("DELETE FROM categorias WHERE id=?", (self.selected_id,))
                self.controller.conn.commit()
                messagebox.showinfo("Sucesso", "Categoria excluída com sucesso.")
                self.clear_form()
                self.reload_data()
                if hasattr(self.controller.frames.get('CadastroProdutos'), 'reload_data'):
                    self.controller.frames['CadastroProdutos'].reload_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir categoria: {e}")
