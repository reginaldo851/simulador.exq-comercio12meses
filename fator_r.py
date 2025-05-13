from datetime import datetime

# Tabelas de cálculo
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

# Distribuição Anexo III
distribuicao_iii = {
    "1ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1282, "PIS": 0.0278, "CPP": 0.434, "ISS": 0.335},
    "2ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1405, "PIS": 0.0305, "CPP": 0.434, "ISS": 0.32},
    "3ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1364, "PIS": 0.0296, "CPP": 0.434, "ISS": 0.325},
    "4ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1364, "PIS": 0.0296, "CPP": 0.434, "ISS": 0.325},
    "5ª Faixa": {"IRPJ": 0.04, "CSLL": 0.035, "COFINS": 0.1282, "PIS": 0.0278, "CPP": 0.434, "ISS": 0.335},
    "6ª Faixa": {"IRPJ": 0.35, "CSLL": 0.15, "COFINS": 0.1603, "PIS": 0.0347, "CPP": 0.305, "ISS": 0.0}
}

# Distribuição Anexo V (última versão importada)
distribuicao_v = {
    "1ª Faixa": {"IRPJ": 0.155, "CSLL": 0.035, "COFINS": 0.1101, "PIS": 0.0239, "CPP": 0.314, "ISS": 0.362},
    "2ª Faixa": {"IRPJ": 0.17, "CSLL": 0.035, "COFINS": 0.1151, "PIS": 0.0249, "CPP": 0.314, "ISS": 0.341},
    "3ª Faixa": {"IRPJ": 0.17, "CSLL": 0.035, "COFINS": 0.1151, "PIS": 0.0249, "CPP": 0.314, "ISS": 0.341},
    "4ª Faixa": {"IRPJ": 0.17, "CSLL": 0.035, "COFINS": 0.1151, "PIS": 0.0249, "CPP": 0.314, "ISS": 0.341},
    "5ª Faixa": {"IRPJ": 0.17, "CSLL": 0.035, "COFINS": 0.1151, "PIS": 0.0249, "CPP": 0.314, "ISS": 0.341},
    "6ª Faixa": {"IRPJ": 0.135, "CSLL": 0.10, "COFINS": 0.2827, "PIS": 0.0613, "CPP": 0.421, "ISS": 0.0}
}

# Redistribuição do excedente do ISS
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

# Entradas
periodo = input("Período de apuração (MM/AAAA): ")
data = datetime.strptime("01/" + periodo, "%d/%m/%Y")
receita_mes = float(input("Receita bruta do mês: R$ ").replace(",", "."))
rbt12 = float(input("Receita bruta total dos últimos 12 meses (RBT12): R$ ").replace(",", "."))
folha12 = float(input("Total da folha de salários dos últimos 12 meses: R$ ").replace(",", "."))
rba = float(input("Receita Bruta Anual (RBA): R$ ").replace(",", "."))

# Cálculo do Fator R
if rbt12 == 0 and folha12 == 0:
    fator_r = 0.01
elif rbt12 == 0 and folha12 > 0:
    fator_r = 0.28
elif rbt12 > 0 and folha12 == 0:
    fator_r = 0.01
else:
    fator_r = folha12 / rbt12

# Anexo e distribuição
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
    print("RBT12 fora do limite permitido.")
    exit()

# Cálculo final
aliquota_efetiva = ((rbt12 * aliquota) - deduzir) / rbt12
imposto = receita_mes * aliquota_efetiva

# Distribuição
dist = distribuicao[nome_faixa].copy()
valores = {trib: imposto * perc for trib, perc in dist.items()}

# Regra do ISS
limite_iss = receita_mes * 0.05
if valores["ISS"] > limite_iss:
    excedente = valores["ISS"] - limite_iss
    valores["ISS"] = limite_iss
    for trib in ["IRPJ", "CSLL", "COFINS", "PIS", "CPP"]:
        valores[trib] += excedente * redistribuicao_excedente[trib]

# Exibição
print("\nResumo do Cálculo:")
print(f"Período: {periodo}")
print(f"Anexo: {anexo}")
print(f"Faixa: {nome_faixa}")
print(f"Fator R: {fator_r:.2%}")
print(f"Alíquota Efetiva: {aliquota_efetiva * 100:.2f}%")
print(f"Imposto Devido: {formatar(imposto)}\n")

print("Distribuição dos Tributos:")
for trib, valor in valores.items():
    print(f"{trib}: {formatar(valor)}")

print(f"\nTotal distribuído: {formatar(sum(valores.values()))}")

# Regras do ISS fora do Simples
if rba > 4320000.00:
    print("\n⚠️ ISS a ser recolhido FORA do Simples Nacional no mês seguinte.")
elif rba > 3600000.00:
    print("\n⚠️ ISS a ser recolhido FORA do Simples Nacional no ano seguinte.")

# Regras de exclusão do Simples
if rba > 5760000.00:
    print("❗ Empresa sujeita a EXCLUSÃO do Simples Nacional a partir do mês seguinte.")
elif rba > 4800000.00:
    print("❗ Empresa sujeita a EXCLUSÃO do Simples Nacional a partir do ano seguinte.")
