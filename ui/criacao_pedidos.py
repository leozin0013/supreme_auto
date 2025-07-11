import os
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import uuid

MATERIAL_PERCENTUAL = 0.12  # Percentual de material extra
VALOR_HORA_TRABALHO = 70  # Valor da hora de trabalho
HORAS_POR_PRODUTO = 2      # Horas estimadas por produto instalado
MARGEM_LUCRO = 0.25         # Margem de lucro
IMPOSTOS_FIXOS = 80      # imposto DAS (INSS, ISS e ICMS) = 76,90


class CriacaoPedidos(tk.Frame):
    """
    Tela para criação de pedidos, cálculo de valores e geração de PDF.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_client_id = None
        self.items = []

        self.configure(padx=20, pady=20)
        self.build_layout()
        self.reload_data()

    def build_layout(self):
        # Cliente
        frame_cliente = ttk.LabelFrame(self, text="Cliente")
        frame_cliente.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        frame_cliente.columnconfigure(1, weight=1)

        ttk.Label(frame_cliente, text="Cliente:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.combo_cliente = ttk.Combobox(frame_cliente, state="readonly")
        self.combo_cliente.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.combo_cliente.bind("<<ComboboxSelected>>", self.on_client_select)

        # Produto
        frame_produto = ttk.LabelFrame(self, text="Adicionar Produto")
        frame_produto.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        for i in range(4): frame_produto.columnconfigure(i, weight=1)

        ttk.Label(frame_produto, text="Categoria:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combo_cat = ttk.Combobox(frame_produto, state="readonly")
        self.combo_cat.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.combo_cat.bind("<<ComboboxSelected>>", self.on_category_select)

        ttk.Label(frame_produto, text="Produto:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.combo_prod = ttk.Combobox(frame_produto, state="readonly")
        self.combo_prod.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        ttk.Label(frame_produto, text="Qtde:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.spin_qtde = tk.Spinbox(frame_produto, from_=1, to=100, width=5)
        self.spin_qtde.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        btn_add = ttk.Button(frame_produto, text="Adicionar", command=self.add_item)
        btn_add.grid(row=1, column=2, padx=10, pady=5)
        btn_remove = ttk.Button(frame_produto, text="Remover", command=self.remove_item)
        btn_remove.grid(row=1, column=3, padx=10, pady=5)

        # Itens
        cols = ("Produto", "Categoria", "Qtde", "Unit", "Total")
        self.tree_itens = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree_itens.heading(c, text=c.capitalize()); self.tree_itens.column(c, anchor="center")
        self.tree_itens.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(0, 10))
        self.tree_itens.column("Qtde", width=35); self.tree_itens.column("Unit", width=70); self.tree_itens.column("Total", width=70)

        # Totais
        frame_calc = ttk.LabelFrame(self, text="Totais")
        frame_calc.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        for i in range(5): frame_calc.columnconfigure(i, weight=1)

        self.lbl_total_prod = ttk.Label(frame_calc, text="Total Produtos: R$ 0,00")
        self.lbl_total_prod.grid(row=0, column=0, padx=10, pady=5)
        self.lbl_mat_extra = ttk.Label(frame_calc, text=f"Material Extra ({int(MATERIAL_PERCENTUAL * 100)}%): R$ 0,00")
        self.lbl_mat_extra.grid(row=0, column=1, padx=10, pady=5)
        self.lbl_mao_obra = ttk.Label(frame_calc, text="Mão de Obra: R$ 0,00")
        self.lbl_mao_obra.grid(row=0, column=2, padx=10, pady=5)
        self.lbl_margem_lucro = ttk.Label(frame_calc, text=f"Margem de Lucro ({int(MARGEM_LUCRO * 100)}%): R$ 0,00")
        self.lbl_margem_lucro.grid(row=0, column=3, padx=10, pady=5)
        self.lbl_impostos = ttk.Label(frame_calc, text=f"Impostos Fixos: R$ {IMPOSTOS_FIXOS:.2f}")
        self.lbl_impostos.grid(row=0, column=4, padx=10, pady=5)
        self.lbl_total = ttk.Label(frame_calc, text="Valor Total: R$ 0,00", font=("Helvetica", 12, "bold"))
        self.lbl_total.grid(row=1, column=0, columnspan=5, padx=10, pady=5)

        # Botões de ação
        frame_botoes = ttk.Frame(self)
        frame_botoes.grid(row=4, column=0, columnspan=4, pady=15)
        for i in range(3): frame_botoes.columnconfigure(i, weight=1)

        btn_finalize = ttk.Button(frame_botoes, text="Finalizar Pedido", command=self.finalize_order)
        btn_finalize.grid(row=0, column=0, padx=10)
        btn_segv = ttk.Button(frame_botoes, text="2ª via", command=self.second_copy)
        btn_segv.grid(row=0, column=1, padx=10)
        btn_voltar = ttk.Button(frame_botoes, text="Voltar", command=lambda: self.controller.show_frame("MenuPrincipal"))
        btn_voltar.grid(row=0, column=2, padx=10)

        # Histórico
        frame_hist = ttk.LabelFrame(self, text="Histórico de Pedidos")
        frame_hist.grid(row=5, column=0, columnspan=4, sticky="nsew")
        frame_hist.columnconfigure(0, weight=1)

        cols_h = ("ID", "Cliente", "Data", "Total")
        self.tree_hist = ttk.Treeview(frame_hist, columns=cols_h, show="headings", height=6)
        for c in cols_h:
            self.tree_hist.heading(c, text=c.capitalize()); self.tree_hist.column(c, anchor="center")
        self.tree_hist.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tree_hist.bind("<Double-1>", self.on_hist_double)
        self.tree_hist.column("ID", width=40); self.tree_hist.column("Total", width=70)

        self.grid_rowconfigure(2, weight=1); self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure((0,1,2,3), weight=1)

    def reload_data(self):
        # Carregar clientes, categorias e histórico
        cur = self.controller.cursor
        self.client_map = {f"{cid} - {nm}": cid for cid, nm in cur.execute("SELECT id, nome FROM clientes ORDER BY nome").fetchall()}
        vals = ["Simulação"] + list(self.client_map.keys())
        self.combo_cliente['values'] = vals; self.combo_cliente.set("Simulação"); self.on_client_select()

        self.cat_map = {nm: cid for cid, nm in cur.execute("SELECT id, nome FROM categorias ORDER BY nome").fetchall()}
        self.combo_cat['values'] = list(self.cat_map.keys()); self.combo_cat.set(''); self.combo_prod.set('')

        for row in self.tree_hist.get_children(): self.tree_hist.delete(row)
        for pid, cliente, data, total in cur.execute(
            "SELECT p.id, CASE WHEN p.simulacao=1 THEN 'Simulação' ELSE c.nome END, p.data, p.valor_total "
            "FROM pedidos p LEFT JOIN clientes c ON p.cliente_id=c.id ORDER BY p.data DESC").fetchall():
            self.tree_hist.insert('', 'end', values=(pid, cliente, data, f"R$ {total:.2f}"))

        self.items.clear()
        for row in self.tree_itens.get_children(): self.tree_itens.delete(row)
        self.update_totals()

    def on_client_select(self, event=None):
        sel = self.combo_cliente.get()
        self.selected_client_id = None if sel == "Simulação" else self.client_map.get(sel)

    def on_category_select(self, event=None):
        cid = self.cat_map.get(self.combo_cat.get())
        prods = self.controller.cursor.execute(
            "SELECT id, nome, valor FROM produtos WHERE categoria_id=? ORDER BY nome", (cid,)
        ).fetchall() if cid else []
        self.prod_map = {f"{nm} (R$ {vl:.2f})": (pid, vl) for pid, nm, vl in prods}
        self.combo_prod['values'] = list(self.prod_map.keys()); self.combo_prod.set('')

    def add_item(self):
        sel = self.combo_prod.get()
        if not sel:
            return messagebox.showwarning("Atenção", "Selecione um produto.")
        pid, vl = self.prod_map[sel]
        qt = int(self.spin_qtde.get())
        cat = self.combo_cat.get()

        # Verificar estoque disponível
        cur = self.controller.cursor
        cur.execute("SELECT estoque FROM produtos WHERE id=?", (pid,))
        result = cur.fetchone()
        estoque_disponivel = result[0] if result else 0

        # Só exibe a mensagem se NÃO for simulação (ou seja, se um cliente estiver selecionado)
        if self.selected_client_id is not None and qt > estoque_disponivel:
            resposta = messagebox.askyesno(
                "Estoque insuficiente",
                f"O estoque disponível para este produto é {estoque_disponivel}.\n"
                f"Não é possível adicionar {qt} unidades.\n\n"
                "Tem certeza que deseja adicionar mesmo assim?"
            )
            if not resposta:
                return

        self.items.append((pid, sel.split(' (')[0], cat, qt, vl))
        self.reload_items_view()

    def remove_item(self):
        sel = self.tree_itens.selection()
        if not sel:
            return messagebox.showwarning("Atenção", "Selecione um item para remover.")
        idx = self.tree_itens.index(sel[0]); self.items.pop(idx); self.reload_items_view()

    def reload_items_view(self):
        for row in self.tree_itens.get_children(): self.tree_itens.delete(row)
        for pid, nome, cat, qt, vl in self.items:
            self.tree_itens.insert('', 'end', values=(nome, cat, qt, f"R$ {vl:.2f}", f"R$ {qt*vl:.2f}"))
        self.update_totals()

    def update_totals(self):
        # Se não houver produtos no pedido, zera os valores
        if not self.items:
            self.lbl_total_prod.config(text="Total Produtos: R$ 0,00")
            self.lbl_mat_extra.config(text=f"Material Extra ({int(MATERIAL_PERCENTUAL * 100)}%): R$ 0,00")
            self.lbl_mao_obra.config(text="Mão de Obra: R$ 0,00")
            self.lbl_margem_lucro.config(text=f"Margem de Lucro ({int(MARGEM_LUCRO * 100)}%): R$ 0,00")
            self.lbl_impostos.config(text=f"Impostos Fixos: R$ {IMPOSTOS_FIXOS:.2f}")
            self.lbl_total.config(text="Valor Total: R$ 0,00")
            return

        # Valor total dos produtos
        tp = sum(qt * vl for *_, qt, vl in self.items)

        # Excluir produtos da categoria "Alexa" do cálculo de material extra
        total_sem_alexa = sum(
            qt * vl for _, _, cat, qt, vl in self.items if cat.lower() != "alexa"
        )

        # Material extra
        me = total_sem_alexa * MATERIAL_PERCENTUAL

        # Mão de obra
        num_produtos = sum(qt for _, _, cat, qt, _ in self.items if cat.lower() != "alexa")
        mao_obra = num_produtos * (VALOR_HORA_TRABALHO * HORAS_POR_PRODUTO)

        # Valor total antes da margem de lucro
        subtotal = tp + me + mao_obra

        # Aplicar margem de lucro
        margem = subtotal * MARGEM_LUCRO
        valor_com_lucro = subtotal + margem

        # Adicionar impostos fixos
        valor_total = valor_com_lucro + IMPOSTOS_FIXOS

        # Atualizar os rótulos
        self.lbl_total_prod.config(text=f"Total Produtos: R$ {tp:.2f}")
        self.lbl_mat_extra.config(text=f"Material Extra ({int(MATERIAL_PERCENTUAL * 100)}%): R$ {me:.2f}")
        self.lbl_mao_obra.config(text=f"Mão de Obra: R$ {mao_obra:.2f}")
        self.lbl_margem_lucro.config(text=f"Margem de Lucro ({int(MARGEM_LUCRO * 100)}%): R$ {margem:.2f}")
        self.lbl_impostos.config(text=f"Impostos Fixos: R$ {IMPOSTOS_FIXOS:.2f}")
        self.lbl_total.config(text=f"Valor Total: R$ {valor_total:.2f}")

    def finalize_order(self):
        if not self.items:
            return messagebox.showwarning("Atenção", "Adicione ao menos um item ao pedido.")
        if self.selected_client_id is None:
            return messagebox.showinfo("Simulação", "Este é um pedido de simulação e não será salvo no histórico.")

        # Cálculo do total
        tp = sum(qt * vl for *_, qt, vl in self.items)

        # Excluir produtos da categoria "Alexa" do cálculo de material extra
        total_sem_alexa = sum(
            qt * vl for _, _, cat, qt, vl in self.items if cat.lower() != "alexa"
        )

        # Material extra
        me = total_sem_alexa * MATERIAL_PERCENTUAL

        # Mão de obra
        num_produtos = sum(qt for _, _, cat, qt, _ in self.items if cat.lower() != "alexa")
        mao_obra = num_produtos * (VALOR_HORA_TRABALHO * HORAS_POR_PRODUTO)

        # Valor total antes da margem de lucro
        subtotal = tp + me + mao_obra

        # Aplicar margem de lucro
        margem = subtotal * MARGEM_LUCRO
        valor_com_lucro = subtotal + margem

        # Adicionar impostos fixos
        valor_total = valor_com_lucro + IMPOSTOS_FIXOS

        # Inserir o pedido no banco de dados
        cur = self.controller.cursor
        conn = self.controller.conn
        external_reference = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO pedidos (cliente_id, simulacao, valor_total, external_reference) VALUES (?, ?, ?, ?)",
            (self.selected_client_id, 0, valor_total, external_reference)
        )
        pid = cur.lastrowid
        for pid_item, _, _, qt, vl in self.items:
            cur.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, valor_unitario) VALUES (?, ?, ?, ?)",
                (pid, pid_item, qt, vl)
            )
        conn.commit()

        # Gerar PDF do pedido
        try:
            self._generate_pdf(pid)
            messagebox.showinfo(
                "Sucesso", f"Pedido #{pid} finalizado e contrato gerado!"
            )
        except Exception as e:
            messagebox.showerror(
                "Erro", f"Pedido finalizado, mas falha ao gerar PDF:\n{e}"
            )
        self.reload_data()

    def second_copy(self):
        sel = self.tree_hist.selection()
        if not sel:
            return messagebox.showwarning("Atenção", "Selecione um pedido no histórico para gerar 2ª via.")
        pid = self.tree_hist.item(sel[0], 'values')[0]
        try:
            self._generate_pdf(pid)
            messagebox.showinfo("Sucesso", f"2ª via do Pedido #{pid} gerada!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:\n{e}")

    def on_hist_double(self, event):
        self.second_copy()

    def _generate_pdf(self, pedido_id):
        """
        Gera um PDF para o pedido especificado com nome e logo da empresa no topo.
        """
        cur = self.controller.cursor
        pedido = cur.execute(
            "SELECT cliente_id, simulacao, valor_total, data FROM pedidos WHERE id=?", (pedido_id,)
        ).fetchone()
        itens = cur.execute(
            "SELECT p.nome, c.nome, i.quantidade, i.valor_unitario "
            "FROM itens_pedido i "
            "JOIN produtos p ON i.produto_id=p.id "
            "LEFT JOIN categorias c ON p.categoria_id=c.id "
            "WHERE i.pedido_id=?", (pedido_id,)
        ).fetchall()

        if pedido[1] == 1:
            nome_cli = "Simulação"
            cpf_cli = ""
            endereco_cli = ""
        else:
            cli = cur.execute(
                "SELECT nome, cpf, telefone, email, endereco FROM clientes WHERE id=?", (pedido[0],)
            ).fetchone()
            nome_cli = cli[0].replace(" ", "_") if cli else "Cliente_Desconhecido"
            cpf_cli = cli[1] if cli else ""
            endereco_cli = cli[4] if cli else ""

        out_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'Contratos')
        os.makedirs(out_dir, exist_ok=True)
        pdf_path = os.path.join(out_dir, f"Contrato_{pedido_id}_{nome_cli}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=A4)
        w, h = A4
        margin = 50
        y = h - margin

        # Cabeçalho com logo e nome da empresa
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
            if os.path.exists(logo_path):
                logo = ImageReader(logo_path)
                c.drawImage(logo, margin, y - 50, width=80, height=80, mask='auto')
        except Exception as e:
            print(f"Erro ao carregar o logo: {e}")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin + 90, y - 20, "Supreme Automações Residenciais")
        y -= 70  # Ajusta o início do conteúdo após o cabeçalho

        # Título do pedido
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, f"Pedido #{pedido_id}")
        y -= 30

        # Dados do cliente
        c.setFont("Helvetica", 10)
        if pedido[1] == 1:
            c.drawString(margin, y, "Cliente: Simulação")
            y -= 20
        else:
            if cli:
                text_cli = f"Cliente: {cli[0]} | CPF: {cli[1]} | Tel: {cli[2]} | Email: {cli[3]} | Endereço: {cli[4]}"
                for line in self._wrap_text(text_cli, w - 2 * margin, c):
                    c.drawString(margin, y, line)
                    y -= 15
            else:
                c.drawString(margin, y, "Cliente: Desconhecido")
                y -= 20

        # Itens
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Itens:")
        y -= 20
        c.setFont("Helvetica", 10)
        for nm, cat, qt, vl in itens:
            total_item = qt * vl
            c.drawString(
                margin,
                y,
                # f"{cat} - Total: R$ {total_item:.2f}",
                f"{cat}"
            )
            y -= 15
        y -= 10

        # Valor total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Valor Total: R$ {pedido[2]:.2f}")
        y -= 30

        # Contrato de prestação de serviços
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE AUTOMAÇÃO RESIDENCIAL")
        y -= 20
        c.setFont("Helvetica", 9)

        contrato_texto = f"""
            Pelo presente instrumento particular, de um lado:
            SUPREME AUTOMAÇÕES, inscrita no CNPJ sob o nº 60.785.475/0001-62, com sede à Rua Jayr Amaury Koebe, 220 - AP 1007A, neste ato representada por seu titular Leonardo Moreto Azambuja, doravante denominada CONTRATADA,
            E, de outro lado,
            {cli[0] if pedido[1] != 1 and cli else '[NOME DO CLIENTE]'}, inscrito no CPF sob o nº {cpf_cli or '[CPF]'}, residente à {endereco_cli or '[ENDEREÇO COMPLETO DO APARTAMENTO]'}, doravante denominado CONTRATANTE,
            firmam o presente contrato de prestação de serviços de automação residencial, mediante as seguintes cláusulas e condições:

            CLÁUSULA 1: OBJETO
            1.1. O presente contrato tem por objeto a prestação de serviços de automação residencial, incluindo fornecimento, instalação, configuração e ativação de dispositivos inteligentes para iluminação, climatização, cortinas, entre outros, conforme proposta previamente aprovada.
            1.2. Os serviços serão realizados sem descaracterizar a estética do imóvel e, sempre que possível, mantendo os interruptores originais, salvo quando expressamente autorizado pelo CONTRATANTE.

            CLÁUSULA 2: VISTORIA PRÉVIA
            2.1. A assinatura deste contrato está condicionada à realização de vistoria técnica presencial obrigatória, pela CONTRATADA, no local da instalação, com o objetivo de avaliar as condições físicas e elétricas do ambiente, identificando eventuais limitações e intervenções necessárias.
            2.2. A CONTRATADA se compromete a informar previamente quaisquer adaptações que envolvam intervenções físicas, como cortes em forro de gesso, perfurações ou ajustes no acabamento. Tais medidas somente serão realizadas mediante autorização expressa do CONTRATANTE.
            2.3. A CONTRATADA poderá registrar imagens do local de instalação exclusivamente para fins técnicos e documentais. Tais imagens não serão divulgadas ou compartilhadas com terceiros, sendo armazenadas com segurança e utilizadas apenas em caso de necessidade técnica ou comprovação contratual.

            CLÁUSULA 3: ESCOPO DOS SERVIÇOS
            3.1. Os serviços abrangem:
                - Fornecimento e instalação dos dispositivos de automação conforme proposta aprovada;
                - Passagem de novos cabos, reorganização ou desativação de condutores, se necessário;
                - Configuração e testes dos sistemas instalados;
                - Instruções básicas de uso ao CONTRATANTE.
            3.2. A CONTRATADA não se responsabiliza por limitações físicas, estruturais ou elétricas preexistentes, tais como:
                - Conduítes obstruídos;
                - Instalações fora de norma;
                - Ligações mal executadas anteriormente.
            3.3. Caso o CONTRATANTE opte por manter interruptores antigos, reconhece e aceita eventuais limitações técnicas ou falhas decorrentes dessa escolha, isentando a CONTRATADA de responsabilidades.

            CLÁUSULA 4: ACESSO TÉCNICO TEMPORÁRIO A CREDENCIAIS DIGITAIS
            4.1. Para a vinculação dos módulos de automação às contas do CONTRATANTE, será necessário o acesso temporário às credenciais de login das seguintes plataformas:
                - Amazon Alexa (conta Amazon)
                - Smart Life ou aplicativo equivalente utilizado pelo CONTRATANTE
            4.2. As credenciais serão utilizadas exclusivamente durante a fase de instalação e configuração, sendo acessadas em ambiente controlado e supervisionado.
            4.3. A CONTRATADA compromete-se a não armazenar, copiar, compartilhar ou reutilizar tais dados após a conclusão do serviço.
            4.4. O CONTRATANTE declara estar ciente e responsável por alterar as senhas imediatamente após o término da instalação, isentando a CONTRATADA de qualquer responsabilidade por acessos indevidos, falhas de segurança ou usos posteriores dessas contas.

            CLÁUSULA 5: PRAZO DE EXECUÇÃO
            5.1. Os serviços serão realizados no prazo de até [____] dias úteis, contados a partir da data de início acordada entre as partes, podendo haver prorrogação mediante comum acordo, caso identificado impedimento técnico durante a execução.

            CLÁUSULA 6: VALOR E CONDIÇÕES DE PAGAMENTO
            6.1. O valor total dos serviços contratados é de R$ {pedido[2]:.2f}, pago da seguinte forma:
                - [___] À vista via PIX ou transferência bancária;
                - [___] Parcelado em [____] vezes de R$ {pedido[2]:.2f};
            6.2. O não pagamento nos prazos acordados sujeitará o CONTRATANTE a multa de 2% sobre o valor em atraso, além de juros de mora de 1% ao mês.
            6.3. O valor estipulado para cada categoria de serviço inclui o fornecimento dos dispositivos, materiais auxiliares, mão de obra de instalação, testes e configurações. A CONTRATADA não está obrigada a apresentar ao CONTRATANTE o custo individual de cada item, salvo exigência legal.

            CLÁUSULA 7: GARANTIA E SUPORTE
            7.1. A CONTRATADA oferece 90 (noventa) dias de garantia legal sobre a execução dos serviços, contados a partir da data de finalização.
            7.2. A garantia dos equipamentos fornecidos respeitará os prazos e condições estipulados pelo fabricante.
            7.3. O suporte técnico será prestado de forma pontual e sob demanda, limitado a orientações, configurações ou ajustes iniciais, sem cobertura de manutenção periódica.
            7.4. Qualquer solicitação de reconfiguração dos dispositivos após a entrega técnica será atendida mediante novo agendamento e poderá gerar cobrança adicional, conforme tabela vigente da CONTRATADA.

            CLÁUSULA 8: LIMITAÇÃO DE RESPONSABILIDADE
            8.1. A CONTRATADA se responsabiliza exclusivamente pelos serviços e dispositivos fornecidos e instalados sob este contrato.
            8.2. A CONTRATADA não responderá por:
                - Intervenções realizadas por terceiros após a instalação;
                - Mau uso dos dispositivos;
                - Danos ocasionados por falhas ou irregularidades na estrutura elétrica do imóvel.
            8.3. O CONTRATANTE declara estar ciente de que os dispositivos de automação instalados pela CONTRATADA são compatíveis com cargas elétricas de, no máximo, 10 amperes (10A), conforme especificações técnicas dos fabricantes.
            8.4. A utilização de equipamentos ou circuitos com corrente superior à recomendada poderá acarretar danos permanentes aos dispositivos instalados, bem como riscos de curto-circuito, incêndio ou mau funcionamento do sistema de automação.
            8.5. A CONTRATADA não se responsabiliza por quaisquer danos materiais, falhas técnicas ou prejuízos decorrentes da utilização indevida de equipamentos que excedam o limite de corrente especificado, sendo esta conduta considerada mau uso, isentando a CONTRATADA de qualquer obrigação de reparo, substituição ou reembolso.

            CLÁUSULA 9: RESCISÃO
            9.1. O contrato poderá ser rescindido por qualquer das partes, mediante aviso prévio de 5 (cinco) dias úteis.
            9.2. Caso a rescisão ocorra após o início da execução dos serviços, o CONTRATANTE se compromete a pagar valor proporcional aos serviços realizados, acrescido de indenização de até 30% do total do contrato, referente a custos operacionais.
            
            CLÁUSULA 10: FORO
            10.1. Para dirimir quaisquer controvérsias oriundas deste contrato, as partes elegem o foro da comarca de Porto Alegre/RS, renunciando a qualquer outro, por mais privilegiado que seja.

            DECLARAÇÃO FINAL:
            Declaro ter lido, compreendido e concordado com todas as cláusulas do presente contrato, bem como ter recebido as devidas explicações sobre os serviços contratados.

            Porto Alegre, ____/____/20____.

            CONTRATADA:
            ________________________________________
            Leonardo Moreto Azambuja
            CNPJ: 60.785.475/0001-62

            CONTRATANTE:
            ________________________________________
            {cli[0] if pedido[1] != 1 and cli else '[Nome do Cliente]'}
            CPF: {cpf_cli or '[CPF]'}
        """
        # Quebra o texto do contrato em linhas para caber na página, respeitando as quebras originais
        for raw_line in contrato_texto.strip().splitlines():
            line = raw_line.rstrip()
            if not line:  # Linha em branco
                y -= 13
                continue
            wrapped_lines = self._wrap_text(line, w - 2 * margin, c)
            for i, wrapped_line in enumerate(wrapped_lines):
                if y < margin + 60:
                    c.showPage()
                    y = h - margin
                    c.setFont("Helvetica", 9)
                # Justifica todas as linhas exceto a última do parágrafo
                if i < len(wrapped_lines) - 1 and len(wrapped_line.split()) > 1:
                    self._draw_justified_string(c, margin, y, wrapped_line, w - 2 * margin)
                else:
                    c.drawString(margin, y, wrapped_line)
                y -= 13
        y -= 8

        c.save()
        return pdf_path

    def _draw_justified_string(self, canvas, x, y, text, max_width):
        # Conta espaços à esquerda para preservar indentação
        leading_spaces = len(text) - len(text.lstrip(' '))
        indent = canvas.stringWidth(' ' * leading_spaces, "Helvetica", 9)
        words = text.lstrip().split()
        if len(words) == 1:
            canvas.drawString(x + indent, y, text.lstrip())
            return
        total_text_width = sum(canvas.stringWidth(word, "Helvetica", 9) for word in words)
        space_count = len(words) - 1
        space_width = (max_width - indent - total_text_width) / space_count if space_count else 0
        cursor_x = x + indent
        for i, word in enumerate(words):
            canvas.drawString(cursor_x, y, word)
            word_width = canvas.stringWidth(word, "Helvetica", 9)
            cursor_x += word_width
            if i < space_count:
                cursor_x += space_width

    def _wrap_text(self, text, max_width, canvas, font_name="Helvetica", font_size=9):
        """
        Quebra o texto em várias linhas para caber no max_width do PDF.
        """
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if canvas.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
