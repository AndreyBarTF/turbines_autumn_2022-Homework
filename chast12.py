# -*- coding: utf-8 -*-
""""chast12.ipynb""

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bJ0oObpl274USZF3rjLcAIu5zvuqn5mb
"""

import matplotlib.pyplot as plt
import numpy as np
import iapws
from iapws import IAPWS97 as gas

import pandas as pd 
import math as m

MPa = 10 ** 6
kPa = 10 ** 3
unit = 1 / MPa
to_kelvin = lambda x: x + 273.15 if x else None

#Потери давления
def real_point(p_0, p_middle):
  delta_p0 = 0.05 *  p_0
  delta_p_middle = 0.1 * p_middle
  delta_p_1 = 0.03 * p_middle

  real_p0 = p_0 - delta_p0
  real_p1t = p_middle + delta_p_middle
  real_p_middle = p_middle - delta_p_1
  return real_p0,real_p1t,real_p_middle
      
def get_points(p_0, t_0, p_middle, t_middle, p_k, p_feed_water, t_feed_water, internal_efficiency):
  real_p0,real_p1t,real_p_middle = real_point(p_0, p_middle)
  _point_0 = gas(P = p_0 * unit, T=to_kelvin(t_0))
  point_0 = gas(P=real_p0 * unit, h=_point_0.h)
  point_1t = gas(P=real_p1t * unit, s=_point_0.s)

  hp_heat_drop = (_point_0.h - point_1t.h) * internal_efficiency
  h_1 = point_0.h - hp_heat_drop
  point_1 = gas(P=real_p1t * unit, h=h_1)

  _point_middle = gas(P=p_middle * unit, T=to_kelvin(t_middle))
  point_middle = gas(P=real_p_middle * unit, h=_point_middle.h)
  point_2t = gas(P=p_k * unit, s=_point_middle.s)

  lp_heat_drop = (_point_middle.h - point_2t.h) * internal_efficiency
  h_2 = point_middle.h - lp_heat_drop
  point_2 = gas(P=p_k * unit, h=h_2)
  point_k_water = gas(P=p_k * unit, x=0)
  point_feed_water = gas(P=p_feed_water * unit, T=to_kelvin(t_feed_water))
  return _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water

def get_coeff(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency):
  _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water = get_points(p_0, t_0, p_middle, t_middle, p_k, p_feed_water, t_feed_water, internal_efficiency) 
  coeff = (point_feed_water.T - point_2.T) / (to_kelvin(374.2) - point_2.T)
  print("Значение по оси абсцисс для расчета кси", coeff)
  return coeff

def coeff():
  print("Зная значение по оси абсцисс (ось x), определите значение по оси ординат (ось y), с учетом заданного количества подогревателей (z)")
  coef = float(input("Введите коэффициент с графика "))
  return coef

def get_ksi(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency):
  _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water = get_points(p_0, t_0, p_middle, t_middle, p_k, p_feed_water, t_feed_water, internal_efficiency)
  numenator_without = point_2.T * (_point_middle.s - point_k_water.s)
  denumenator_without = (point_0.h - point_1t.h) + (point_middle.h - point_k_water.h)
  without_part = 1 - (numenator_without / denumenator_without)

  numenator_infinity = point_2.T * (_point_middle.s - point_feed_water.s)
  denumenator_infinity = (point_0.h - point_1t.h) + (point_middle.h - point_feed_water.h)
  infinity_part = 1 - (numenator_infinity / denumenator_infinity)

  ksi_infinity = 1 - (without_part / infinity_part)  
  coef = coeff()
  ksi = coef * ksi_infinity
  return ksi

