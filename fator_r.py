import streamlit as st

# Distribuição atualizada - Anexo III
distribuicao_iii = {
    "1ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1282, "PIS": 0.0278, "CPP": 0.434, "ISS": 0.335},
    "2ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1405, "PIS": 0.0305, "CPP": 0.434, "ISS": 0.32},
    "3ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1364, "PIS": 0.0296, "CPP": 0.434, "ISS": 0.325},
    "4ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1364, "PIS": 0.0296, "CPP": 0.434, "ISS": 0.325},
    "5ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1282, "PIS": 0.0278, "CPP": 0.434, "ISS": 0.335},
    "6ª Faixa": {"IRPJ": 0.35, "CSLL": 0.15, "COFINS": 0.1603, "PIS": 0.0347, "CPP": 0.305, "ISS": 0.0},
}

# Distribuição atualizada - Anexo V
distribuicao_v = {
    "1ª Faixa": {"IRPJ": 0.25, "CSLL": 0.15, "COFINS": 0.1410, "PIS": 0.0305, "CPP": 0.2885, "ISS": 0.14},
    "2ª Faixa": {"IRPJ": 0.23, "CSLL": 0.15, "COFINS": 0.1410, "PIS": 0.0305, "CPP": 0.2785, "ISS": 0.17},
    "3ª Faixa": {"IRPJ": 0.24, "CSLL": 0.15, "COFINS": 0.1492, "PIS": 0.0323, "CPP": 0.2385, "ISS": 0.19},
    "4ª Faixa": {"IRPJ": 0.21, "CSLL": 0.15, "COFINS": 0.1574, "PIS": 0.0341, "CPP": 0.2385, "ISS": 0.21},
    "5ª Faixa": {"IRPJ": 0.23, "CSLL": 0.125, "COFINS": 0.1410, "PIS": 0.0305, "CPP": 0.2385, "ISS": 0.235},
    "6ª Faixa": {"IRPJ": 0.35, "CSLL": 0.155, "COFINS": 0.1644, "PIS": 0.0356, "CPP": 0.295, "ISS": 0.0},
}

# Redistribuição do excedente do ISS
redistribuicao_excedente = {
    "IRPJ": 0.0602,
    "CSLL": 0.0526,
    "COFINS": 0.1928,
    "PIS": 0.0418,
    "CPP": 0.6526,
}

# Tabelas com alíquotas e deduções
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

# Função para formatar valores
def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Interface
st.title("Simulador Fator R - Teste com Diagnóstico")

periodo = st.text_input("Período de apuração (MM/AAAA)")
receita_mes = st.number_input("Receita bruta do mês (R$)", min_value=0.0, step=100.0)
rbt12 = st.number_input("Receita bruta total dos últimos 12 meses (RBT12)", min_value=0.0, step=100.0)
folha12 = st.number_input("Total da folha de salários dos últimos 12 meses (R$)", min_value=0.0, step=100.0)
rba = st.number_input("Receita Bruta Anual (RBA)", min_value=0.0, step=100.0)

if st.button("🔵 Calcular"):
    try:
        if rbt12 == 0 and folha12 == 0:
            fator_r = 0.01
        elif rbt12 == 0:
            fator_r = 0.28
        elif folha12 == 0:
            fator_r = 0.01
        else:
            fator_r = folha12 / rbt12

        if fator_r >= 0.28:
            tabela = tabela_anexo_iii
            distribuicao = distribuicao_iii
            anexo = "III"
        else:
            tabela = tabela_anexo_v
            distribuicao = distribuicao_v
            anexo = "V"

        for faixa in tabela:
            if faixa[0] <= rbt12 <= faixa[1]:
                aliquota = faixa[2]
                deduzir = faixa[3]
                nome_faixa = faixa[4]
                break
        else:
            st.error("RBT12 fora do limite permitido.")
            st.stop()

        aliquota_efetiva = ((rbt12 * aliquota) - deduzir) / rbt12
        imposto = receita_mes * aliquota_efetiva

        # Diagnóstico
        st.write(f"🧪 **DEBUG**")
        st.write(f"Anexo: {anexo}")
        st.write(f"Faixa: {nome_faixa}")
        st.write(f"Alíquota Nominal: {aliquota:.4f}")
        st.write(f"Parcela a Deduzir: {deduzir:.2f}")
        st.write(f"Alíquota Efetiva: {aliquota_efetiva:.6f}")
        st.write(f"Imposto Devido: {formatar(imposto)}")

        dist = distribuicao[nome_faixa].copy()
        valores = {trib: imposto * perc for trib, perc in dist.items()}

        limite_iss = receita_mes * 0.05
        if valores.get("ISS", 0) > limite_iss:
            excedente = valores["ISS"] - limite_iss
            valores["ISS"] = limite_iss
            for trib in redistribuicao_excedente:
                valores[trib] += excedente * redistribuicao_excedente[trib]
            st.info("ISS ajustado para limite de 5% sobre a Receita Bruta do mês.")

        st.subheader("Distribuição dos Tributos:")
        for trib, valor in valores.items():
            st.write(f"{trib}: {formatar(valor)}")
        st.write(f"**Total distribuído: {formatar(sum(valores.values()))}**")

    except Exception as e:
        st.error("Erro ao realizar o cálculo. Contate: reginaldo.cont@gmail.com")
        st.text(f"DEBUG: {e}")
