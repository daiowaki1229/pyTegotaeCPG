# streamlit_pyTegotaeCPG.py
# Copyright (c) 2025 Dai Owaki <owaki@tohoku.ac.jp>
# ver. 2025.2.11.

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import time
from pyTegotaeCPG_odeint import run_simulation
import SMDwPO as swp  # バネ-ダンパー系のシミュレーションを含むモジュール


# Streamlit アプリの設定
st.title("Tegotae CPG Simulation")

# 初期条件の設定
#max_t = 15.0  # シミュレーションの最大時間 [s]
dt = 0.00010  # 時間ステップ [s]

# シミュレーションの時間パラメータの設定
max_t = float(st.sidebar.number_input("Simulation Time (s)", min_value=10.0, max_value=30.0, value=15.0, step=5.0, format="%.1f"))
times = int(st.sidebar.number_input("Animation Speed Multiplier", min_value=0.0, max_value=500.0, value=100.0, step=100.0, format="%.1f"))

video_dt = dt * times

# シミュレーションのパラメータ設定
m = 0.10 # ボディの質量 [kg] 
c = 0.2  # ダンパー係数 [Ns/m] 
k = 5.0  # バネ定数 [N/m] 
l = 1.0  # バネ自然長 [m] 
g = 9.81 # 重力加速度 [m/s^2]
Fa = 0.0 # アクチュエータ力（時変：SMDwPO） [N] 

m = float(st.sidebar.number_input("m (kg)", min_value=0.10, max_value=10.00, value=0.10, step=0.1, format="%.2f"))
c = float(st.sidebar.number_input("c (Ns/m)", min_value=0.10, max_value=10.00, value=0.20, step=0.1, format="%.2f"))
k = float(st.sidebar.number_input("k (N/m)", min_value=1.0, max_value=100.00, value=5.00, step=1.0, format="%.2f"))


omega = 5.0   # 位相振動子の固有角周波数 [rad/s] 
Fo    = 0.0   # 位相振動子へのフィードバック項（時変：SMDwPO） [rad/s] 
Amp   = 4.0   # アクチュエータの最大発生力[N] 
Dur   = 0.02*omega*np.pi # アクチュエータ力の発生期間(Durtion) [rad] 
Sigma = 2.753 #　位相振動子へのフィードバックゲイン [rad/s] 
Phase = 1.6*np.pi # アクチュエータ力の発生開始位相 [rad]

omega = float(st.sidebar.number_input("Omega (rad/s)", min_value=1.00, max_value=10.00, value=5.00, step=0.5, format="%.2f"))
Sigme = float(st.sidebar.number_input("Sigma (rad/Ns)", min_value=1.00, max_value=5.00, value=2.50, step=0.5, format="%.2f"))



# セッションステートの初期化
if "run_simulation" not in st.session_state:
    st.session_state.run_simulation = False
if "stop_simulation" not in st.session_state:
    st.session_state.stop_simulation = False

# シミュレーションの実行制御
if st.button("Run Simulation"):
    st.session_state.run_simulation = True
    st.session_state.stop_simulation = False

if st.button("Stop Simulation"):
    st.session_state.run_simulation = False
    st.session_state.stop_simulation = True

