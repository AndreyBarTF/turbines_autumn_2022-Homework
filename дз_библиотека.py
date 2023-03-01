# -*- coding: utf-8 -*-
"""ДЗ Библиотека.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/AndreyBarTF/turbines_autumn_2022-Homework/blob/GAS-%D0%94%D0%97.1/%D0%94%D0%97%20%D0%91%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B0.ipynb

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

def check (CH, N2, CO2):
  sum = 0
  for value in CH:
    sum += CH
  sum = sum + N2 + CO2
  if (sum == 1): 
    return True 
  else:
    return False

def Qnp (CH):
  Qnp = 358.2 * CH[0] + 637.46 * CH[1] + 860.05 * CH[2] + 1185.8 * CH[3]
  return Qnp

#def Btg(Ngtu, effgtu, Qnp):
  #Btg = Ngtu/(effgtu * Qnp)
  #return Btg

def V0 (CH):
  sum = 0
  m = 1 
  n = 4
  for value in CH:
   sum += (m + (n/4)) * value
   m += 1
   n += 2
  V0 = 0.0476 * sum
  return V0

def V0N2 (V0, N2):
  V0N2 = 0.79 * V0 + 0.01 * N2
  return V0N2

def V0RO2 (CH, CO2):
  sum = 0
  m = 1 
  for value in CH:
   sum += m * value
   m += 1
  V0RO2 = 0.01 * (CO2 + sum) 
  return V0RO2

def V0HO2 (CH, V0):
  sum = 0
  n = 4
  for value in CH:
   sum += (n/2) * value
   n += 2
  V0HO2 = 0.01 * (sum + 1.61 * V0) 
  return V0HO2

def VHO2 (V0HO2, alfa, V0):
  VHO2 = V0HO2 + 0.0161 * (alfa - 1) * V0
  return VHO2

def Vg (V0RO2, V0N2, VHO2, V0, alfa):
  Vg = V0RO2 + V0N2 + VHO2 + (alfa - 1) * V0
  return Vg

def Cco2 (Tg):
  Cco2 = 4.1868 * ((4.5784 * math.pow(10, -11) * (Tg ** 3)) - (1.51719 * math.pow(10, -7) * (Tg ** 2)) + (2.50113 * math.pow(10, -4) * Tg) + 0.382325)
  return Cco2

def CN2 (Tg):
  CN2 = 4.1868 * ((-2.24553 * math.pow(10, -11) * (Tg ** 3)) + (4.85082 * math.pow(10, -8) * (Tg ** 2)) - (2.90598 * math.pow(10, -6) * Tg) + 0.309241)
  return CN2

def Ch2o (Tg):
  Ch2o = 4.1868 * ((-2.10956 * math.pow(10, -11) * (Tg ** 3)) + (4.9732 * math.pow(10, -8) * (Tg ** 2)) + (2.60629 * math.pow(10, -5) * Tg) + 0.356691)
  return Ch2o

def Cvozd (Tg):
  Cvozd = 4.1868 * ((-2.1717 * math.pow(10, -11) * (Tg ** 3)) + (4.19344 * math.pow(10, -8) * (Tg ** 2)) + (8.00891 * math.pow(10, -6) * Tg) + 0.315027)
  return Cvozd

def hg0 (V0RO2, Cco2, V0N2, CN2, VHO2, Ch2o, Tg):
  hg0 = Tg * (V0RO2 * Cco2 + V0N2 * CN2 + VHO2 * Ch2o)
  return hg0

def hvozd0 (V0, Cvozd, Tg):
  hvozd0 = Tg * (V0 * Cvozd)
  return hvozd0

def Hg0 (hg0, alfa, hvozd0):
  Hg0 = hg0 + (alfa - 1) * hvozd0
  return Hg0

def PVRT (Vg, R, Tg):
  PVRT = (R * Tg) / Vg
  return PVRT

def all (alfa, name, Tg):
  gas_info = [
    {"name":"Уренгойское", 'CH': [0.984, 0.001, 0, 0, 0], 'N2': 0.012, 'CO2':0.003},
    {"name":"Ямбургское", 'CH': [0.986, 0.001, 0, 0, 0], 'N2': 0.012, 'CO2':0.001},
    {"name":"Заполярное", 'CH': [0.993, 0.001, 0, 0, 0], 'N2': 0.004, 'CO2':0.002},
    {"name":"Медвежье", 'CH': [0.973, 0.01, 0.001, 0.001, 0.001], 'N2': 0.005, 'CO2':0.005},
    {"name":"Оренбургское", 'CH': [0.8377, 0.046, 0.0164, 0.0081, 0.0188], 'N2': 0.0434, 'CO2':0.0087},
    {"name":"Вуктыльское", 'CH': [0.751, 0.089, 0.036, 0.015, 0.064], 'N2': 0.044, 'CO2':0.001},
    {"name":"Шебелинское", 'CH': [0.9207, 0.0326, 0.0059, 0.0018, 0.006], 'N2': 0.013, 'CO2':0.02},
    {"name":"Газлинское", 'CH': [0.969, 0.0174, 0.0004, 0.0001, 0.0001], 'N2': 0.0115, 'CO2':0.0015},
    {"name":"Астраханское", 'CH': [0.9048, 0.0207, 0.0099, 0.0175, 0.0061], 'N2': 0.0345, 'CO2':0.0065}
    ]
  i = 0
  for j in range(len(gas_info)):
    if (gas_info[j]["name"] == name):
        i = j
  CH = gas_info[i]['CH']
  N2 = gas_info[i]['N2']
  CO2 = gas_info[i]['CO2']
  #Tg = 450
  R = 8.3144598
  Q_np = Qnp(CH) 
  V_0 = V0(CH)
  V_0N2 = V0N2(V_0, 0.005)
  V_0RO2 = V0RO2(CH, 0.005)
  V_0HO2 = V0HO2(CH, V_0)
  V_HO2 = VHO2(V_0HO2, 3.131, V_0)
  V_g = Vg(V_0RO2, V_0N2, V_HO2, V_0, 3.131)
  C_co2 = Cco2(Tg)
  C_N2 = CN2(Tg)
  C_h2o = Ch2o(Tg)
  C_vozd = Cvozd(Tg)
  hg_0 = hg0(V_0RO2, C_co2, V_0N2, C_N2, V_HO2, C_h2o, Tg)
  hvozd_0 = hvozd0(V_0, C_vozd, Tg)
  Hg_0 = Hg0(hg_0, alfa, hvozd_0)
  PV_RT = PVRT(V_g, R, Tg)
  return (Q_np, V_g, Hg_0, PV_RT)

print(all(3.313, 'Медвежье', 450))