#КПД
def get_eff(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency):
  _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water = get_points(p_0, t_0, p_middle, t_middle, p_k, p_feed_water, t_feed_water, internal_efficiency)
  ksi = get_ksi(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  eff_num = hp_heat_drop + lp_heat_drop
  eff_denum = hp_heat_drop + (point_middle.h - point_k_water.h)

  efficiency = (eff_num / eff_denum) * (1 / (1 - ksi))

  estimated_heat_drop = efficiency * ((point_0.h - point_feed_water.h) + (point_middle.h - point_1.h))

  return efficiency, estimated_heat_drop

#Массовый расход в турбину на входе
def get_inlet_mass_flow(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency):
  _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water = get_points(p_0, t_0, p_middle, t_middle, p_k, p_feed_water, t_feed_water, internal_efficiency)
    
  efficiency, estimated_heat_drop = get_eff(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  inlet_mass_flow = electrical_power / (estimated_heat_drop * 1000 * mechanical_efficiency * generator_efficiency)
  return inlet_mass_flow

#Массовый расход в конденсатор
def get_condenser_mass_flow(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency):
  efficiency, estimated_heat_drop = get_eff(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water = get_points(p_0, t_0, p_middle, t_middle, p_k, p_feed_water, t_feed_water, internal_efficiency)
  condenser_mass_flow = (electrical_power /((point_2.h - point_k_water.h) * 1000 * mechanical_efficiency * generator_efficiency) * ((1 / efficiency) - 1))
  return condenser_mass_flow

def all(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency):
  real_p0, real_p1t, real_p_middle = real_point(p_0, p_middle) 
  _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water = get_points(p_0, t_0, p_middle, t_middle, p_k, p_feed_water, t_feed_water, internal_efficiency)
  coeff = get_coeff(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  ksi = get_ksi(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  efficiency, estimated_heat_drop = get_eff(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  G_0 = get_inlet_mass_flow(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  G_k = get_condenser_mass_flow(p_0, t_0, p_middle, t_middle, p_k, t_feed_water, electrical_power, p_feed_water, internal_efficiency, mechanical_efficiency,generator_efficiency)
  return real_p0, real_p1t, real_p_middle, _point_0, point_0, point_1t, hp_heat_drop, point_1, _point_middle, point_middle, lp_heat_drop, point_2, point_2t, point_k_water, point_feed_water, ksi, efficiency, estimated_heat_drop, G_0, G_k

#Построение процесса расширения в турбине 
def legend_without_duplicate_labels(ax: plt.Axes) -> None:
    """
    Убирает дубликаты из легенды графика
    :param plt.Axes ax: AxesSubplot с отрисованными графиками
    :return None:
    """
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique))

def get_isobar(point):
  s = point.s
  points_s = np.arange(s * 0.9, s * 1.1, 0.2 * s / 1000)     
  points_h = [gas(P=point.P, s=_s).h for _s in points_s]  
  return points_h, points_s

def get_isoterm_steam(point):
  p = point.P
  s = point.s
  p_00 = np.arange(p * 0.8, p * 1.2, 0.4 * p / 1000)
  points_ss = [] 
  points_hh = []
  for value in p_00:
    if (gas(P = value, T=point.T).s > s * 0.8 and gas(P = value, T=point.T).s < s * 1.2):
      points_ss.append(gas(P = value, T=point.T).s)
      points_hh.append(gas(P = value, T=point.T).h)
  return points_hh, points_ss

def get_isoterm_two_phases(point):
    """
    Собрать координаты изотермы для влажного пара в hs осях    
    """
    x = point.x
    p = point.P
    x_values = np.arange(x * 0.9, min(x * 1.1, 1), (1 - x) / 1000)
    h_values = np.array([gas(P=p, x=_x).h for _x in x_values])
    s_values = np.array([gas(P=p, x=_x).s for _x in x_values])
    return h_values, s_values

def get_isoterm(point):
    """
    Собрать координаты изотермы в hs осях
    """
    if point.phase == 'Two phases':
        return get_isoterm_two_phases(point)
    return get_isoterm_steam(point)

def plot_hs(points: list, ax):
  for point in points:
    isobar_h, isobar_s = get_isobar(point)    
    isoterm_h, isoterm_s = get_isoterm(point)  
    ax.plot(isobar_s, isobar_h, color="blue", label='Изобара')   
    ax.plot(isoterm_s, isoterm_h, color="red", label='Изотерма')
    ax.scatter(point.s, point.h,  s=40, color="yellow")
    ax.set_xlabel(r"S, $\frac{кДж}{кг * K}$", fontsize=14)
    ax.set_ylabel(r"h, $\frac{кДж}{кг}$", fontsize=14)
    ax.set_title("HS-диаграмма процесса расширения", fontsize=18)
    ax.legend()
    
    legend_without_duplicate_labels(ax)   
       
def plot_process(points, ax, **kwargs):
  ax.plot([point.s for point in  points], [point.h for point in points], **kwargs)

def calculation_of_circumferential_speed(avg_diameter, rotation_speed):
  u = m.pi * avg_diameter * rotation_speed 
  return u

#расчет параметров для выбора сопловой решетки
def calculation_of_parameters_for_the_nozzle(H_0, G_0, point_0, ro):
  Ho_c = (1 - ro) * H_0
  Ho_p = H_0 * ro
  h1t = point_0.h - Ho_c
  c1t = m.sqrt(2 * Ho_c * 1000)
  point_1_t = gas(h = h1t, s = point_0.s)
  k = 1.4
  a1t = m.sqrt(k * (point_1_t.P * MPa) * point_1_t.v)
  #a1t = point_1_t.w
  M1t = c1t / a1t
  mu1 = 0.97
  F1_ = (G_0 * point_1_t.v) / (mu1 * c1t)
  return Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_, point_1_t

#вывод параметров в табличном виде
def data_output(Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_, point_1_t):
  d = {
      'Name': ["Теплоперепад в сопловой решётке", 
              "Теплоперепад в рабочей решётке", 
              "Теоретическая энтальпия пара за сопловой решёткой", 
              "Теоретическая абсолютная скорость на выходе из сопловой решётки", 
              "Скорость звука на выходе из сопловой решётки", 
              "Число Маха на выходе из сопловой решётки", 
              "Предварительная площадь выхода потока из сопловой решётки"],
     'Parameters': ["Ho_c", "Ho_p", "h1t", "c1t", "a1t", "M1t", "F1_"],
    'Value': [Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#параметры выбранной сопловой решетки С-90-15А
def selection_of_the_nozzle_grating_profile():
  alpha0 = 90
  alpha1_e = 15
  t_opt = [0.70,0.85]
  M1t_ = 0.85
  b1 = 51.5
  f1 = 3.3
  I1_min = 0.36
  W1_min = 0.45
  return alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min ,W1_min

#вывод параметров в табличном виде
def data_output1(alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min, W1_min):
  d = {
     'Name': ["Угол выхода потока из решётки", 
              "Угол входа потока в решётку", 
              "Оптимальный шаг решётки", 
              "Число Маха предварительное", 
              "Хорда сопловой решётки", 
              "Площадь поперечного сечения сопловой решётки", 
              "Момент инерции сопловой решётки", 
              "Момент сопротивления сопловой решётки"],
     'Parameters': ["alpha1_e", "alpha0", "t_opt", "M1t_", "b1", "f1", "I1_min", "W1_min"],
     'Value': [alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min, W1_min]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#определение дополнительных параметров сопловой решетки С-90-15А
def Clarification_nozzle_grating(c1t, G_0, F1_, avg_diameter, alpha1_e, b1, point_1_t):
  el1 = F1_ / (m.pi * avg_diameter * m.sin(m.radians(alpha1_e)))
  e_opt = 4 * m.sqrt(el1)
  if e_opt > 0.85:
    e_opt = 0.85
  l1 = el1 / e_opt
  mu1 = 0.982 - 0.005 * ((b1 * 10**-3) / l1)
  F1 = (G_0 * point_1_t.v) / (mu1 * c1t)
  t1opt_ = 0.75
  z1 = (m.pi * avg_diameter * e_opt) / (b1 * 10**-3  * t1opt_)  
  z_1 = round(z1+0.5)-1 if (round(z1) % 2) else round(z1+0.5)
  t1opt = (m.pi * avg_diameter * e_opt) / (b1 * 10**-3  * z_1)
  return el1, e_opt, l1, mu1, F1, z_1, t1opt, z1

def data_output2(el1, e_opt, l1, mu1, F1, z_1, t1opt, z1):
  d = {
     'Name': ["Произведение el1", 
              "Оптимальное значение степени парциальности", 
              "Высота сопловых лопаток", 
              "Уточняем коэффициент расхода сопловой решетки", 
              "Выходная площадь сопловой решетки (предварительная)", 
              "Количество лопаток в сопловой решетке (предварительная)", 
              "Оптимальный относительный шаг", 
              "Количество лопаток в сопловой решетке"], 
     'Parameters': ["el1", "e_opt", "l1", "mu1", "F1", "z_1", "t1opt", "z1"],
     'Value': [el1, e_opt, l1, mu1, F1, z_1, t1opt, z1]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#параметры сопловой решетки С-90-15А из атласа
def Clarification_other_nozzle_grating_parameters(mu1, c1t, alpha1_e, t1opt, l1, b1):
  alpha_ust = alpha1_e - 16 * (t1opt - 0.75) + 23.1 #альфа установочная 
  b1_l1 = (b1 * 10 ** -3) / l1
  ksi_noz = 1.98 * 10 **(-2) #коэфф профильных потерь    
  ksi_sum = 5.9 * 10 **(-2) #коэфф профильных потерь суммарный
  ksi_end_noz = ksi_sum - ksi_noz #коэфф концевых потерь
  fi = m.sqrt(1 - ksi_sum) #Коэффициент скорости сопловой решетки φ  
  fi_ = 0.98 - 0.008 * (b1 * 10 ** -3 / l1) #Проверяем коэффициент скорости сопловой решетки φ'  
  delta_fi = (fi - fi_) / fi #Находим расхождение между φ и φ'  
  c_1 = c1t * fi #Скорость выхода пара из сопловой решетки с1  
  alpha_1 = m.degrees(m.asin((mu1/fi)* m.sin(m.radians(alpha1_e)))) #Угол alpha1 вектора скорости с1
  return alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1

def data_output3(alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1):
  d = {
     'Name': ["Угол установки профиля решётки", 
              "Отношение: b1/l1", 
              "Коэффициент профильных потерь", 
              "Коэффициент суммарных потерь", 
              "Коэффициент концевых потерь", 
              "Коэффициент скорости сопловой решетки", 
              "Коэффициент скорости сопловой решетки (уточ)", 
              "расхождение между fi и fi_",
              "Скорость выхода пара из сопловой решетки",
              "Реальный угол выхода потока из сопловой решётки"],      
     'Parameters': ["alpha_ust", "b1_l1", "ksi_noz", "ksi_sum", "ksi_end_noz", "fi", "fi_", "delta_fi", "c_1", "alpha_1"],
     'Value': [alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#расчет параметров для выбора рабочей решетки
def calculation_of_parameters_for_the_selection_of_the_working_grid(l1, fi, c_1, c1t, alpha_1, u, point_1_t, Ho_p):
  w_1 = m.sqrt(c_1 ** 2 + u ** 2 - 2 * c_1 * u * m.cos(m.radians(alpha_1)))
  beta_1 = m.degrees(m.atan(m.sin(m.radians(alpha_1)) / (m.cos(m.radians(alpha_1)) - u / c_1)))
  delta_Hc = c1t ** 2 / 2 * (1 - fi ** 2) / 1000  
  h1 = point_1_t.h + delta_Hc
  point_1_ = gas(P = point_1_t.P, h = h1)  
  h2t = point_1_.h - Ho_p
  point_2_t = gas(s = point_1_.s, h = h2t)
  w2t = m.sqrt(2 * Ho_p * 1000 + w_1 ** 2)
  delta = 0.004
  l2 = l1 + delta  
  k2 = 1.3
  a2t = m.sqrt(k2 * (point_2_t.P * MPa) * point_2_t.v)
  M2t = w2t / a2t
  return w_1, beta_1, point_1_, point_2_t, w2t, l2, a2t, M2t, delta_Hc

def data_output4(w_1, beta_1, point_1_, point_2_t, w2t, l2, a2t, M2t, delta_Hc):
  d = {
     'Name': ["Относительная скорость на выходе из сопловой решётки", 
              "Угол направления относительной скорости потока на выходе из сопловой решётки", 
              "Теоретическая относительная скорость на выходе из рабочей решётки", 
              "Высота рабочих лопаток", 
              "Скорость звука за рабочей решеткой (теоретическая)", 
              "Теоретическое число Маха за рабочей решёткой", 
              "Потери в сопловой решетке"],       
     'Parameters': ["w_1", "beta_1", "w2t", "l2", "a2t", "M2t", "delta_Hc"],
     'Value': [w_1, beta_1, w2t, l2, a2t, M2t, delta_Hc]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#выбор профиля рабочей решетки Р-46-29А
def selection_of_the_working_grid_profile():
  beta0 = 50
  beta2_e = 28 #25-32
  t_opt = [0.45,0.58]
  M2t_ = 0.85
  b2_atl = 25.6 #спросить как узнать реальный?   
  f2 = 1.22
  I2_min = 0.071
  W2_min = 0.112
  return beta0, beta2_e, t_opt, M2t_, b2_atl, f2, I2_min, W2_min

def data_output5(beta0, beta2_e, t_opt, M2t_, b2_atl, f2, I2_min, W2_min):
  d = {
     'Name': ["Угол входа потока в рабочую решётку по атласу", 
              "Угол выхода потока из рабочей решётки по атласу", 
              "Оптимальный шаг рабочей решётки", 
              "Число Маха предварительное", 
              "Хорда рабочей решётки по атласу", 
              "Площадь поперечного сечения рабочей решётки", 
              "Момент инерции рабочей решётки", 
              "Момент сопротивления рабочей решётки"],       
     'Parameters': ["beta0", "beta2_e", "t_opt", "M2t_", "b2_atl", "f2", "I2_min", "W2_min"],
     'Value': [beta0, beta2_e, t_opt, M2t_, b2_atl, f2, I2_min, W2_min]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#уточнение параметров рабочей решетки Р-46-29А
def specification_of_working_grid_parameters(e_opt, l2, b2, G_0, point_2_t, w2t, avg_diameter):
  mu2 = 0.965 - 0.01 * (b2 * 10 ** -3 / l2)
  F2 = (G_0 * point_2_t.v) / (mu2 * w2t)
  beta2_e = m.degrees(F2 / (e_opt * m.pi * avg_diameter * l2))
  t2opt = 0.55
  z2 = (m.pi * avg_diameter) / (b2 * 10 ** -3 * t2opt)
  z_2 = round(z2+0.5)-1 if (round(z2) % 2) else round(z2+0.5)
  t2opt = (m.pi * avg_diameter) / (b2 * 10 ** -3 * z2)
  beta2_ust = beta2_e - 20.5 * (t2opt - 0.60) + 47.1
  b2_l2 = (b2 * 10 ** -3) / l2  
  return mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2

def data_output6(mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2):
  d = {
     'Name': ["Коэффициент расхода рабочей решётки", 
              "Выходная площадь рабочей решётки", 
              "Эффективный угол выхода потока из рабочей решётки", 
              "Количество лопаток в рабочей решётке", 
              "Оптимальный шаг рабочей решётки", 
              "Угол установки рабочих лопаток", 
              "Отношение b2/l2"],       
     'Parameters': ["mu2", "F2", "beta2_e", "z_2", "t2opt", "beta2_ust", "b2_l2"],
     'Value': [mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#параметры рабочей решетки Р-46-29А по графикам из аталаса
def parameters_of_the_working_grid_according_to_the_atlas(u, beta2_e, b2, l2, w2t, mu2):
  ksi_grid = 4.6 * 10 **(-2) #коэфф профильных потерь    
  ksi_sum_g = 5.1 * 10 **(-2) #коэфф профильных потерь суммарный
  ksi_end_grid = ksi_sum_g - ksi_grid #коэфф концевых потерь
  psi = m.sqrt(1 - ksi_sum_g)
  psi_ = 0.96 - 0.014 * (b2 * 10 ** -3 / l2)
  delta_psi = (psi - psi_) / psi
  w_2 = w2t * psi
  beta_2 = m.degrees(m.asin((mu2 / psi) * m.sin(m.radians(beta2_e))))
  c_2 = m.sqrt(w_2 ** 2 + u ** 2 - 2 * w_2 * u * m.cos(m.radians(beta_2)))
  alpha_2 = m.degrees(m.atan((m.sin(m.radians(beta_2))) / (m.cos(m.radians(beta_2)) - u / w_2)))
  return ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2

def data_output7(ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2):
  d = {
     'Name': ["Коэффициент профильных потерь в решётке", 
              "Коэффициент суммарных потерь", 
              "Коэффициент концевых потерь", 
              "Коэффициент скорости рабочей решётки", 
              "Коэффициент скорости рабочей решётки (уточ)", 
              "расхождение между psi и psi_", 
              "Угол направления относительной скорости на выходе из рабочей решётки", 
              "Абсолютная скорость на выходе из рабочей решётки",
              "Угол выхода абсолютной скорости из рабочей решётки",
              "Действительная относительная скорость на выходе из рабочей решётки"],       
     'Parameters': ["ksi_grid", "ksi_sum_g", "ksi_end_grid", "psi", "psi_", "delta_psi", "beta_2", "c_2", "alpha_2", "w_2"],
     'Value': [ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#функция для посторения треугольников скоростей 
def construction_of_velocity_triangles(u, w_1, c_1, w_2, c_2, alpha_1, beta_2):
  sin_alpha_1 = m.sin(m.radians(alpha_1))
  cos_alpha_1 = m.cos(m.radians(alpha_1))
  sin_beta_2 = m.sin(m.radians(beta_2))
  cos_beta_2 = m.cos(m.radians(beta_2))

  c1_plot = [[0, -c_1 * cos_alpha_1], [0, -c_1 * sin_alpha_1]]
  u1_plot = [[-c_1 * cos_alpha_1, -c_1 * cos_alpha_1 + u], [-c_1 * sin_alpha_1, -c_1 * sin_alpha_1]]
  w1_plot = [[0, -c_1 * cos_alpha_1 + u], [0, -c_1 * sin_alpha_1]]
  w2_plot = [[0, w_2 * cos_beta_2], [0, -w_2 * sin_beta_2]]
  u2_plot = [[w_2 * cos_beta_2, w_2 * cos_beta_2 - u], [-w_2 * sin_beta_2, -w_2 * sin_beta_2]]
  c2_plot = [[0, w_2 * cos_beta_2 - u], [0, -w_2 * sin_beta_2]]

  fig, ax = plt.subplots(1, 1, figsize=(15, 5))
  ax.plot(c1_plot[0], c1_plot[1], label='C_1', c='red')
  ax.plot(u1_plot[0], u1_plot[1], label='u_1', c='blue')
  ax.plot(w1_plot[0], w1_plot[1], label='W_1', c='green') 
  ax.plot(w2_plot[0], w2_plot[1], label='W_2', c='green')
  ax.plot(u2_plot[0], u2_plot[1], label='u_2', c='blue')
  ax.plot(c2_plot[0], c2_plot[1], label='C_2', c='red')
  ax.set_title("Треугольник скоростей",)
  ax.legend()
  ax.grid();

#расчет соотношения u/cf
def calculation_of_the_velocity_ratio(u, H_0, fi, alpha_1, ro):
  cf = m.sqrt(2 * H_0 * 1000)
  u_cf = u / cf
  u_cf_opt = fi * m.cos(m.radians(m.radians(alpha_1))) / (2 * m.sqrt(1 - ro))
  return cf, u_cf, u_cf_opt

def data_output8(cf, u_cf, u_cf_opt):
  d = {
     'Name': ["Фиктивная скорость", 
              "Отношение скоростей", 
              "Оптимальное отношение скоростей"],       
     'Parameters': ["cf", "u_cf", "u_cf_opt"],
     'Value': [cf, u_cf, u_cf_opt]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#расчет относительного кпд
def calculation_of_relative_blade_efficiency(c_1, u, point_0, H_0, point_2_t, w2t, psi, c_2, delta_Hc, alpha_1, alpha_2):
  delta_Hp = w2t ** 2 / 2 * (1 - psi ** 2) / 1000
  h2 = point_2_t.h + delta_Hp
  point_2_ = gas(P = point_2_t.P, h = h2)
  point_t_konec = gas(h =point_0.h - H_0, P = point_2_.P)
  delta_Hvc = c_2 ** 2 / 2 / 1000 
  x_vc = 0
  E0 = H_0 - x_vc * delta_Hvc  
  eff = (E0 - delta_Hc - delta_Hp - (1 - x_vc) * delta_Hvc) / E0
  eff_ = (u * (c_1 * m.cos(m.radians(alpha_1)) + c_2 * m.cos(m.radians(alpha_2)))) / E0 / 1000
  delta_eff = (eff - eff_) / eff   
  return delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff, point_2_, point_t_konec

def data_output9(delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff, point_2_, point_t_konec):
  d = {
     'Name': ["Потери в рабочей решётке", 
              "Потери с выходной скоростью", 
              "Располагаемая энергия ступени", 
              "Лопаточный КПД по расчёту через потери энергии", 
              "Лопаточный КПД по расчёту через скорости", 
              "Расхождение eff и eff_"],       
     'Parameters': ["delta_Hp", "delta_Hvc", "E0", "eff", "eff_", "delta_eff"],
     'Value': [delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

def efficiency_graph_from_U_cf_and_avg_diameter(G_0, H_0, ro, point_0, rotation_speed):
    array_u_cf = []
    d_value = []
    efficiency_ = []
    efficiency = []
    for d_value_ in np.arange(0.9, 1.5, (1.5-0.9)/100):
        avg_diameter = d_value_
        u = calculation_of_circumferential_speed(avg_diameter, rotation_speed)
        Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_, point_1_t = calculation_of_parameters_for_the_nozzle(H_0, G_0, point_0, ro)       
        alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min ,W1_min = selection_of_the_nozzle_grating_profile()
        el1, e_opt, l1, mu1, F1, z_1, t1opt, z1 = Clarification_nozzle_grating(c1t, G_0, F1_, avg_diameter, alpha1_e, b1, point_1_t)
        alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1 = Clarification_other_nozzle_grating_parameters(mu1, c1t, alpha1_e, t1opt, l1, b1)
        w_1, beta_1, point_1_, point_2_t, w2t, l2, a2t, M2t, delta_Hc = calculation_of_parameters_for_the_selection_of_the_working_grid(l1, fi, c_1, c1t, alpha_1, u, point_1_t, Ho_p)
        beta0, beta2_e, t_opt, M2t_, b2, f2, I2_min, W2_min = selection_of_the_working_grid_profile()
        mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2 = specification_of_working_grid_parameters(e_opt, l2, b2, G_0, point_2_t, w2t, avg_diameter)
        ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2 = parameters_of_the_working_grid_according_to_the_atlas(u, beta2_e, b2, l2, w2t, mu2)
        delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff, point_2_, point_t_konec = calculation_of_relative_blade_efficiency(c_1, u, point_0, H_0, point_2_t, w2t, psi, c_2, delta_Hc, alpha_1, alpha_2)
        cf, u_cf, u_cf_opt = calculation_of_the_velocity_ratio(u, H_0, fi, alpha_1, ro)      
        array_u_cf.append(u_cf)
        d_value.append(d_value_)
        efficiency_.append(eff_)
        efficiency.append(eff)
   # Построим график зависимости внутреннего КПД ступени от общего теплоперепада в ступени H_0    
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    X1 = array_u_cf
    X2 = d_value
    Y1 = efficiency_
    Y2 = efficiency
    
    ax.plot(X1,Y1, label = 'По расчёту через скорости', color = 'blue')
    ax.plot(X1,Y2, label = 'По расчёту через потери энергии', color = 'red')
    ax.set_title("Зависимость лопаточного КПД от u/сф")
    ax.set_ylabel("Лопаточный КПД")
    ax.set_xlabel("U/сф")
    ax.legend()
    ax.grid()
    plt.show()

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    plt.plot(X2,Y1, label = 'По расчёту через скорости', color = 'blue')
    plt.plot(X2,Y2, label = 'По расчёту через потери энергии', color = 'red')
    plt.title("Зависимость лопаточного КПД от d")
    plt.ylabel("Лопаточный КПД")
    plt.xlabel("d, м")
    plt.legend()
    plt.grid()
    plt.show()

import math as ma
#определение параметров для расчета внутреннего КПД
def determination_of_parameters_for_calculating_internal_efficiency(beta2_ust, b2, e_opt, alpha1_e, avg_diameter, l2, eff, F1, ro, E0, u_cf):
  peripheral_diameter = avg_diameter + l2
  mu_a = 0.5
  delta_a = 0.0025
  mu_r = 0.75
  delta_r = 0.001 * peripheral_diameter
  z = 6
  delta_e = ma.pow((1 / (mu_a * delta_a) ** 2) + (z / (mu_r * delta_r) ** 2), -0.5)
  ksi_bandage = ((ma.pi * peripheral_diameter * delta_e * eff) / F1) * ma.sqrt(ro + 1.8 * l2 / avg_diameter)
  deltaH_y = ksi_bandage * E0
  k_tr = 0.7 * 10 ** -3
  ksi_friction = k_tr * ma.pow(avg_diameter, 2) / F1 * ma.pow(u_cf, 3)
  deltaH_tr = ksi_friction * E0
  k_v = 0.065
  m = 1
  ksi_v = k_v / ma.sin(ma.radians(alpha1_e)) * (1 - e_opt) / e_opt * ma.pow(u_cf, 3) * m
  B2 = b2 * ma.sin(ma.radians(beta2_ust))
  i = 4
  ksi_segment = 0.25 * B2 * 10**-3 * l2 / F1 * u_cf * eff * i
  ksi_partiality = ksi_v + ksi_segment
  deltaH_partiality = ksi_partiality * E0
  return peripheral_diameter, delta_r, delta_e, ksi_bandage, deltaH_y, ksi_friction, deltaH_tr, ksi_v, B2, ksi_segment, ksi_partiality, deltaH_partiality 

def data_output10(peripheral_diameter, delta_r, delta_e, ksi_bandage, deltaH_y, ksi_friction, deltaH_tr, ksi_v, B2, ksi_segment, ksi_partiality, deltaH_partiality):
  d = {
     'Name': ["Периферийный диаметр", 
              "Радиальный зазор в периферийном уплотнении", 
              "Эквивалентный зазор в уплотнении по бандажу (периферийном)", 
              "Относительные потери от утечек через бандажные уплотнения", 
              "Абсолютные потери от утечек через периферийное уплотнение ступени", 
              "Относительные потери от трения диска", 
              "Абсолютные потери от трения диска", 
              "Коэффициент вентиляционных потерь",
              "Ширина рабочей решетки",
              "Коэффициент сегментных потерь",
              "Относительные потери в ступени, связанные с парциальностью",             
              "Абсолютные потери от парциальности"],       
     'Parameters': ["peripheral_diameter", "delta_r", "delta_e", "ksi_bandage", "deltaH_y", "ksi_friction", "deltaH_tr", "ksi_v", "B2", "ksi_segment", "ksi_partiality", "deltaH_partiality"],
     'Value': [peripheral_diameter, delta_r, delta_e, ksi_bandage, deltaH_y, ksi_friction, deltaH_tr, ksi_v, B2, ksi_segment, ksi_partiality, deltaH_partiality]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#расчет внутреннего относительного КПД
def calculation_of_internal_relative_efficiency(G_0, E0, delta_Hc, delta_Hp, delta_Hvc, deltaH_y, deltaH_tr, deltaH_partiality):
  x_vc = 0
  H_i = E0 - delta_Hc - delta_Hp - (1 - x_vc) * delta_Hvc - deltaH_y - deltaH_tr - deltaH_partiality
  internal_eff = H_i / E0
  N_i = G_0 * H_i
  return H_i, internal_eff, N_i

def data_output11(H_i, internal_eff, N_i):
  d = {
     'Name': ["Использованный теплоперепад ступени", 
              "Внутренний относительный КПД ступени", 
              "Внутренняя мощность ступени"],       
     'Parameters': ["H_i", "internal_eff", "N_i"],
     'Value': [H_i, internal_eff, N_i]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

#расчет на прочность для лопатки
def calculation_of_strength(W2_min, b2, G_0, H_0, eff, l2, u, z_2, e_opt, rotation_speed, avg_diameter):
  b2_atl = 25.6
  W2_min_ = W2_min * m.pow(b2 / b2_atl, 3)
  sigma_bending = (G_0 * H_0 * 1000 * eff * l2) / (2 * u * z_2 * W2_min_ * e_opt)
  omega = 2 * m.pi * rotation_speed
  sigma_stretching = 0.5 * 7800 * m.pow(omega, 2) * avg_diameter * l2
  return W2_min_, sigma_bending, omega, sigma_stretching

def data_output12(W2_min_, sigma_bending, omega, sigma_stretching):
  d = {
     'Name': ["Момент сопротивления профиля рабочей лопатки", 
              "Напряжение изгиба лопатки", 
              "угловая скорость рабочего колеса", 
              "Напряжение растяжения лопатки"],       
     'Parameters': ["W2_min_", "sigma_bending", "omega", "sigma_stretching"],
     'Value': [W2_min_, sigma_bending, omega, sigma_stretching]
  }
  df = pd.DataFrame(data=d)
  blankIndex=[''] * len(df)
  df.index=blankIndex
  display(df.transpose())
  print()

def main(G_0, H_0, ro, point_0, rotation_speed, avg_diameter):
  u = calculation_of_circumferential_speed(avg_diameter, rotation_speed)
  Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_, point_1_t = calculation_of_parameters_for_the_nozzle(H_0, G_0, point_0, ro)       
  alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min ,W1_min = selection_of_the_nozzle_grating_profile()
  el1, e_opt, l1, mu1, F1, z_1, t1opt, z1 = Clarification_nozzle_grating(c1t, G_0, F1_, avg_diameter, alpha1_e, b1, point_1_t)
  alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1 = Clarification_other_nozzle_grating_parameters(mu1, c1t, alpha1_e, t1opt, l1, b1)
  w_1, beta_1, point_1_, point_2_t, w2t, l2, a2t, M2t, delta_Hc = calculation_of_parameters_for_the_selection_of_the_working_grid(l1, fi, c_1, c1t, alpha_1, u, point_1_t, Ho_p)
  beta0, beta2_e, t_opt, M2t_, b2, f2, I2_min, W2_min = selection_of_the_working_grid_profile()
  mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2 = specification_of_working_grid_parameters(e_opt, l2, b2, G_0, point_2_t, w2t, avg_diameter)
  ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2 = parameters_of_the_working_grid_according_to_the_atlas(u, beta2_e, b2, l2, w2t, mu2)
  delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff, point_2_, point_t_konec = calculation_of_relative_blade_efficiency(c_1, u, point_0, H_0, point_2_t, w2t, psi, c_2, delta_Hc, alpha_1, alpha_2)
  cf, u_cf, u_cf_opt = calculation_of_the_velocity_ratio(u, H_0, fi, alpha_1, ro)      
  data_output(*calculation_of_parameters_for_the_nozzle(H_0, G_0, point_0, ro))
  data_output1(*selection_of_the_nozzle_grating_profile())
  data_output2(*Clarification_nozzle_grating(c1t, G_0, F1_, avg_diameter, alpha1_e, b1, point_1_t))
  data_output3(*Clarification_other_nozzle_grating_parameters(mu1, c1t, alpha1_e, t1opt, l1, b1))
  data_output4(*calculation_of_parameters_for_the_selection_of_the_working_grid(l1, fi, c_1, c1t, alpha_1, u, point_1_t, Ho_p))
  data_output5(*selection_of_the_working_grid_profile())
  data_output6(*specification_of_working_grid_parameters(e_opt, l2, b2, G_0, point_2_t, w2t, avg_diameter))
  data_output7(*parameters_of_the_working_grid_according_to_the_atlas(u, beta2_e, b2, l2, w2t, mu2))
  data_output8(*calculation_of_the_velocity_ratio(u, H_0, fi, alpha_1, ro))
  data_output9(*calculation_of_relative_blade_efficiency(c_1, u, point_0, H_0, point_2_t, w2t, psi, c_2, delta_Hc, alpha_1, alpha_2))
  construction_of_velocity_triangles(u, w_1, c_1, w_2, c_2, alpha_1, beta_2)

def main2(G_0, H_0, ro, point_0, rotation_speed, avg_diameter):
  u = calculation_of_circumferential_speed(avg_diameter, rotation_speed)
  Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_, point_1_t = calculation_of_parameters_for_the_nozzle(H_0, G_0, point_0, ro)       
  alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min ,W1_min = selection_of_the_nozzle_grating_profile()
  el1, e_opt, l1, mu1, F1, z_1, t1opt, z1 = Clarification_nozzle_grating(c1t, G_0, F1_, avg_diameter, alpha1_e, b1, point_1_t)
  alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1 = Clarification_other_nozzle_grating_parameters(mu1, c1t, alpha1_e, t1opt, l1, b1)
  w_1, beta_1, point_1_, point_2_t, w2t, l2, a2t, M2t, delta_Hc = calculation_of_parameters_for_the_selection_of_the_working_grid(l1, fi, c_1, c1t, alpha_1, u, point_1_t, Ho_p)
  beta0, beta2_e, t_opt, M2t_, b2, f2, I2_min, W2_min = selection_of_the_working_grid_profile()
  mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2 = specification_of_working_grid_parameters(e_opt, l2, b2, G_0, point_2_t, w2t, avg_diameter)
  ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2 = parameters_of_the_working_grid_according_to_the_atlas(u, beta2_e, b2, l2, w2t, mu2)
  delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff, point_2_, point_t_konec = calculation_of_relative_blade_efficiency(c_1, u, point_0, H_0, point_2_t, w2t, psi, c_2, delta_Hc, alpha_1, alpha_2)
  cf, u_cf, u_cf_opt = calculation_of_the_velocity_ratio(u, H_0, fi, alpha_1, ro)   
  peripheral_diameter, delta_r, delta_e, ksi_bandage, deltaH_y, ksi_friction, deltaH_tr, ksi_v, B2, ksi_segment, ksi_partiality, deltaH_partiality = determination_of_parameters_for_calculating_internal_efficiency(beta2_ust, b2, e_opt, alpha1_e, avg_diameter, l2, eff, F1, ro, E0, u_cf)
  data_output10(*determination_of_parameters_for_calculating_internal_efficiency(beta2_ust, b2, e_opt, alpha1_e, avg_diameter, l2, eff, F1, ro, E0, u_cf))
  data_output11(*calculation_of_internal_relative_efficiency(G_0, E0, delta_Hc, delta_Hp, delta_Hvc, deltaH_y, deltaH_tr, deltaH_partiality))

def graff(G_0, H_0, ro, point_0, rotation_speed, avg_diameter):
  u = calculation_of_circumferential_speed(avg_diameter, rotation_speed)
  Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_, point_1_t = calculation_of_parameters_for_the_nozzle(H_0, G_0, point_0, ro)       
  alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min ,W1_min = selection_of_the_nozzle_grating_profile()
  el1, e_opt, l1, mu1, F1, z_1, t1opt, z1 = Clarification_nozzle_grating(c1t, G_0, F1_, avg_diameter, alpha1_e, b1, point_1_t)
  alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1 = Clarification_other_nozzle_grating_parameters(mu1, c1t, alpha1_e, t1opt, l1, b1)
  w_1, beta_1, point_1_, point_2_t, w2t, l2, a2t, M2t, delta_Hc = calculation_of_parameters_for_the_selection_of_the_working_grid(l1, fi, c_1, c1t, alpha_1, u, point_1_t, Ho_p)
  beta0, beta2_e, t_opt, M2t_, b2, f2, I2_min, W2_min = selection_of_the_working_grid_profile()
  mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2 = specification_of_working_grid_parameters(e_opt, l2, b2, G_0, point_2_t, w2t, avg_diameter)
  ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2 = parameters_of_the_working_grid_according_to_the_atlas(u, beta2_e, b2, l2, w2t, mu2)
  delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff, point_2_, point_t_konec = calculation_of_relative_blade_efficiency(c_1, u, point_0, H_0, point_2_t, w2t, psi, c_2, delta_Hc, alpha_1, alpha_2)
  cf, u_cf, u_cf_opt = calculation_of_the_velocity_ratio(u, H_0, fi, alpha_1, ro)
  return point_1_t, point_1_, point_2_t, point_2_, point_t_konec
  

def endurance(G_0, H_0, ro, point_0, rotation_speed, avg_diameter):
  u = calculation_of_circumferential_speed(avg_diameter, rotation_speed)
  Ho_c, Ho_p, h1t, c1t, a1t, M1t, F1_, point_1_t = calculation_of_parameters_for_the_nozzle(H_0, G_0, point_0, ro)       
  alpha1_e, alpha0, t_opt, M1t_, b1, f1, I1_min ,W1_min = selection_of_the_nozzle_grating_profile()
  el1, e_opt, l1, mu1, F1, z_1, t1opt, z1 = Clarification_nozzle_grating(c1t, G_0, F1_, avg_diameter, alpha1_e, b1, point_1_t)
  alpha_ust, b1_l1, ksi_noz, ksi_sum, ksi_end_noz, fi, fi_, delta_fi, c_1, alpha_1 = Clarification_other_nozzle_grating_parameters(mu1, c1t, alpha1_e, t1opt, l1, b1)
  w_1, beta_1, point_1_, point_2_t, w2t, l2, a2t, M2t, delta_Hc = calculation_of_parameters_for_the_selection_of_the_working_grid(l1, fi, c_1, c1t, alpha_1, u, point_1_t, Ho_p)
  beta0, beta2_e, t_opt, M2t_, b2, f2, I2_min, W2_min = selection_of_the_working_grid_profile()
  mu2, F2, beta2_e, z_2, t2opt, beta2_ust, b2_l2 = specification_of_working_grid_parameters(e_opt, l2, b2, G_0, point_2_t, w2t, avg_diameter)
  ksi_grid, ksi_sum_g, ksi_end_grid, psi, psi_, delta_psi, beta_2, c_2, alpha_2, w_2 = parameters_of_the_working_grid_according_to_the_atlas(u, beta2_e, b2, l2, w2t, mu2)
  delta_Hp, delta_Hvc, E0, eff, eff_, delta_eff, point_2_, point_t_konec = calculation_of_relative_blade_efficiency(c_1, u, point_0, H_0, point_2_t, w2t, psi, c_2, delta_Hc, alpha_1, alpha_2)
  cf, u_cf, u_cf_opt = calculation_of_the_velocity_ratio(u, H_0, fi, alpha_1, ro)     
  data_output12(*calculation_of_strength(W2_min, b2, G_0, H_0, eff, l2, u, z_2, e_opt, rotation_speed, avg_diameter))