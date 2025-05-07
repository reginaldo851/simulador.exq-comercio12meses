import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

# Tabela do Anexo I – Comércio
tabela = [
    (0.00,        180000.00, 0.04,   0.00, "1ª Faixa"),
    (180000.01,   360000.00, 0.073,  5940.00, "2ª Faixa"),
    (360000.01,   720000.00, 0.095, 13860.00, "3ª Faixa"),
    (720000.01, 1800000.00, 0.107, 22500.00, "4ª Faixa"),
    (1800000.01, 3600000.00, 0.143, 87300.00, "5ª Faixa"),
    (3600000.01, 4800000.00, 0.19,  378000.00, "6ª Faixa")
]

# Distribuição por faixa (valores atualizados)
distribuicao = {
    "1ª Faixa":  {"IRPJ": 0.055, "CSLL": 0.035, "COFINS": 0.1274, "PIS": 0.0276, "CPP": 0.415, "ICMS": 0.34},
    "2ª Faixa":  {"IRPJ": 0.055, "CSLL": 0.035, "COFINS": 0.1274, "PIS": 0.0276, "CPP": 0.415, "ICMS": 0.34},
    "3ª Faixa":  {"IRPJ": 0.055, "CSLL": 0.035, "COFINS": 0.1274, "PIS": 0.0276, "CPP": 0.42,  "ICMS": 0.335},
    "4ª Faixa":  {"IRPJ": 0.055, "CSLL": 0.035, "COFINS": 0.1274, "PIS": 0.0276, "CPP": 0.42,  "ICMS": 0.335},
    "5ª Faixa":  {"IRPJ": 0.055, "CSLL": 0.035, "COFINS": 0.1274, "PIS": 0.0276, "CPP": 0.42,  "ICMS": 0.335},
    "6ª Faixa":  {"IRPJ": 0.135, "CSLL": 0.10,  "COFINS": 0.2827, "PIS": 0.0613, "CPP": 0.421, "ICMS": 0.0}
}

# Função de formatação brasileira
def formatar(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Configuração da página
st.set_page_config(page_title="Simples Nacional – Comércio", layout="centered")
st.title("Simulador do Simples Nacional – Comércio (Anexo I)")
st.markdown("**Cálculo com base no período de apuração e nos 12 meses anteriores**")

# Entrada do período de apuração
periodo = st.text_input("Período de apuração (MM/AAAA)", placeholder="Ex: 03/2025")

if periodo:
    try:
        data_apuracao = datetime.strptime("01/" + periodo, "%d/%m/%Y")
        receita_mes = st.number_input(f"Receita Bruta do mês {periodo} (R$)", min_value=0.0, format="%.2f")

        # Coleta dos valores dos 12 meses anteriores
        st.markdown("### Receita Bruta dos 12 meses anteriores")
        meses = [(data_apuracao - relativedelta(months=i)).strftime("%m/%Y") for i in range(1, 13)]
        meses.reverse()
        receitas_anteriores = {}
        for mes in meses:
            receitas_anteriores[mes] = st.number_input(f"Receita de {mes}:", min_value=0.0, key=mes)

        if st.button("Calcular"):
            rbt12 = sum(receitas_anteriores.values())

            # Verifica faixa e calcula alíquota efetiva
            for faixa in tabela:
                if faixa[0] <= rbt12 <= faixa[1]:
                    aliquota_nominal = faixa[2]
                    parcela_deduzir = faixa[3]
                    nome_faixa = faixa[4]
                    break
            else:
                st.error("RBT12 fora do limite do Simples Nacional.")
                st.stop()

            aliquota_efetiva = ((rbt12 * aliquota_nominal) - parcela_deduzir) / rbt12
            imposto = receita_mes * aliquota_efetiva

            st.success("Cálculo realizado com sucesso!")
            st.markdown(f"- **RBT12:** {formatar(rbt12)}")
            st.markdown(f"- **Faixa:** {nome_faixa}")
            st.markdown(f"- **Alíquota Nominal:** {aliquota_nominal * 100:.2f}%")
            st.markdown(f"- **Parcela a Deduzir:** {formatar(parcela_deduzir)}")
            st.markdown(f"- **Alíquota Efetiva:** **{aliquota_efetiva * 100:.2f}%**")
            st.markdown(f"- **Imposto devido no mês:** **{formatar(imposto)}**")

            # Distribuição dos tributos
            st.markdown("### Distribuição dos Tributos:")
            dist = distribuicao[nome_faixa]
            dist_final = []
            total = 0
            for tributo, perc in dist.items():
                if tributo == "ICMS" and rbt12 > 3600000:
                    valor = 0.0
                else:
                    valor = imposto * perc
                total += valor
                dist_final.append({"Tributo": tributo, "Valor": formatar(valor)})

            dist_final.append({"Tributo": "**Total**", "Valor": f"**{formatar(total)}**"})
            df_resultado = pd.DataFrame(dist_final)
            st.table(df_resultado)

            # Alerta sobre ICMS fora do Simples
            if rbt12 > 3600000:
                st.warning("⚠️ RBT12 superior ao valor de R$ 3.600.000,00 – ICMS a ser recolhido pelo regime normal de tributação seguindo as regras do seu Estado.")

            # Rodapé institucional
            st.markdown("""
            <div style="text-align: justify; font-size: 0.9rem; margin-top: 20px;">
            <strong>Cálculo atualizado em Maio/2025. Desenvolvido por Reginaldo Ramos | Explica no Quadro!</strong><br>
            Esta é uma ferramenta auxiliar para a atividade de planejamento fiscal e tributário. Sempre consultar a legislação aplicável para o cálculo e recolhimento de tributos.
            </div>
            """, unsafe_allow_html=True)

    except ValueError:
        st.error("Formato inválido para o período. Use MM/AAAA.")
