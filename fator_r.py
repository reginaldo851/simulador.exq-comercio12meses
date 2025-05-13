import streamlit as st

# Tabelas e distribuição do Simples Nacional
tabela_anexo_iii = [
    (0.00, 180000.00, 0.06, 0.00, "1ª Faixa"),
    (180000.01, 360000.00, 0.112, 9360.00, "2ª Faixa"),
    (360000.01, 720000.00, 0.135, 17640.00, "3ª Faixa"),
    (720000.01, 1800000.00, 0.16, 35640.00, "4ª Faixa"),
    (1800000.01, 3600000.00, 0.21, 125640.00, "5ª Faixa"),
    (3600000.01, 4800000.00, 0.33, 648000.00, "6ª Faixa")
]

tabela_anexo_v = [
    (0.00, 180000.00, 0.155, 0.00, "1ª Faixa"),
    (180000.01, 360000.00, 0.18, 4500.00, "2ª Faixa"),
    (360000.01, 720000.00, 0.195, 9900.00, "3ª Faixa"),
    (720000.01, 1800000.00, 0.205, 17100.00, "4ª Faixa"),
    (1800000.01, 3600000.00, 0.23, 62100.00, "5ª Faixa"),
    (3600000.01, 4800000.00, 0.305, 540000.00, "6ª Faixa")
]

distribuicao_iii = {
    "6ª Faixa": {"IRPJ": 0.35, "CSLL": 0.15, "COFINS": 0.1603, "PIS": 0.0347, "CPP": 0.305, "ISS": 0.0}
}

distribuicao_v = {
    "6ª Faixa": {"IRPJ": 0.135, "CSLL": 0.10, "COFINS": 0.2827, "PIS": 0.0613, "CPP": 0.421, "ISS": 0.0}
}

redistribuicao_excedente = {
    "IRPJ": 0.0602,
    "CSLL": 0.0526,
    "COFINS": 0.1928,
    "PIS": 0.0418,
    "CPP": 0.6526,
    "ISS": 0.0
}

def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Título
st.title("Simulador Fator R - Simples Nacional (Anexos III e V)")

# Entradas
periodo = st.text_input("Período de apuração (MM/AAAA)")
receita_mes = st.number_input("Receita bruta do mês (R$)", min_value=0.0, step=100.0)
rbt12 = st.number_input("Receita bruta total dos últimos 12 meses (RBT12)", min_value=0.0, step=100.0)
folha12 = st.number_input("Total da folha de salários dos últimos 12 meses (R$)", min_value=0.0, step=100.0)
rba = st.number_input("Receita Bruta Anual (RBA)", min_value=0.0, step=100.0)

# Botão para cálculo
if st.button("Calcular"):
    # Cálculo do Fator R
    if rbt12 == 0 and folha12 == 0:
        fator_r = 0.01
    elif rbt12 == 0 and folha12 > 0:
        fator_r = 0.28
    elif rbt12 > 0 and folha12 == 0:
        fator_r = 0.01
    else:
        fator_r = folha12 / rbt12

    # Escolha do anexo
    if fator_r >= 0.28:
        tabela = tabela_anexo_iii
        distribuicao = distribuicao_iii
        anexo = "III"
    else:
        tabela = tabela_anexo_v
        distribuicao = distribuicao_v
        anexo = "V"

    # Faixa e alíquota
    for faixa in tabela:
        if faixa[0] <= rbt12 <= faixa[1]:
            aliquota = faixa[2]
            deduzir = faixa[3]
            nome_faixa = faixa[4]
            break
    else:
        st.error("RBT12 fora do limite permitido.")
        st.stop()

    # Imposto devido
    aliquota_efetiva = ((rbt12 * aliquota) - deduzir) / rbt12
    imposto = receita_mes * aliquota_efetiva

    # Distribuição
    dist = distribuicao[nome_faixa].copy()
    valores = {trib: imposto * perc for trib, perc in dist.items()}

    # Regra do ISS: limitar a 5%
    limite_iss = receita_mes * 0.05
    if valores["ISS"] > limite_iss:
        excedente = valores["ISS"] - limite_iss
        valores["ISS"] = limite_iss
        for trib in ["IRPJ", "CSLL", "COFINS", "PIS", "CPP"]:
            valores[trib] += excedente * redistribuicao_excedente[trib]

    # Resultados
    st.subheader("Resumo do Cálculo")
    st.write(f"Anexo: **{anexo}**")
    st.write(f"Fator R: **{fator_r:.2%}**")
    st.write(f"Faixa: **{nome_faixa}**")
    st.write(f"Alíquota Efetiva: **{aliquota_efetiva * 100:.2f}%**")
    st.write(f"Imposto Devido: **{formatar(imposto)}**")

    st.subheader("Distribuição dos Tributos:")
    for trib, valor in valores.items():
        st.write(f"{trib}: {formatar(valor)}")
    st.write(f"**Total distribuído: {formatar(sum(valores.values()))}**")

    # Mensagens adicionais
    if rba > 4320000.00:
        st.warning("ISS a ser recolhido FORA do Simples Nacional no mês seguinte.")
    elif rba > 3600000.00:
        st.warning("ISS a ser recolhido FORA do Simples Nacional no ano seguinte.")

    if rba > 5760000.00:
        st.error("Empresa sujeita a EXCLUSÃO do Simples Nacional a partir do mês seguinte.")
    elif rba > 4800000.00:
        st.error("Empresa sujeita a EXCLUSÃO do Simples Nacional a partir do ano seguinte.")
