# -*- coding: utf-8 -*-
"""ДЗ_Библиотека.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/AndreyBarTF/turbines_autumn_2022-Homework/blob/GAS-%D0%94%D0%97.1/%D0%94%D0%97_%D0%91%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B0.ipynb

*   ФИО Барбашин Андрей Алексеевич
*   Группа ТФэ-01-20
*   Тлеграмм @QwertyAlexx

Написать модуль кода в .py файле для дайльнейшего переиспользования в других домашних работах Модуль должен как минимум:

1. Считать объемы продуктов сгорания
2. Этальпию воздуха и продуктов сгорания
3. PV=RT
4. Процессов расширения (Опционально, все равно придется потом расширять)
"""

import numpy as np
import math

R = 8.3144598
GAS_INFO = {"Уренгойское": {"CH": [98.4, 0.1, 0, 0, 0], 'N2': 1.2, 'CO2':0.3},
     "Ямбургское": {"CH": [98.6, 0.1, 0, 0, 0], 'N2': 1.2, 'CO2':0.1},
     "Заполярное": {"CH": [99.3, 0.1, 0, 0, 0], 'N2': 0.4, 'CO2':0.2},
     "Медвежье": {"CH": [97.3, 1, 0.1, 0.1, 0.1], 'N2': 0.5, 'CO2':0.5},
     "Оренбургское": {"CH": [83.77, 4.6, 1.64, 0.81, 1.88], 'N2': 4.34, 'CO2':0.87},
     "Вуктыльское": {"CH": [75.1, 8.9, 3.6, 1.5, 6.4], 'N2': 4.4, 'CO2':0.1},
     "Шебелинское": {"CH": [92.07, 3.26, 0.59, 0.18, 0.6], 'N2': 1.3, 'CO2':2},
     "Газлинское": {"CH": [96.9, 1.74, 0.04, 0.01, 0.01], 'N2': 1.15, 'CO2':0.15},
     "Астраханское": {"CH": [90.48, 2.07, 0.99, 1.75, 0.61], 'N2': 3.45, 'CO2':0.65}
    }

def check (CH, N2, CO2):
  summ = sum(CH) + N2 + CO2
  if summ != 100:
    raise ValueError('Проверь сумму компонентов!!!   \0/ ')

def Heat_calculation (CH):
  Qnp = 358.2 * CH[0] + 637.46 * CH[1] + 860.05 * CH[2] + 1185.8 * CH[3]
  return Qnp

def air_volume_calculation (CH):
  sum = 0
  m = 1 
  n = 4
  for value in CH:
    sum += (m + (n/4)) * value
    m += 1
    n += 2
    V0 = 0.0476 * sum
  return V0

def nitrogen_volume_calculation (V0, N2):
  V0N2 = 0.79 * V0 + 0.01 * N2
  return V0N2

def calculation_of_the_volume_of_triatomic_gases (CH, CO2):
  sum = 0
  m = 1 
  for value in CH:
    sum += m * value
    m += 1
    V0RO2 = 0.01 * (CO2 + sum) 
  return V0RO2

def water_volume_calculation (CH, V0):
  sum = 0
  n = 4
  for value in CH:
    sum += (n/2) * value
    n += 2
    V0HO2 = 0.01 * (sum + 1.61 * V0) 
  return V0HO2

def actual_water_volume_calculation (V0HO2, alfa, V0):
  VHO2 = V0HO2 + 0.0161 * (alfa - 1) * V0
  return VHO2

def calculation_of_the_volume_of_combustion_products (V0RO2, V0N2, VHO2, V0, alfa):
  Vg = V0RO2 + V0N2 + VHO2 + (alfa - 1) * V0
  return Vg

def heat_capacity_calculation_co2 (Tg):
  Cco2 = 4.1868 * ((4.5784 * 1e-11 * (Tg ** 3)) - (1.51719 * 1e-7 * (Tg ** 2)) + (2.50113 * 1e-4 * Tg) + 0.382325)
  return Cco2

def heat_capacity_calculation_N2 (Tg):
  CN2 = 4.1868 * ((-2.24553 * 1e-11 * (Tg ** 3)) + (4.85082 * 1e-8 * (Tg ** 2)) - (2.90598 * 1e-6 * Tg) + 0.309241)
  return CN2

def heat_capacity_calculation_h2o (Tg):
  Ch2o = 4.1868 * ((-2.10956 * 1e-11 * (Tg ** 3)) + (4.9732 * 1e-8 * (Tg ** 2)) + (2.60629 * 1e-5 * Tg) + 0.356691)
  return Ch2o

def heat_capacity_calculation_vozd (Tg):
  Cvozd = 4.1868 * ((-2.1717 * 1e-11 * (Tg ** 3)) + (4.19344 * 1e-8 * (Tg ** 2)) + (8.00891 * 1e-6 * Tg) + 0.315027)
  return Cvozd

def calculation_of_the_enthalpy_of_combustion_products (V0RO2, Cco2, V0N2, CN2, VHO2, Ch2o, Tg):
  hg0 = Tg * (V0RO2 * Cco2 + V0N2 * CN2 + VHO2 * Ch2o)
  return hg0

def air_enthalpy_calculation (V0, Cvozd, Tg):
  hvozd0 = Tg * (V0 * Cvozd)
  return hvozd0

def enthalpy_calculation (hg0, alfa, hvozd0):
  Hg0 = hg0 + (alfa - 1) * hvozd0
  return Hg0

def all (alfa, name, Tg):
  CH = GAS_INFO[name]['CH']
  N2 = GAS_INFO[name]['N2']
  CO2 = GAS_INFO[name]['CO2']
  check(CH, N2, CO2)
  Qnp = Heat_calculation(CH) 
  V0 = air_volume_calculation(CH)
  V0N2 = nitrogen_volume_calculation(V0, N2)
  V0RO2 = calculation_of_the_volume_of_triatomic_gases(CH, CO2)
  V0HO2 = water_volume_calculation(CH, V0)
  VHO2 = actual_water_volume_calculation(V0HO2, alfa, V0)
  Vg = calculation_of_the_volume_of_combustion_products(V0RO2, V0N2, VHO2, V0, alfa)

  Cco2 = heat_capacity_calculation_co2(Tg)
  CN2 = heat_capacity_calculation_N2(Tg)
  Ch2o = heat_capacity_calculation_h2o(Tg)
  Cvozd = heat_capacity_calculation_vozd(Tg)

  hg0 = calculation_of_the_enthalpy_of_combustion_products(V0RO2, Cco2, V0N2, CN2, VHO2, Ch2o, Tg)
  hvozd0 = air_enthalpy_calculation(V0, Cvozd, Tg)
  Hg0 = enthalpy_calculation(hg0, alfa, hvozd0)

  return (Qnp, Vg, Hg0)
  
def PV_RT (P=None, V=None, Tg=None):
  if (P):
    if (Tg):
      if (V):
        print("ошибка")
      else:  
        P = int(P)
        Tg = int(Tg)
        V = (R * Tg) / P
    else:
      P = int(P)
      V = int(V)
      Tg = (P * V) / R
  else:
    V = int(V)
    Tg = int(Tg)
    P = (R * Tg) / V
  return P, V, Tg

print(all(3.313, "Астраханское", 450))
print(PV_RT(12000, 25))