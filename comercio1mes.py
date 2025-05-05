import streamlit as st
import pandas as pd

# Tabela Anexo I (Comércio)
tabela = pd.DataFrame([
    (0.00,        180000.00, 0.04,      0.00, "1º Faixa"),
    (180000.01,   360000.00, 0.073,  5940.00, "2º Faixa"),
    (360000.01,   720000.00, 0.095, 13860.00, "3º Faixa"),
    (720000.01, 1800000.00, 0.107, 22500.00, "4º Faixa"),
    (1800000.01, 3600000.00, 0.143, 87300.00, "5º Faixa"),
    (3600000.01, 4800000.00, 0.19,  378000.00, "6º Faixa")
], columns=["limite_inferior", "limite_superior", "aliquota_nominal", "parcela_deduzir", "faixa"])

# Tabela de repartição dos tributos
df_reparticao = pd.DataFrame([
    ("1º Faixa", 5.5, 3.5, 12.74, 2.76, 41.4, 34.0),
    ("2º Faixa", 5.5, 3.5, 12.74, 2.76, 41.4, 34.0),
    ("3º Faixa", 5.5, 3.5, 12.74, 2.76, 42.0, 33.5),
    ("4º Faixa", 5.5, 3.5, 12.74, 2.76, 42.0, 33.5),
    ("5º Faixa", 5.5, 3.5, 12.74, 2.76, 42.0, 33.5),
    ("6º Faixa", 13.5, 10.0, 28.27, 6.13, 42.10, 0.0)
], columns=["Faixa", "IRPJ", "CSLL", "COFINS", "PIS", "CPP", "ICMS"])

# Função auxiliar para formatar valores em R$ (pt-BR)
def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função principal de cálculo
def calcular_simples_primeiro_mes(receita_mes, tabela):
    receita_anual = receita_mes * 12
    for _, linha in tabela.iterrows():
        if linha["limite_inferior"] <= receita_anual <= linha["limite_superior"]:
            aliquota_efetiva = ((receita_anual * linha["aliquota_nominal"]) - linha["parcela_deduzir"]) / receita_anual
            imposto = receita_mes * aliquota_efetiva
            return {
                "receita_anual": receita_anual,
                "aliquota_nominal": linha["aliquota_nominal"],
                "parcela_deduzir": linha["parcela_deduzir"],
                "aliquota_efetiva": aliquota_efetiva,
                "imposto": imposto,
                "faixa": linha["faixa"]
            }
    raise ValueError("Faixa não encontrada")

# Interface do Streamlit
st.set_page_config(page_title="Simulador do Simples Nacional (Comércio)", layout="centered")
st.title("Simulador do Simples Nacional (Comércio)")
st.markdown("**Cálculo válido apenas para o 1º mês de atividade – Anexo I (Comércio)**")

receita = st.number_input("Informe a Receita Bruta do 1º mês (R$)", min_value=0.0, step=100.0, format="%.2f")

# CSS para botão azul claro
custom_css = """
    <style>
    div.stButton > button {
        background-color: #7EC8E3;
        color: black;
        border: none;
        padding: 0.6em 1.2em;
        font-size: 1em;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #A4D8EA;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Botão de cálculo com tratamento de erro oculto
if st.button("Calcular"):
    try:
        if receita > 0:
            resultado = calcular_simples_primeiro_mes(receita, tabela)
            rbt12 = resultado["receita_anual"]

            st.success("Cálculo realizado com sucesso:")
            st.write(f"💰 Receita Anual Estimada: {formatar(rbt12)}")
            st.write(f"📊 Alíquota Nominal: {resultado['aliquota_nominal']*100:.2f}%")
            st.write(f"➖ Parcela a Deduzir: {formatar(resultado['parcela_deduzir'])}")
            st.write(f"✅ Alíquota Efetiva: **{resultado['aliquota_efetiva']*100:.2f}%**")
            st.write(f"📌 Imposto devido: **{formatar(resultado['imposto'])}**")

            # Repartição por tributo
            faixa = resultado["faixa"]
            reparticao = df_reparticao[df_reparticao["Faixa"] == faixa]
            if not reparticao.empty:
                linha = reparticao.iloc[0]

                dados_tabela = []
                for tributo in ["IRPJ", "CSLL", "COFINS", "PIS", "CPP", "ICMS"]:
                    if tributo == "ICMS" and rbt12 > 3600000.00:
                        valor = 0.00
                    else:
                        valor = resultado["imposto"] * (linha[tributo] / 100)
                    dados_tabela.append({
                        "Tributo": tributo,
                        "Valor": formatar(round(valor, 2))
                    })

                df_resultado = pd.DataFrame(dados_tabela)
                st.subheader("Distribuição dos Tributos:")
                st.table(df_resultado)
            else:
                raise ValueError("Repartição não encontrada para a faixa")

            # Alerta sobre ICMS após a tabela
            if rbt12 > 3600000.00:
                st.warning("⚠️ RBT12 superior ao valor de R$ 3.600.000,00 – ICMS a ser recolhido pelo regime normal de tributação, seguindo as regras do seu Estado.")

            # Mensagem final de rodapé
            mensagem = """
            <div style="text-align: justify; font-size: 0.9rem; margin-top: 20px;">
            <strong>Cálculo atualizado em Maio/2025. Desenvolvido por Reginaldo Ramos | Explica no Quadro!</strong><br>
            Esta é uma ferramenta auxiliar para a atividade de planejamento fiscal e tributário. Sempre consultar a legislação aplicável para o cálculo e recolhimento de tributos.
            </div>
            """
            st.markdown(mensagem, unsafe_allow_html=True)

    except:
        st.error("Erro ao processar o cálculo. Se possível comunicar o erro para contato@explicanoquadro.com.br")
