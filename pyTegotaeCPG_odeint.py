#!/usr/bin/env python3

# pyTegotaeCPG_odeint.py
# Copyright (c) 2025 Dai Owaki <owaki@tohoku.ac.jp>
# ver. 2025.2.11.

# 必要なライブラリをインポート
from scipy.integrate import odeint
import numpy as np

# 自作モジュールのインポート
import video_pyTegotaeCPG as vPCPG
import SMDwPO as swp

# シミュレーションのパラメータ設定
m = 0.10 # ボディの質量 [kg] 
c = 0.2  # ダンパー係数 [Ns/m] 
k = 5.0  # バネ定数 [N/m] 
l = 1.0  # バネ自然長 [m] 
g = 9.81 # 重力加速度 [m/s^2]
Fa = 0.0 # アクチュエータ力（時変：SMDwPO） [N] 

omega = 5.0   # 位相振動子の固有角周波数 [rad/s] 
Fo    = 0.0   # 位相振動子へのフィードバック項（時変：SMDwPO） [rad/s] 
Amp   = 4.0   # アクチュエータの最大発生力[N] 
Dur   = 0.02*omega*np.pi # アクチュエータ力の発生期間(Durtion) [rad] 
Sigma = 2.753 #　位相振動子へのフィードバックゲイン [rad/s] 
Phase = 1.6*np.pi # アクチュエータ力の発生開始位相 [rad]

params = [m, c, k, l, g, Fa, omega, Fo, Amp, Dur, Sigma, Phase] # シミュレーションパラメータ

# 初期条件の設定
max_t = 15.0 # シミュレーションの最大時間 [s]
dt = 0.00010  # 時間ステップ [s]
times = 100   # 動画のスピード倍率

video_dt = dt*times # 動画の時間ステップ [s]


def run_simulation(max_t, dt, params, times):

    # 時間の配列を準備
    t = np.arange(0.0, max_t, dt)

    # 初期状態を格納 
    p0 = [1.0, 0.0, 0.0*np.pi, 0.0]
    
    # シミュレーションの実行
    p = odeint(swp.DynamicalSystem, p0, t, args=(params,))

    # 動画用データの作成
    
    length =len(p)  # pサイズを取得
    indices = np.arange(0, length, times)  # 安全な範囲でインデックスを生成
    video_p = p[indices]
    
    return video_p


if __name__ == '__main__':

    video_p = run_simulation(max_t, dt, params, times)

    # 動画を高速再生
    vPCPG.video(video_p, video_dt, max_t, params)
