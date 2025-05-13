import streamlit as st

# Distribuição Anexo III
distribuicao_iii = {
    "1ª Faixa": {"IRPJ": 0.0400, "CSLL": 0.0350, "COFINS": 0.1282, "PIS": 0.0278, "CPP": 0.4340, "ISS": 0.3350},
    "2ª Faixa": {"IRPJ": 0.0400, "CSLL": 0.0350, "COFINS": 0.1405, "PIS": 0.0305, "CPP": 0.4340, "ISS": 0.3200},
    "3ª Faixa": {"IRPJ": 0.0400, "CSLL": 0.0350, "COFINS": 0.1364, "PIS": 0.0296, "CPP": 0.4340, "ISS": 0.3250},
    "4ª Faixa": {"IRPJ": 0.0400, "CSLL": 0.0350, "COFINS": 0.1364, "PIS": 0.0296, "CPP": 0.4340, "ISS": 0.3250},
    "5ª Faixa": {"IRPJ": 0.0400, "CSLL": 0.0350, "COFINS": 0.1282, "PIS": 0.0278, "CPP": 0.4340, "ISS": 0.3350},
    "6ª Faixa": {"IRPJ": 0.3500, "CSLL": 0.1500, "COFINS": 0.1603, "PIS": 0.0347, "CPP": 0.3050, "ISS": 0.0000},
}

# Distribuição Anexo V
distribuicao_v = {
    "1ª Faixa": {"IRPJ": 0.2500, "CSLL": 0.1500, "COFINS": 0.1410, "PIS": 0.0305, "CPP": 0.2885, "ISS": 0.1400},
    "2ª Faixa": {"IRPJ": 0.2300, "CSLL": 0.1500, "COFINS": 0.1410, "PIS": 0.0305, "CPP": 0.2785, "ISS": 0.1700},
    "3ª Faixa": {"IRPJ": 0.2400, "CSLL": 0.1500, "COFINS": 0.1492, "PIS": 0.0323, "CPP": 0.2385, "ISS": 0.1900},
    "4ª Faixa": {"IRPJ": 0.2100, "CSLL": 0.1500, "COFINS": 0.1574, "PIS": 0.0341, "CPP": 0.2385, "ISS": 0.2100},
    "5ª Faixa": {"IRPJ": 0.2300, "CSLL": 0.1250, "COFINS": 0.1410, "PIS": 0.0305, "CPP": 0.2385, "ISS": 0.2350},
    "6ª Faixa": {"IRPJ": 0.3500, "CSLL": 0.1550, "COFINS": 0.1644, "PIS": 0.0356, "CPP": 0.2950, "ISS": 0.0000},
}

# Redistribuição do excedente do ISS
redistribuir = {
    "IRPJ": 0.0602,
    "CSLL": 0.0526,
    "COFINS": 0.1928,
    "PIS": 0.0418,
    "CPP": 0.6526
}

def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Interface Streamlit
st.title("Simulador Fator R - Simples Nacional (Anexos III e V)")

periodo = st.text_input("Período de apuração (MM/AAAA)")
receita_mes = st.number_input("Receita bruta do mês (R$)", min_value=0.0, step=100.0)
rbt12 = st.number_input("Receita bruta total dos últimos 12 meses (RBT12)", min_value=0.0, step=100.0)
folha12 = st.number_input("Total da folha de salários dos últimos 12 meses (R$)", min_value=0.0, step=100.0)
rba = st.number_input("Receita Bruta Anual (RBA)", min_value=0.0, step=100.0)

if st.button("🔵 Calcular"):
    try:
        # Fator R
        if rbt12 == 0 and folha12 == 0:
            fator_r = 0.01
        elif rbt12 == 0 and folha12 > 0:
            fator_r = 0.28
        elif rbt12 > 0 and folha12 == 0:
            fator_r = 0.01
        else:
            fator_r = folha12 / rbt12

        anexo = "III" if fator_r >= 0.28 else "V"
        tabela = distribuicao_iii if anexo == "III" else distribuicao_v

        if rbt12 <= 180000.00:
            faixa = "1ª Faixa"
        elif rbt12 <= 360000.00:
            faixa = "2ª Faixa"
        elif rbt12 <= 720000.00:
            faixa = "3ª Faixa"
        elif rbt12 <= 1800000.00:
            faixa = "4ª Faixa"
        elif rbt12 <= 3600000.00:
            faixa = "5ª Faixa"
        else:
            faixa = "6ª Faixa"

        distribuicao = tabela[faixa]
        aliquota = sum(distribuicao.values())
        imposto = receita_mes * aliquota

        valores = {trib: imposto * perc for trib, perc in distribuicao.items()}

        # Regra do ISS
        limite_iss = receita_mes * 0.05
        if valores["ISS"] > limite_iss:
            excedente = valores["ISS"] - limite_iss
            valores["ISS"] = limite_iss
            for trib, perc in redistribuir.items():
                valores[trib] += excedente * perc
            st.info("ISS ajustado para limite de 5% sobre a Receita Bruta do mês.")

        # Resultados
        st.subheader("Resultado do Cálculo")
        st.write(f"Anexo: **{anexo}**")
        st.write(f"Faixa: **{faixa}**")
        st.write(f"Fator R: **{fator_r:.2%}**")
        st.write(f"Alíquota Efetiva Total: **{aliquota*100:.2f}%**")
        st.write(f"Imposto Devido: **{formatar(imposto)}**")

        st.subheader("Distribuição dos Tributos")
        total = 0
        for trib, valor in valores.items():
            st.write(f"{trib}: {formatar(valor)}")
            total += valor
        st.write(f"**Total: {formatar(total)}**")

        # Avisos complementares
        if rba > 4320000.00:
            st.warning("ISS a ser recolhido FORA do Simples Nacional no mês seguinte.")
        elif rba > 3600000.00:
            st.warning("ISS a ser recolhido FORA do Simples Nacional no ano seguinte.")
        if rba > 5760000.00:
            st.error("Empresa sujeita a EXCLUSÃO do Simples Nacional a partir do mês seguinte.")
        elif rba > 4800000.00:
            st.error("Empresa sujeita a EXCLUSÃO do Simples Nacional a partir do ano seguinte.")

        # Mensagem final institucional
        st.markdown("""
<div style='text-align: justify; font-size: 15px; margin-top: 20px;'>
<strong>Cálculo atualizado em Maio/2025. Desenvolvido por Reginaldo Ramos | Explica no Quadro!</strong><br>
Esta é uma ferramenta auxiliar para a atividade de planejamento fiscal e tributário.<br>
Sempre consultar a legislação aplicável para o cálculo e recolhimento de tributos.
</div>
""", unsafe_allow_html=True)


    except Exception:
        st.error("Erro ao realizar o cálculo, entre em contato pelo número de whatsapp abaixo ou envie um e-mail para: reginaldo.cont@gmail.com")
