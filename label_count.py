import os
import pandas as pd

# ====== 修改成你的 CICIDS2017 CSV 資料夾 ======
DATA_DIR = "D:/candy/CICIDS2017/data/0_ori"

csv_files = [
    "Monday-WorkingHours.pcap_ISCX.csv",
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
]

all_counts = []

for file_name in csv_files:
    file_path = os.path.join(DATA_DIR, file_name)

    print(f"Reading: {file_name}")

    df = pd.read_csv(file_path)

    # 清除欄位前後空白，CICIDS2017 常有這個問題
    df.columns = df.columns.str.strip()

    if "Label" not in df.columns:
        raise ValueError(f"{file_name} 找不到 Label 欄位，目前欄位有：{df.columns.tolist()}")

    counts = df["Label"].value_counts().reset_index()
    counts.columns = ["Label", "Count"]
    counts.insert(0, "File", file_name)

    all_counts.append(counts)

# 合併每個檔案的 Label 統計
result_df = pd.concat(all_counts, ignore_index=True)

# 統計全部檔案總數
total_df = result_df.groupby("Label", as_index=False)["Count"].sum()
total_df.insert(0, "File", "TOTAL")

# 合併輸出
final_df = pd.concat([result_df, total_df], ignore_index=True)

# 儲存
output_path = os.path.join(DATA_DIR, "cicids2017_label_counts.csv")
final_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("\n===== Label Counts =====")
print(final_df)

print(f"\n已儲存：{output_path}")