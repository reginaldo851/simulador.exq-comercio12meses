import streamlit as st
import pandas as pd

# Título da aplicação
st.title("Cálculo do Simples Nacional - Anexo III (1º mês de atividade)")

try:
    # Mensagem antes do campo de entrada em caixa verde
    st.success("Informe abaixo a receita bruta do primeiro mês de atividade da empresa para calcular o valor devido no Simples Nacional:")

    # Entrada do usuário: receita bruta do primeiro mês
    receita_mes = st.number_input("Receita bruta do primeiro mês (R$):", min_value=0.0, format="%.2f")

    # Botão azul para iniciar o cálculo
    calcular = st.markdown("""
        <style>
            .stButton>button {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                border: none;
                padding: 0.5em 1em;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
        <form action="#">
            <button type="submit">Calcular</button>
        </form>
    """, unsafe_allow_html=True)

    if receita_mes > 0:
        # Cálculo da receita bruta dos 12 meses (RBT12)
        rbt12 = receita_mes * 12

        # Tabela do Anexo III
        faixas = [
            (180000.00, 0.06, 0.00),
            (360000.00, 0.112, 9360.00),
            (720000.00, 0.135, 17640.00),
            (1800000.00, 0.16, 35640.00),
            (3600000.00, 0.21, 125640.00),
            (4800000.00, 0.33, 648000.00),
        ]

        # Distribuição por faixa (incluindo a 6ª faixa com ISS = 0%)
        distribuicoes = [
            {"IRPJ": 0.04, "CSLL": 0.035, "Cofins": 0.1282, "PIS/Pasep": 0.0278, "CPP": 0.434, "ISS": 0.335},
            {"IRPJ": 0.04, "CSLL": 0.035, "Cofins": 0.1405, "PIS/Pasep": 0.0305, "CPP": 0.434, "ISS": 0.320},
            {"IRPJ": 0.04, "CSLL": 0.035, "Cofins": 0.1364, "PIS/Pasep": 0.0296, "CPP": 0.434, "ISS": 0.325},
            {"IRPJ": 0.04, "CSLL": 0.035, "Cofins": 0.1364, "PIS/Pasep": 0.0296, "CPP": 0.434, "ISS": 0.325},
            {"IRPJ": 0.04, "CSLL": 0.035, "Cofins": 0.1282, "PIS/Pasep": 0.0278, "CPP": 0.434, "ISS": 0.335},
            {"IRPJ": 0.04, "CSLL": 0.035, "Cofins": 0.1261, "PIS/Pasep": 0.0274, "CPP": 0.434, "ISS": 0.00},
        ]

        # Determinação da faixa e distribuição
        for i, (teto, aliquota_nominal, parcela_deduzir) in enumerate(faixas):
            if rbt12 <= teto:
                distribuicao = distribuicoes[i]
                break

        # Cálculo da alíquota efetiva
        aliquota_efetiva = ((rbt12 * aliquota_nominal) - parcela_deduzir) / rbt12

        # Cálculo do valor devido
        valor_devido = receita_mes * aliquota_efetiva

        st.markdown("### Resultado do Cálculo")
        st.write(f"Receita Bruta Acumulada (RBT12): R$ {rbt12:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
        st.write(f"Alíquota Nominal: {aliquota_nominal * 100:.2f}%")
        st.write(f"Parcela a Deduzir: R$ {parcela_deduzir:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
        st.write(f"Alíquota Efetiva: {aliquota_efetiva * 100:.2f}%")
        st.success(f"Valor devido do Simples Nacional: R$ {valor_devido:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

        # Verificação do sublimite para ISS
        calcular_iss = rbt12 <= 3600000.00

        if not calcular_iss:
            st.warning("Receita bruta dos últimos 12 meses excede R$ 3.600.000,00. O ISS deve ser recolhido fora do Simples Nacional.")

        # Distribuição dos tributos
        st.markdown("### Distribuição dos Tributos")
        distribuicao_final = {}
        total_base = 1 - distribuicao["ISS"] if calcular_iss else 1
        excedente_iss = 0

        for tributo, percentual in distribuicao.items():
            distribuicao_final[tributo] = percentual * valor_devido if (tributo != "ISS" or calcular_iss) else 0

        # Novo limite: 5% da receita do mês
        if calcular_iss:
            limite_iss = receita_mes * 0.05
            if distribuicao_final["ISS"] > limite_iss:
                excedente_iss = distribuicao_final["ISS"] - limite_iss
                distribuicao_final["ISS"] = limite_iss
                for tributo in [k for k in distribuicao_final if k != "ISS"]:
                    proporcao = distribuicao[tributo] / total_base
                    distribuicao_final[tributo] += excedente_iss * proporcao

        for tributo, valor in distribuicao_final.items():
            st.write(f"{tributo}: R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

        if excedente_iss > 0:
            st.info("O valor do ISS foi limitado a 5% da receita mensal. A diferença foi redistribuída proporcionalmente aos demais tributos.")

        # Rodapé institucional
        st.markdown("---")
        st.markdown("**Cálculo atualizado em Maio/2025.** Desenvolvido por Reginaldo Ramos | Explica no Quadro! Esta é uma ferramenta auxiliar para a atividade de planejamento fiscal e tributário. Sempre consultar a legislação aplicável para o cálculo e recolhimento de tributos.")

        # Botão verde do WhatsApp
        st.markdown("""
            <a href="https://wa.me/554133284014" target="_blank">
                <button style="background-color:green;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-weight:bold;">
                    WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error("Erro ao processar o cálculo. Se possível, comunicar o erro para contato@explicanoquadro.com.br.")
    st.markdown("[Fale comigo no WhatsApp](https://wa.me/554133284014)")
