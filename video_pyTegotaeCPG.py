#!/usr/bin/env python3

# video_PhysicalCPG.py
# Copyright (c) 2025 Dai Owaki <owaki@tohoku.ac.jp>
# ver. 2025.2.11.
#
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.animation as animation

import SMDwPO as swp  # バネ-ダンパー系のシミュレーションを含むモジュール


def video(x, dt, max_t, params):
    """
    シミュレーション結果を動画として可視化する関数。
    
    Parameters:
        x      : ndarray シミュレーション結果の状態変数
        dt     : float   シミュレーションの時間ステップ
        max_t  : float   シミュレーションの総時間
        params : list    システムのパラメータ
    """
    
    # パラメータの取得
    l     = params[3]  # バネの自然長
    Omega = params[6]  # 角速度
    Amp   = params[8]  # 力の振幅
    Dur   = params[9]  # 力の作用時間
    Sigma = params[10] # フィードバックの係数
    Phase = params[11] # フェーズオフセット

    # 時間リストの作成
    time = np.arange(0.0, max_t, dt)
    
    # 力、フィードバック、パワーを格納する配列の作成
    force = np.empty(int(max_t/dt))
    feedback = np.empty(int(max_t/dt))
    power = np.empty(int(max_t/dt))

    # シミュレーション結果を解析
    for j in range(int(max_t/dt)):
        
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
    half_max = int(max_t / (2 * dt))
    full_max = int(max_t / dt)
    data = np.empty(half_max)
    sum_power = 0
    
    period = 6 * np.pi / Omega  # 1周期の時間
    period_int = int(period / dt)  # 1周期の時間ステップ数

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
    line10, = plt.plot(time, np.sin(x[:, 2]), 'r-', lw=2, alpha=0.5)
    line_2y0, = plt.plot((0, max_t), (0, 0), 'k-', lw=1, alpha=1., animated=False)
    line_feedback = plt.fill_between(time, 0.00 * feedback, 0.30 * feedback, color='c', alpha=0.5)

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
    line_m1, = plt.plot(time, x[:,0], 'g-', lw=2, alpha=0.5)  # 高さの推移
    line_m0, = plt.plot((0, max_t), (1, 1), 'k-', lw=1, alpha=1., animated=False)  # 基準線
    line_force = plt.fill_between(time, 0.0*force, 0.5*force, color='m', alpha=0.3)  # 力の影響範囲
    line_aveh, = plt.plot((0, max_t), (AveHeight, AveHeight), 'b--', lw=2, alpha=1., animated=False)  # 平均高さのライン

    # アニメーション用のバーとマーカー
    bar2, = plt.plot([], [], 'b-', lw=1, animated=True)  # 時間バー
    pm1, = plt.plot([], [], 'go', markersize=10, animated=True)  # ポイントマーカー

    # 平均高さのテキスト表示
    ave_text = ax4.text(0.55*max_t, 2.1, 'Averaged height={:.2f} m'.format(AveHeight), color='blue')
    # ave_text = ax4.text(0.15*max_t, 2.1, 'ave={:.2f}, max-min={:.2f}, Ec={:.2f}, Ee={:.4f}'.format(AveHeight,MaxHeight-MinHeight,Ec,(MaxHeight-MinHeight)/Ec), color='blue')

    plt.tight_layout()  # グラフのレイアウトを調整

    # アニメーションの初期化関数
    def init():
        ax1.add_patch(circle1)  # 円（物体）を描画
        return circle1, line10, line_force, line_feedback, line_aveh, line_2y0, bar, time_text, line_x0, line_y0, spring, angle_phi0, position1, pm1, bar2, osci10, posci10, arrow10

    # アニメーションの更新関数
    def anime(i):
        next_bx = [time[i], time[i]]  # 時間バーのx座標
        next_by = [-1.5, 1.5]  # 時間バーのy座標
        bar.set_data([next_bx], [next_by])  # 時間バーの位置を更新

        osci10.set_data([np.cos(x[i,2])], [np.sin(x[i,2])])  # 振動子の位置を更新

        # フィードバック矢印の設定
        FB_scale = 0.2
        arrow10.set_data([np.cos(x[i,2]), np.cos(x[i,2]) + FB_scale * feedback[i] * (-np.sin(x[i,2]))], 
                         [np.sin(x[i,2]), np.sin(x[i,2]) + FB_scale * feedback[i] * (np.cos(x[i,2]))])

        # 振動子の位相を表示
        angle_x0 = [0, np.cos(x[i,2])]
        angle_y0 = [0, np.sin(x[i,2])]
        angle_phi0.set_data([angle_x0], [angle_y0])

        posci10.set_data([time[i]], [np.sin(x[i,2])])  # 振動子の位相（sin phi）
        time_text.set_text(time_template % time[i])  # 時間表示

        next_by2 = [0, 2.0]  # 別の時間バーのy座標
        bar2.set_data([next_bx], [next_by2])  # 時間バーの位置を更新

        position1.set_data([0], [x[i,0]])  # ロボットの位置を更新
        pm1.set_data([time[i]], [x[i,0]])  # ロボットの高さを更新

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

        return circle1, line10, line_force, line_feedback, line_aveh, line_2y0, bar, time_text, line_x0, line_y0, angle_phi0, spring, position1, pm1, bar2, osci10, posci10, arrow10

    # アニメーションの設定と実行
    ani = animation.FuncAnimation(fig, anime, np.arange(1, len(x)), interval=dt*1.0e+4, blit=True, init_func=init)
    #ani.save('pyTegotaeCPG.mp4', writer='ffmpeg')  # アニメーションを保存（コメントアウト）

    plt.show()  # グラフを表示
