import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os

# CSVファイルのパス
LOG_FILE = "task_log.csv"
TASKS_FILE = "task_list.csv"

# CSVファイルが存在しない or 中身が空なら初期化
if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
    pd.DataFrame(columns=["date", "task", "reward"]).to_csv(LOG_FILE, index=False)

if not os.path.exists(TASKS_FILE) or os.path.getsize(TASKS_FILE) == 0:
    pd.DataFrame({
        "task": ["トイレ掃除", "風呂掃除", "洗い物", "料理の手伝い"],
        "reward": [50, 50, 30, 30]
    }).to_csv(TASKS_FILE, index=False)

# タスクリスト読み込み
tasks_df = pd.read_csv(TASKS_FILE)

# アプリタイトル
st.title("おこづかい管理アプリ")

# お仕事リスト編集
st.subheader("🛠️ お仕事リストの編集")
with st.form("edit_tasks"):
    edited_tasks = st.data_editor(tasks_df, num_rows="dynamic")
    submitted = st.form_submit_button("保存")
    if submitted:
        edited_tasks.to_csv(TASKS_FILE, index=False)
        st.success("保存しました！")
        st.rerun()

# お手伝い記録
st.subheader("🧹 今日のお手伝い")
task = st.selectbox("お手伝い内容を選んでください", tasks_df["task"].tolist())
if st.button("報酬を記録"):
    reward = tasks_df[tasks_df["task"] == task]["reward"].values[0]
    new_log = pd.DataFrame([[datetime.date.today(), task, reward]],
                           columns=["date", "task", "reward"])
    new_log.to_csv(LOG_FILE, mode='a', header=False, index=False)
    st.success(f"{task} を記録しました！ {reward}円を獲得！")

# 三分法スライダー
st.subheader("📊 三分法の配分設定")
use_ratio = st.slider("使う (%)", 0, 100, 60)
save_ratio = st.slider("貯める (%)", 0, 100 - use_ratio, 30)
invest_ratio = 100 - use_ratio - save_ratio
st.write(f"増やす (%)：{invest_ratio}")

# ログ読み込みと合計計算（空でも安全に）
try:
    log_df = pd.read_csv(LOG_FILE)
except pd.errors.EmptyDataError:
    log_df = pd.DataFrame(columns=["date", "task", "reward"])

total = log_df["reward"].sum() if not log_df.empty else 0

# グラフ用の金額計算（NaN対策）
if total > 0:
    use = total * use_ratio / 100
    save = total * save_ratio / 100
    invest = total * invest_ratio / 100
else:
    use = save = invest = 1  # 初期状態は1:1:1で表示

# 円グラフ表示
st.subheader("💰 現在の三分法残高")
fig, ax = plt.subplots()
ax.pie([use, save, invest],
       labels=["使う", "貯める", "増やす"],
       autopct="%1.1f%%")
st.pyplot(fig)

# 履歴表示
st.subheader("📜 お手伝い履歴")
st.dataframe(log_df.sort_values("date", ascending=False))
