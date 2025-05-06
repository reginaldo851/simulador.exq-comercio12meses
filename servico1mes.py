import streamlit as st
import pandas as pd

# Tabela do Anexo III – Serviços
tabela = pd.DataFrame([
    (0.00,        180000.00, 0.06,      0.00, "1a Faixa"),
    (180000.01,   360000.00, 0.112,     9360.00, "2a Faixa"),
    (360000.01,   720000.00, 0.135,    17640.00, "3a Faixa"),
    (720000.01, 1800000.00, 0.16,     35640.00, "4a Faixa"),
    (1800000.01, 3600000.00, 0.21,    125640.00, "5a Faixa"),
    (3600000.01, 4800000.00, 0.33,    648000.00, "6a Faixa")
], columns=["limite_inferior", "limite_superior", "aliquota_nominal", "parcela_deduzir", "faixa"])

# Tabela de distribuição dos tributos
distribuicao = pd.DataFrame([
    ("1a Faixa", 0.04, 0.035, 0.1282, 0.0278, 0.434, 0.335),
    ("2a Faixa", 0.04, 0.035, 0.1405, 0.0305, 0.434, 0.320),
    ("3a Faixa", 0.04, 0.035, 0.1364, 0.0296, 0.434, 0.325),
    ("4a Faixa", 0.04, 0.035, 0.1364, 0.0296, 0.434, 0.325),
    ("5a Faixa", 0.04, 0.035, 0.1282, 0.0278, 0.434, 0.335),
    ("6a Faixa", 0.04, 0.035, 0.1282, 0.0278, 0.434, 0.335),
], columns=["Faixa", "IRPJ", "CSLL", "Cofins", "PIS/Pasep", "CPP", "ISS"])

# Redistribuição do excedente do ISS
redistribuicao_excedente = {
    "IRPJ": 0.0602,
    "CSLL": 0.0526,
    "Cofins": 0.1928,
    "PIS/Pasep": 0.0418,
    "CPP": 0.6526
}

def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(page_title="Simulador do Simples Nacional (Serviços)", layout="centered")
st.title("Simulador do Simples Nacional (Serviços)")
st.markdown("**Cálculo válido apenas para o 1º mês de atividade – Anexo III (Serviços em Geral)**")

receita_mes = st.number_input("Informe a Receita Bruta do 1º mês (R$):", min_value=0.0, step=100.0, format="%.2f")

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #7EC8E3;
        color: black;
        font-weight: 500;
        border: none;
        padding: 0.6em 1.2em;
        font-size: 1em;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #A4D8EA;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("Calcular"):
    try:
        if receita_mes <= 0:
            st.warning("Por favor, insira um valor de receita maior que zero.")
        else:
            rbt12 = receita_mes * 12

            for _, linha in tabela.iterrows():
                if linha["limite_inferior"] <= rbt12 <= linha["limite_superior"]:
                    aliquota_efetiva = ((rbt12 * linha["aliquota_nominal"]) - linha["parcela_deduzir"]) / rbt12
                    imposto = receita_mes * aliquota_efetiva
                    faixa = linha["faixa"]
                    break

            st.success("Cálculo realizado com sucesso:")
            st.write(f"💰 Receita Bruta Anual Estimada: {formatar(rbt12)}")
            st.write(f"📊 Alíquota Nominal: {linha['aliquota_nominal']*100:.2f}%")
            st.write(f"➖ Parcela a Deduzir: {formatar(linha['parcela_deduzir'])}")
            st.write(f"✅ Alíquota Efetiva: **{aliquota_efetiva*100:.2f}%**")
            st.write(f"📌 Imposto devido: **{formatar(imposto)}**")

            linha_rep = distribuicao[distribuicao["Faixa"] == faixa].iloc[0]
            dados_tabela = []
            valores = {}

            for tributo in ["IRPJ", "CSLL", "Cofins", "PIS/Pasep", "CPP", "ISS"]:
                perc = linha_rep[tributo]
                valores[tributo] = imposto * perc

            limite_iss = receita_mes * 0.05
            if valores["ISS"] > limite_iss and rbt12 <= 3600000:
                excedente = valores["ISS"] - limite_iss
                valores["ISS"] = limite_iss
                for t, p in redistribuicao_excedente.items():
                    valores[t] += excedente * p
                iss_ajustado = True
            else:
                iss_ajustado = False

            if rbt12 > 3600000:
                valores["ISS"] = 0.0
                iss_ajustado = False

            total = 0
            for tributo in ["IRPJ", "CSLL", "Cofins", "PIS/Pasep", "CPP", "ISS"]:
                valor = valores[tributo]
                total += valor
                texto_valor = formatar(valor)
                if tributo == "ISS" and iss_ajustado:
                    texto_valor += " (ISS ajustado para limite de 5% sobre a Receita Bruta do mês)"
                dados_tabela.append({"Tributo": tributo, "Valor": texto_valor})

            dados_tabela.append({"Tributo": "**Total**", "Valor": f"**{formatar(total)}**"})

            st.subheader("Distribuição dos Tributos:")
            st.table(pd.DataFrame(dados_tabela))

            if rbt12 > 3600000:
                st.warning("⚠️ RBT12 superior ao valor de R$ 3.600.000,00 – ISS a ser recolhido pelo regime normal de tributação seguindo as regras do seu Estado.")

            st.markdown("""
            <div style="text-align: justify; font-size: 0.9rem; margin-top: 20px;">
            <strong>Cálculo atualizado em Maio/2025. Desenvolvido por Reginaldo Ramos | Explica no Quadro!</strong><br>
            Esta é uma ferramenta auxiliar para a atividade de planejamento fiscal e tributário. Sempre consultar a legislação aplicável para o cálculo e recolhimento de tributos.
            </div>
            """, unsafe_allow_html=True)

    except:
        st.error("Erro ao processar o cálculo. Se possível comunicar o erro para contato@explicanoquadro.com.br")
