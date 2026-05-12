# -*- coding: utf-8 -*-

import os
import pandas as pd

# =========================
# 路徑設定
# =========================
BASE_DIR = "D:/candy/CICIDS2017/preprocess/preprocess_8batch"          # 你前面輸出的資料夾
SAVE_DIR = "D:/candy/CICIDS2017/preprocess/preprocess_8batch"    # batch1~batch7 輸出位置

os.makedirs(SAVE_DIR, exist_ok=True)

# =========================
# 8 天資料夾順序
# =========================
folders = [
    "Monday_WorkingHours_pcap_ISCX",
    "Tuesday_WorkingHours_pcap_ISCX",
    "Wednesday_workingHours_pcap_ISCX",
    "Thursday_WorkingHours_Morning_WebAttacks_pcap_ISCX",
    "Thursday_WorkingHours_Afternoon_Infilteration_pcap_ISCX",
    "Friday_WorkingHours_Morning_pcap_ISCX",
    "Friday_WorkingHours_Afternoon_PortScan_pcap_ISCX",
    "Friday_WorkingHours_Afternoon_DDos_pcap_ISCX",
]

# batch1 = Monday + Tuesday
# batch2 = batch1 + Wednesday
# ...
# batch7 = batch6 + Friday DDos
batch_groups = {
    "batch1": folders[:2],
    "batch2": folders[:3],
    "batch3": folders[:4],
    "batch4": folders[:5],
    "batch5": folders[:6],
    "batch6": folders[:7],
    "batch7": folders[:8],
}

split_files = {
    "train": "train_60.csv",
    "val": "val_20.csv",
    "test": "test_20.csv",
}

summary_rows = []

for batch_name, used_folders in batch_groups.items():
    print("=" * 80)
    print(f"Processing {batch_name}")
    print("Included folders:")
    for f in used_folders:
        print(" -", f)

    batch_dir = os.path.join(SAVE_DIR, batch_name)
    os.makedirs(batch_dir, exist_ok=True)

    for split_name, split_file in split_files.items():
        dfs = []

        for folder in used_folders:
            file_path = os.path.join(BASE_DIR, folder, split_file)

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"找不到檔案：{file_path}")

            df = pd.read_csv(file_path)
            dfs.append(df)

        merged_df = pd.concat(dfs, ignore_index=True)

        save_path = os.path.join(batch_dir, split_file)
        merged_df.to_csv(save_path, index=False, encoding="utf-8-sig")

        label_counts = merged_df["label"].value_counts().to_dict()

        summary_rows.append({
            "batch": batch_name,
            "split": split_name,
            "total": len(merged_df),
            "label_0_benign": label_counts.get(0, 0),
            "label_1_attack": label_counts.get(1, 0),
            "included_days": " + ".join(used_folders),
        })

        print(
            f"{split_name.upper()} saved:",
            save_path,
            merged_df.shape,
            label_counts
        )

# =========================
# 儲存統計
# =========================
summary_df = pd.DataFrame(summary_rows)
summary_path = os.path.join(SAVE_DIR, "batch_summary.csv")
summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")

print("\nDone.")
print("Summary saved to:", summary_path)