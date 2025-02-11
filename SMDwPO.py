#!/usr/bin/env python3

# SMDwPO.py
# Copyright (c) 2025 Dai Owaki <owaki@tohoku.ac.jp>
# ver. 2025.2.11.

import numpy as np

# バネの力を計算する関数
def SpringFunc(x, params):
    k = params[2]  # バネ定数
    l = params[3]  # バネの自然長

    if x <= l:
        force = k * (l - x)  # フックの法則による力の計算
    elif x > l:
        force = 0  # 自然長を超えると力はゼロ

    return force

# 質量-ダンパ-バネ系の運動方程式を定義する関数
def SMD(p, t, params):
    m  = params[0]  # 質量
    c  = params[1]  # ダンパの減衰係数
    g  = params[4]  # 重力加速度
    Fa = params[5]  # 外力（アクチュエータによる力）

    x = p[0]  # 位置
    y = p[1]  # 速度

    dx = y  # 速度の時間変化
    dy = (1.0 / m) * (-c * y + SpringFunc(x, params) - m * g + Fa)  # 運動方程式

    return [dx, dy]

# 振動子（位相オシレータ）の運動方程式を定義する関数
def PO(p, t, params):
    omega = params[6]  # 固有角速度
    Fo    = params[7]  # フィードバック制御入力

    phi  = p[0]  # 位相
    dphi = p[1]  # 位相の時間変化（角速度）

    dphi = omega + Fo  # 位相オシレータの更新
    ddphi = 0.0  # 角加速度はゼロとする

    return [dphi, ddphi]

# TEGOTAE（手応え）フィードバックを計算する関数
def TEGOTAE_FB(p, params):
    x    = p[0]  # 質量-バネ系の位置
    y    = p[1]  # 質量-バネ系の速度
    phi  = p[2]  # 位相
    dphi = p[3]  # 角速度
    
    #TEGOTAE（手応え）関数の定義
    # T = Ni * (- sin phi_i)
    # SpringFunc(x, params)*(-np.cos(phi)) 
    
    # TEGOTAE（手応え）フィードバックの計算
    # dT/dphi = Ni * (-cos phi_i)
    tegotae_FB = SpringFunc(x, params) * (-np.cos(phi))
    
    return tegotae_FB

# 質量-バネ-ダンパ系と位相オシレータを統合した動的システムの運動方程式
def DynamicalSystem(p, t, params):
    pSMD = [p[0], p[1]]  # 質量-バネ-ダンパ系の状態
    pPO  = [p[2], p[3]]  # 位相オシレータの状態

    x    = p[0]  # 位置
    y    = p[1]  # 速度
    phi  = p[2]  # 位相
    dphi = p[3]  # 角速度

    Amp   = params[8]  # 振幅
    Dur   = params[9]  # 持続時間
    Sigma = params[10] # ゲイン（フィードバック強度）
    Phase = params[11] # 位相オフセット

    l = params[3]  # バネの自然長

    # バネの自然長を超えない場合、フィードバックを適用
    if x <= l:
        params[7] = Sigma * TEGOTAE_FB(p, params)  # TEGOTAEフィードバックの適用
    else:
        params[7] = 0  # それ以外の場合はフィードバックなし

    # 位相オシレータの特定の時間範囲でアクチュエータを作動させる
    if (Phase <= (phi % (2 * np.pi)) < Phase + Dur) and x <= l:
        params[5] = Amp  # アクチュエータを作動
    else:
        params[5] = 0  # アクチュエータなし

    # 各サブシステムの運動方程式を計算
    dpSMD = SMD(pSMD, t, params)
    dpPO  = PO(pPO, t, params)

    return [dpSMD[0], dpSMD[1], dpPO[0], dpPO[1]]
