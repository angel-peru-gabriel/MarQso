# Cálculo del cambio de energía interna (Delta U) de un gas

# Datos proporcionados
masa = 49  # masa en kg
Cp = 4.69 * 1000  # Calor específico a presión constante en J/kg·K
M_molar = 93  # Masa molar en g/mol
Tc = 555  # Temperatura crítica en K

# Estado inicial y final
multiplicador_T1 = 3.92
multiplicador_T2 = 2.06

# Constante de los gases ideales
R_universal = 8.314  # J/mol·K

# 1. Convertir masa molar a kg/mol
M_molar_kg = M_molar / 1000  # kg/mol

# 2. Calcular R específico
R_especifico = R_universal / M_molar_kg  # J/kg·K

# 3. Calcular Cv
Cv = Cp - R_especifico  # J/kg·K

# 4. Calcular Delta T
delta_T = Tc * (multiplicador_T2 - multiplicador_T1)  # K

# 5. Calcular Delta U
delta_U_J = masa * Cv * delta_T  # en Joules
delta_U_kJ = delta_U_J / 1000  # en kJ

# 6. Redondear al entero más cercano
delta_U_kJ = round(delta_U_kJ)

# Mostrar resultado
print(f"El cambio de energía interna es {delta_U_kJ} kJ")
