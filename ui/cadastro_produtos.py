import tkinter as tk
from tkinter import ttk, messagebox
import json

class CadastroProdutos(tk.Frame):
    """
    Tela de cadastro, edição e exclusão de produtos com layout reorganizado.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_id = None
        self.configure(padx=20, pady=20)

        # Título
        titulo = tk.Label(self, text="Cadastro de Produtos", font=("Helvetica", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=4, pady=(0, 15))

        # Formulário de Dados
        form = ttk.LabelFrame(self, text="Dados do Produto")
        form.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 15))
        # Configurar colunas para responsividade
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        # Linha 1: Nome
        tk.Label(form, text="Nome:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome = tk.Entry(form)
        self.entry_nome.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # Linha 2: Descrição
        tk.Label(form, text="Descrição:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        self.entry_descricao = tk.Entry(form)
        self.entry_descricao.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # Linha 3: Valor e Categoria
        tk.Label(form, text="Valor (R$):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_valor = tk.Entry(form)
        self.entry_valor.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form, text="Categoria:").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.combo_categoria = ttk.Combobox(form, state="readonly")
        self.combo_categoria.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Linha 4: Links (URLs)
        tk.Label(form, text="Links (um por linha):").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
        self.text_urls = tk.Text(form, height=3, width=40)
        self.text_urls.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # Botões de Ação
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=(0, 15))
        btn_novo = ttk.Button(btn_frame, text="Novo", command=self.clear_form)
        btn_salvar = ttk.Button(btn_frame, text="Salvar", command=self.save_product)
        btn_excluir = ttk.Button(btn_frame, text="Excluir", command=self.delete_product)
        btn_voltar = ttk.Button(btn_frame, text="Voltar", command=lambda: controller.show_frame("MenuPrincipal"))
        btn_novo.grid(row=0, column=0, padx=10)
        btn_salvar.grid(row=0, column=1, padx=10)
        btn_excluir.grid(row=0, column=2, padx=10)
        btn_voltar.grid(row=0, column=3, padx=10)

        # Treeview de Listagem
        cols = ("ID", "Nome", "Descrição", "Valor", "Categoria", "URLs", "Estoque")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.grid(row=3, column=0, columnspan=4, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Configurar grid para responsividade
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.tree.column("ID", width=40, minwidth=40, stretch=True)
        self.tree.column("Valor", width=70, minwidth=70, stretch=True)
        self.tree.column("URLs", width=60, minwidth=60, stretch=True)
        self.tree.column("Estoque", width=70, minwidth=70, stretch=True)  # Nova coluna para estoque

        # Carregar dados
        self.reload_data()

    def reload_data(self):
        # Carregar produtos
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            self.controller.cursor.execute(
                "SELECT id, nome, descricao, valor, (SELECT nome FROM categorias WHERE id=produtos.categoria_id), urls, estoque FROM produtos ORDER BY nome"
            )
            for prod in self.controller.cursor.fetchall():
                # prod[5] = urls (JSON string), prod[6] = estoque
                try:
                    urls_list = json.loads(prod[5]) if prod[5] else []
                    urls_count = len(urls_list)
                except Exception:
                    urls_count = 0
                estoque = prod[6] if prod[6] is not None else 0
                self.tree.insert(
                    '', 'end',
                    values=(prod[0], prod[1], prod[2], f"R$ {prod[3]:.2f}", prod[4] or '', urls_count, estoque)
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos: {e}")

        # Carregar categorias no combobox
        try:
            self.controller.cursor.execute("SELECT nome FROM categorias ORDER BY nome")
            categorias = [cat[0] for cat in self.controller.cursor.fetchall()]
            self.combo_categoria['values'] = categorias
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar categorias: {e}")

        self.clear_form()

    def clear_form(self):
        self.selected_id = None
        self.entry_nome.delete(0, tk.END)
        self.entry_descricao.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)
        self.combo_categoria.set('')
        self.text_urls.delete('1.0', tk.END)

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            self.selected_id = values[0]
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, values[1])
            self.entry_descricao.delete(0, tk.END)
            self.entry_descricao.insert(0, values[2])
            self.entry_valor.delete(0, tk.END)
            # Remove o prefixo "R$ " antes de inserir
            self.entry_valor.insert(0, values[3].replace('R$ ', ''))
            self.combo_categoria.set(values[4])
            # Carregar URLs do produto selecionado
            try:
                self.controller.cursor.execute("SELECT urls FROM produtos WHERE id=?", (self.selected_id,))
                result = self.controller.cursor.fetchone()
                if result and result[0]:
                    urls_list = json.loads(result[0])
                    self.text_urls.delete('1.0', tk.END)
                    self.text_urls.insert('1.0', '\n'.join(urls_list))
                else:
                    self.text_urls.delete('1.0', tk.END)
            except Exception:
                self.text_urls.delete('1.0', tk.END)

    def save_product(self):
        nome = self.entry_nome.get().strip()
        descricao = self.entry_descricao.get().strip()
        try:
            valor = float(self.entry_valor.get().replace(',', '.'))
        except ValueError:
            messagebox.showwarning("Atenção", "Valor deve ser numérico.")
            return
        cat_nome = self.combo_categoria.get()
        cat_id = None
        if cat_nome:
            self.controller.cursor.execute("SELECT id FROM categorias WHERE nome=?", (cat_nome,))
            cat_id = self.controller.cursor.fetchone()[0]
        urls_raw = self.text_urls.get('1.0', tk.END).strip()
        urls_list = [u.strip() for u in urls_raw.split('\n') if u.strip()]
        urls_json = json.dumps(urls_list, ensure_ascii=False)
        # Sempre recalcula o estoque ao salvar
        from estoque import get_estoque_from_urls
        estoque = get_estoque_from_urls(urls_json) if urls_list else 0

        if not nome:
            messagebox.showwarning("Atenção", "Nome do produto é obrigatório.")
            return
        try:
            if self.selected_id:
                self.controller.cursor.execute(
                    "UPDATE produtos SET nome=?, descricao=?, valor=?, categoria_id=?, urls=?, estoque=? WHERE id=?",
                    (nome, descricao, valor, cat_id, urls_json, estoque, self.selected_id)
                )
            else:
                self.controller.cursor.execute(
                    "INSERT INTO produtos (nome, descricao, valor, categoria_id, urls, estoque) VALUES (?, ?, ?, ?, ?, ?)",
                    (nome, descricao, valor, cat_id, urls_json, estoque)
                )
            self.controller.conn.commit()
            messagebox.showinfo("Sucesso", "Produto salvo com sucesso.")
            self.clear_form()
            self.reload_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar produto: {e}")

    def delete_product(self):
        if not self.selected_id:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.")
            return
        if messagebox.askyesno("Confirmar", "Deseja realmente excluir este produto?"):
            try:
                self.controller.cursor.execute("DELETE FROM produtos WHERE id=?", (self.selected_id,))
                self.controller.conn.commit()
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso.")
                self.clear_form()
                self.reload_data()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir produto: {e}")