if st.session_state.run_simulation:
    with st.spinner("Running Simulation..."):
        
        params = [m, c, k, l, g, Fa, omega, Fo, Amp, Dur, Sigma, Phase] # シミュレーションパラメータ
        x = run_simulation(max_t, dt, params, times)

        # プロット用の空のコンテナ
        plot_area = st.empty()
        
        # 時間リストの作成
        time_st = np.arange(0.0, max_t, video_dt)
        
        # 力、フィードバック、パワーを格納する配列の作成
        force = np.empty(int(max_t/video_dt))
        feedback = np.empty(int(max_t/video_dt))
        power = np.empty(int(max_t/video_dt))

        # シミュレーション結果を解析
        for j in range(int(max_t/video_dt)):
            
            # フィードバック計算（バネの伸びが閾値 l 以下の場合のみ）
            if x[j, 0] <= l:
                feedback[j] = -Sigma * swp.SpringFunc(x[j, 0], params) * np.cos(x[j, 2])
            else:
                feedback[j] = 0
            
            # 外力の発生（フェーズと時間の条件を満たす場合）
            if Phase <= (x[j, 2] % (2 * np.pi)) < Phase + Dur and x[j, 0] <= l:
                force[j] = Amp
            else:
                force[j] = 0
            
            # パワー計算（外力×速度）
            power[j] = force[j] * x[j, 1]

        # 高さの解析用データの準備
        half_max = int(max_t / (2 * video_dt))
        full_max = int(max_t / video_dt)
        data = np.empty(half_max)
        sum_power = 0
        
        period = 6 * np.pi / omega  # 1周期の時間
        period_int = int(period / video_dt)  # 1周期の時間ステップ数

        for j in range(half_max):
            data[j] = x[half_max + j, 0]
        
        for j in range(period_int):
            sum_power += power[half_max + j]
        
        # 高さの統計量計算
        AveHeight = sum(data) / len(data)  # 平均高さ
        MinHeight = min(data)  # 最小高さ
        MaxHeight = max(data)  # 最大高さ
        Ec = sum_power / period_int  # エネルギーコスト

        cmap1 = plt.get_cmap("hsv")

        # 初期設定（図のサイズ設定）
        fig = plt.figure(figsize=(12, 8))
        gs = gridspec.GridSpec(2, 3)
        
        # フォント設定（Times New Roman, フォントサイズ18）
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['font.size'] = 18

        # ax1（位相振動子の可視化エリア）の設定
        ax1 = fig.add_subplot(gs[0, 0], xlim=(-1.5, 1.5), ylim=(-1.5, 1.5))
        ax1.set_xlabel('Phase oscillator')
        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.grid()

        # 円の半径設定
        radius = 1.0
        circle1 = plt.Circle((0, 0), radius, linestyle=':', color='k', fill=False)

        # 座標軸の中心線の描画
        line_x0, = plt.plot((0, 0), (-1.5, 1.5), 'k-', lw=1, alpha=0.5, animated=False)
        line_y0, = plt.plot((-1.5, 1.5), (0, 0), 'k-', lw=1, alpha=0.5, animated=False)

        # 矢印・角度の描画（アニメーション）
        arrow10, = plt.plot([], [], 'c-', lw=5, alpha=0.8, animated=True)
        angle_phi0, = plt.plot([], [], 'r-', lw=2, alpha=0.5, animated=True)
        osci10, = plt.plot([], [], 'ro', markersize=10, animated=True)

        # 時間表示の設定
        time_template = 'time = %.2fs'
        time_text = ax1.text(0.51, 0.90, '', transform=ax1.transAxes)

        # 位相の範囲を示す線
        line_lim1_phase = plt.plot([0.0, radius * np.cos(Phase)], [0.0, radius * np.sin(Phase)], '-', color='magenta', lw=2, alpha=0.5, animated=False)
        line_lim2_phase = plt.plot([0.0, radius * np.cos(Phase + Dur)], [0.0, radius * np.sin(Phase + Dur)], '-', color='magenta', lw=2, alpha=0.5, animated=False)

        # ax2（時間変化の可視化エリア）の設定
        ax2 = fig.add_subplot(gs[0, 1:3], xlim=(0, max_t), ylim=(-1.5, 1.5))
        ax2.set_xlabel('time [s]')
        ax2.set_ylabel('Phase: sin( phi )')
        ax2.grid()

        # データ系列の描画
        line10, = plt.plot(time_st, np.sin(x[:, 2]), 'r-', lw=2, alpha=0.5)
        line_2y0, = plt.plot((0, max_t), (0, 0), 'k-', lw=1, alpha=1., animated=False)
        line_feedback = plt.fill_between(time_st, 0.00 * feedback, 0.30 * feedback, color='c', alpha=0.5)

        # 時間バーの描画（アニメーション）
        bar, = plt.plot([], [], 'b-', lw=1, animated=True)
        posci10, = plt.plot([], [], 'ro', markersize=10, animated=True)

        # ax3（ホッピングロボットの可視化エリア）の設定
        ax3 = fig.add_subplot(gs[1, 0], xlim=(-1, 1), ylim=(0, 2.0))
        ax3.set_xlabel('x [m]')
        ax3.set_ylabel('y [m]')
        ax3.set_title('Hopping robot', fontsize=18)
        ax3.grid()

        # バネの力の範囲
        force_min = 0
        force_max = 2.5

        # カラーマップの設定（青から赤）
        cmap = cm.get_cmap('coolwarm')
        norm = mcolors.Normalize(vmin=force_min, vmax=force_max)

        # 座標軸の描画
        line_x0, = plt.plot((0, 0), (0, 2.0), 'k-', lw=1, alpha=0.5, animated=False)
        line_y0, = plt.plot((-1, 1), (1, 1), 'k:', lw=1, alpha=0.5, animated=False)

        # ホッピングロボットの部品（位置・バネ）
        spring, = plt.plot([], [], 'b-', lw=7.5, animated=True)
        position1, = plt.plot([], [], 'go', markersize=30, animated=True)


        # ax4エリアの設定
        ax4 = fig.add_subplot(gs[1,1:3], xlim=(0, max_t), ylim=(0, 2.0))
        ax4.set_xlabel('time [s]')  # x軸ラベル（時間）
        ax4.set_ylabel('Height: y [m]')  # y軸ラベル（高さ）
        ax4.grid()  # グリッドを表示

        # 線のプロット（高さデータ、基準線、力の影響範囲など）
        line_m1, = plt.plot(time_st, x[:,0], 'g-', lw=2, alpha=0.5)  # 高さの推移
        line_m0, = plt.plot((0, max_t), (1, 1), 'k-', lw=1, alpha=1., animated=False)  # 基準線
        line_force = plt.fill_between(time_st, 0.0*force, 0.5*force, color='m', alpha=0.3)  # 力の影響範囲
        line_aveh, = plt.plot((0, max_t), (AveHeight, AveHeight), 'b--', lw=2, alpha=1., animated=False)  # 平均高さのライン

        # アニメーション用のバーとマーカー
        bar2, = plt.plot([], [], 'b-', lw=1, animated=True)  # 時間バー
        pm1, = plt.plot([], [], 'go', markersize=10, animated=True)  # ポイントマーカー

        # 平均高さのテキスト表示
        ave_text = ax4.text(0.55*max_t, 2.1, 'Averaged height={:.2f} m'.format(AveHeight), color='blue')
        # ave_text = ax4.text(0.15*max_t, 2.1, 'ave={:.2f}, max-min={:.2f}, Ec={:.2f}, Ee={:.4f}'.format(AveHeight,MaxHeight-MinHeight,Ec,(MaxHeight-MinHeight)/Ec), color='blue')

        plt.tight_layout()  # グラフのレイアウトを調整

        
        for i in range(len(x)):
            if st.session_state.stop_simulation:
                break
        
            next_bx = [time_st[i], time_st[i]]  # 時間バーのx座標
            next_by = [-1.5, 1.5]  # 時間バーのy座標
            bar.set_data([next_bx], [next_by])  # 時間バーの位置を更新

            osci10.set_data([np.cos(x[i,2])], [np.sin(x[i,2])])  # 振動子の位置を更新

            # フィードバック矢印の設定
            FB_scale = 0.2
            arrow10.set_data([np.cos(x[i,2]), np.cos(x[i,2]) + FB_scale * feedback[i] * (-np.sin(x[i,2]))],[np.sin(x[i,2]), np.sin(x[i,2]) + FB_scale * feedback[i] * (np.cos(x[i,2]))])

            # 振動子の位相を表示
            angle_x0 = [0, np.cos(x[i,2])]
            angle_y0 = [0, np.sin(x[i,2])]
            angle_phi0.set_data([angle_x0], [angle_y0])

            posci10.set_data([time_st[i]], [np.sin(x[i,2])])  # 振動子の位相（sin phi）
            time_text.set_text(time_template % time_st[i])  # 時間表示

            next_by2 = [0, 2.0]  # 別の時間バーのy座標
            bar2.set_data([next_bx], [next_by2])  # 時間バーの位置を更新

            position1.set_data([0], [x[i,0]])  # ロボットの位置を更新
            pm1.set_data([time_st[i]], [x[i,0]])  # ロボットの高さを更新

            # バネの描画を更新
            if x[i,0] <= l:
                spring_x = [0, 0]
                spring_y = [0, x[i,0]]
            else:
                spring_x = [0, 0]
                spring_y = [x[i,0]-l, x[i,0]]
            spring.set_data([spring_x], [spring_y])

            # バネの色を力に応じて色を変化させる
            color = cmap(norm(swp.SpringFunc(x[i,0], params)))
            spring.set_color(color)

            ax1.add_patch(circle1)  # 円を描画

            
            plot_area.pyplot(fig)  # Streamlit上でプロットを更新
            time.sleep(video_dt)  # フレーム更新間隔

