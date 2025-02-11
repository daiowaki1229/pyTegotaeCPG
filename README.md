# pyTegotaeCPG

## Overview / 概要
This repository provides a Python simulation of a hopping robot controlled by a Tegotae-based Central Pattern Generator (CPG). The simulation includes dynamics modeling, feedback control, and visualization tools.

このリポジトリは、Tegotae-based CPGを利用したホッピングロボットの制御シミュレーションを提供します。動力学モデリング、フィードバック制御、ビジュアライザーションツールが含まれています。

---

## Files and Their Roles / ファイルとその役割

### 1. `pyTegotaeCPG_odeint.py`
- **Main program:** Sets parameters and initial conditions, and runs the simulation loop using ODE calculations.
- **メインプログラム:** パラメータの設定、初期条件の設定、ODE計算を用いたシミュレーションループの実行

### 2. `SMDwPO.py`
- **Dynamics library:**
  - Models the physics of a spring-mass-damper system (hopping robot dynamics).
  - Computes the time evolution of phase oscillators.
  - Implements the Tegotae feedback function and control.
- **動力学用ライブラリ:**
  - バネーマスダンパ動力(ホッピングロボットの動力学)
  - 位相振動子の時間発展
  - TEGOTAE(手応え)関数とTAGOTAE(手応え)フィードバック制御

### 3. `video_pyTegotaeCPG.py`
- **Visualization library:** Displays animations with:
  - **Top left:** Phase oscillators and Tegotae feedback.
  - **Bottom left:** Hopping robot dynamics.
  - **Top right:** Temporal evolution of phase oscillators and Tegotae feedback.
  - **Bottom right:** Hopping height (dashed line represents the average height) and driving force.
- **アニメーション用ライブラリ:**
  - **左上:** 位相振動子と手応えフィードバック
  - **左下:** ホッピングロボットの動力学
  - **右上:** 位相振動子と手応えフィードバックの時間発展
  - **右下:** ホッピング高さ(点線は平均高さ)と駆動力

### 4. `streamlit_pyTegotaeCPG.py`
- **Web app implementation using Streamlit.**
- **Streamlit用実行コード(ウェブアプリ用)**

---

## How to Run / 実行方法

### Run the Simulation / シミュレーションの実行
```bash
python pyTegotaeCPG_odeint.py
```
This will run the simulation and display the animation.

上記のコマンドを実行すると、シミュレーションが実行され、アニメーションが表示されます。

### Run the Web App / ウェブアプリの実行
```bash
streamlit run streamlit_pyTegotaeCPG.py
```
This will launch a web-based animation visualization.

上記のコマンドを実行すると、ウェブ上でアニメーションを表示するアプリが動作します。

---

## Required Libraries / 必要なライブラリ
The required libraries are listed in `requirements.txt`.
```bash
pip install -r requirements.txt
```
This will install all the necessary dependencies.

必要なライブラリは `requirements.txt` に記述されています。

---

## License / ライセンス
This project is released under the MIT License.

このプロジェクトはMITライセンスのもとに公開されています。

## Acknowledgments / 謝辞
This project is inspired by Tegotae-based CPG studies and serves as an educational tool for understanding embodied intelligence.

このプロジェクトは、TEGOTAEに基づくCPG制御の研究から着想を得ており、身体性知能を理解するための教育ツールとして役立つ。

## References / 参考文献
- Dai Owaki, Takeshi Kano, Kou Nagasawa, Atsushi Tero, and Akio Ishiguro, Simple Robot Suggests Physical Interlimb Communication Is Essential for Quadruped Walking, *Journal of Royal Society Interface*, vol. 10, https://doi.org/10.1098/rsif.2012.0669 (2012)
- Dai Owaki and Akio Ishiguro, A Quadruped Robot Exhibiting Spontaneous Gait Transitions from Walking to Trotting to Galloping, *Scientific Reports*, vol. 7:277, https://doi.org/10.1038/s41598-017-00348-9, (2017)
- Dai Owaki, Masashi Goda, Sakiko Miyazawa, and Akio Ishiguro, A Minimal Model Describing Hexapedal Interlimb Coordination: the Tegotae-based Approach, *Front. Neurorobot.*, vol.11:29, https://doi.org/10.3389/fnbot.2017.00029 (2017)
- Riccardo Zamboni, Dai Owaki, Mitsuhiro Hayashibe, Adaptive and Energy-Efficient Optimal Control in CPGs Through Tegotae-Based Feedback, *Frontiers in Robotics and AI*, Vol. 8, https://doi.org/10.3389/frobt.2021.632804, (2021) 
- Dai Owaki, Shun-ya Horikiri, Jun Nishii, Akio Ishiguro, Tegotae-Based Control Produces Adaptive Inter- and Intra-limb Coordination in Bipedal Walking, *Frontiers in Neurorobotics*, Vol. 15, https://doi.org/10.3389/fnbot.2021.629595, (2021)

---
Feel free to contribute or report any issues!

貢献や問題報告を歓迎します！
