import mercadopago
import sqlite3
from datetime import datetime
import requests
from fpdf import FPDF
import os
from config import load_env_var, load_bool_env_var

DB_FILE = load_env_var("DATABASE_PATH", "database.db")
DEBUG = load_bool_env_var("DEBUG_MODE", True)

# Configuração de tokens do Mercado Pago
# IMPORTANTE: Configure suas credenciais em um arquivo .env ou variáveis de ambiente
# Nunca commite tokens reais no repositório
if DEBUG:
    ACCESS_TOKEN = load_env_var("MERCADOPAGO_TEST_TOKEN", "YOUR_MERCADOPAGO_TEST_TOKEN_HERE")
else:
    ACCESS_TOKEN = load_env_var("MERCADOPAGO_PRODUCTION_TOKEN", "YOUR_MERCADOPAGO_PRODUCTION_TOKEN_HERE")

sdk = mercadopago.SDK(ACCESS_TOKEN)
webhook_url = load_env_var("MERCADOPAGO_WEBHOOK_URL", "YOUR_WEBHOOK_URL_HERE")

def salvar_pagamento(external_reference, preference_id, status, valor, title):
    """ Salva um pagamento no banco de dados, evitando duplicatas """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Verifica se o pagamento já existe
    cursor.execute("SELECT 1 FROM pagamentos WHERE external_reference = ?", (external_reference,))
    if cursor.fetchone():
        print(f"Pagamento para o pedido {external_reference} já existe. Ignorando inserção.")
        conn.close()
        return

    # Insere o pagamento se não existir
    cursor.execute('''INSERT INTO pagamentos (external_reference, preference_id, status, valor, title, data_criacao, executado)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (external_reference, preference_id, status, valor, title, datetime.now().isoformat(), False))
    conn.commit()
    conn.close()


def atualizar_status(external_reference, novo_status, executado):
    """ Atualiza o status do pagamento no banco de dados """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''UPDATE pagamentos SET status = ?, executado = ? WHERE external_reference = ?''',
                   (novo_status, executado, external_reference))
    conn.commit()
    conn.close()


def carregar_pagamentos_pendentes():
    """ Carrega todos os pagamentos com status pendente ou em processo """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM pagamentos WHERE status IN ('aguardando_pagamento', 'in_process')''')
    pagamentos = cursor.fetchall()
    conn.close()
    return pagamentos


def create_payment(external_reference, titulo, valor):

    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {
        'x-idempotency-key': '<SOME_UNIQUE_VALUE>'
    }

    payment_data = {
        "items": [
            {
                "id": external_reference,  # agora é o UUID
                "title": titulo,
                "quantity": 1,
                "unit_price": valor,
                "currency_id": "BRL",
            }
        ],
        "external_reference": external_reference,
    }
    result = sdk.preference().create(payment_data, request_options)
    preference = result["response"]
    preference_id = preference["id"]

    salvar_pagamento(str(external_reference), preference_id, "aguardando_pagamento", valor, titulo)

    payment_link = preference["init_point"]
    return payment_link

def verificar_pagamentos():
    pagamentos = carregar_pagamentos_pendentes()
    for pagamento in pagamentos:
        external_reference = pagamento[1]
        status_atual = pagamento[3]

        # Verifica o status atual do pagamento
        resultado = sdk.payment().search({
            "external_reference": external_reference
        })

        pagamentos_encontrados = resultado["response"]["results"]
        if not pagamentos_encontrados:
            continue

        pagamento_info = pagamentos_encontrados[0]  # Acessa diretamente o primeiro resultado

        # Obtém o status do pagamento
        novo_status = pagamento_info.get("status")
        if not novo_status:
            print(f"Status não encontrado para o pagamento {external_reference}.")
            continue

        # Se o status mudou, atualize e execute as funções correspondentes
        if novo_status != status_atual:
            print(f"Pagamento {external_reference} - Status: {novo_status}")
            atualizar_status(external_reference, novo_status, executado=False)

            if novo_status == "approved" and pagamento[7] == 0:  # Se aprovado e ainda não executado
                atualizar_status(external_reference, novo_status, executado=True)
                salvar_comprovante(external_reference)

def salvar_comprovante(external_reference):
     # Buscar o ID real do pagamento com a external_reference
    resultado = sdk.payment().search({
        "external_reference": external_reference
    })

    pagamentos_encontrados = resultado["response"]["results"]
    if not pagamentos_encontrados:
        print(f"Nenhum pagamento encontrado com external_reference {external_reference}.")
        return

    pagamento_info = pagamentos_encontrados[0]  # Usamos o primeiro pagamento encontrado
    payment_id = pagamento_info["id"]

    # Agora sim, usa o ID real na URL
    url = f'https://api.mercadopago.com/v1/payments/{payment_id}'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao obter dados do pagamento {payment_id}: {response.status_code}")
        return

    data = response.json()

    comprovante = {
        'ID do Pagamento': data['id'],
        'Status': data['status'],
        'Descrição': data.get('description', ''),

        'Tipo de Pagamento': data.get('payment_type_id', 'Não informado'),
        'Método de pagamento': data['payment_method_id'],
        'Parcelas': data.get('installment_amount', 'Não informado'),
        'Valor': f"R$ {data['transaction_amount']:.2f}",
        'Recebido por': data['collector_id'],

        'Primeiro Nome do Pagador': data['payer']['first_name'],
        'Último Nome do Pagador': data['payer']['last_name'],
        'Email do pagador': data['payer']['email'],

        'Tipo de Identificação': data['payer']['identification']['type'],
        'Número de Identificação': data['payer']['identification']['number'],

        'Data de criação': data['date_created'],
        'Data de aprovação': data['date_approved'],
    }

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Comprovante de Pagamento do pedido {external_reference}", ln=True, align='C')
    pdf.ln(10)

    for chave, valor in comprovante.items():
        pdf.cell(200, 10, txt=f"{chave}: {valor}", ln=True)

    # Salva o PDF em memória
    output_dir = "assets/temp/Comprovantes"
    os.makedirs(output_dir, exist_ok=True)  # Cria o diretório, se não existir
    pdf_file_path = os.path.join(output_dir, f"comprovante_pedido_{external_reference}.pdf")
    pdf.output(pdf_file_path)

    # Lê o PDF como binário
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_blob = pdf_file.read()

    # Salva o PDF no banco de dados
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Atualiza o registro com o PDF
    cursor.execute('''
        UPDATE pagamentos
        SET comprovante_pdf = ?
        WHERE external_reference = ?
    ''', (pdf_blob, external_reference))
    conn.commit()
    conn.close()

    # Remove o arquivo PDF temporário
    os.remove(pdf_file_path)