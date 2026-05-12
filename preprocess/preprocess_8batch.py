# -*- coding: utf-8 -*-

import os
import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


# =====================================================
# Config
# =====================================================
DATA_DIR = "D:/candy/CICIDS2017/data/0_ori"   # 改成你的資料夾
SAVE_DIR = "D:/candy/CICIDS2017/preprocess/preprocess_8batch"

os.makedirs(SAVE_DIR, exist_ok=True)

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


# =====================================================
# Utils
# =====================================================
def sanitize_feature_names(columns):
    sanitized = []

    for col in columns:
        c = str(col).strip().lower()
        c = re.sub(r'[\/\\\s:%()\-\+]', '_', c)
        c = re.sub(r'_+', '_', c)
        c = c.strip('_')
        sanitized.append(c)

    return sanitized


def preprocess_numeric_dataset(df, label_col="label", benign_name="benign", random_state=42):
    df = df.copy()

    df.columns = df.columns.str.strip()
    df.columns = sanitize_feature_names(df.columns)

    if label_col not in df.columns:
        raise ValueError(f"找不到 label 欄位，目前欄位：{df.columns.tolist()}")

    df[label_col] = (
        df[label_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df[label_col] = np.where(
        df[label_col] == benign_name.upper(),
        0,
        1
    ).astype(np.int16)

    feature_cols = [c for c in df.columns if c != label_col]

    for col in feature_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.dropna().reset_index(drop=True)

    feature_cols = [c for c in df.columns if c != label_col]

    # 如果該檔案只有單一類別，無法 stratify
    stratify_y = df[label_col] if df[label_col].nunique() > 1 else None

    train_df, temp_df = train_test_split(
        df,
        test_size=0.4,
        random_state=random_state,
        stratify=stratify_y
    )

    stratify_temp = temp_df[label_col] if temp_df[label_col].nunique() > 1 else None

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        random_state=random_state,
        stratify=stratify_temp
    )

    scaler = MinMaxScaler()
    train_df.loc[:, feature_cols] = scaler.fit_transform(train_df[feature_cols])
    val_df.loc[:, feature_cols] = scaler.transform(val_df[feature_cols])
    test_df.loc[:, feature_cols] = scaler.transform(test_df[feature_cols])

    return train_df, val_df, test_df


# =====================================================
# Main
# =====================================================
summary_rows = []

for file_name in csv_files:
    file_path = os.path.join(DATA_DIR, file_name)

    print("=" * 80)
    print("Processing:", file_name)

    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    df.columns = sanitize_feature_names(df.columns)

    base_name = os.path.splitext(file_name)[0]
    base_name = re.sub(r'[^a-zA-Z0-9_]+', '_', base_name).strip("_")

    out_dir = os.path.join(SAVE_DIR, base_name)
    os.makedirs(out_dir, exist_ok=True)

    print("Original shape:", df.shape)
    print("Original label distribution:")
    print(df["label"].value_counts())

    train_df, val_df, test_df = preprocess_numeric_dataset(
        df,
        label_col="label",
        benign_name="BENIGN"
    )

    train_path = os.path.join(out_dir, "train_60.csv")
    val_path = os.path.join(out_dir, "val_20.csv")
    test_path = os.path.join(out_dir, "test_20.csv")

    train_df.to_csv(train_path, index=False, encoding="utf-8-sig")
    val_df.to_csv(val_path, index=False, encoding="utf-8-sig")
    test_df.to_csv(test_path, index=False, encoding="utf-8-sig")

    for split_name, split_df in [
        ("train", train_df),
        ("val", val_df),
        ("test", test_df),
    ]:
        counts = split_df["label"].value_counts().to_dict()
        summary_rows.append({
            "file": file_name,
            "split": split_name,
            "total": len(split_df),
            "label_0_benign": counts.get(0, 0),
            "label_1_attack": counts.get(1, 0),
        })

    print("Saved to:", out_dir)
    print("TRAIN:", train_df.shape, train_df["label"].value_counts().to_dict())
    print("VAL  :", val_df.shape, val_df["label"].value_counts().to_dict())
    print("TEST :", test_df.shape, test_df["label"].value_counts().to_dict())


summary_df = pd.DataFrame(summary_rows)
summary_path = os.path.join(SAVE_DIR, "split_summary.csv")
summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")

print("\nDone.")
print("Summary saved to:", summary_path)