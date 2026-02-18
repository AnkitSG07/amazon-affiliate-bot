############################# LIBRARY IMPORTS #############################

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.cluster import DBSCAN
from datetime import date, timedelta
from functools import reduce
import polars as pl
#import pyarrow
import gc
# import pandas as pd
import numpy as np
import time
import warnings
warnings.filterwarnings("ignore")

########################### DATA READING ###################################
start1 = time.perf_counter()
#df_part = spark.table("s99grp.c26779e_Payroll_Txn_Partition_1").toPandas()
#df_part = pl.from_pandas(df_part)

df_part = pl.read_csv("C:/Users/C26779E/OneDrive - EXPERIAN SERVICES CORP/Desktop/Projects/1. Payday Attributes/Corrected_Logic/200k_random_customers_txns_output_remaining.csv")
df_part = df_part[['experian_consumer_key','account_vid','cleaned_description','D_appMonth','enriched_category','account_type_code','txn_amount','txn_timestamp']]
end1 = time.perf_counter()
print(f"Data Reading Time: {end1 - start1:.4f} seconds")
#print(df_part.dtypes)
################### DATA CLEANING ####################################

df_part = df_part.with_columns(
    pl.col("cleaned_description")
      .fill_null("")                                # fill NaN/Null with empty string
      .str.to_lowercase()                           # lowercase
      .str.replace_all(r"[^a-zA-Z\s]", "")          # regex replace (remove non-letters/spaces)
      .str.strip_chars()                            # strip whitespace
      .alias("cleaned_description")
)


df_part = df_part.with_columns(
    pl.col("txn_timestamp")
      .str.slice(0, 10)                   # take only first 10 chars (YYYY-MM-DD)
      .str.strptime(pl.Date, format="%Y-%m-%d", strict=False)  # parse into Date
      .alias("txn_timestamp")
)

df_part = df_part.with_columns(
    pl.col("D_appMonth")
      .str.slice(0, 10)                   # take only first 10 chars (YYYY-MM-DD)
      .str.strptime(pl.Date, format="%Y-%m-%d", strict=False)  # parse into Date
      .alias("D_appMonth")
)

df_part = df_part.with_columns( pl.col("experian_consumer_key").cast(pl.Int64) )
df_part = df_part.with_columns( pl.col("account_vid").cast(pl.Int64) )
print(df_part.dtypes)
####################### PRE-DEFINITIONS ############################

############# CENTRAL WINDOW MODULE ###########

def build_window_module_pl(
    df_txn_with_ranks: pl.DataFrame
):
    # -----------------------------------------
    # 1. Cutoffs (all derived from ref_date)
    # -----------------------------------------
    cutoff = {
        "ref":  ref_date,
        "d30":  ref_date - timedelta(days=30),
        "d60":  ref_date - timedelta(days=60),
        "d90":  ref_date - timedelta(days=90),
        "d180": ref_date - timedelta(days=180),
        "d365": ref_date - timedelta(days=365),
    }

    # -----------------------------------------
    # 2. Window masks (expressions only)
    # -----------------------------------------
    windows = {
        "0_30":   (pl.col("txn_timestamp") > cutoff["d30"])  & (pl.col("txn_timestamp") <= cutoff["ref"]),
        "31_60":  (pl.col("txn_timestamp") > cutoff["d60"])  & (pl.col("txn_timestamp") <= cutoff["d30"]),
        "61_90":  (pl.col("txn_timestamp") > cutoff["d90"])  & (pl.col("txn_timestamp") <= cutoff["d60"]),
        "0_90":   (pl.col("txn_timestamp") > cutoff["d90"])  & (pl.col("txn_timestamp") <= cutoff["ref"]),
        "0_180":  (pl.col("txn_timestamp") > cutoff["d180"]) & (pl.col("txn_timestamp") <= cutoff["ref"]),
        "0_365":  (pl.col("txn_timestamp") > cutoff["d365"]) & (pl.col("txn_timestamp") <= cutoff["ref"]),
    }

    # -----------------------------------------
    # 3. Override codes (centralized)
    # -----------------------------------------
    override = {
        # Group A
        "NO_DDA": 999999999.0,
        "NO_INCOME_ALLTIME": 999999998.0,
        "NO_INCOME_180": 999999997.0,

        # Group B ratios
        "NUM0": 999999996.0,
        "DEN0": 999999995.0,
        "BOTH0": 999999994.0,

        # Group B intervals
        "NO_TXN": 999999990.0,
        "ONE_TXN": 999999991.0,
        
        #EXTRA
        "ZERO" : 0
    }

    key = "experian_consumer_key"

    # -----------------------------------------
    # 4. Horizon flags per customer (ALL txns)
    # -----------------------------------------
    cust_horizon = (
        df_txn_with_ranks
        .group_by(key)
        .agg([
            (pl.col("txn_timestamp") > cutoff["d365"]).any().alias("has_365"),
            (pl.col("txn_timestamp") > cutoff["d180"]).any().alias("has_180"),
        ])
    )

    # -----------------------------------------
    # 5. Split customers into Group A / Group B
    # -----------------------------------------
    cust_groupA = cust_horizon.filter(~pl.col("has_180"))
    cust_groupB = cust_horizon.filter(pl.col("has_180"))

    # -----------------------------------------
    # 6. Precompute override value for Group A
    # -----------------------------------------
    df_groupA_overrides = (
        cust_groupA
        .join(
            df_txn_with_ranks.group_by(key).agg([
                (pl.col("account_type_code") == "DDA").any().alias("has_dda"),
                (pl.col("is_income_txn")).any().alias("has_income_all_time"),
                ((pl.col("txn_timestamp") > cutoff["d180"]) & pl.col("is_income_txn")).any().alias("has_income_180"),
            ]),
            on=key,
            how="left"
        )
        .with_columns(
            pl.when(~pl.col("has_dda"))
              .then(override["NO_DDA"])
              .when(~pl.col("has_income_all_time"))
              .then(override["NO_INCOME_ALLTIME"])
              .when(~pl.col("has_income_180"))
              .then(override["NO_INCOME_180"])
              .alias("override_value")
        )
    )

    # -----------------------------------------
    # 7. Filter df_txn_with_ranks down to Group B only
    # -----------------------------------------
    df_groupB_txn = df_txn_with_ranks.join(
        cust_groupB.select([key]),
        on=key,
        how="inner"
    )

    # -----------------------------------------
    # 8. Valid ranks mask (for Group B feature logic)
    # -----------------------------------------
    valid_ranks_mask = pl.col("rank").is_in([1, 2, 3])

    # -----------------------------------------
    # 9. Override helpers for Group B
    # -----------------------------------------
    def apply_ratio_overrides(expr, num, den, is_count_amount=False):
        return (
            pl.when((num == 0) & (den == 0))
              .then(override["BOTH0"])
            .when(num == 0)
              .then(override["NUM0"] if not is_count_amount else 0)
            .when(den == 0)
              .then(override["DEN0"])
            .otherwise(expr)
        )


    def apply_interval_overrides(expr, count):
        return (
            pl.when(count == 0).then(override["NO_TXN"])
            .when(count == 1).then(override["ONE_TXN"])
            .otherwise(expr)
        )

    # For count-based features
    def apply_null_override_count(expr):
        return expr.fill_null(0)

    # For categorical features (account_vid, enriched_category)
    def apply_null_override_category(expr):
        return expr.fill_null(override["NO_TXN"])


    # -----------------------------------------
    # 10. Mode tie resolution helper
    # -----------------------------------------
    def resolve_mode_tie(modes: list[float]) -> float:
        # pick the one with highest absolute value
        return max(modes, key=lambda x: abs(x))

    return (
        cutoff,
        windows,
        override,
        df_groupA_overrides,   # customers with no 180-day txns (Group A overrides)
        df_groupB_txn,         # customers with 180-day txns (full feature pipeline)
        valid_ranks_mask,
        key,
        apply_ratio_overrides,
        apply_interval_overrides,
        apply_null_override_count,
        apply_null_override_category,
        resolve_mode_tie,
    )

############################ DATA CONCAT FUNCTION ######################################################
# Sets you specified (A11_* only, no AT_ prefix)
STRING_FEATS = {
    "A11_PDAY1050", "A11_PDAY2050", "A11_PDAY3050"
}

DATE_FEATS = {
    "A11_PDAY1403","A11_PDAY2403","A11_PDAY3403",
    "A11_PDAY1414","A11_PDAY2414","A11_PDAY3414",
    "A11_PDAY1413","A11_PDAY2413","A11_PDAY3413",
    "A11_PDAY1710","A11_PDAY2710","A11_PDAY3710",
    "A11_PDAY1720","A11_PDAY2720","A11_PDAY3720",
    "A11_PDAY1730","A11_PDAY2730","A11_PDAY3730",
    "A11_PDAY1740","A11_PDAY2740","A11_PDAY3740",
    "A11_PDAY1750","A11_PDAY2750","A11_PDAY3750",
    "A11_PDAY1760","A11_PDAY2760","A11_PDAY3760",
    "A11_PDAY4403","A11_PDAY4414","A11_PDAY4413"
}

def _ensure_all_feature_columns(df: pl.DataFrame, all_a11_cols: list[str]) -> pl.DataFrame:
    missing = [c for c in all_a11_cols if c not in df.columns]
    if not missing:
        return df
    # add as nulls; types will be set by the cast step
    return df.with_columns([pl.lit(None).alias(c) for c in missing])

def _cast_one_customer(df: pl.DataFrame) -> pl.DataFrame:
    """
    Casts, based on current dtype (checked from df.schema):
      - A11_* in STRING_FEATS -> Utf8
      - A11_* in DATE_FEATS   -> Date  (Utf8->parse, Datetime->date, others->cast)
      - Other A11_*           -> Float64
    """
    casts = []
    schema = df.schema  # dict: {col_name: pl.DataType}

    for col in df.columns:
        if not col.startswith("A11_"):
            continue

        cur = schema.get(col, None)

        if col in STRING_FEATS:
            casts.append(pl.col(col).cast(pl.Utf8).alias(col))
            continue

        if col in DATE_FEATS:
            if cur == pl.Date:
                # already Date -> no-op
                continue
            elif cur == pl.Datetime:
                casts.append(pl.col(col).dt.date().alias(col))
            elif cur == pl.Utf8:
                casts.append(pl.col(col).str.strptime(pl.Date, strict=False).alias(col))
            else:
                casts.append(pl.col(col).cast(pl.Date).alias(col))
            continue

        # Everything else: Float64
        # If already Float64, skip; else cast.
        if cur != pl.Float64:
            casts.append(pl.col(col).cast(pl.Float64).alias(col))

    return df.with_columns(casts) if casts else df

def cast_and_concat_customer_list(all_customer_feats: list[pl.DataFrame]) -> pl.DataFrame:
    """
    all_customer_feats: list of per-customer DataFrames (key + 235 A11_* features).
    Returns a single concatenated DataFrame with consistent dtypes:
      - 3 A11_* string features -> Utf8
      - listed A11_* date features -> Date
      - all other A11_* -> Float64
    """
    if not all_customer_feats:
        return pl.DataFrame()

    # 1) Union of all A11_* columns across customers
    union_cols = set()
    for df in all_customer_feats:
        union_cols.update([c for c in df.columns if c.startswith("A11_")])
    all_a11_cols = sorted(union_cols)

    # 2) Normalize each DF: add missing cols, then cast
    normalized = []
    for df in all_customer_feats:
        dfn = _ensure_all_feature_columns(df, all_a11_cols)
        dfn = _cast_one_customer(dfn)
        normalized.append(dfn)

    # 3) Concatenate. coerce=True as a safety net (should already align)
    return pl.concat(normalized, how="vertical")

##################################################################################

#### HASHING VECTORISER ####
hash_vectorizer = HashingVectorizer(
    n_features=1000,
    ngram_range=(1, 2),
    alternate_sign=False,
    norm="l2"
)
##### DBSCAN ALGORITHM #####

dbscan = DBSCAN(eps=0.5, min_samples=3)

#######################################################################################################

#results = []
count = 0
count_ping_break = 0
clustering_time = 0
attributes_creation_time = 0
all_customers_feats = []
#start = time.perf_counter()
print("Loop start")
#results_all = []

############################################ PIPELINE START ############################################

#df_part = df_part.filter(pl.col('experian_consumer_key') == 39912435985)
# Outer loop: one customer at a time
for eck, df_eck in df_part.group_by("experian_consumer_key", maintain_order=False):

    customer_results = []

    # Inner loop: all account_vid + enriched_category combos for this customer
    for (acc_vid, category), df in df_eck.group_by(
        ["account_vid", "enriched_category"], maintain_order=True
    ):
        ################ HASHING VECTORISATION ################
        texts = df["cleaned_description"].to_list()
        hash_matrix = hash_vectorizer.transform(texts)

        hash_feature_names = [f"hash_{i}" for i in range(hash_matrix.shape[1])]
        hash_df = pl.DataFrame(hash_matrix.toarray(), schema=hash_feature_names)

        ################ DROP ZERO-ONLY COLUMNS ################
        non_zero_cols = [col for col in hash_df.columns if (hash_df[col].sum() != 0)]
        hv_filtered = hash_df.select(non_zero_cols)

        ################ RUN DBSCAN ################
        
        start_clust = time.perf_counter()
        
        if hv_filtered.shape[1] > 0:
            labels = dbscan.fit_predict(hv_filtered.to_numpy())
        else:
            labels = np.full(hash_df.shape[0], -1)

        end_clust = time.perf_counter()
        customer_clust_time = end_clust-start_clust
        clustering_time = clustering_time + customer_clust_time
        #print(f"Clustering Time: {end_clust - start_clust:.4f} seconds")
        
        cluster_df = pl.DataFrame({"cluster_label": labels})

        ################ MERGE METADATA + CLUSTER ################
        meta_cols = df.select([
            "experian_consumer_key",
            "account_vid",
            "txn_amount",
            "txn_timestamp",
            "cleaned_description",
            "account_type_code",
            "enriched_category"
        ])

        final_df = pl.concat([meta_cols, cluster_df], how="horizontal")

        ################ KEEP NECESSARY COLUMNS ################
        customer_df = final_df.select([
            "experian_consumer_key",
            "account_vid",
            "enriched_category",
            "cleaned_description",
            "txn_timestamp",
            "txn_amount",
            "account_type_code",
            "cluster_label"
        ])

        customer_results.append(customer_df)

        # Cleanup
        del texts, hash_matrix, hash_df, hv_filtered, cluster_df, final_df
        gc.collect()

    # After finishing all account_vid + categories for this eck
    df_income_pl = pl.concat(customer_results, how="vertical")



################################################# TOP 3 SOURCES IDENTIFICATION #######################################################
    start2 = time.perf_counter()
    
    ref_date = (df_eck.select(pl.col("D_appMonth").max().alias("ref_date")).item())
    
    category_int = (
    pl.when(pl.col("enriched_category") == "INC-OTH-001").then(1)
    .when(pl.col("enriched_category") == "INC-OTH-002").then(2)
    .when(pl.col("enriched_category") == "INC-OTH-003").then(3)
    .when(pl.col("enriched_category") == "INC-OTH-004").then(4)
    .when(pl.col("enriched_category") == "INC-SAL-000").then(5)
    .when(pl.col("enriched_category") == "INC-SAL-002").then(6)
    .when(pl.col("enriched_category") == "INC-SAL-003").then(7)
    .when(pl.col("enriched_category") == "INC-SAL-005").then(8)
    .otherwise(0)  # fallback if category not in mapping
    )

    cutoff_180 = ref_date - timedelta(days=180)
    cutoff_30  = ref_date - timedelta(days=30)
    cutoff_60  = ref_date - timedelta(days=60)
    cutoff_90  = ref_date - timedelta(days=90)

    # 1. Filter last 180 days & exclude noise
    df_180 = (
        df_income_pl
        .filter((pl.col("txn_timestamp") >= cutoff_180) & (pl.col("txn_timestamp") <= ref_date))
        .filter(pl.col("cluster_label") != -1)
        .with_columns([
            # Create acct_cluster_id ONCE here
            (pl.col("account_vid") * 1000 + category_int + pl.col("cluster_label")).alias("acct_cluster_id")
        ])
    )

    # 2. Conditional sums
    agg = (
        df_180.group_by(["experian_consumer_key", "acct_cluster_id"])
        .agg([
            pl.when(pl.col("txn_timestamp") > cutoff_30).then(pl.col("txn_amount")).otherwise(0).sum().alias("sum_30"),
            pl.when(pl.col("txn_timestamp") > cutoff_60).then(pl.col("txn_amount")).otherwise(0).sum().alias("sum_60"),
            pl.when(pl.col("txn_timestamp") > cutoff_90).then(pl.col("txn_amount")).otherwise(0).sum().alias("sum_90"),
            pl.col("txn_amount").sum().alias("sum_180"),
        ])
    )

    # 3. Sort within each customer group
    agg_sorted = (
        agg
        .sort(
            by=["experian_consumer_key", "sum_30", "sum_60", "sum_90", "sum_180"],
            descending=[False, True, True, True, True]
        )
        .with_row_count("row_idx")
        .with_columns(
            (pl.col("row_idx") - pl.col("row_idx").min().over("experian_consumer_key") + 1)
            .alias("rank")
        )
    )

    # 4. Filter top 3
    top3_sources = agg_sorted.filter(pl.col("rank") <= 3)

    df_income_pl = df_income_pl.with_columns(
    (pl.col("account_vid") * 1000 + category_int + pl.col("cluster_label")).alias("acct_cluster_id")
    )

    # 2. Prepare df_top3 subset
    df_top3_subset = top3_sources.select([
        "experian_consumer_key", "acct_cluster_id", "rank"
    ])
    
    # 3. Fast join on integer keys
    df_txn_with_ranks = df_income_pl.join(
        df_top3_subset,
        on=["experian_consumer_key", "acct_cluster_id"],
        how="left"
    )

    income_categories = ["INC-OTH-001","INC-OTH-002","INC-OTH-003","INC-OTH-004","INC-SAL-000","INC-SAL-002","INC-SAL-003","INC-SAL-005"]

    df_txn_with_ranks = df_txn_with_ranks.with_columns( pl.col("enriched_category").is_in(income_categories).alias("is_income_txn") )

    
    (cutoff, windows, override, df_groupA_overrides, df_groupB_txn, valid_ranks_mask, key, apply_ratio_overrides, apply_interval_overrides, apply_null_override_count, apply_null_override_category, resolve_mode_tie) = build_window_module_pl(df_txn_with_ranks)


##################################### GROUP A/B identification ##################################################
    
    # --- Group A / B Identification ---
    income_categories = [
        "INC-OTH-001","INC-OTH-002","INC-OTH-003","INC-OTH-004",
        "INC-SAL-000","INC-SAL-002","INC-SAL-003","INC-SAL-005"
    ]
    
    has_dda = (df_txn_with_ranks.filter(pl.col("account_type_code") == "DDA").height > 0)
    
    has_income_all = (
        df_txn_with_ranks
        .filter(pl.col("enriched_category").is_in(income_categories))
        .height > 0
    )
    
    has_income_180 = (
        df_txn_with_ranks
        .filter((pl.col("txn_timestamp") > cutoff["d180"]) & pl.col("enriched_category").is_in(income_categories))
        .height > 0
    )
    
    if not has_dda:
        group_type = "A"; override_value = override["NO_DDA"]
    elif not has_income_all:
        group_type = "A"; override_value = override["NO_INCOME_ALLTIME"]
    elif not has_income_180:
        group_type = "A"; override_value = override["NO_INCOME_180"]
    else:
        group_type = "B"; override_value = None
    
 
######################################### ATTRIBUTE CREATION ##################################################
    
#################################################################################################
#                              FEATURES 1 - 9

# Feature 1 — A11_PDAY0010  
# Count of unique paycheck sources in last 180 days.

# Feature 2 — A11_PDAY0020  
# Ratio: sources in 0–30 days ÷ sources in 31–60 days
# Uses ratio overrides: BOTH0, DEN0, 0.

# Feature 3 — A11_PDAY0030  
# Ratio: sources in 0–30 days ÷ sources in 61–90 days
# Same override rules as Feature 2.

# Features 4–6 — A11_PDAY1040 / 2040 / 3040  
# Top‑3 account_vid by income rank.
# Missing → NO_TXN.

# Features 7–9 — A11_PDAY1050 / 2050 / 3050  
# Top‑3 enriched_category by income rank.
# Missing → NO_TXN, final output forced to string.

# Group A rule (applies to all 1–9):  
# No DDA, or no income ever, or no income in 180 days →
# all features = same override (NO_DDA / NO_INCOME_ALLTIME / NO_INCOME_180).
#################################################################################################

    
    if group_type == "A":
        # Group A → assign overrides directly
        df_demography = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY0010": [override_value],
            "A11_PDAY0020": [override_value],
            "A11_PDAY0030": [override_value],
            "A11_PDAY1040": [override_value],
            "A11_PDAY2040": [override_value],
            "A11_PDAY3040": [override_value],
            "A11_PDAY1050": [override_value],
            "A11_PDAY2050": [override_value],
            "A11_PDAY3050": [override_value],
        })
    
    else:
        # Group B → compute features
        cust_txn_B = df_txn_with_ranks.filter(valid_ranks_mask)
        df_demography = pl.DataFrame({key: [df_txn_with_ranks[0, key]]})
    
        # Feature 1 — Count of unique paycheck sources (0–180 days)
        src_count = (
            cust_txn_B
            .filter(windows["0_180"])
            .group_by(key)
            .agg(pl.col("acct_cluster_id").n_unique().alias("A11_PDAY0010"))
        )
        df_demography = df_demography.join(src_count, on=key, how="left")
        df_demography = df_demography.with_columns(
            apply_null_override_count(pl.col("A11_PDAY0010")).alias("A11_PDAY0010")
        )
    
        # Feature 2 — Ratio: sources in 0–30 / 31–60
        num_30 = (
            cust_txn_B.filter(windows["0_30"])
            .group_by(key)
            .agg(pl.col("acct_cluster_id").n_unique().alias("num_30"))
        )
        den_60 = (
            cust_txn_B.filter(windows["31_60"])
            .group_by(key)
            .agg(pl.col("acct_cluster_id").n_unique().alias("den_60"))
        )
        df_demography = df_demography.join(num_30, on=key, how="left").join(den_60, on=key, how="left")
        df_demography = df_demography.with_columns(
            apply_ratio_overrides(
                expr = pl.col("num_30") / pl.col("den_60"),
                num  = pl.col("num_30"),
                den  = pl.col("den_60"),
                is_count_amount=True  # ratio of counts → NUM0 not applicable
            ).alias("A11_PDAY0020")
        )
        df_demography = df_demography.with_columns(
            apply_null_override_count(pl.col("A11_PDAY0020")).alias("A11_PDAY0020")
        )
    
        # Feature 3 — Ratio: sources in 0–30 / 61–90
        den_90 = (
            cust_txn_B.filter(windows["61_90"])
            .group_by(key)
            .agg(pl.col("acct_cluster_id").n_unique().alias("den_90"))
        )
        df_demography = df_demography.join(den_90, on=key, how="left")
        df_demography = df_demography.with_columns(
            apply_ratio_overrides(
                expr = pl.col("num_30") / pl.col("den_90"),
                num  = pl.col("num_30"),
                den  = pl.col("den_90"),
                is_count_amount=True  # ratio of counts
            ).alias("A11_PDAY0030")
        )
        df_demography = df_demography.with_columns(
            apply_null_override_count(pl.col("A11_PDAY0030")).alias("A11_PDAY0030")
        )
    
        # Features 4–6 — account_vid of rank 1/2/3
        for r, feat in [(1, "A11_PDAY1040"), (2, "A11_PDAY2040"), (3, "A11_PDAY3040")]:
            rank_acct = (
                cust_txn_B.filter(pl.col("rank") == r)
                .group_by(key)
                .agg(pl.col("account_vid").first().alias(feat))
            )
            df_demography = df_demography.join(rank_acct, on=key, how="left")
            df_demography = df_demography.with_columns(
                apply_null_override_category(pl.col(feat)).alias(feat)
            )
    
        # Features 7–9 — enriched_category of rank 1/2/3
        for r, feat in [(1, "A11_PDAY1050"), (2, "A11_PDAY2050"), (3, "A11_PDAY3050")]:
            rank_cat = (
                cust_txn_B.filter(pl.col("rank") == r)
                .group_by(key)
                .agg(pl.col("enriched_category").first().alias(feat))
            )
            df_demography = df_demography.join(rank_cat, on=key, how="left")
            df_demography = df_demography.with_columns(
                apply_null_override_category(pl.col(feat)).alias(feat)
            )
            
        
        # Cleanup helper cols
        df_demography = df_demography.drop(["num_30", "den_60", "den_90"])
    
    df_demography = df_demography.with_columns( apply_null_override_category(pl.col('A11_PDAY1050')).cast(pl.Utf8).alias('A11_PDAY1050') )
    df_demography = df_demography.with_columns( apply_null_override_category(pl.col('A11_PDAY2050')).cast(pl.Utf8).alias('A11_PDAY2050') )   
    df_demography = df_demography.with_columns( apply_null_override_category(pl.col('A11_PDAY3050')).cast(pl.Utf8).alias('A11_PDAY3050') )   
    #print(df_demography)

    df_demography = df_demography.with_columns(pl.col('A11_PDAY0010').cast(pl.Float64).alias('A11_PDAY0010'))
    df_demography = df_demography.with_columns(pl.col('A11_PDAY0020').cast(pl.Float64).alias('A11_PDAY0020'))
    df_demography = df_demography.with_columns(pl.col('A11_PDAY0030').cast(pl.Float64).alias('A11_PDAY0030'))
    
        
#################################################################################################
#                              FEATURES 10 - 15
# ===========================================
# FEATURE FAMILY: 10–15 (Txn Count by Rank)
# ===========================================

# All features are defined only for Group B.
# Group A → all 6 features set to the same
# override (NO_DDA / NO_INCOME_ALLTIME / NO_INCOME_180).

# -------------------------------------------
# FEATURE 10 — A11_PDAY1104
# "Count of txns for Rank‑1 source in last 30 days"

# FEATURE 11 — A11_PDAY2104
# "Count of txns for Rank‑2 source in last 30 days"

# FEATURE 12 — A11_PDAY3104
# "Count of txns for Rank‑3 source in last 30 days"

# Window: 0–30 days
# Logic: count all txns for that rank within window.
# Null handling: missing → 0, then apply_null_override.

# -------------------------------------------
# FEATURE 13 — A11_PDAY1103
# "Count of txns for Rank‑1 source in last 90 days"

# FEATURE 14 — A11_PDAY2103
# "Count of txns for Rank‑2 source in last 90 days"

# FEATURE 15 — A11_PDAY3103
# "Count of txns for Rank‑3 source in last 90 days"

# Window: 0–90 days
# Logic: count all txns for that rank within window.
# Null handling: missing → 0, then apply_null_override.

#################################################################################################
  

    if group_type == "A":
        # All six features get the same override_value
        feats_10_15 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1104": [override_value],   # Rank 1, 30‑day count
            "A11_PDAY2104": [override_value],   # Rank 2, 30‑day count
            "A11_PDAY3104": [override_value],   # Rank 3, 30‑day count
            "A11_PDAY1103": [override_value],   # Rank 1, 90‑day count
            "A11_PDAY2103": [override_value],   # Rank 2, 90‑day count
            "A11_PDAY3103": [override_value],   # Rank 3, 90‑day count
        })
    
    else:
        # Group B → compute counts
        feats_10_15 = pl.DataFrame({key: [df_txn_with_ranks[0, key]]})
    
        # Helper to compute count for a given rank + window
        def add_count_feature(rank, window_mask, feat_name):
            cnt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
                .group_by(key)
                .agg(pl.count().alias(feat_name))
            )
            # Join + fill nulls with 0 + apply override logic
            return (
                feats_10_15
                .join(cnt, on=key, how="left")
                .with_columns(pl.col(feat_name).fill_null(0))
                .with_columns(apply_null_override_count(pl.col(feat_name)).alias(feat_name))
            )
    
        # Last 30 days
        feats_10_15 = add_count_feature(1, windows["0_30"], "A11_PDAY1104")
        feats_10_15 = add_count_feature(2, windows["0_30"], "A11_PDAY2104")
        feats_10_15 = add_count_feature(3, windows["0_30"], "A11_PDAY3104")
    
        # Last 90 days
        feats_10_15 = add_count_feature(1, windows["0_90"], "A11_PDAY1103")
        feats_10_15 = add_count_feature(2, windows["0_90"], "A11_PDAY2103")
        feats_10_15 = add_count_feature(3, windows["0_90"], "A11_PDAY3103")

    feats_10_15 = feats_10_15.with_columns(pl.col('A11_PDAY1104').cast(pl.Float64).alias('A11_PDAY1104'))
    feats_10_15 = feats_10_15.with_columns(pl.col('A11_PDAY2104').cast(pl.Float64).alias('A11_PDAY2104'))
    feats_10_15 = feats_10_15.with_columns(pl.col('A11_PDAY3104').cast(pl.Float64).alias('A11_PDAY3104'))
    feats_10_15 = feats_10_15.with_columns(pl.col('A11_PDAY1103').cast(pl.Float64).alias('A11_PDAY1103'))
    feats_10_15 = feats_10_15.with_columns(pl.col('A11_PDAY2103').cast(pl.Float64).alias('A11_PDAY2103'))
    feats_10_15 = feats_10_15.with_columns(pl.col('A11_PDAY3103').cast(pl.Float64).alias('A11_PDAY3103'))
##############################################################################################
#                                       FEATURES 16-21
# ===========================================
# FEATURE FAMILY: 16–21 (Rank‑wise Ratio of Txn Counts)
# ===========================================

# Group A → all six features set to the same override
# (NO_DDA / NO_INCOME_ALLTIME / NO_INCOME_180).

# Group B → compute ratios of transaction counts for ranks 1–3
# across different time windows.

# -------------------------------------------
# FEATURE 16 — A11_PDAY1113
# "Ratio of txn counts for Rank‑1 source:
#   0–30 days ÷ 31–60 days"

# FEATURE 17 — A11_PDAY2113
# "Ratio of txn counts for Rank‑2 source:
#   0–30 days ÷ 31–60 days"

# FEATURE 18 — A11_PDAY3113
# "Ratio of txn counts for Rank‑3 source:
#   0–30 days ÷ 31–60 days"

# -------------------------------------------
# FEATURE 19 — A11_PDAY1123
# "Ratio of txn counts for Rank‑1 source:
#   0–30 days ÷ 61–90 days"

# FEATURE 20 — A11_PDAY2123
# "Ratio of txn counts for Rank‑2 source:
#   0–30 days ÷ 61–90 days"

# FEATURE 21 — A11_PDAY3123
# "Ratio of txn counts for Rank‑3 source:
#   0–30 days ÷ 61–90 days"

# -------------------------------------------
# Ratio override rules (applied via apply_ratio_overrides_count_amount):
#   • num = 0 AND den = 0 → BOTH0
#   • num = 0 AND den > 0 → 0   (count‑ratio rule)
#   • num > 0 AND den = 0 → DEN0
#   • else → num/den

# Null handling:
#   • Fill missing counts with 0
#   • Apply null override after ratio assignment
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 16–21
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_16_21 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1113": [override_value],   # Rank 1, ratio 0–30 / 31–60
            "A11_PDAY2113": [override_value],   # Rank 2, ratio 0–30 / 31–60
            "A11_PDAY3113": [override_value],   # Rank 3, ratio 0–30 / 31–60
            "A11_PDAY1123": [override_value],   # Rank 1, ratio 0–30 / 61–90
            "A11_PDAY2123": [override_value],   # Rank 2, ratio 0–30 / 61–90
            "A11_PDAY3123": [override_value],   # Rank 3, ratio 0–30 / 61–90
        })
    
    else:
        # Group B → compute ratios
        feats_16_21 = df_groupB_txn.select(key).unique()
    
        # Helper: count txns for a given rank & window
        def count_txns(rank: int, window_mask: pl.Expr, alias: str):
            return (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
                .group_by(key)
                .agg(pl.count().alias(alias))
            )
    
        # Helper: compute ratio for a given rank
        def ratio_feature(rank: int, num_mask: pl.Expr, den_mask: pl.Expr, feature_name: str):
            num_alias = f"{feature_name}_num"
            den_alias = f"{feature_name}_den"
    
            num_df = count_txns(rank, num_mask, num_alias)
            den_df = count_txns(rank, den_mask, den_alias)
    
            out = (
                feats_16_21
                .join(num_df, on=key, how="left")
                .join(den_df, on=key, how="left")
                .with_columns([
                    pl.col(num_alias).fill_null(0),
                    pl.col(den_alias).fill_null(0),
                ])
                .with_columns(
                    apply_ratio_overrides(
                        expr = pl.col(num_alias) / pl.col(den_alias),
                        num  = pl.col(num_alias),
                        den  = pl.col(den_alias),
                        is_count_amount=True
                    ).alias(feature_name)
                )
                .with_columns(
                    apply_null_override_count(pl.col(feature_name)).alias(feature_name)
                )
                .drop([num_alias, den_alias])
            )
            return out
    
        # Build all 6 ratio features
        # 0–30 / 31–60
        feats_16_21 = ratio_feature(1, windows["0_30"], windows["31_60"], "A11_PDAY1113")
        feats_16_21 = ratio_feature(2, windows["0_30"], windows["31_60"], "A11_PDAY2113")
        feats_16_21 = ratio_feature(3, windows["0_30"], windows["31_60"], "A11_PDAY3113")
    
        # 0–30 / 61–90
        feats_16_21 = ratio_feature(1, windows["0_30"], windows["61_90"], "A11_PDAY1123")
        feats_16_21 = ratio_feature(2, windows["0_30"], windows["61_90"], "A11_PDAY2123")
        feats_16_21 = ratio_feature(3, windows["0_30"], windows["61_90"], "A11_PDAY3123")

    #print(feats_16_21)
#########################################################################################################
#                                       FEATURES 22-27
# ===========================================
# FEATURE FAMILY: 22–27 (Mode interval)
# ===========================================
# Features 22–24: Mode interval (days between txns) for Rank 1–3 sources in last 30 days
# Features 25–27: Mode interval (days between txns) for Rank 1–3 sources in last 90 days

# Overrides:
#   • NO_TXN → if no transactions in window
#   • ONE_TXN → if only one transaction (no interval possible)

# Tie‑breaker:
#   • If multiple intervals have equal frequency, choose the largest interval.

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 22–27
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_22_27 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1204": [override_value],   # Rank 1, mode interval in 30 days
            "A11_PDAY2204": [override_value],   # Rank 2, mode interval in 30 days
            "A11_PDAY3204": [override_value],   # Rank 3, mode interval in 30 days
            "A11_PDAY1203": [override_value],   # Rank 1, mode interval in 90 days
            "A11_PDAY2203": [override_value],   # Rank 2, mode interval in 90 days
            "A11_PDAY3203": [override_value],   # Rank 3, mode interval in 90 days
        })
    
    else:
        # Group B → compute mode intervals
        feats_22_27 = df_groupB_txn.select(key).unique()
    
        # Helper: compute mode interval for a given rank + window
        def mode_interval_feature(rank: int, window_mask: pl.Expr, feature_name: str):
            # Filter transactions for this rank + window
            txns = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
                .with_columns(
                    (pl.col("txn_timestamp").diff().dt.total_days().alias("interval_days"))
                )
            )
    
            # Compute mode of interval_days with tie‑breaker (largest wins)
            mode_df = (
                txns.group_by(key)
                .agg(
                    pl.col("interval_days")
                    .mode()
                    .max()   # tie‑breaker: choose largest interval if multiple modes
                    .alias(feature_name)
                )
            )
    
            # Apply overrides: NO_TXN, ONE_TXN
            out = (
                feats_22_27
                .join(mode_df, on=key, how="left")
                .with_columns(
                    pl.when(pl.col(feature_name).is_null())
                      .then(override["NO_TXN"])   # no transactions in window
                      .when(pl.col(feature_name) == 0)
                      .then(override["ONE_TXN"])  # only one txn → no interval
                      .otherwise(pl.col(feature_name))
                      .alias(feature_name)
                )
            )
            return out

        # Build all 6 mode interval features
        # 30‑day window
        feats_22_27 = mode_interval_feature(1, windows["0_30"], "A11_PDAY1204")
        feats_22_27 = mode_interval_feature(2, windows["0_30"], "A11_PDAY2204")
        feats_22_27 = mode_interval_feature(3, windows["0_30"], "A11_PDAY3204")
    
        # 90‑day window
        feats_22_27 = mode_interval_feature(1, windows["0_90"], "A11_PDAY1203")
        feats_22_27 = mode_interval_feature(2, windows["0_90"], "A11_PDAY2203")
        feats_22_27 = mode_interval_feature(3, windows["0_90"], "A11_PDAY3203")

    #print(feats_22_27)
###################################################################################################################
#                                FEATURES 28-33
# ===========================================
# FEATURE FAMILY: 28–33 (Mode Dominance Ratios)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Compute intervals between consecutive txns.
#     - Find the mode interval (most frequent gap).
#     - Dominance = % of intervals equal to that mode.

# Tie‑breaker:
#   • If multiple intervals have equal frequency, pick the largest interval.

# Overrides:
#   • NO_TXN → if no transactions in the window.
#   • ONE_TXN → if only one transaction in the window (no interval possible).
#   • For ≥2 txns → compute dominance normally.

# -------------------------------------------
# FEATURE 28 — A11_PDAY1214
# Mode dominance (%) for Rank‑1 source in last 30 days

# FEATURE 29 — A11_PDAY2214
# Mode dominance (%) for Rank‑2 source in last 30 days

# FEATURE 30 — A11_PDAY3214
# Mode dominance (%) for Rank‑3 source in last 30 days

# -------------------------------------------
# FEATURE 31 — A11_PDAY1213
# Mode dominance (%) for Rank‑1 source in last 90 days

# FEATURE 32 — A11_PDAY2213
# Mode dominance (%) for Rank‑2 source in last 90 days

# FEATURE 33 — A11_PDAY3213
# Mode dominance (%) for Rank‑3 source in last 90 days
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 28–33
###############################################


    if group_type == "A":
        # All six features get the same override_value
        feats_28_33 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1214": [override_value],
            "A11_PDAY2214": [override_value],
            "A11_PDAY3214": [override_value],
            "A11_PDAY1213": [override_value],
            "A11_PDAY2213": [override_value],
            "A11_PDAY3213": [override_value],
        })
    
    else:
        feats_28_33 = df_groupB_txn.select(key).unique()
    
        # Helper: compute mode dominance for rank × window
        def mode_dominance(rank: int, window_mask: pl.Expr, feature_name: str):
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
    
            # Compute day intervals
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg(
                    (pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals"))
                )
            )
    
            # If no txns → NO_TXN
            # If only one txn → ONE_TXN
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            mode_vals = (
                intervals.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])  # tie‑breaker: largest interval
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_interval"))
            )
    
            dominance = (
                intervals.explode("intervals")
                .join(mode_vals, on=key, how="left")
                .with_columns((pl.col("intervals") == pl.col("mode_interval")).alias("is_mode"))
                .group_by(key)
                .agg((pl.col("is_mode").sum() / pl.count() * 100).alias("mode_dominance"))
            )
    
            out = (
                feats_28_33
                .join(txn_counts, on=key, how="left")
                .join(dominance, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    apply_interval_overrides(
                        expr=pl.col("mode_dominance"),
                        count=pl.col("txn_count"),
                    ).alias(feature_name)
                )
                .select([key, feature_name])
            )
            return out
    
        # Build all 6 features
        for r, fname in [(1, "A11_PDAY1214"), (2, "A11_PDAY2214"), (3, "A11_PDAY3214")]:
            feats_28_33 = feats_28_33.join(mode_dominance(r, windows["0_30"], fname), on=key, how="left")
    
        for r, fname in [(1, "A11_PDAY1213"), (2, "A11_PDAY2213"), (3, "A11_PDAY3213")]:
            feats_28_33 = feats_28_33.join(mode_dominance(r, windows["0_90"], fname), on=key, how="left")
  
    #print(feats_28_33)
#############################################################################
#                          FEATURES 33-39
# ===========================================
# FEATURE FAMILY: 34–39 (Large Interval Counts)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Compute intervals (days between consecutive txns).
#     - Compute mode interval (most frequent gap, tie‑breaker = largest).
#     - Count how many intervals > 1.5 × mode interval.

# Overrides:
#   • NO_TXN → if no transactions in the window.
#   • ONE_TXN → if only one transaction (no interval possible).
#   • For ≥2 txns → compute large interval count normally.

# -------------------------------------------
# FEATURE 34 — A11_PDAY1224
# Count of intervals > 1.5 × mode interval for Rank‑1 in last 30 days

# FEATURE 35 — A11_PDAY2224
# Count of intervals > 1.5 × mode interval for Rank‑2 in last 30 days

# FEATURE 36 — A11_PDAY3224
# Count of intervals > 1.5 × mode interval for Rank‑3 in last 30 days

# -------------------------------------------
# FEATURE 37 — A11_PDAY1223
# Count of intervals > 1.5 × mode interval for Rank‑1 in last 90 days

# FEATURE 38 — A11_PDAY2223
# Count of intervals > 1.5 × mode interval for Rank‑2 in last 90 days

# FEATURE 39 — A11_PDAY3223
# Count of intervals > 1.5 × mode interval for Rank‑3 in last 90 days
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 34–39
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_34_39 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1224": [override_value],
            "A11_PDAY2224": [override_value],
            "A11_PDAY3224": [override_value],
            "A11_PDAY1223": [override_value],
            "A11_PDAY2223": [override_value],
            "A11_PDAY3223": [override_value],
        })
    
    else:
        feats_34_39 = df_groupB_txn.select(key).unique()
    
        def count_large_intervals(rank: int, window_mask: pl.Expr, feature_name: str):
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg(
                    (pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals"))
                )
            )
    
            mode_vals = (
                intervals.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])  # tie‑breaker: largest interval
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_interval"))
            )
    
            large_counts = (
                intervals.explode("intervals")
                .join(mode_vals, on=key, how="left")
                .with_columns((pl.col("intervals") > (1.5 * pl.col("mode_interval"))).alias("is_large"))
                .group_by(key)
                .agg(pl.col("is_large").sum().alias("large_count"))
            )
    
            out = (
                feats_34_39
                .join(txn_counts, on=key, how="left")
                .join(large_counts, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    apply_interval_overrides(
                        expr=pl.col("large_count"),
                        count=pl.col("txn_count"),
                    ).alias(feature_name)
                )
                .select([key, feature_name])
            )
            return out
    
        # Build all 6 features
        for r, fname in [(1, "A11_PDAY1224"), (2, "A11_PDAY2224"), (3, "A11_PDAY3224")]:
            feats_34_39 = feats_34_39.join(count_large_intervals(r, windows["0_30"], fname), on=key, how="left")
    
        for r, fname in [(1, "A11_PDAY1223"), (2, "A11_PDAY2223"), (3, "A11_PDAY3223")]:
            feats_34_39 = feats_34_39.join(count_large_intervals(r, windows["0_90"], fname), on=key, how="left")

    #print(feats_34_39)

#######################################################################
#                           Features 40-45
# ===========================================
# FEATURE FAMILY: 40–45 (Recent-to-Mode Interval Ratios)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Compute intervals (days between consecutive txns).
#     - Find mode interval (most frequent gap, tie‑breaker = largest).
#     - Compute most recent interval (last gap).
#     - Ratio = recent_interval ÷ mode_interval.

# Override rules:
#   • NO_TXN → if no transactions in the window.
#   • ONE_TXN → if only one transaction (no interval possible).
#   • For ≥2 txns:
#       - num = 0 AND den = 0 → BOTH0
#       - den = 0 → DEN0
#       - num = 0 → NUM0
#   • Tie‑breaker: if multiple intervals have equal frequency, choose the larger interval.
#   • Null safety: txn_count null → 0.

# -------------------------------------------
# FEATURE 40 — A11_PDAY1234
# Ratio of recent interval / mode interval for Rank‑1 in last 30 days

# FEATURE 41 — A11_PDAY2234
# Ratio of recent interval / mode interval for Rank‑2 in last 30 days

# FEATURE 42 — A11_PDAY3234
# Ratio of recent interval / mode interval for Rank‑3 in last 30 days

# -------------------------------------------
# FEATURE 43 — A11_PDAY1233
# Ratio of recent interval / mode interval for Rank‑1 in last 90 days

# FEATURE 44 — A11_PDAY2233
# Ratio of recent interval / mode interval for Rank‑2 in last 90 days

# FEATURE 45 — A11_PDAY3233
# Ratio of recent interval / mode interval for Rank‑3 in last 90 days
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 40–45
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_40_45 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1234": [override_value],
            "A11_PDAY2234": [override_value],
            "A11_PDAY3234": [override_value],
            "A11_PDAY1233": [override_value],
            "A11_PDAY2233": [override_value],
            "A11_PDAY3233": [override_value],
        })
    
    else:
        feats_40_45 = df_groupB_txn.select(key).unique()
    
        def ratio_recent_to_mode(rank: int, window_mask: pl.Expr, feature_name: str):
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg(
                    (pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals"))
                )
            )
    
            mode_vals = (
                intervals.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])  # tie‑breaker: largest interval
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_interval"))
            )
    
            recent_vals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg(
                    (pl.col("txn_timestamp").diff().dt.total_days().last()).alias("recent_interval")
                )
            )
    
            ratio_vals = (
                mode_vals
                .join(recent_vals, on=key, how="left")
                .with_columns((pl.col("recent_interval") / pl.col("mode_interval")).alias("ratio_raw"))
            )
    
            out = (
                feats_40_45
                .join(txn_counts, on=key, how="left")
                .join(ratio_vals, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    apply_interval_overrides(
                        expr=pl.col("ratio_raw"),
                        count=pl.col("txn_count"),
                    ).alias("ratio_after_interval")
                )
                .with_columns(
                    apply_ratio_overrides(
                        expr=pl.col("ratio_after_interval"),
                        num=pl.col("recent_interval"),
                        den=pl.col("mode_interval"),
                    ).alias(feature_name)
                )
                .select([key, feature_name])
            )
            return out
    
        # Build all 6 features
        for r, fname in [(1, "A11_PDAY1234"), (2, "A11_PDAY2234"), (3, "A11_PDAY3234")]:
            feats_40_45 = feats_40_45.join(ratio_recent_to_mode(r, windows["0_30"], fname), on=key, how="left")
    
        for r, fname in [(1, "A11_PDAY1233"), (2, "A11_PDAY2233"), (3, "A11_PDAY3233")]:
            feats_40_45 = feats_40_45.join(ratio_recent_to_mode(r, windows["0_90"], fname), on=key, how="left")

    #print(feats_40_45)

#######################################################################################
#                               Features 46-63
# ===========================================
# FEATURE FAMILY: 46–63 (Interval Statistics)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Compute intervals (days between consecutive txns).
#     - Derive three statistics:
#         • Max interval
#         • Min interval
#         • Average interval

# Overrides:
#   • NO_TXN → if no transactions in the window.
#   • ONE_TXN → if only one transaction (no interval possible).
#   • For ≥2 txns → compute max, min, avg normally.
#   • No ratio overrides apply here.

# -------------------------------------------
# FEATURES 46–54 (30‑day window)
# Rank 1 → A11_PDAY1244 (max), A11_PDAY1254 (min), A11_PDAY1264 (avg)
# Rank 2 → A11_PDAY2244, A11_PDAY2254, A11_PDAY2264
# Rank 3 → A11_PDAY3244, A11_PDAY3254, A11_PDAY3264

# FEATURES 55–63 (90‑day window)
# Rank 1 → A11_PDAY1243 (max), A11_PDAY1253 (min), A11_PDAY1263 (avg)
# Rank 2 → A11_PDAY2243, A11_PDAY2253, A11_PDAY2263
# Rank 3 → A11_PDAY3243, A11_PDAY3253, A11_PDAY3263
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 46–63
###############################################

    if group_type == "A":
        # All 18 features get the same override_value
        feats_46_63 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            # 30-day features
            "A11_PDAY1244": [override_value],
            "A11_PDAY1254": [override_value],
            "A11_PDAY1264": [override_value],
            "A11_PDAY2244": [override_value],
            "A11_PDAY2254": [override_value],
            "A11_PDAY2264": [override_value],
            "A11_PDAY3244": [override_value],
            "A11_PDAY3254": [override_value],
            "A11_PDAY3264": [override_value],
            # 90-day features
            "A11_PDAY1243": [override_value],
            "A11_PDAY1253": [override_value],
            "A11_PDAY1263": [override_value],
            "A11_PDAY2243": [override_value],
            "A11_PDAY2253": [override_value],
            "A11_PDAY2263": [override_value],
            "A11_PDAY3243": [override_value],
            "A11_PDAY3253": [override_value],
            "A11_PDAY3263": [override_value],
        })
    
    else:
        feats_46_63 = df_groupB_txn.select(key).unique()
    
        def interval_stats(rank: int, window_mask: pl.Expr,
                           fname_max: str, fname_min: str, fname_avg: str):
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg(
                    (pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals"))
                )
            )
    
            stats = (
                intervals.explode("intervals")
                .group_by(key)
                .agg([
                    pl.col("intervals").max().alias("max_interval"),
                    pl.col("intervals").min().alias("min_interval"),
                    pl.col("intervals").mean().alias("avg_interval"),
                ])
            )
    
            out = (
                feats_46_63
                .join(txn_counts, on=key, how="left")
                .join(stats, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns([
                    apply_interval_overrides(pl.col("max_interval"), pl.col("txn_count")).alias(fname_max),
                    apply_interval_overrides(pl.col("min_interval"), pl.col("txn_count")).alias(fname_min),
                    apply_interval_overrides(pl.col("avg_interval"), pl.col("txn_count")).alias(fname_avg),
                ])
                .select([key, fname_max, fname_min, fname_avg])
            )
            return out
    
        # Build all 18 features
        for r, fnames in [
            (1, ("A11_PDAY1244","A11_PDAY1254","A11_PDAY1264")),
            (2, ("A11_PDAY2244","A11_PDAY2254","A11_PDAY2264")),
            (3, ("A11_PDAY3244","A11_PDAY3254","A11_PDAY3264")),
        ]:
            feats_46_63 = feats_46_63.join(interval_stats(r, windows["0_30"], *fnames), on=key, how="left")
    
        for r, fnames in [
            (1, ("A11_PDAY1243","A11_PDAY1253","A11_PDAY1263")),
            (2, ("A11_PDAY2243","A11_PDAY2253","A11_PDAY2263")),
            (3, ("A11_PDAY3243","A11_PDAY3253","A11_PDAY3263")),
        ]:
            feats_46_63 = feats_46_63.join(interval_stats(r, windows["0_90"], *fnames), on=key, how="left")


    #print(feats_46_63)
#######################################################################
#                          Feats 64-69
# ===========================================
# FEATURE FAMILY: 64–69 (Range Ratio of Intervals)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Compute intervals (days between consecutive txns).
#     - Derive max, min, and average interval.
#     - Numerator = max_interval – min_interval
#     - Denominator = avg_interval
#     - Ratio = (max – min) ÷ avg

# Override rules:
#   • NO_TXN → if no transactions in the window.
#   • ONE_TXN → if only one transaction (no interval possible).
#   • For ≥2 txns:
#       - If num == 0 and den == 0 → BOTH0
#       - If den == 0 → DEN0
#       - NUM0 does not apply here (because max – min = 0 is valid → ratio = 0).
#   • Null safety: txn_count null → 0.

# -------------------------------------------
# FEATURES 64–66 (30‑day window)
# Rank 1 → A11_PDAY1274 (range ratio)
# Rank 2 → A11_PDAY2274
# Rank 3 → A11_PDAY3274

# FEATURES 67–69 (90‑day window)
# Rank 1 → A11_PDAY1273 (range ratio)
# Rank 2 → A11_PDAY2273
# Rank 3 → A11_PDAY3273
# ===========================================


###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 64–69
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_64_69 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1274": [override_value],
            "A11_PDAY2274": [override_value],
            "A11_PDAY3274": [override_value],
            "A11_PDAY1273": [override_value],
            "A11_PDAY2273": [override_value],
            "A11_PDAY3273": [override_value],
        })
    
    else:
        feats_64_69 = df_groupB_txn.select(key).unique()
    
        def range_ratio(rank: int, window_mask: pl.Expr, fname_rr: str):
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg(
                    (pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals"))
                )
            )
    
            stats = (
                intervals.explode("intervals")
                .group_by(key)
                .agg([
                    pl.col("intervals").max().alias("max_interval"),
                    pl.col("intervals").min().alias("min_interval"),
                    pl.col("intervals").mean().alias("avg_interval"),
                ])
            )
    
            ratio_vals = (
                stats
                .with_columns([
                    (pl.col("max_interval") - pl.col("min_interval")).alias("num"),
                    pl.col("avg_interval").alias("den"),
                ])
                .with_columns((pl.col("num") / pl.col("den")).alias("ratio_raw"))
            )
    
            out = (
                feats_64_69
                .join(txn_counts, on=key, how="left")
                .join(ratio_vals, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    apply_interval_overrides(pl.col("ratio_raw"), pl.col("txn_count")).alias("ratio_after_interval")
                )
                .with_columns(
                    apply_ratio_overrides(
                        expr=pl.col("ratio_after_interval"),
                        num=pl.col("num"),
                        den=pl.col("den"),
                        is_count_amount = True
                    ).alias(fname_rr)
                )
                .select([key, fname_rr])
            )
            return out
    
        # Build all 6 features
        for r, fname_rr in [(1, "A11_PDAY1274"), (2, "A11_PDAY2274"), (3, "A11_PDAY3274")]:
            feats_64_69 = feats_64_69.join(range_ratio(r, windows["0_30"], fname_rr), on=key, how="left")
    
        for r, fname_rr in [(1, "A11_PDAY1273"), (2, "A11_PDAY2273"), (3, "A11_PDAY3273")]:
            feats_64_69 = feats_64_69.join(range_ratio(r, windows["0_90"], fname_rr), on=key, how="left")

    #print(feats_64_69)

###################################################################
#                      Features 70-75
# ===========================================
# FEATURE FAMILY: 70–75 (Coefficient of Variation of Intervals)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Compute intervals (days between consecutive txns).
#     - Derive mean interval and standard deviation of intervals.
#     - CV = std(intervals) ÷ mean(intervals).

# Override rules:
#   • NO_TXN → if no transactions in the window.
#   • ONE_TXN → if only one transaction (no interval possible).
#   • For ≥2 txns:
#       - num = std_interval, den = mean_interval
#       - If num == 0 and den == 0 → BOTH0
#       - If den == 0 → DEN0
#       - NUM0 does not apply here (std = 0 is valid → CV = 0).
#   • Null safety: txn_count null → 0.

# -------------------------------------------
# FEATURES 70–72 (30‑day window)
# Rank 1 → A11_PDAY1284 (CV)
# Rank 2 → A11_PDAY2284
# Rank 3 → A11_PDAY3284

# FEATURES 73–75 (90‑day window)
# Rank 1 → A11_PDAY1283 (CV)
# Rank 2 → A11_PDAY2283
# Rank 3 → A11_PDAY3283
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 70–75
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_70_75 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1284": [override_value],
            "A11_PDAY2284": [override_value],
            "A11_PDAY3284": [override_value],
            "A11_PDAY1283": [override_value],
            "A11_PDAY2283": [override_value],
            "A11_PDAY3283": [override_value],
        })
    
    else:
        feats_70_75 = df_groupB_txn.select(key).unique()
    
        def cv_interval(rank: int, window_mask: pl.Expr, fname_cv: str):
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == rank) & window_mask)
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg(
                    (pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals"))
                )
            )
    
            stats = (
                intervals.explode("intervals")
                .group_by(key)
                .agg([
                    pl.col("intervals").mean().alias("mean_interval"),
                    pl.col("intervals").std().fill_null(0).alias("std_interval"),
                ])
            )
    
            ratio_vals = (
                stats
                .with_columns([
                    pl.col("std_interval").alias("num"),
                    pl.col("mean_interval").alias("den"),
                ])
                .with_columns((pl.col("num") / pl.col("den")).alias("ratio_raw"))
            )
    
            out = (
                feats_70_75
                .join(txn_counts, on=key, how="left")
                .join(ratio_vals, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    apply_interval_overrides(pl.col("ratio_raw"), pl.col("txn_count")).alias("ratio_after_interval")
                )
                .with_columns(
                    apply_ratio_overrides(
                        expr=pl.col("ratio_after_interval"),
                        num=pl.col("num"),
                        den=pl.col("den"),
                        is_count_amount=True   # ensures NUM0 not applied, CV=0 is valid
                    ).alias(fname_cv)
                )
                .select([key, fname_cv])
            )
            return out
    
        # Build all 6 features
        for r, fname_cv in [(1, "A11_PDAY1284"), (2, "A11_PDAY2284"), (3, "A11_PDAY3284")]:
            feats_70_75 = feats_70_75.join(cv_interval(r, windows["0_30"], fname_cv), on=key, how="left")
    
        for r, fname_cv in [(1, "A11_PDAY1283"), (2, "A11_PDAY2283"), (3, "A11_PDAY3283")]:
            feats_70_75 = feats_70_75.join(cv_interval(r, windows["0_90"], fname_cv), on=key, how="left")

    #print(feats_70_75)

#######################################################
#                     Feats 76-81
# ===========================================
# FEATURE FAMILY: 76–81 (Cross-Window Mode Interval Ratios)
# ===========================================

# Definition:
#   • For each rank (1–3), compare mode interval in 30‑day window
#     against mode interval in another window.
#   • Two sets of ratios:
#       • 30d ÷ 31–60d (Features 76–78)
#       • 30d ÷ 61–90d (Features 79–81)

# Computation:
#   • Mode interval = most frequent gap between txns (tie‑breaker: largest interval).
#   • Ratio = mode_num ÷ mode_den.

# Override rules:
#   • Interval overrides (apply first):
#       - If numerator window has 0 txns → NO_TXN
#       - If numerator window has 1 txn → ONE_TXN
#       - If denominator window has 0 txns → NO_TXN
#       - If denominator window has 1 txn → ONE_TXN
#       - Only when BOTH windows have ≥2 txns do we compute ratio.
#   • Ratio overrides (apply second):
#       - If num == 0 and den == 0 → BOTH0
#       - If den == 0 → DEN0
#       - NUM0 does not apply here (mode interval = 0 is valid).
#   • Null safety: txn_count null → 0.

# -------------------------------------------
# FEATURES 76–78 (30d ÷ 31–60d)
# Rank 1 → A11_PDAY1293
# Rank 2 → A11_PDAY2293
# Rank 3 → A11_PDAY3293

# FEATURES 79–81 (30d ÷ 61–90d)
# Rank 1 → A11_PDAY1303
# Rank 2 → A11_PDAY2303
# Rank 3 → A11_PDAY3303
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 76–81
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_76_81 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1293": [override_value],
            "A11_PDAY2293": [override_value],
            "A11_PDAY3293": [override_value],
            "A11_PDAY1303": [override_value],
            "A11_PDAY2303": [override_value],
            "A11_PDAY3303": [override_value],
        })
    
    else:
        feats_76_81 = df_groupB_txn.select(key).unique()
    
        # 30d vs 31–60d (IDs 76–78)
        for r, fname_ratio in [(1, "A11_PDAY1293"), (2, "A11_PDAY2293"), (3, "A11_PDAY3293")]:
            df_num = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
            df_den = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["31_60"])
    
            txn_counts_num = df_num.group_by(key).agg(pl.count().alias("txn_count_num"))
            txn_counts_den = df_den.group_by(key).agg(pl.count().alias("txn_count_den"))
    
            intervals_num = (
                df_num.sort("txn_timestamp")
                .group_by(key)
                .agg((pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals")))
            )
            intervals_den = (
                df_den.sort("txn_timestamp")
                .group_by(key)
                .agg((pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals")))
            )
    
            mode_num = (
                intervals_num.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_num"))
            )
            mode_den = (
                intervals_den.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_den"))
            )
    
            ratio_vals = (
                feats_76_81
                .with_columns(pl.lit(r).alias("rank"))
                .join(mode_num, on=key, how="left")
                .join(mode_den, on=key, how="left")
                .join(txn_counts_num, on=key, how="left")
                .join(txn_counts_den, on=key, how="left")
                .with_columns([
                    pl.col("txn_count_num").fill_null(0),
                    pl.col("txn_count_den").fill_null(0),
                ])
                .with_columns((pl.col("mode_num") / pl.col("mode_den")).alias("ratio_raw"))
                .with_columns(
                    apply_interval_overrides(
                        expr=pl.col("ratio_raw"),
                        count=pl.min_horizontal("txn_count_num", "txn_count_den"),
                    ).alias("ratio_after_interval")
                )
                .with_columns(
                    apply_ratio_overrides(
                        expr=pl.col("ratio_after_interval"),
                        num=pl.col("mode_num"),
                        den=pl.col("mode_den"),
                        is_count_amount=True
                    ).alias(fname_ratio)
                )
                .select([key, fname_ratio])
            )
    
            feats_76_81 = feats_76_81.join(ratio_vals, on=key, how="left")
    
        # 30d vs 61–90d (IDs 79–81)
        for r, fname_ratio in [(1, "A11_PDAY1303"), (2, "A11_PDAY2303"), (3, "A11_PDAY3303")]:
            df_num = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
            df_den = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["61_90"])
    
            txn_counts_num = df_num.group_by(key).agg(pl.count().alias("txn_count_num"))
            txn_counts_den = df_den.group_by(key).agg(pl.count().alias("txn_count_den"))
    
            intervals_num = (
                df_num.sort("txn_timestamp")
                .group_by(key)
                .agg((pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals")))
            )
            intervals_den = (
                df_den.sort("txn_timestamp")
                .group_by(key)
                .agg((pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals")))
            )
    
            mode_num = (
                intervals_num.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_num"))
            )
            mode_den = (
                intervals_den.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_den"))
            )
    
            ratio_vals = (
                feats_76_81
                .with_columns(pl.lit(r).alias("rank"))
                .join(mode_num, on=key, how="left")
                .join(mode_den, on=key, how="left")
                .join(txn_counts_num, on=key, how="left")
                .join(txn_counts_den, on=key, how="left")
                .with_columns([
                    pl.col("txn_count_num").fill_null(0),
                    pl.col("txn_count_den").fill_null(0),
                ])
                .with_columns((pl.col("mode_num") / pl.col("mode_den")).alias("ratio_raw"))
                .with_columns(
                    apply_interval_overrides(
                        expr=pl.col("ratio_raw"),
                        count=pl.min_horizontal("txn_count_num", "txn_count_den"),
                    ).alias("ratio_after_interval")
                )
                .with_columns(
                    apply_ratio_overrides(
                        expr=pl.col("ratio_after_interval"),
                        num=pl.col("mode_num"),
                        den=pl.col("mode_den"),
                        is_count_amount=True
                    ).alias(fname_ratio)
                )
                .select([key, fname_ratio])
            )
    
            feats_76_81 = feats_76_81.join(ratio_vals, on=key, how="left")

    #print(feats_76_81)

#######################################################
#                     Feats 82-87
# ===========================================
# FEATURE FAMILY: 82–87 (Missed Paychecks Count)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Compute intervals (days between consecutive txns).
#     - Find mode interval (most frequent gap, tie‑breaker = largest).
#     - Flag intervals > mode_interval as "missed paychecks".
#     - Count total missed paychecks.

# Override rules:
#   • NO_TXN → if no transactions in the window.
#   • ONE_TXN → if only one transaction (no interval possible).
#   • For ≥2 txns → compute missed_count normally.
#   • No ratio overrides apply here.

# -------------------------------------------
# FEATURES 82–84 (30‑day window)
# Rank 1 → A11_PDAY1314
# Rank 2 → A11_PDAY2314
# Rank 3 → A11_PDAY3314

# FEATURES 85–87 (90‑day window)
# Rank 1 → A11_PDAY1313
# Rank 2 → A11_PDAY2313
# Rank 3 → A11_PDAY3313
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 82–87
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_82_87 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1314": [override_value],
            "A11_PDAY2314": [override_value],
            "A11_PDAY3314": [override_value],
            "A11_PDAY1313": [override_value],
            "A11_PDAY2313": [override_value],
            "A11_PDAY3313": [override_value],
        })
    
    else:
        feats_82_87 = df_groupB_txn.select(key).unique()
    
        # 30‑day window (IDs 82–84)
        for r, fname_out in [(1, "A11_PDAY1314"), (2, "A11_PDAY2314"), (3, "A11_PDAY3314")]:
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg((pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals")))
            )
    
            mode_tbl = (
                intervals.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_interval"))
            )
    
            joined = (
                intervals.explode("intervals")
                .join(mode_tbl, on=key, how="left")
                .with_columns((pl.col("intervals") > pl.col("mode_interval")).cast(pl.Int64).alias("missed_flag"))
            )
    
            missed_tbl = joined.group_by(key).agg(pl.col("missed_flag").sum().alias("missed_count"))
    
            out = (
                feats_82_87
                .with_columns(pl.lit(r).alias("rank"))
                .join(missed_tbl, on=key, how="left")
                .join(txn_counts, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    apply_interval_overrides(pl.col("missed_count"), pl.col("txn_count")).alias(fname_out)
                )
                .select([key, fname_out])
            )
    
            feats_82_87 = feats_82_87.join(out, on=key, how="left")
    
        # 90‑day window (IDs 85–87)
        for r, fname_out in [(1, "A11_PDAY1313"), (2, "A11_PDAY2313"), (3, "A11_PDAY3313")]:
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            intervals = (
                df_filt.sort("txn_timestamp")
                .group_by(key)
                .agg((pl.col("txn_timestamp").diff().dt.total_days().drop_nulls().alias("intervals")))
            )
    
            mode_tbl = (
                intervals.explode("intervals")
                .group_by([key, "intervals"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "intervals"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("intervals").alias("mode_interval"))
            )
    
            joined = (
                intervals.explode("intervals")
                .join(mode_tbl, on=key, how="left")
                .with_columns((pl.col("intervals") > pl.col("mode_interval")).cast(pl.Int64).alias("missed_flag"))
            )
    
            missed_tbl = joined.group_by(key).agg(pl.col("missed_flag").sum().alias("missed_count"))
    
            out = (
                feats_82_87
                .with_columns(pl.lit(r).alias("rank"))
                .join(missed_tbl, on=key, how="left")
                .join(txn_counts, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    apply_interval_overrides(pl.col("missed_count"), pl.col("txn_count")).alias(fname_out)
                )
                .select([key, fname_out])
            )
    
            feats_82_87 = feats_82_87.join(out, on=key, how="left")

    #print(feats_82_87)


##############################################################
#                        Features 88-93
# ===========================================
# FEATURE FAMILY: 88–93 (Mode Day of the Week)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Extract weekday (0=Monday … 6=Sunday) from txn_timestamp.
#     - If txn_count = 0 → override["NULL"].
#     - If txn_count = 1 → single_dow (weekday of that txn).
#     - If txn_count ≥ 2 → mode_dow (most frequent weekday, tie‑breaker = larger weekday value).

# Overrides:
#   • NO_TXN → override["NULL"].
#   • ONE_TXN → weekday of that single txn.
#   • For ≥2 txns → mode_dow computed normally.

# -------------------------------------------
# FEATURES 88–90 (30‑day window)
# Rank 1 → A11_PDAY1324
# Rank 2 → A11_PDAY2324
# Rank 3 → A11_PDAY3324

# FEATURES 91–93 (90‑day window)
# Rank 1 → A11_PDAY1323
# Rank 2 → A11_PDAY2323
# Rank 3 → A11_PDAY3323
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 88–93
###############################################


    if group_type == "A":
        # All six features get the same override_value
        feats_88_93 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1324": [override_value],
            "A11_PDAY2324": [override_value],
            "A11_PDAY3324": [override_value],
            "A11_PDAY1323": [override_value],
            "A11_PDAY2323": [override_value],
            "A11_PDAY3323": [override_value],
        })
    
    else:
        feats_88_93 = df_groupB_txn.select(key).unique()
    
        # 30‑day window (IDs 88–90)
        for r, fname_out in [(1, "A11_PDAY1324"), (2, "A11_PDAY2324"), (3, "A11_PDAY3324")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
                .with_columns(pl.col("txn_timestamp").dt.weekday().alias("dow"))
            )
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
            single_dow = df_filt.group_by(key).agg(pl.col("dow").first().alias("single_dow"))
    
            mode_tbl = (
                df_filt.group_by([key, "dow"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "dow"], descending=[True, True])  # tie‑breaker: larger weekday wins
                .group_by(key)
                .agg(pl.first("dow").alias("mode_dow"))
            )
    
            out = (
                feats_88_93
                .with_columns(pl.lit(r).alias("rank"))
                .join(txn_counts, on=key, how="left")
                .join(single_dow, on=key, how="left")
                .join(mode_tbl, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    pl.when(pl.col("txn_count") == 0)
                      .then(override["NO_TXN"])
                    .when(pl.col("txn_count") == 1)
                      .then(pl.col("single_dow"))
                    .otherwise(pl.col("mode_dow"))
                    .alias(fname_out)
                )
                .select([key, fname_out])
            )
    
            feats_88_93 = feats_88_93.join(out, on=key, how="left")
    
        # 90‑day window (IDs 91–93)
        for r, fname_out in [(1, "A11_PDAY1323"), (2, "A11_PDAY2323"), (3, "A11_PDAY3323")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.weekday().alias("dow"))
            )
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
            single_dow = df_filt.group_by(key).agg(pl.col("dow").first().alias("single_dow"))
    
            mode_tbl = (
                df_filt.group_by([key, "dow"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "dow"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("dow").alias("mode_dow"))
            )
    
            out = (
                feats_88_93
                .with_columns(pl.lit(r).alias("rank"))
                .join(txn_counts, on=key, how="left")
                .join(single_dow, on=key, how="left")
                .join(mode_tbl, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    pl.when(pl.col("txn_count") == 0)
                      .then(override["NO_TXN"])
                    .when(pl.col("txn_count") == 1)
                      .then(pl.col("single_dow"))
                    .otherwise(pl.col("mode_dow"))
                    .alias(fname_out)
                )
                .select([key, fname_out])
            )
    
            feats_88_93 = feats_88_93.join(out, on=key, how="left")

    #print(feats_88_93)

##############################################################
#                        Features 94-99
# ===========================================
# FEATURE FAMILY: 94–99 (Mode Dominance of Day of Week)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Extract weekday (0=Monday … 6=Sunday) from txn_timestamp.
#     - If txn_count = 0 → override["NO_TXN"].
#     - If txn_count = 1 → dominance = 1.0.
#     - If txn_count ≥ 2 → mode_dow = most frequent weekday (tie‑breaker = larger weekday).
#       Dominance = (# txns on mode_dow ÷ txn_count).

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • ONE_TXN → dominance = 1.0.
#   • For ≥2 txns → dominance computed normally.

# -------------------------------------------
# FEATURES 94–96 (30‑day window)
# Rank 1 → A11_PDAY1334
# Rank 2 → A11_PDAY2334
# Rank 3 → A11_PDAY3334

# FEATURES 97–99 (90‑day window)
# Rank 1 → A11_PDAY1333
# Rank 2 → A11_PDAY2333
# Rank 3 → A11_PDAY3333
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 94–99
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_94_99 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1334": [override_value],
            "A11_PDAY2334": [override_value],
            "A11_PDAY3334": [override_value],
            "A11_PDAY1333": [override_value],
            "A11_PDAY2333": [override_value],
            "A11_PDAY3333": [override_value],
        })
    
    else:
        feats_94_99 = df_groupB_txn.select(key).unique()
    
        # 30‑day window (IDs 94–96)
        for r, fname_out in [(1, "A11_PDAY1334"), (2, "A11_PDAY2334"), (3, "A11_PDAY3334")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
                .with_columns(pl.col("txn_timestamp").dt.weekday().alias("dow"))
            )
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            mode_tbl = (
                df_filt.group_by([key, "dow"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "dow"], descending=[True, True])  # tie‑breaker: larger weekday wins
                .group_by(key)
                .agg(pl.first("dow").alias("mode_dow"))
            )
    
            joined = (
                df_filt.join(mode_tbl, on=key, how="left")
                .with_columns((pl.col("dow") == pl.col("mode_dow")).cast(pl.Int64).alias("is_mode"))
            )
    
            dom_tbl = joined.group_by(key).agg((pl.col("is_mode").sum() / pl.col("dow").count()).alias("dominance"))
    
            out = (
                feats_94_99
                .with_columns(pl.lit(r).alias("rank"))
                .join(txn_counts, on=key, how="left")
                .join(dom_tbl, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    pl.when(pl.col("txn_count") == 0)
                      .then(override["NO_TXN"])
                    .when(pl.col("txn_count") == 1)
                      .then(1.0)
                    .otherwise(pl.col("dominance"))
                    .alias(fname_out)
                )
                .select([key, fname_out])
            )
    
            feats_94_99 = feats_94_99.join(out, on=key, how="left")
    
        # 90‑day window (IDs 97–99)
        for r, fname_out in [(1, "A11_PDAY1333"), (2, "A11_PDAY2333"), (3, "A11_PDAY3333")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.weekday().alias("dow"))
            )
    
            txn_counts = df_filt.group_by(key).agg(pl.count().alias("txn_count"))
    
            mode_tbl = (
                df_filt.group_by([key, "dow"])
                .agg(pl.count().alias("freq"))
                .sort(["freq", "dow"], descending=[True, True])
                .group_by(key)
                .agg(pl.first("dow").alias("mode_dow"))
            )
    
            joined = (
                df_filt.join(mode_tbl, on=key, how="left")
                .with_columns((pl.col("dow") == pl.col("mode_dow")).cast(pl.Int64).alias("is_mode"))
            )
    
            dom_tbl = joined.group_by(key).agg((pl.col("is_mode").sum() / pl.col("dow").count()).alias("dominance"))
    
            out = (
                feats_94_99
                .with_columns(pl.lit(r).alias("rank"))
                .join(txn_counts, on=key, how="left")
                .join(dom_tbl, on=key, how="left")
                .with_columns(pl.col("txn_count").fill_null(0))
                .with_columns(
                    pl.when(pl.col("txn_count") == 0)
                      .then(override["NO_TXN"])
                    .when(pl.col("txn_count") == 1)
                      .then(1.0)
                    .otherwise(pl.col("dominance"))
                    .alias(fname_out)
                )
                .select([key, fname_out])
            )
    
            feats_94_99 = feats_94_99.join(out, on=key, how="left")


    #print(feats_94_99)

########################################################
#                 Feats 100-108
# ===========================================
# FEATURE FAMILY: 100–108 (Latest & Earliest Paydates)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Extract transaction date from txn_timestamp.
#     - Latest paydate = max(date).
#     - Earliest paydate = min(date).
#     - If no txns in window → override with 2099‑12‑31.

# Overrides:
#   • NO_TXN → override with 2099‑12‑31.
#   • Otherwise → compute normally.

# -------------------------------------------
# FEATURES 100–102 (Latest paydates, 90‑day window)
# Rank 1 → A11_PDAY1403
# Rank 2 → A11_PDAY2403
# Rank 3 → A11_PDAY3403

# FEATURES 103–105 (Earliest paydates, 30‑day window)
# Rank 1 → A11_PDAY1414
# Rank 2 → A11_PDAY2414
# Rank 3 → A11_PDAY3414

# FEATURES 106–108 (Earliest paydates, 90‑day window)
# Rank 1 → A11_PDAY1413
# Rank 2 → A11_PDAY2413
# Rank 3 → A11_PDAY3413
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 100–108
###############################################

    override_date = pl.Series("override_date", [date(2099, 12, 31)]).cast(pl.Date)
    
    if group_type == "A":
        # All nine features get the same override_value
        feats_100_108 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1403": override_date,
            "A11_PDAY2403": override_date,
            "A11_PDAY3403": override_date,
            "A11_PDAY1414": override_date,
            "A11_PDAY2414": override_date,
            "A11_PDAY3414": override_date,
            "A11_PDAY1413": override_date,
            "A11_PDAY2413": override_date,
            "A11_PDAY3413": override_date,
        })
    
    else:
        feats_100_108 = df_groupB_txn.select(key).unique()
    
        # 100–102: Latest paydates (90‑day)
        for r, fname_out in [(1, "A11_PDAY1403"), (2, "A11_PDAY2403"), (3, "A11_PDAY3403")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            latest_tbl = df_filt.group_by(key).agg(pl.col("dt").max().alias(fname_out))
    
            out = (
                feats_100_108
                .with_columns(pl.lit(r).alias("rank"))
                .join(latest_tbl, on=key, how="left")
                .with_columns(pl.col(fname_out).fill_null(override_date))
                .select([key, fname_out])
            )
    
            feats_100_108 = feats_100_108.join(out, on=key, how="left")
    
        # 103–105: Earliest paydates (30‑day)
        for r, fname_out in [(1, "A11_PDAY1414"), (2, "A11_PDAY2414"), (3, "A11_PDAY3414")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            earliest_tbl = df_filt.group_by(key).agg(pl.col("dt").min().alias(fname_out))
    
            out = (
                feats_100_108
                .with_columns(pl.lit(r).alias("rank"))
                .join(earliest_tbl, on=key, how="left")
                .with_columns(pl.col(fname_out).fill_null(override_date))
                .select([key, fname_out])
            )
    
            feats_100_108 = feats_100_108.join(out, on=key, how="left")
    
        # 106–108: Earliest paydates (90‑day)
        for r, fname_out in [(1, "A11_PDAY1413"), (2, "A11_PDAY2413"), (3, "A11_PDAY3413")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            earliest_tbl = df_filt.group_by(key).agg(pl.col("dt").min().alias(fname_out))
    
            out = (
                feats_100_108
                .with_columns(pl.lit(r).alias("rank"))
                .join(earliest_tbl, on=key, how="left")
                .with_columns(pl.col(fname_out).fill_null(override_date))
                .select([key, fname_out])
            )
    
            feats_100_108 = feats_100_108.join(out, on=key, how="left")

    #print(feats_100_108)

##################################################
#             Feats 109-111
# ===========================================
# FEATURE FAMILY: 109–111 (Days Since Last Paydate)
# ===========================================

# Definition:
#   • For each rank (1–3) in the 90‑day window:
#     - Extract transaction date from txn_timestamp.
#     - Find last paydate = max(date).
#     - Compute days_since_last = (ref_date – last_dt).
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally.

# -------------------------------------------
# FEATURES 109–111 (90‑day window)
# Rank 1 → A11_PDAY1423
# Rank 2 → A11_PDAY2423
# Rank 3 → A11_PDAY3423
# ===========================================


###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 109–111
###############################################
    
    if group_type == "A":
        # All three features get the same override_value
        feats_109_111 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1423": [override_value],
            "A11_PDAY2423": [override_value],
            "A11_PDAY3423": [override_value],
        })
    
    else:
        feats_109_111 = df_groupB_txn.select(key).unique()
    
        for r, fname_out in [(1, "A11_PDAY1423"), (2, "A11_PDAY2423"), (3, "A11_PDAY3423")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            last_date_tbl = df_filt.group_by(key).agg(pl.col("dt").max().alias("last_dt"))
    
            out = (
                feats_109_111
                .with_columns(pl.lit(r).alias("rank"))
                .join(last_date_tbl, on=key, how="left")
                .with_columns(
                    ((ref_date - pl.col("last_dt")).dt.total_days()).alias(fname_out)
                )
                .with_columns(
                    pl.col(fname_out).fill_null(override["NO_TXN"])
                )
                .select([key, fname_out])
            )
    
            feats_109_111 = feats_109_111.join(out, on=key, how="left")

    #print(feats_109_111)

############################################################
#                       Features 112-114
# ===========================================
# FEATURE FAMILY: 112–114 (Days Since Last Large Paydate)
# ===========================================

# Definition:
#   • For each rank (1–3) in the 90‑day window:
#     - Compute avg_all = mean(txn_amount) across ALL ranks in 0–90 days.
#     - Filter to "large paychecks" = txn_amount > 70% of avg_all.
#     - Find last_large_dt = max(date of large paychecks).
#     - Compute days_since_last_large = (ref_date – last_large_dt).
#     - If no large txn in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no large transactions in the window.
#   • Otherwise → compute normally.

# -------------------------------------------
# FEATURES 112–114 (90‑day window)
# Rank 1 → A11_PDAY1433
# Rank 2 → A11_PDAY2433
# Rank 3 → A11_PDAY3433
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 112–114
###############################################

    if group_type == "A":
        # All three features get the same override_value
        feats_112_114 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1433": [override_value],
            "A11_PDAY2433": [override_value],
            "A11_PDAY3433": [override_value],
        })
    
    else:
        feats_112_114 = df_groupB_txn.select(key).unique()
    
        # Precompute avg_all across ALL ranks in 0–90 window
        df_90 = df_groupB_txn.filter(valid_ranks_mask & windows["0_90"])
        avg_all_tbl = df_90.group_by(key).agg(pl.col("txn_amount").mean().alias("avg_all"))
    
        # Build all 3 features
        for r, fname_out in [(1, "A11_PDAY1433"), (2, "A11_PDAY2433"), (3, "A11_PDAY3433")]:
            df_rank_90 = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            df_joined = df_rank_90.join(avg_all_tbl, on=key, how="left")
    
            # Filter to large paychecks
            df_large = df_joined.filter(pl.col("txn_amount") > 0.7 * pl.col("avg_all"))
    
            # Latest large paydate
            last_large_tbl = df_large.group_by(key).agg(pl.col("dt").max().alias("last_large_dt"))
    
            out = (
                feats_112_114
                .with_columns(pl.lit(r).alias("rank"))
                .join(last_large_tbl, on=key, how="left")
                .with_columns(((ref_date - pl.col("last_large_dt")).dt.total_days()).alias(fname_out))
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_112_114 = feats_112_114.join(out, on=key, how="left")

    #print(feats_112_114)

##################################################################
#                      Feats 115-120
# ===========================================
# FEATURE FAMILY: 115–120 (Days Since Earliest Paydate)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Extract transaction date from txn_timestamp.
#     - Find earliest paydate = min(date).
#     - Compute days_since_earliest = (ref_date – earliest_dt).
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally.

# -------------------------------------------
# FEATURES 115–117 (30‑day window)
# Rank 1 → A11_PDAY1444
# Rank 2 → A11_PDAY2444
# Rank 3 → A11_PDAY3444

# FEATURES 118–120 (90‑day window)
# Rank 1 → A11_PDAY1443
# Rank 2 → A11_PDAY2443
# Rank 3 → A11_PDAY3443
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 115–120
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_115_120 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1444": [override_value],
            "A11_PDAY2444": [override_value],
            "A11_PDAY3444": [override_value],
            "A11_PDAY1443": [override_value],
            "A11_PDAY2443": [override_value],
            "A11_PDAY3443": [override_value],
        })
    
    else:
        feats_115_120 = df_groupB_txn.select(key).unique()
    
        # 115–117: earliest paydate in 30‑day window
        for r, fname_out in [(1, "A11_PDAY1444"), (2, "A11_PDAY2444"), (3, "A11_PDAY3444")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            earliest_tbl = df_filt.group_by(key).agg(pl.col("dt").min().alias("earliest_dt"))
    
            out = (
                feats_115_120
                .with_columns(pl.lit(r).alias("rank"))
                .join(earliest_tbl, on=key, how="left")
                .with_columns(((ref_date - pl.col("earliest_dt")).dt.total_days()).alias(fname_out))
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_115_120 = feats_115_120.join(out, on=key, how="left")
    
        # 118–120: earliest paydate in 90‑day window
        for r, fname_out in [(1, "A11_PDAY1443"), (2, "A11_PDAY2443"), (3, "A11_PDAY3443")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            earliest_tbl = df_filt.group_by(key).agg(pl.col("dt").min().alias("earliest_dt"))
    
            out = (
                feats_115_120
                .with_columns(pl.lit(r).alias("rank"))
                .join(earliest_tbl, on=key, how="left")
                .with_columns(((ref_date - pl.col("earliest_dt")).dt.total_days()).alias(fname_out))
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_115_120 = feats_115_120.join(out, on=key, how="left")

    #print(feats_115_120)

###################################################################
#                        Feats 121-126
# ===========================================
# FEATURE FAMILY: 121–126 (Day Difference Between Earliest & Latest Paydates)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Extract transaction date from txn_timestamp.
#     - Find earliest paydate = min(date).
#     - Find latest paydate = max(date).
#     - Compute day_diff = (latest_dt – earliest_dt).
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally.

# -------------------------------------------
# FEATURES 121–123 (30‑day window)
# Rank 1 → A11_PDAY1454
# Rank 2 → A11_PDAY2454
# Rank 3 → A11_PDAY3454

# FEATURES 124–126 (90‑day window)
# Rank 1 → A11_PDAY1453
# Rank 2 → A11_PDAY2453
# Rank 3 → A11_PDAY3453
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 121–126
###############################################
    
    if group_type == "A":
        # All six features get the same override_value
        feats_121_126 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1454": [override_value],
            "A11_PDAY2454": [override_value],
            "A11_PDAY3454": [override_value],
            "A11_PDAY1453": [override_value],
            "A11_PDAY2453": [override_value],
            "A11_PDAY3453": [override_value],
        })
    
    else:
        feats_121_126 = df_groupB_txn.select(key).unique()
    
        # 121–123: 30‑day window
        for r, fname_out in [(1, "A11_PDAY1454"), (2, "A11_PDAY2454"), (3, "A11_PDAY3454")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            dt_tbl = df_filt.group_by(key).agg([
                pl.col("dt").min().alias("earliest_dt"),
                pl.col("dt").max().alias("latest_dt"),
            ])
    
            out = (
                feats_121_126
                .with_columns(pl.lit(r).alias("rank"))
                .join(dt_tbl, on=key, how="left")
                .with_columns((pl.col("latest_dt") - pl.col("earliest_dt")).dt.total_days().alias(fname_out))
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_121_126 = feats_121_126.join(out, on=key, how="left")
    
        # 124–126: 90‑day window
        for r, fname_out in [(1, "A11_PDAY1453"), (2, "A11_PDAY2453"), (3, "A11_PDAY3453")]:
            df_filt = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            dt_tbl = df_filt.group_by(key).agg([
                pl.col("dt").min().alias("earliest_dt"),
                pl.col("dt").max().alias("latest_dt"),
            ])
    
            out = (
                feats_121_126
                .with_columns(pl.lit(r).alias("rank"))
                .join(dt_tbl, on=key, how="left")
                .with_columns((pl.col("latest_dt") - pl.col("earliest_dt")).dt.total_days().alias(fname_out))
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_121_126 = feats_121_126.join(out, on=key, how="left")

    #print(feats_121_126)

########################################################################
#                        Feats 127-132
# ===========================================
# FEATURE FAMILY: 127–132 (Sum of Paycheck Amounts)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Filter transactions in the window.
#     - Sum txn_amount for that rank × window.
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally.

# -------------------------------------------
# FEATURES 127–129 (30‑day window)
# Rank 1 → A11_PDAY1504
# Rank 2 → A11_PDAY2504
# Rank 3 → A11_PDAY3504

# FEATURES 130–132 (90‑day window)
# Rank 1 → A11_PDAY1503
# Rank 2 → A11_PDAY2503
# Rank 3 → A11_PDAY3503
# ===========================================


###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 127–132
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_127_132 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1504": [override_value],
            "A11_PDAY2504": [override_value],
            "A11_PDAY3504": [override_value],
            "A11_PDAY1503": [override_value],
            "A11_PDAY2503": [override_value],
            "A11_PDAY3503": [override_value],
        })
    
    else:
        feats_127_132 = df_groupB_txn.select(key).unique()
    
        # 127–129: 30‑day window
        for r, fname_out in [(1, "A11_PDAY1504"), (2, "A11_PDAY2504"), (3, "A11_PDAY3504")]:
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
    
            sum_tbl = df_filt.group_by(key).agg(pl.col("txn_amount").sum().alias(fname_out))
    
            out = (
                feats_127_132
                .with_columns(pl.lit(r).alias("rank"))
                .join(sum_tbl, on=key, how="left")
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_127_132 = feats_127_132.join(out, on=key, how="left")
    
        # 130–132: 90‑day window
        for r, fname_out in [(1, "A11_PDAY1503"), (2, "A11_PDAY2503"), (3, "A11_PDAY3503")]:
            df_filt = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
    
            sum_tbl = df_filt.group_by(key).agg(pl.col("txn_amount").sum().alias(fname_out))
    
            out = (
                feats_127_132
                .with_columns(pl.lit(r).alias("rank"))
                .join(sum_tbl, on=key, how="left")
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_127_132 = feats_127_132.join(out, on=key, how="left")

    #print(feats_127_132)

###############################################################
#                        Feats 133-138
# ===========================================
# FEATURE FAMILY: 133–138 (Sum of Paycheck Amounts as % of 180-day Total)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Numerator = sum of txn_amount in window.
#     - Denominator = sum of txn_amount in 180d window.
#     - Percentage = (num ÷ den) × 100.
#     - If numerator window has no txns → override["NO_TXN"].
#     - Apply ratio overrides (BOTH0, DEN0, numerator=0→0).

# Overrides:
#   • NO_TXN → when numerator window has no transactions.
#   • Otherwise → compute normally with ratio overrides.

# -------------------------------------------
# FEATURES 133–135 (30‑day window)
# Rank 1 → A11_PDAY1514
# Rank 2 → A11_PDAY2514
# Rank 3 → A11_PDAY3514

# FEATURES 136–138 (90‑day window)
# Rank 1 → A11_PDAY1513
# Rank 2 → A11_PDAY2513
# Rank 3 → A11_PDAY3513
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 133–138
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_133_138 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1514": [override_value],
            "A11_PDAY2514": [override_value],
            "A11_PDAY3514": [override_value],
            "A11_PDAY1513": [override_value],
            "A11_PDAY2513": [override_value],
            "A11_PDAY3513": [override_value],
        })
    
    else:
        feats_133_138 = df_groupB_txn.select(key).unique()
    
        # Precompute denominator (180‑day sum) per rank
        den_tbls = {}
        for r in [1, 2, 3]:
            df_180 = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_180"])
            den_tbls[r] = df_180.group_by(key).agg(pl.col("txn_amount").sum().alias("den"))
    
        # 133–135: 30‑day window
        for r, fname_out in [(1, "A11_PDAY1514"), (2, "A11_PDAY2514"), (3, "A11_PDAY3514")]:
            df_w = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
            num_tbl = df_w.group_by(key).agg(pl.col("txn_amount").sum().alias("num"))
    
            out = (
                feats_133_138
                .with_columns(pl.lit(r).alias("rank"))
                .join(num_tbl, on=key, how="left")
                .join(den_tbls[r], on=key, how="left")
                .with_columns(((pl.col("num") / pl.col("den")) * 100).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("ratio_raw"),
                        pl.col("num"),
                        pl.col("den"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_133_138 = feats_133_138.join(out, on=key, how="left")
    
        # 136–138: 90‑day window
        for r, fname_out in [(1, "A11_PDAY1513"), (2, "A11_PDAY2513"), (3, "A11_PDAY3513")]:
            df_w = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
            num_tbl = df_w.group_by(key).agg(pl.col("txn_amount").sum().alias("num"))
    
            out = (
                feats_133_138
                .with_columns(pl.lit(r).alias("rank"))
                .join(num_tbl, on=key, how="left")
                .join(den_tbls[r], on=key, how="left")
                .with_columns(((pl.col("num") / pl.col("den")) * 100).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("ratio_raw"),
                        pl.col("num"),
                        pl.col("den"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_133_138 = feats_133_138.join(out, on=key, how="left")

    #print(feats_133_138)

##########################################################################
#                          Feats 139-144
# ===========================================
# FEATURE FAMILY: 139–144 (Average Paycheck Amount)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Filter transactions in the window with txn_amount > 0.
#     - Compute average paycheck amount = mean(txn_amount).
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally.

# -------------------------------------------
# FEATURES 139–141 (30‑day window)
# Rank 1 → A11_PDAY1524
# Rank 2 → A11_PDAY2524
# Rank 3 → A11_PDAY3524

# FEATURES 142–144 (90‑day window)
# Rank 1 → A11_PDAY1523
# Rank 2 → A11_PDAY2523
# Rank 3 → A11_PDAY3523
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 139–144
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_139_144 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1524": [override_value],
            "A11_PDAY2524": [override_value],
            "A11_PDAY3524": [override_value],
            "A11_PDAY1523": [override_value],
            "A11_PDAY2523": [override_value],
            "A11_PDAY3523": [override_value],
        })
    
    else:
        feats_139_144 = df_groupB_txn.select(key).unique()
    
        # 139–141: 30‑day avg paycheck per rank
        for r, fname_out in [(1, "A11_PDAY1524"), (2, "A11_PDAY2524"), (3, "A11_PDAY3524")]:
            df_filt = df_groupB_txn.filter(
                valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"] & (pl.col("txn_amount") > 0)
            )
    
            avg_tbl = df_filt.group_by(key).agg(pl.col("txn_amount").mean().alias(fname_out))
    
            out = (
                feats_139_144
                .with_columns(pl.lit(r).alias("rank"))
                .join(avg_tbl, on=key, how="left")
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_139_144 = feats_139_144.join(out, on=key, how="left")
    
        # 142–144: 90‑day avg paycheck per rank
        for r, fname_out in [(1, "A11_PDAY1523"), (2, "A11_PDAY2523"), (3, "A11_PDAY3523")]:
            df_filt = df_groupB_txn.filter(
                valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"] & (pl.col("txn_amount") > 0)
            )
    
            avg_tbl = df_filt.group_by(key).agg(pl.col("txn_amount").mean().alias(fname_out))
    
            out = (
                feats_139_144
                .with_columns(pl.lit(r).alias("rank"))
                .join(avg_tbl, on=key, how="left")
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_139_144 = feats_139_144.join(out, on=key, how="left")

    #print(feats_139_144)

###########################################################################
#                             Feats 145-150
# ===========================================
# FEATURE FAMILY: 145–150 (Latest ÷ Average Paycheck Amount)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - Extract transaction date from txn_timestamp.
#     - latest_amt = last txn_amount in window (by date).
#     - avg_amt = mean(txn_amount) in window.
#     - Ratio = latest_amt ÷ avg_amt.
#     - Apply ratio overrides (BOTH0, DEN0, numerator=0→0).
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally with ratio overrides.

# -------------------------------------------
# FEATURES 145–147 (30‑day window)
# Rank 1 → A11_PDAY1534  
# Rank 2 → A11_PDAY2534  
# Rank 3 → A11_PDAY3534  

# FEATURES 148–150 (90‑day window)
# Rank 1 → A11_PDAY1533  
# Rank 2 → A11_PDAY2533  
# Rank 3 → A11_PDAY3533  
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 145–150
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_145_150 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1534": [override_value],
            "A11_PDAY2534": [override_value],
            "A11_PDAY3534": [override_value],
            "A11_PDAY1533": [override_value],
            "A11_PDAY2533": [override_value],
            "A11_PDAY3533": [override_value],
        })
    
    else:
        feats_145_150 = df_groupB_txn.select(key).unique()
    
        # 145–147: 30‑day window
        for r, fname_out in [(1, "A11_PDAY1534"), (2, "A11_PDAY2534"), (3, "A11_PDAY3534")]:
            df_w = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            agg_tbl = (
                df_w.group_by(key).agg([
                    pl.col("txn_amount").sort_by("dt").last().alias("latest_amt"),
                    pl.col("txn_amount").mean().alias("avg_amt"),
                ])
            )
    
            out = (
                feats_145_150
                .with_columns(pl.lit(r).alias("rank"))
                .join(agg_tbl, on=key, how="left")
                .with_columns((pl.col("latest_amt") / pl.col("avg_amt")).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("ratio_raw"),
                        pl.col("latest_amt"),
                        pl.col("avg_amt"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_145_150 = feats_145_150.join(out, on=key, how="left")
    
        # 148–150: 90‑day window
        for r, fname_out in [(1, "A11_PDAY1533"), (2, "A11_PDAY2533"), (3, "A11_PDAY3533")]:
            df_w = (
                df_groupB_txn
                .filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            agg_tbl = (
                df_w.group_by(key).agg([
                    pl.col("txn_amount").sort_by("dt").last().alias("latest_amt"),
                    pl.col("txn_amount").mean().alias("avg_amt"),
                ])
            )
    
            out = (
                feats_145_150
                .with_columns(pl.lit(r).alias("rank"))
                .join(agg_tbl, on=key, how="left")
                .with_columns((pl.col("latest_amt") / pl.col("avg_amt")).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("ratio_raw"),
                        pl.col("latest_amt"),
                        pl.col("avg_amt"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_145_150 = feats_145_150.join(out, on=key, how="left")

    #print(feats_145_150)

############################################################################
#                               Features 151-156
# ===========================================
# FEATURE FAMILY: 151–156 (Range Ratio of Paycheck Amounts)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - max_amt = maximum txn_amount in window.
#     - min_amt = minimum txn_amount in window.
#     - avg_amt = mean txn_amount in window.
#     - Range ratio = (max_amt – min_amt) ÷ avg_amt.
#     - Apply ratio overrides (BOTH0, DEN0, numerator=0→0).
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally with ratio overrides.

# -------------------------------------------
# FEATURES 151–153 (30‑day window)
# Rank 1 → A11_PDAY1544  
# Rank 2 → A11_PDAY2544  
# Rank 3 → A11_PDAY3544  

# FEATURES 154–156 (90‑day window)
# Rank 1 → A11_PDAY1543  
# Rank 2 → A11_PDAY2543  
# Rank 3 → A11_PDAY3543  
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 151–156
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_151_156 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1544": [override_value],
            "A11_PDAY2544": [override_value],
            "A11_PDAY3544": [override_value],
            "A11_PDAY1543": [override_value],
            "A11_PDAY2543": [override_value],
            "A11_PDAY3543": [override_value],
        })
    
    else:
        feats_151_156 = df_groupB_txn.select(key).unique()
    
        # 151–153: 30‑day window
        for r, fname_out in [(1, "A11_PDAY1544"), (2, "A11_PDAY2544"), (3, "A11_PDAY3544")]:
            df_w = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
    
            agg_tbl = df_w.group_by(key).agg([
                pl.col("txn_amount").max().alias("max_amt"),
                pl.col("txn_amount").min().alias("min_amt"),
                pl.col("txn_amount").mean().alias("avg_amt"),
            ])
    
            out = (
                feats_151_156
                .with_columns(pl.lit(r).alias("rank"))
                .join(agg_tbl, on=key, how="left")
                .with_columns((pl.col("max_amt") - pl.col("min_amt")).alias("num"))
                .with_columns((pl.col("num") / pl.col("avg_amt")).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("ratio_raw"),
                        pl.col("num"),
                        pl.col("avg_amt"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_151_156 = feats_151_156.join(out, on=key, how="left")
    
        # 154–156: 90‑day window
        for r, fname_out in [(1, "A11_PDAY1543"), (2, "A11_PDAY2543"), (3, "A11_PDAY3543")]:
            df_w = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
    
            agg_tbl = df_w.group_by(key).agg([
                pl.col("txn_amount").max().alias("max_amt"),
                pl.col("txn_amount").min().alias("min_amt"),
                pl.col("txn_amount").mean().alias("avg_amt"),
            ])
    
            out = (
                feats_151_156
                .with_columns(pl.lit(r).alias("rank"))
                .join(agg_tbl, on=key, how="left")
                .with_columns((pl.col("max_amt") - pl.col("min_amt")).alias("num"))
                .with_columns((pl.col("num") / pl.col("avg_amt")).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("ratio_raw"),
                        pl.col("num"),
                        pl.col("avg_amt"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_151_156 = feats_151_156.join(out, on=key, how="left")

    #print(feats_151_156)

##############################################################################
#                         Feats 157-162
# ===========================================
# FEATURE FAMILY: 157–162 (Coefficient of Variation of Paycheck Amounts)
# ===========================================

# Definition:
#   • For each rank (1–3) and window (30d, 90d):
#     - mean_amt = average txn_amount in window.
#     - std_amt = standard deviation of txn_amount in window.
#     - CV = std_amt ÷ mean_amt.
#     - Replace NULL std (single txn case) with 0.
#     - Apply ratio overrides (BOTH0, DEN0, numerator=0→0).
#     - If no txns in window → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when no transactions in the window.
#   • Otherwise → compute normally with ratio overrides.

# -------------------------------------------
# FEATURES 157–159 (30‑day window)
# Rank 1 → A11_PDAY1554  
# Rank 2 → A11_PDAY2554  
# Rank 3 → A11_PDAY3554  

# FEATURES 160–162 (90‑day window)
# Rank 1 → A11_PDAY1553  
# Rank 2 → A11_PDAY2553  
# Rank 3 → A11_PDAY3553  
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 157–162
###############################################

    if group_type == "A":
        # All six features get the same override_value
        feats_157_162 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1554": [override_value],
            "A11_PDAY2554": [override_value],
            "A11_PDAY3554": [override_value],
            "A11_PDAY1553": [override_value],
            "A11_PDAY2553": [override_value],
            "A11_PDAY3553": [override_value],
        })
    
    else:
        feats_157_162 = df_groupB_txn.select(key).unique()
    
        # 157–159: 30‑day CV per rank
        for r, fname_out in [(1, "A11_PDAY1554"), (2, "A11_PDAY2554"), (3, "A11_PDAY3554")]:
            df_w = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
    
            agg_tbl = df_w.group_by(key).agg([
                pl.col("txn_amount").mean().alias("mean_amt"),
                pl.col("txn_amount").std().alias("std_amt"),
            ])
    
            out = (
                feats_157_162
                .with_columns(pl.lit(r).alias("rank"))
                .join(agg_tbl, on=key, how="left")
                .with_columns(pl.col("std_amt").fill_null(0).alias("std_amt"))
                .with_columns((pl.col("std_amt") / pl.col("mean_amt")).alias("cv_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("cv_raw"),
                        pl.col("std_amt"),
                        pl.col("mean_amt"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_157_162 = feats_157_162.join(out, on=key, how="left")
    
        # 160–162: 90‑day CV per rank
        for r, fname_out in [(1, "A11_PDAY1553"), (2, "A11_PDAY2553"), (3, "A11_PDAY3553")]:
            df_w = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_90"])
    
            agg_tbl = df_w.group_by(key).agg([
                pl.col("txn_amount").mean().alias("mean_amt"),
                pl.col("txn_amount").std().alias("std_amt"),
            ])
    
            out = (
                feats_157_162
                .with_columns(pl.lit(r).alias("rank"))
                .join(agg_tbl, on=key, how="left")
                .with_columns(pl.col("std_amt").fill_null(0).alias("std_amt"))
                .with_columns((pl.col("std_amt") / pl.col("mean_amt")).alias("cv_raw"))
                .with_columns(
                    apply_ratio_overrides(
                        pl.col("cv_raw"),
                        pl.col("std_amt"),
                        pl.col("mean_amt"),
                        is_count_amount = True
                    ).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_157_162 = feats_157_162.join(out, on=key, how="left")

    #print(feats_157_162)

####################################################################################
#                                 Feats 163-174
# ===========================================
# FEATURE FAMILY: 163–174 (Ratios of Total/Avg Paycheck Amounts)
# ===========================================

# Definition:
#   • For each rank (1–3):
#     - Compare 0–30d window vs 31–60d or 61–90d window.
#     - Aggregates:
#         - Total amount (sum).
#         - Average amount (mean).
#     - Ratio = numerator ÷ denominator.
#     - Apply ratio overrides (BOTH0, DEN0, numerator=0→0).
#     - If numerator window has no txns → override["NO_TXN"].

# Overrides:
#   • NO_TXN → when numerator window has no transactions.
#   • Otherwise → compute normally with ratio overrides.

# -------------------------------------------
# FEATURES 163–165 (Total amt 30 vs 31–60)  
# Rank 1 → A11_PDAY1563  
# Rank 2 → A11_PDAY2563  
# Rank 3 → A11_PDAY3563  

# FEATURES 166–168 (Total amt 30 vs 61–90)  
# Rank 1 → A11_PDAY1573  
# Rank 2 → A11_PDAY2573  
# Rank 3 → A11_PDAY3573  

# FEATURES 169–171 (Avg amt 30 vs 31–60)  
# Rank 1 → A11_PDAY1583  
# Rank 2 → A11_PDAY2583  
# Rank 3 → A11_PDAY3583  

# FEATURES 172–174 (Avg amt 30 vs 61–90)  
# Rank 1 → A11_PDAY1593  
# Rank 2 → A11_PDAY2593  
# Rank 3 → A11_PDAY3593  
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 163–174
###############################################

    if group_type == "A":
        feats_163_174 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1563": [override_value],
            "A11_PDAY2563": [override_value],
            "A11_PDAY3563": [override_value],
            "A11_PDAY1573": [override_value],
            "A11_PDAY2573": [override_value],
            "A11_PDAY3573": [override_value],
            "A11_PDAY1583": [override_value],
            "A11_PDAY2583": [override_value],
            "A11_PDAY3583": [override_value],
            "A11_PDAY1593": [override_value],
            "A11_PDAY2593": [override_value],
            "A11_PDAY3593": [override_value],
        })
    
    else:
        feats_163_174 = df_groupB_txn.select(key).unique()
    
        # --- Total amount ratios ---
        for r, fname_out, den_window in [
            (1, "A11_PDAY1563", "31_60"),
            (2, "A11_PDAY2563", "31_60"),
            (3, "A11_PDAY3563", "31_60"),
            (1, "A11_PDAY1573", "61_90"),
            (2, "A11_PDAY2573", "61_90"),
            (3, "A11_PDAY3573", "61_90"),
        ]:
            df_num = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
            df_den = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows[den_window])
    
            num_tbl = df_num.group_by(key).agg(pl.col("txn_amount").sum().alias("N"))
            den_tbl = df_den.group_by(key).agg(pl.col("txn_amount").sum().alias("D"))
    
            out = (
                feats_163_174
                .with_columns(pl.lit(r).alias("rank"))
                .join(num_tbl, on=key, how="left")
                .join(den_tbl, on=key, how="left")
                .with_columns([pl.col("N").fill_null(0), pl.col("D").fill_null(0)])
                .with_columns((pl.col("N") / pl.col("D")).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(pl.col("ratio_raw"), pl.col("N"), pl.col("D"),is_count_amount=True).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_163_174 = feats_163_174.join(out, on=key, how="left")
    
        # --- Average amount ratios ---
        for r, fname_out, den_window in [
            (1, "A11_PDAY1583", "31_60"),
            (2, "A11_PDAY2583", "31_60"),
            (3, "A11_PDAY3583", "31_60"),
            (1, "A11_PDAY1593", "61_90"),
            (2, "A11_PDAY2593", "61_90"),
            (3, "A11_PDAY3593", "61_90"),
        ]:
            df_num = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows["0_30"])
            df_den = df_groupB_txn.filter(valid_ranks_mask & (pl.col("rank") == r) & windows[den_window])
    
            num_tbl = df_num.group_by(key).agg(pl.col("txn_amount").mean().alias("N"))
            den_tbl = df_den.group_by(key).agg(pl.col("txn_amount").mean().alias("D"))
    
            out = (
                feats_163_174
                .with_columns(pl.lit(r).alias("rank"))
                .join(num_tbl, on=key, how="left")
                .join(den_tbl, on=key, how="left")
                .with_columns([pl.col("N").fill_null(0), pl.col("D").fill_null(0)])
                .with_columns((pl.col("N") / pl.col("D")).alias("ratio_raw"))
                .with_columns(
                    apply_ratio_overrides(pl.col("ratio_raw"), pl.col("N"), pl.col("D"),is_count_amount=True).alias(fname_out)
                )
                .with_columns(pl.col(fname_out).fill_null(override["NO_TXN"]))
                .select([key, fname_out])
            )
    
            feats_163_174 = feats_163_174.join(out, on=key, how="left")

    #print(feats_163_174)

#################################################################################################
#                               Feats 175-180
# ===========================================
# FEATURE FAMILY: 175–180 (Stability Index)
# ===========================================

# Definition:
#   • Composite measure of paycheck stability across multiple dimensions:
#     - txn count (normalized)
#     - mode dominance of intervals
#     - CV of intervals
#     - recency penalty
#     - span of activity
#     - normalized total amount
#   • Final index = average of 6 component scores, clipped to [0,1].

# Overrides:
#   • Group A → always 0.0
#   • Group B → computed per rank × window
#   • Missing ranks → 0.0

# -------------------------------------------
# FEATURES 175–177 (30‑day window)
# Rank 1 → A11_PDAY1604  
# Rank 2 → A11_PDAY2604  
# Rank 3 → A11_PDAY3604  

# FEATURES 178–180 (90‑day window)
# Rank 1 → A11_PDAY1603  
# Rank 2 → A11_PDAY2603  
# Rank 3 → A11_PDAY3603  
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 175–180
###############################################

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 175–180
###############################################

    if group_type == "A":
        # Group A → stability always 0.0
        feats_175_180 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1604": [0.0],
            "A11_PDAY2604": [0.0],
            "A11_PDAY3604": [0.0],
            "A11_PDAY1603": [0.0],
            "A11_PDAY2603": [0.0],
            "A11_PDAY3603": [0.0],
        })
    
    else:
        feats_175_180 = pl.concat([df_groupA_overrides.select(key), df_groupB_txn.select(key)], how="vertical").unique()
    
        # -----------------------------
        # Helper functions for intervals
        # -----------------------------
        def compute_intervals(ts_list):
            if ts_list is None or len(ts_list) <= 1:
                return []
            ts_sorted = sorted(ts_list)
            return [(ts_sorted[i] - ts_sorted[i - 1]).days for i in range(1, len(ts_sorted))]
    
        def mode_dom_fn(ivals):
            if len(ivals) == 0:
                return None
            freq = {}
            for v in ivals:
                freq[v] = freq.get(v, 0) + 1
            return max(freq.values()) / len(ivals)
    
        def cv_interval_fn(ivals):
            if len(ivals) == 0:
                return None
            mean_val = sum(ivals) / len(ivals)
            if mean_val == 0:
                return None
            if len(ivals) == 1:
                sd = 0.0
            else:
                mean = mean_val
                sd = (sum((x - mean) ** 2 for x in ivals) / (len(ivals) - 1)) ** 0.5
            return sd / mean_val
    
        # -----------------------------
        # Stability Index for 30-day window
        # -----------------------------
        df_30 = df_groupB_txn.filter(windows["0_30"]).sort([key, "rank", "txn_timestamp"])
        agg_30 = (
            df_30.group_by([key, "rank"])
            .agg([
                pl.count().alias("n_txn"),
                pl.col("txn_timestamp").first().alias("first_date"),
                pl.col("txn_timestamp").last().alias("last_date"),
                pl.col("txn_amount").sum().alias("total_amt"),
                pl.col("txn_timestamp").alias("ts_list"),
            ])
        )
    
        agg_30 = agg_30.with_columns(
            pl.col("ts_list").map_elements(compute_intervals, return_dtype=pl.List(pl.Int64)).alias("intervals")
        ).drop("ts_list")
    
        agg_30 = agg_30.with_columns([
            pl.col("intervals").map_elements(mode_dom_fn, return_dtype=pl.Float64).alias("mode_dom"),
            pl.col("intervals").map_elements(cv_interval_fn, return_dtype=pl.Float64).alias("cv_interval"),
        ])
    
        # global percentiles
        x_count_95 = agg_30.filter(pl.col("n_txn") > 0).select("n_txn").to_series().quantile(0.95, "linear") if agg_30.filter(pl.col("n_txn") > 0).height > 0 else 1.0
        y_cv_95 = agg_30.filter((pl.col("n_txn") >= 2) & pl.col("cv_interval").is_not_null()).select("cv_interval").to_series().quantile(0.95, "linear") if agg_30.filter((pl.col("n_txn") >= 2) & pl.col("cv_interval").is_not_null()).height > 0 else 1.0
        u_total_95 = agg_30.filter(pl.col("total_amt") > 0).select("total_amt").to_series().quantile(0.95, "linear") if agg_30.filter(pl.col("total_amt") > 0).height > 0 else 1.0
    
        # component scores
        agg_30 = agg_30.with_columns((pl.col("n_txn").clip(0, x_count_95) / x_count_95).alias("score1"))
        agg_30 = agg_30.with_columns(
            pl.when(pl.col("n_txn") <= 1).then(0.0)
             .when(pl.col("n_txn") == 2).then(0.5)
             .otherwise(pl.col("mode_dom").fill_null(0.0))
             .alias("score2")
        )
        agg_30 = agg_30.with_columns(
            pl.when(pl.col("n_txn") <= 1).then(1.0)
             .when(pl.col("n_txn") == 2).then(0.5)
             .otherwise(pl.col("cv_interval").fill_null(0.0).clip(0, y_cv_95) / y_cv_95)
             .alias("score3")
        )
        agg_30 = agg_30.with_columns(((pl.lit(ref_date) - pl.col("last_date")).dt.total_days().clip(0, 30) / 30).alias("score4"))
        agg_30 = agg_30.with_columns(((pl.col("last_date") - pl.col("first_date")).dt.total_days()).alias("span_days"))
        agg_30 = agg_30.with_columns(pl.when(pl.col("n_txn") == 1).then(0.5).otherwise(pl.col("span_days").clip(0, 30) / 30).alias("score5"))
        agg_30 = agg_30.with_columns((pl.col("total_amt").clip(0, u_total_95) / u_total_95).alias("score6"))
    
        agg_30 = agg_30.with_columns(
            ((pl.col("score1") + pl.col("score2") + (1 - pl.col("score3")) + (1 - pl.col("score4")) + pl.col("score5") + pl.col("score6")) / 6).alias("stability_index")
        ).with_columns(pl.col("stability_index").clip(0, 1).alias("stability_index"))
    
        for r, fname_out in [(1, "A11_PDAY1604"), (2, "A11_PDAY2604"), (3, "A11_PDAY3604")]:
            feats_175_180 = feats_175_180.join(
                agg_30.filter(pl.col("rank") == r).select([key, "stability_index"]).rename({"stability_index": fname_out}),
                on=key,
                how="left",
            )
    
        # -----------------------------
        # Stability Index for 90-day window
        # -----------------------------
        df_90 = df_groupB_txn.filter(windows["0_90"]).sort([key, "rank", "txn_timestamp"])
        agg_90 = (
            df_90.group_by([key, "rank"])
            .agg([
                pl.count().alias("n_txn"),
                pl.col("txn_timestamp").first().alias("first_date"),
                pl.col("txn_timestamp").last().alias("last_date"),
                pl.col("txn_amount").sum().alias("total_amt"),
                pl.col("txn_timestamp").alias("ts_list"),
            ])
        )
    
        agg_90 = agg_90.with_columns(
            pl.col("ts_list").map_elements(compute_intervals, return_dtype=pl.List(pl.Int64)).alias("intervals")
        ).drop("ts_list")
    
        agg_90 = agg_90.with_columns([
            pl.col("intervals").map_elements(mode_dom_fn, return_dtype=pl.Float64).alias("mode_dom"),
            pl.col("intervals").map_elements(cv_interval_fn, return_dtype=pl.Float64).alias("cv_interval"),
        ])
    
        x_count_95 = agg_90.filter(pl.col("n_txn") > 0).select("n_txn").to_series().quantile(0.95, "linear") if agg_90.filter(pl.col("n_txn") > 0).height > 0 else 1.0
        y_cv_95 = agg_90.filter((pl.col("n_txn") >= 2) & pl.col("cv_interval").is_not_null()).select("cv_interval").to_series().quantile(0.95, "linear") if agg_90.filter((pl.col("n_txn") >= 2) & pl.col("cv_interval").is_not_null()).height > 0 else 1.0
        u_total_95 = agg_90.filter(pl.col("total_amt") > 0).select("total_amt").to_series().quantile(0.95, "linear") if agg_90.filter(pl.col("total_amt") > 0).height > 0 else 1.0
    
        agg_90 = agg_90.with_columns((pl.col("n_txn").clip(0, x_count_95) / x_count_95).alias("score1"))
        agg_90 = agg_90.with_columns(
            pl.when(pl.col("n_txn") <= 1).then(0.0)
             .when(pl.col("n_txn") == 2).then(0.5)
             .otherwise(pl.col("mode_dom").fill_null(0.0))
             .alias("score2")
        )
        agg_90 = agg_90.with_columns(
            pl.when(pl.col("n_txn") <= 1).then(1.0)
             .when(pl.col("n_txn") == 2).then(0.5)
             .otherwise(pl.col("cv_interval").fill_null(0.0).clip(0, y_cv_95) / y_cv_95)
             .alias("score3")
        )
        agg_90 = agg_90.with_columns(((pl.lit(ref_date) - pl.col("last_date")).dt.total_days().clip(0, 90) / 90).alias("score4"))
        agg_90 = agg_90.with_columns(((pl.col("last_date") - pl.col("first_date")).dt.total_days()).alias("span_days"))
        agg_90 = agg_90.with_columns(
            pl.when(pl.col("n_txn") == 1).then(0.0).otherwise(pl.col("span_days").clip(0, 90) / 90).alias("score5")
        )
        agg_90 = agg_90.with_columns((pl.col("total_amt").clip(0, u_total_95) / u_total_95).alias("score6"))
    
        agg_90 = agg_90.with_columns(
            ((pl.col("score1") + pl.col("score2") + (1 - pl.col("score3")) + (1 - pl.col("score4")) + pl.col("score5") + pl.col("score6")) / 6).alias("stability_index")
        ).with_columns(pl.col("stability_index").clip(0, 1).alias("stability_index"))
    
        # join 90-day features into feats_175_180
        for r, fname_out in [(1, "A11_PDAY1603"), (2, "A11_PDAY2603"), (3, "A11_PDAY3603")]:
            feats_175_180 = feats_175_180.join(
                agg_90.filter(pl.col("rank") == r).select([key, "stability_index"]).rename({"stability_index": fname_out}),
                on=key,
                how="left",
            )
    
        # Group A and missing ranks → 0
        feats_175_180 = feats_175_180.fill_null(0.0)
    
    feats_175_180 = feats_175_180.with_columns(pl.col("experian_consumer_key").cast(pl.Int64))
    #print(feats_175_180)


########################################################################################
#                              Features 181-198
# ===========================================
# FEATURE FAMILY: 181–198 (Estimated Next Paydates)
# ===========================================

# Definition:
#   • For each rank (1–3), estimate the next 6 paydates by:
#     1. Taking the last paydate in the last 90 days
#     2. Computing the mode interval between paydates (days)
#     3. Adding the mode interval repeatedly:
#          est_k = last_date + k * mode_interval
#   • Overrides:
#     - 2099‑12‑31 → No txns in last 90 days
#     - 2100‑01‑01 → Only 1 txn in last 90 days
#     - 2100‑12‑31 → Cascading override: once est_k < ref_date, all subsequent est_k..est6 = 2100‑12‑31
#     - Mode interval tie‑breaker → choose largest interval

# Feature Names:
#   • Rank 1 → A11_PDAY1710 ... A11_PDAY1760
#   • Rank 2 → A11_PDAY2710 ... A11_PDAY2760
#   • Rank 3 → A11_PDAY3710 ... A11_PDAY3760
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 181–198
###############################################

    OV_NO_TXN = date(2099, 12, 31)
    OV_ONE_TXN = date(2100, 1, 1)
    OV_BEFORE_REF = date(2100, 12, 31)
    
    if group_type == "A":
        # Group A → all 18 features set to OV_NO_TXN
        feats_181_198 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY1710": [OV_NO_TXN], "A11_PDAY1720": [OV_NO_TXN], "A11_PDAY1730": [OV_NO_TXN],
            "A11_PDAY1740": [OV_NO_TXN], "A11_PDAY1750": [OV_NO_TXN], "A11_PDAY1760": [OV_NO_TXN],
            "A11_PDAY2710": [OV_NO_TXN], "A11_PDAY2720": [OV_NO_TXN], "A11_PDAY2730": [OV_NO_TXN],
            "A11_PDAY2740": [OV_NO_TXN], "A11_PDAY2750": [OV_NO_TXN], "A11_PDAY2760": [OV_NO_TXN],
            "A11_PDAY3710": [OV_NO_TXN], "A11_PDAY3720": [OV_NO_TXN], "A11_PDAY3730": [OV_NO_TXN],
            "A11_PDAY3740": [OV_NO_TXN], "A11_PDAY3750": [OV_NO_TXN], "A11_PDAY3760": [OV_NO_TXN],
        })
    
    else:
        feats_181_198 = df_groupB_txn.select(key).unique()
    
        # Python helper for computing 6 estimated dates
        def compute_est_list(dt_list: list[date]) -> list[date]:
            n = len(dt_list)
            if n == 0:
                return [OV_NO_TXN] * 6
            if n == 1:
                return [OV_ONE_TXN] * 6
    
            # Compute intervals
            intervals = [(dt_list[i] - dt_list[i - 1]).days for i in range(1, n)]
            freq = {}
            for v in intervals:
                freq[v] = freq.get(v, 0) + 1
            max_freq = max(freq.values())
            mode_interval = max([v for v, f in freq.items() if f == max_freq])
    
            last_dt = dt_list[-1]
            est_dates = [last_dt + timedelta(days=mode_interval * k) for k in range(1, 7)]
    
            # Cascading override
            fixed = []
            invalid_seen = False
            for d in est_dates:
                if invalid_seen or d < ref_date:
                    fixed.append(OV_BEFORE_REF)
                    invalid_seen = True
                else:
                    fixed.append(d)
            return fixed
    
        # Rank → feature names
        rank_feature_map = {
            1: ["A11_PDAY1710","A11_PDAY1720","A11_PDAY1730","A11_PDAY1740","A11_PDAY1750","A11_PDAY1760"],
            2: ["A11_PDAY2710","A11_PDAY2720","A11_PDAY2730","A11_PDAY2740","A11_PDAY2750","A11_PDAY2760"],
            3: ["A11_PDAY3710","A11_PDAY3720","A11_PDAY3730","A11_PDAY3740","A11_PDAY3750","A11_PDAY3760"],
        }
    
        # Build features for each rank
        for r in [1, 2, 3]:
            df_r = (
                df_groupB_txn
                .filter((pl.col("rank") == r) & windows["0_90"])
                .with_columns(pl.col("txn_timestamp").dt.date().alias("dt"))
            )
    
            agg = (
                df_r.group_by(key)
                .agg(pl.col("dt").sort().alias("dt_list"))
            )
    
            agg = agg.with_columns(
                pl.col("dt_list").map_elements(compute_est_list, return_dtype=pl.List(pl.Date)).alias("est_list")
            ).drop("dt_list")
    
            # Split est_list into 6 columns
            agg = agg.with_columns([
                pl.col("est_list").list.get(0).alias("est1"),
                pl.col("est_list").list.get(1).alias("est2"),
                pl.col("est_list").list.get(2).alias("est3"),
                pl.col("est_list").list.get(3).alias("est4"),
                pl.col("est_list").list.get(4).alias("est5"),
                pl.col("est_list").list.get(5).alias("est6"),
            ]).drop("est_list")
    
            # Join into feats_181_198
            cols = rank_feature_map[r]
            feats_181_198 = feats_181_198.join(
                agg.select([key, "est1","est2","est3","est4","est5","est6"]).rename({
                    "est1": cols[0], "est2": cols[1], "est3": cols[2],
                    "est4": cols[3], "est5": cols[4], "est6": cols[5],
                }),
                on=key,
                how="left",
            )
    
        # Keys with no txns for a given rank → OV_NO_TXN
        feats_181_198 = feats_181_198.with_columns([
            pl.col(c).fill_null(OV_NO_TXN)
            for c in feats_181_198.columns
            if c != key
        ])


    #print(feats_181_198)

###############################################################################
#                            Feats 199-200
# ===========================================
# FEATURE FAMILY: 199–200 (Rank‑agnostic Transaction Counts)
# ===========================================

# Definition:
#   • Count total transactions (all valid ranks > 0) in:
#     - Last 30 days → A11_PDAY4104
#     - Last 90 days → A11_PDAY4103

# Overrides:
#   • Group A → override_value
#   • Group B → if no txns in window → 0
# ===========================================

# Notes:
#   • Rank‑agnostic: no rank filter applied
#   • Uses central window masks (windows dict)
# ===========================================


###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 199–200
###############################################


    if group_type == "A":
        feats_199_200 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4104": [override_value],  # 30-day txn count
            "A11_PDAY4103": [override_value],  # 90-day txn count
        })
    
    else:
        feats_199_200 = df_groupB_txn.select(key).unique()
    
        # --- Feature 199: 30-day txn count ---
        df_30 = df_groupB_txn.filter(windows["0_30"] & (pl.col("rank") > 0))
        agg_30 = df_30.group_by(key).agg(pl.count().alias("txn_count"))
    
        out_30 = (
            feats_199_200.join(agg_30, on=key, how="left")
            .with_columns(
                pl.when(pl.col("txn_count").is_null())
                  .then(0)   # no txns → 0
                  .otherwise(pl.col("txn_count"))
                  .alias("A11_PDAY4104")
            )
            .select([key, "A11_PDAY4104"])
        )
    
        feats_199_200 = feats_199_200.join(out_30, on=key, how="left")
    
        # --- Feature 200: 90-day txn count ---
        df_90 = df_groupB_txn.filter(windows["0_90"] & (pl.col("rank") > 0))
        agg_90 = df_90.group_by(key).agg(pl.count().alias("txn_count"))
    
        out_90 = (
            feats_199_200.join(agg_90, on=key, how="left")
            .with_columns(
                pl.when(pl.col("txn_count").is_null())
                  .then(0)   # no txns → 0
                  .otherwise(pl.col("txn_count"))
                  .alias("A11_PDAY4103")
            )
            .select([key, "A11_PDAY4103"])
        )
    
        feats_199_200 = feats_199_200.join(out_90, on=key, how="left")

    feats_199_200 = feats_199_200.with_columns(pl.col('A11_PDAY4104').cast(pl.Float64).alias('A11_PDAY4104'))
    feats_199_200 = feats_199_200.with_columns(pl.col('A11_PDAY4103').cast(pl.Float64).alias('A11_PDAY4103'))
    #print(feats_199_200)

##########################################################################
#                          Feats 201-202
# ===========================================
# FEATURE FAMILY: 201–202 (Rank‑agnostic Txn Count Ratios)
# ===========================================

# Definition:
#   • Ratio of transaction counts across all valid ranks (>0):
#     - Feature 201 → (0–30 days) ÷ (31–60 days) → A11_PDAY4113
#     - Feature 202 → (0–30 days) ÷ (61–90 days) → A11_PDAY4123

# Overrides (Group B):
#   • BOTH0 → if numerator=0 and denominator=0
#   • DEN0  → if denominator=0 but numerator>0
#   • 0.0   → if numerator=0 but denominator>0

# Overrides (Group A):
#   • Always set to override_value

# Notes:
#   • Rank‑agnostic: no rank filter applied beyond requiring rank > 0
#   • Uses central window masks (windows dict)
#   • Ratios are computed per customer across all valid ranks
# ===========================================


###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 201–202
###############################################

    BOTH0 = override["BOTH0"]
    DEN0  = override["DEN0"]
    
    if group_type == "A":
        feats_201_202 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4113": [override_value],  # (0–30)/(31–60)
            "A11_PDAY4123": [override_value],  # (0–30)/(61–90)
        })
    
    else:
        feats_201_202 = df_groupB_txn.select(key).unique()
    
        # --- Helper: ratio of txn counts ---
        def count_ratio(window_den_mask: pl.Expr, fname_out: str):
            num_tbl = (
                df_groupB_txn
                .filter(windows["0_30"] & (pl.col("rank") > 0))
                .group_by(key)
                .agg(pl.count().alias("num_cnt"))
            )
    
            den_tbl = (
                df_groupB_txn
                .filter(window_den_mask & (pl.col("rank") > 0))
                .group_by(key)
                .agg(pl.count().alias("den_cnt"))
            )
    
            out = (
                feats_201_202
                .join(num_tbl, on=key, how="left")
                .join(den_tbl, on=key, how="left")
            )
    
            ratio_expr = (
                pl.when((pl.col("num_cnt").fill_null(0) == 0) & (pl.col("den_cnt").fill_null(0) == 0))
                  .then(BOTH0)
                .when(pl.col("den_cnt").fill_null(0) == 0)
                  .then(
                      pl.when(pl.col("num_cnt").fill_null(0) == 0)
                        .then(BOTH0)
                      .otherwise(DEN0)
                  )
                .when(pl.col("num_cnt").fill_null(0) == 0)
                  .then(0.0)
                .otherwise(pl.col("num_cnt") / pl.col("den_cnt"))
            )
    
            out = out.with_columns(ratio_expr.alias(fname_out)).select([key, fname_out])
            return out
    
        # --- Feature 201: (0–30)/(31–60) ---
        feats_201_202 = feats_201_202.join(
            count_ratio(windows["31_60"], "A11_PDAY4113"),
            on=key, how="left"
        )
    
        # --- Feature 202: (0–30)/(61–90) ---
        feats_201_202 = feats_201_202.join(
            count_ratio(windows["61_90"], "A11_PDAY4123"),
            on=key, how="left"
        )


    #print(feats_201_202)
###################################################################
#                    Features 203-208
# ===========================================
# FEATURE FAMILY: 203–208 (Rank‑agnostic Max/Min/Avg Intervals)
# ===========================================

# Definition:
#   • Compute max, min, and average payday intervals (days between consecutive txns)
#     across all valid ranks (>0).
#   • Windows:
#     - 30‑day → Features 203–205
#       • Max → A11_PDAY4244
#       • Min → A11_PDAY4254
#       • Avg → A11_PDAY4264
#     - 90‑day → Features 206–208
#       • Max → A11_PDAY4243
#       • Min → A11_PDAY4253
#       • Avg → A11_PDAY4263

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – No transactions in window → NO_TXN
#     – Only one transaction → ONE_TXN
#     – Otherwise compute intervals normally

# Notes:
#   • Rank‑agnostic: no rank filter applied beyond requiring rank > 0
#   • Uses central window masks (windows dict)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 203–208
###############################################

    NO_TXN  = override["NO_TXN"]
    ONE_TXN = override["ONE_TXN"]
    
    if group_type == "A":
        feats_203_208 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4244": [override_value],  # 30d Max
            "A11_PDAY4254": [override_value],  # 30d Min
            "A11_PDAY4264": [override_value],  # 30d Avg
            "A11_PDAY4243": [override_value],  # 90d Max
            "A11_PDAY4253": [override_value],  # 90d Min
            "A11_PDAY4263": [override_value],  # 90d Avg
        })
    
    else:
        feats_203_208 = df_groupB_txn.select(key).unique()
    
        # --- Helper: compute interval stats for a window ---
        def interval_stats(window_mask, fname_max, fname_min, fname_avg):
            base = feats_203_208
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            # No transactions → NO_TXN
            if df_w.height == 0:
                return base.select([key]).with_columns([
                    pl.lit(NO_TXN).alias(fname_max),
                    pl.lit(NO_TXN).alias(fname_min),
                    pl.lit(NO_TXN).alias(fname_avg),
                ])
    
            # One transaction → ONE_TXN
            if df_w.height == 1:
                return base.select([key]).with_columns([
                    pl.lit(ONE_TXN).alias(fname_max),
                    pl.lit(ONE_TXN).alias(fname_min),
                    pl.lit(ONE_TXN).alias(fname_avg),
                ])
    
            ts_tbl = (
                df_w.group_by(key)
                    .agg(pl.col("txn_timestamp").sort().alias("ts_sorted"))
            )
    
            ts_tbl = ts_tbl.with_columns([
                (pl.col("ts_sorted").list.diff().list.eval(pl.element().dt.total_days())).alias("intervals")
            ])
    
            out = ts_tbl.with_columns([
                pl.col("intervals").list.max().alias(fname_max),
                pl.col("intervals").list.min().alias(fname_min),
                pl.col("intervals").list.mean().alias(fname_avg),
            ]).select([key, fname_max, fname_min, fname_avg])
    
            out = base.join(out, on=key, how="left")
    
            # Fill nulls with NO_TXN
            out = out.with_columns([
                pl.col(fname_max).fill_null(NO_TXN),
                pl.col(fname_min).fill_null(NO_TXN),
                pl.col(fname_avg).fill_null(NO_TXN),
            ])
    
            return out.select([key, fname_max, fname_min, fname_avg])
    
        # --- Features 203–205: 30-day window ---
        feats_203_208 = feats_203_208.join(
            interval_stats(
                windows["0_30"],
                "A11_PDAY4244",  # Max
                "A11_PDAY4254",  # Min
                "A11_PDAY4264",  # Avg
            ),
            on=key, how="left"
        )
    
        # --- Features 206–208: 90-day window ---
        feats_203_208 = feats_203_208.join(
            interval_stats(
                windows["0_90"],
                "A11_PDAY4243",  # Max
                "A11_PDAY4253",  # Min
                "A11_PDAY4263",  # Avg
            ),
            on=key, how="left"
        )
    
        feats_203_208 = feats_203_208.select([
            key,
            "A11_PDAY4244", "A11_PDAY4254", "A11_PDAY4264",
            "A11_PDAY4243", "A11_PDAY4253", "A11_PDAY4263",
        ])

    #print(feats_203_208)

###############################################################
#                      Feats 209-210
# ===========================================
# FEATURE FAMILY: 209–210 (Rank‑agnostic Range Ratio of Payday Intervals)
# ===========================================

# Definition:
#   • Compute the range ratio of payday intervals across all valid ranks (>0):
#       Range ratio = (max_interval – min_interval) / avg_interval
#   • Windows:
#     - Feature 209 → 30‑day window → A11_PDAY4274
#     - Feature 210 → 90‑day window → A11_PDAY4273

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – NO_TXN → if no transactions in window
#     – ONE_TXN → if only one transaction in window
#     – Else → compute ratio normally

# Notes:
#   • Rank‑agnostic: all valid ranks included
#   • Uses central window masks (windows dict)
# ===========================================


###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 209–210
###############################################

    NO_TXN  = override["NO_TXN"]
    ONE_TXN = override["ONE_TXN"]
    
    if group_type == "A":
        feats_209_210 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4274": [override_value],  # 30-day range ratio
            "A11_PDAY4273": [override_value],  # 90-day range ratio
        })
    
    else:
        feats_209_210 = df_groupB_txn.select(key).unique()
    
        # --- Helper: compute range ratio for a window ---
        def range_ratio(window_mask, fname_out):
            base = feats_209_210
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            # No transactions → NO_TXN
            if df_w.height == 0:
                return base.select([key]).with_columns([pl.lit(NO_TXN).alias(fname_out)])
    
            # One transaction → ONE_TXN
            if df_w.height == 1:
                return base.select([key]).with_columns([pl.lit(ONE_TXN).alias(fname_out)])
    
            ts_tbl = (
                df_w.group_by(key)
                    .agg(pl.col("txn_timestamp").sort().alias("ts_sorted"))
            )
    
            ts_tbl = ts_tbl.with_columns([
                (pl.col("ts_sorted").list.diff().list.eval(pl.element().dt.total_days())).alias("intervals")
            ])
    
            ts_tbl = ts_tbl.with_columns([
                pl.col("intervals").list.max().alias("max_int"),
                pl.col("intervals").list.min().alias("min_int"),
                pl.col("intervals").list.mean().alias("avg_int"),
            ])
    
            ts_tbl = ts_tbl.with_columns(
                ((pl.col("max_int") - pl.col("min_int")) / pl.col("avg_int")).alias(fname_out)
            )
    
            out = ts_tbl.select([key, fname_out])
            out = base.join(out, on=key, how="left")
    
            # Fill nulls with NO_TXN
            out = out.with_columns([pl.col(fname_out).fill_null(NO_TXN)])
            return out.select([key, fname_out])
    
        # --- Feature 209: 30-day window ---
        feats_209_210 = feats_209_210.join(
            range_ratio(windows["0_30"], "A11_PDAY4274"),
            on=key, how="left"
        )
    
        # --- Feature 210: 90-day window ---
        feats_209_210 = feats_209_210.join(
            range_ratio(windows["0_90"], "A11_PDAY4273"),
            on=key, how="left"
        )
    
        feats_209_210 = feats_209_210.select([key, "A11_PDAY4274", "A11_PDAY4273"])


    #print(feats_209_210)

#####################################################################################
#                            Feats 211-212
# ===========================================
# FEATURE FAMILY: 211–212 (Rank‑agnostic CV of Transaction Amounts)
# ===========================================

# Definition:
#   • Compute coefficient of variation (CV = std / mean) of transaction amounts
#     across all valid ranks (>0).
#   • Windows:
#     - Feature 211 → 30‑day window → A11_PDAY4284
#     - Feature 212 → 90‑day window → A11_PDAY4283

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – No transactions in window → NULL
#     – Only one transaction → 0.0
#     – Else → compute std/mean

# Notes:
#   • Rank‑agnostic: all valid ranks included
#   • Uses central window masks (windows dict)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 211–212
###############################################

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 211–212
###############################################

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 211–212
###############################################

    if group_type == "A":
        feats_211_212 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4284": [override_value],  # 30-day CV
            "A11_PDAY4283": [override_value],  # 90-day CV
        })
    
    else:
        feats_211_212 = df_groupB_txn.select(key).unique()
    
        # --- Helper: CV of txn amounts for a window ---
        def cv_amounts(window_mask, fname_out):
            base = feats_211_212
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            # No transactions → BOTH0
            if df_w.height == 0:
                return base.select([key]).with_columns([pl.lit(override["BOTH0"]).alias(fname_out)])
    
            # One transaction → CV = 0.0
            if df_w.height == 1:
                return base.select([key]).with_columns([pl.lit(0.0).alias(fname_out)])
    
            # Compute mean and std per consumer
            agg_tbl = (
                df_w.group_by(key)
                    .agg([
                        pl.col("txn_amount").mean().alias("mean_amt"),
                        pl.col("txn_amount").std().alias("std_amt"),
                    ])
            )
    
            # CV = std / mean, wrapped in apply_ratio_overrides
            out = agg_tbl.with_columns(
                apply_ratio_overrides(
                    pl.col("std_amt") / pl.col("mean_amt"),
                    pl.col("std_amt"),
                    pl.col("mean_amt"),
                    is_count_amount=True
                ).alias(fname_out)
            ).select([key, fname_out])
    
            out = base.join(out, on=key, how="left")
            return out.select([key, fname_out])
    
        # --- Feature 211: 30-day window ---
        feats_211_212 = feats_211_212.join(
            cv_amounts(windows["0_30"], "A11_PDAY4284"),
            on=key, how="left"
        )
    
        # --- Feature 212: 90-day window ---
        feats_211_212 = feats_211_212.join(
            cv_amounts(windows["0_90"], "A11_PDAY4283"),
            on=key, how="left"
        )
    
        feats_211_212 = feats_211_212.select([key, "A11_PDAY4284", "A11_PDAY4283"])


    #print(feats_211_212)

##############################################################################
#                        Feats 213-216
# ===========================================
# FEATURE FAMILY: 213–216 (Rank‑agnostic Paydates)
# ===========================================

# Definition:
#   • Feature 213 → Latest paydate in last 90d → A11_PDAY4403
#   • Feature 214 → Earliest paydate in last 30d → A11_PDAY4414
#   • Feature 215 → Earliest paydate in last 90d → A11_PDAY4413
#   • Feature 216 → Days between earliest & latest in last 90d → A11_PDAY4423

# Overrides:
#   • Group A:
#     – 213–215 → sentinel date 2099‑12‑31
#     – 216 → override_value
#   • Group B:
#     – Latest/Earliest paydates → sentinel date 2099‑12‑31 if no txns
#     – Days between → BOTH0 override if no txns or only one txn

# Notes:
#   • Rank‑agnostic: all valid ranks included (rank > 0)
#   • Uses central window masks (windows dict)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 213–216
###############################################

    OVERRIDE_TS = date(2099, 12, 31)
    BOTH0 = override["BOTH0"]
    
    if group_type == "A":
        feats_213_216 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4403": [OVERRIDE_TS],     # Latest 90d
            "A11_PDAY4414": [OVERRIDE_TS],     # Earliest 30d
            "A11_PDAY4413": [OVERRIDE_TS],     # Earliest 90d
            "A11_PDAY4423": [override_value],  # Days between earliest & latest 90d
        })
    
    else:
        feats_213_216 = df_groupB_txn.select(key).unique()
    
        # --- Helper: latest timestamp in a window ---
        def latest_ts(window_mask, fname_out):
            base = feats_213_216
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(OVERRIDE_TS).alias(fname_out))
    
            agg_tbl = df_w.group_by(key).agg(pl.col("txn_timestamp").max().alias(fname_out))
            out = base.join(agg_tbl, on=key, how="left")
            out = out.with_columns(pl.col(fname_out).fill_null(OVERRIDE_TS))
            return out.select([key, fname_out])
    
        # --- Helper: earliest timestamp in a window ---
        def earliest_ts(window_mask, fname_out):
            base = feats_213_216
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(OVERRIDE_TS).alias(fname_out))
    
            agg_tbl = df_w.group_by(key).agg(pl.col("txn_timestamp").min().alias(fname_out))
            out = base.join(agg_tbl, on=key, how="left")
            out = out.with_columns(pl.col(fname_out).fill_null(OVERRIDE_TS))
            return out.select([key, fname_out])
        

        def days_since_latest(window_mask, fname_out):
            # base frame to preserve shape/keys (same pattern as earliest_ts)
            base = feats_213_216

            # Filter Group-B transactions by window and rank>0 (same as your family)
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))

            # No transactions in window -> override BOTH0 (consistent with your “days since …” features)
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(BOTH0).alias(fname_out))

            # Latest paydate within the window (rank-agnostic)
            latest_tbl = (
                df_w.group_by(key)
                    .agg(pl.col("txn_timestamp").max().alias("latest_paydate"))
            )

            # Join to base and compute days since latest: (ref_date - latest_paydate)
            out = (
                base.join(latest_tbl, on=key, how="left")
                    .with_columns(
                        (pl.lit(ref_date) - pl.col("latest_paydate"))
                        .dt.total_days()
                        .cast(pl.Int32)        # adjust dtype if you store as Float64 elsewhere
                        .alias(fname_out)
                    )
                    .drop("latest_paydate")
                    .with_columns(pl.col(fname_out).fill_null(BOTH0))
                    .select([key, fname_out])
            )
            return out

    
        # --- Feature 213: Latest paydate in last 90 days ---
        feats_213_216 = feats_213_216.join(
            latest_ts(windows["0_90"], "A11_PDAY4403"),
            on=key, how="left"
        )
    
        # --- Feature 214: Earliest paydate in last 30 days ---
        feats_213_216 = feats_213_216.join(
            earliest_ts(windows["0_30"], "A11_PDAY4414"),
            on=key, how="left"
        )
    
        # --- Feature 215: Earliest paydate in last 90 days ---
        feats_213_216 = feats_213_216.join(
            earliest_ts(windows["0_90"], "A11_PDAY4413"),
            on=key, how="left"
        )
    
        # --- Feature 216: Days between earliest & latest in last 90 days ---
        
        feats_213_216 = feats_213_216.join(
            days_since_latest(windows["0_90"], "A11_PDAY4423"),
            on=key, how="left"
        )

    
        feats_213_216 = feats_213_216.select([
            key,
            "A11_PDAY4403", "A11_PDAY4414", "A11_PDAY4413", "A11_PDAY4423"
        ])

    #print(feats_213_216)

###########################################################################
#                         Feat 217
# ===========================================
# FEATURE 217 : Days Since Last Large Paydate
# ===========================================

# Definition:
#   • Days since last paydate with txn amount > 70% of avg txn amount
#     in last 90 days across all valid ranks (>0).

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – BOTH0 → if no txns in window
#     – BOTH0 → if no qualifying txn (>70% of avg)
#     – Else → (cutoff["ref"] - latest qualifying txn).total_days()

# Notes:
#   • Rank‑agnostic: all valid ranks included
#   • Uses central window masks (windows dict)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURE 217
###############################################

    BOTH0 = override["NO_TXN"]
    
    if group_type == "A":
        feats_217 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4433": [override_value],  # Days since last large paydate
        })
    
    else:
        feats_217 = df_groupB_txn.select(key).unique()
    
        def days_since_last_large_paydate(window_mask, fname_out):
            base = feats_217
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            # 0 txns → BOTH0
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(BOTH0).alias(fname_out))
    
            # Avg amount per consumer
            avg_tbl = (
                df_w.group_by(key)
                   .agg(pl.col("txn_amount").mean().alias("avg_amt"))
            )
    
            # Join avg back to window data
            df_w_avg = df_w.join(avg_tbl, on=key, how="inner")
    
            # Qualifying txns: amount > 70% of avg
            df_qual = df_w_avg.filter(pl.col("txn_amount") > 0.7 * pl.col("avg_amt"))
    
            # Latest qualifying timestamp per consumer
            latest_tbl = (
                df_qual.group_by(key)
                      .agg(pl.col("txn_timestamp").max().alias("latest_large_ts"))
            )
    
            out = base.join(latest_tbl, on=key, how="left")
    
            # If no qualifying txn → BOTH0, else days since
            out = out.with_columns(
                pl.when(pl.col("latest_large_ts").is_null())
                  .then(BOTH0)
                .otherwise((cutoff["ref"] - pl.col("latest_large_ts")).dt.total_days())
                .alias(fname_out)
            ).drop(["latest_large_ts"])
    
            return out.select([key, fname_out])
    
        # --- Feature 217: 90-day window ---
        feats_217 = feats_217.join(
            days_since_last_large_paydate(windows["0_90"], "A11_PDAY4433"),
            on=key, how="left"
        )
    
        feats_217 = feats_217.select([key, "A11_PDAY4433"])

    #print(feats_217)

##################################################################################
#                              Feats 218-221
# ===========================================
# FEATURE FAMILY: 218–221 (Rank‑agnostic Paydate Differences)
# ===========================================

# Definition:
#   • Feature 218 → Days since earliest paydate (30d) → A11_PDAY4444
#   • Feature 219 → Days since earliest paydate (90d) → A11_PDAY4443
#   • Feature 220 → Latest - earliest diff (30d) → A11_PDAY4454
#   • Feature 221 → Latest - earliest diff (90d) → A11_PDAY4453

# Overrides:
#   • Group A:
#     – 218–219 → override_value
#     – 220–221 → override_value
#   • Group B:
#     – Days since earliest:
#         • BOTH0 → if no txns
#         • Else → (cutoff["ref"] - earliest_ts).total_days()
#     – Latest - earliest diff:
#         • BOTH0 → if no txns
#         • 0 → if only one txn
#         • Else → (latest_ts - earliest_ts).total_days()

# Notes:
#   • Rank‑agnostic: all valid ranks included (rank > 0)
#   • Uses central window masks (windows dict)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 218–221
###############################################

    BOTH0 = override["NO_TXN"]
    
    if group_type == "A":
        feats_218_221 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4444": [override_value],  # Days since earliest (30d)
            "A11_PDAY4443": [override_value],  # Days since earliest (90d)
            "A11_PDAY4454": [override_value],  # Latest - earliest diff (30d)
            "A11_PDAY4453": [override_value],  # Latest - earliest diff (90d)
        })
    
    else:
        feats_218_221 = df_groupB_txn.select(key).unique()
    
        # --- Helper: days since earliest paydate ---
        def days_since_earliest(window_mask, fname_out):
            base = feats_218_221
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(BOTH0).alias(fname_out))
    
            agg_tbl = df_w.group_by(key).agg(pl.col("txn_timestamp").min().alias("earliest_ts"))
            out = base.join(agg_tbl, on=key, how="left")
    
            out = out.with_columns(
                pl.when(pl.col("earliest_ts").is_null())
                  .then(BOTH0)
                .otherwise((cutoff["ref"] - pl.col("earliest_ts")).dt.total_days())
                .alias(fname_out)
            ).drop(["earliest_ts"])
    
            return out.select([key, fname_out])
    
        # --- Helper: latest - earliest paydate diff ---
        def diff_latest_earliest(window_mask, fname_out):
            base = feats_218_221
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(BOTH0).alias(fname_out))
    
            if df_w.height == 1:
                return base.select([key]).with_columns(pl.lit(0).alias(fname_out))
    
            agg_tbl = df_w.group_by(key).agg([
                pl.col("txn_timestamp").max().alias("max_ts"),
                pl.col("txn_timestamp").min().alias("min_ts"),
            ])
    
            out = base.join(agg_tbl, on=key, how="left")
    
            out = out.with_columns(
                pl.when(pl.col("max_ts").is_null() | pl.col("min_ts").is_null())
                  .then(BOTH0)
                .otherwise((pl.col("max_ts") - pl.col("min_ts")).dt.total_days())
                .alias(fname_out)
            ).drop(["max_ts", "min_ts"])
    
            return out.select([key, fname_out])
    
        # --- Feature 218: Days since earliest paydate (30d) ---
        feats_218_221 = feats_218_221.join(
            days_since_earliest(windows["0_30"], "A11_PDAY4444"),
            on=key, how="left"
        )
    
        # --- Feature 219: Days since earliest paydate (90d) ---
        feats_218_221 = feats_218_221.join(
            days_since_earliest(windows["0_90"], "A11_PDAY4443"),
            on=key, how="left"
        )
    
        # --- Feature 220: Latest - earliest diff (30d) ---
        feats_218_221 = feats_218_221.join(
            diff_latest_earliest(windows["0_30"], "A11_PDAY4454"),
            on=key, how="left"
        )
    
        # --- Feature 221: Latest - earliest diff (90d) ---
        feats_218_221 = feats_218_221.join(
            diff_latest_earliest(windows["0_90"], "A11_PDAY4453"),
            on=key, how="left"
        )
    
        feats_218_221 = feats_218_221.select([
            key,
            "A11_PDAY4444", "A11_PDAY4443", "A11_PDAY4454", "A11_PDAY4453"
        ])

    feats_218_221 = feats_218_221.with_columns(pl.col('A11_PDAY4444').cast(pl.Float64).alias('A11_PDAY4444'))
    feats_218_221 = feats_218_221.with_columns(pl.col('A11_PDAY4443').cast(pl.Float64).alias('A11_PDAY4443'))
    feats_218_221 = feats_218_221.with_columns(pl.col('A11_PDAY4454').cast(pl.Float64).alias('A11_PDAY4454'))
    feats_218_221 = feats_218_221.with_columns(pl.col('A11_PDAY4453').cast(pl.Float64).alias('A11_PDAY4453'))
                                               
    #print(feats_218_221)

##################################################################################
#                            Feats 222-225
# ===========================================
# FEATURE FAMILY: 222–225 (Rank‑agnostic Sum & Avg of Paycheck Amounts)
# ===========================================

# Definition:
#   • Feature 222 → Sum of txn amounts in last 30d → A11_PDAY4504
#   • Feature 223 → Sum of txn amounts in last 90d → A11_PDAY4503
#   • Feature 224 → Avg of txn amounts in last 30d → A11_PDAY4524
#   • Feature 225 → Avg of txn amounts in last 90d → A11_PDAY4523

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – BOTH0 → if no txns in window
#     – Else → compute sum or average normally

# Notes:
#   • Rank‑agnostic: all valid ranks included (rank > 0)
#   • Uses central window masks (windows dict)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 222–225
###############################################

    BOTH0 = override["ZERO"]
    
    if group_type == "A":
        feats_222_225 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4504": [override_value],  # Sum 30d
            "A11_PDAY4503": [override_value],  # Sum 90d
            "A11_PDAY4524": [override_value],  # Avg 30d
            "A11_PDAY4523": [override_value],  # Avg 90d
        })
    
    else:
        feats_222_225 = df_groupB_txn.select(key).unique()
    
        # --- Helper: sum of amounts in window ---
        def sum_amount(window_mask, fname_out):
            base = feats_222_225
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(BOTH0).alias(fname_out))
    
            agg_tbl = df_w.group_by(key).agg(pl.col("txn_amount").sum().alias(fname_out))
            out = base.join(agg_tbl, on=key, how="left")
            out = out.with_columns(pl.col(fname_out).fill_null(BOTH0))
            return out.select([key, fname_out])
    
        # --- Helper: average of amounts in window ---
        def avg_amount(window_mask, fname_out):
            base = feats_222_225
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(BOTH0).alias(fname_out))
    
            agg_tbl = df_w.group_by(key).agg(pl.col("txn_amount").mean().alias(fname_out))
            out = base.join(agg_tbl, on=key, how="left")
            out = out.with_columns(pl.col(fname_out).fill_null(BOTH0))
            return out.select([key, fname_out])
    
        # --- Feature 222: Sum in 30d ---
        feats_222_225 = feats_222_225.join(
            sum_amount(windows["0_30"], "A11_PDAY4504"),
            on=key, how="left"
        )
    
        # --- Feature 223: Sum in 90d ---
        feats_222_225 = feats_222_225.join(
            sum_amount(windows["0_90"], "A11_PDAY4503"),
            on=key, how="left"
        )
    
        # --- Feature 224: Avg in 30d ---
        feats_222_225 = feats_222_225.join(
            avg_amount(windows["0_30"], "A11_PDAY4524"),
            on=key, how="left"
        )
    
        # --- Feature 225: Avg in 90d ---
        feats_222_225 = feats_222_225.join(
            avg_amount(windows["0_90"], "A11_PDAY4523"),
            on=key, how="left"
        )
    
        feats_222_225 = feats_222_225.select([
            key,
            "A11_PDAY4504", "A11_PDAY4503", "A11_PDAY4524", "A11_PDAY4523"
        ])

    #print(feats_222_225)

#############################################################################
#                             Feats 226-227
# ===========================================
# FEATURE FAMILY: 226–227 (Ratio of Last Paycheck to Avg Paycheck)
# ===========================================

# Definition:
#   • Feature 226 → Ratio last_amt / avg_amt in last 30d → A11_PDAY4534
#   • Feature 227 → Ratio last_amt / avg_amt in last 90d → A11_PDAY4533

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – BOTH0 → if last_amt = 0 AND avg_amt = 0
#     – DEN0  → if avg_amt = 0 AND last_amt > 0
#     – NUM0  → if last_amt = 0 but avg_amt > 0
#     – Else  → last_amt / avg_amt

# Notes:
#   • Rank‑agnostic: all valid ranks included (rank > 0)
#   • Uses central window masks (windows dict)
#   • Override logic applied via apply_ratio_overrides(expr, num, den, is_count_amount=True)
# ===========================================
###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 226–227
###############################################

    if group_type == "A":
        feats_226_227 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4534": [override_value],  # Ratio last/avg in 30d
            "A11_PDAY4533": [override_value],  # Ratio last/avg in 90d
        })
    
    else:
        feats_226_227 = df_groupB_txn.select(key).unique()
    
        # --- Helper: ratio last_amt / avg_amt ---
        def ratio_last_to_avg(window_mask, fname_out):
            base = feats_226_227
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            # No txns → BOTH0
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(override["BOTH0"]).alias(fname_out))
    
            agg_tbl = (
                df_w.group_by(key)
                    .agg([
                        pl.col("txn_amount").mean().alias("avg_amt"),
                        pl.col("txn_amount")
                          .sort_by("txn_timestamp")
                          .last()
                          .alias("last_amt"),
                    ])
            )
    
            out = base.join(agg_tbl, on=key, how="left")
    
            # Apply ratio overrides
            out = out.with_columns(
                apply_ratio_overrides(
                    pl.col("last_amt") / pl.col("avg_amt"),
                    pl.col("last_amt"),
                    pl.col("avg_amt"),
                    is_count_amount=True
                ).alias(fname_out)
            ).drop(["last_amt", "avg_amt"])
    
            return out.select([key, fname_out])
    
        # --- Feature 226: last_amt / avg_30d ---
        feats_226_227 = feats_226_227.join(
            ratio_last_to_avg(windows["0_30"], "A11_PDAY4534"),
            on=key, how="left"
        )
    
        # --- Feature 227: last_amt / avg_90d ---
        feats_226_227 = feats_226_227.join(
            ratio_last_to_avg(windows["0_90"], "A11_PDAY4533"),
            on=key, how="left"
        )
    
        feats_226_227 = feats_226_227.select([key, "A11_PDAY4534", "A11_PDAY4533"])

    #print(feats_226_227)

####################################################################################
#                          Feats 228-229
# ===========================================
# FEATURE FAMILY: 228–229 (Range Ratio of Paycheck Amounts)
# ===========================================

# Definition:
#   • Feature 228 → Range ratio in last 30d → A11_PDAY4544
#   • Feature 229 → Range ratio in last 90d → A11_PDAY4543
#   • Range ratio = (max_amt – min_amt) / avg_amt

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – BOTH0 → if avg_amt = 0 AND range = 0
#     – DEN0  → if avg_amt = 0 AND range > 0
#     – NUM0  → if range = 0 but avg_amt > 0 (via apply_ratio_overrides)
#     – Else  → (max_amt – min_amt) / avg_amt

# Notes:
#   • Rank‑agnostic: all valid ranks included (rank > 0)
#   • Uses central window masks (windows dict)
#   • Override logic applied via apply_ratio_overrides(expr, num, den, is_count_amount=True)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 228–229
###############################################

    if group_type == "A":
        feats_228_229 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4544": [override_value],  # Range ratio 30d
            "A11_PDAY4543": [override_value],  # Range ratio 90d
        })
    
    else:
        feats_228_229 = df_groupB_txn.select(key).unique()
    
        # --- Helper: range_ratio = (max - min) / avg ---
        def range_ratio(window_mask, fname_out):
            base = feats_228_229
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            # No txns → BOTH0
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(override["BOTH0"]).alias(fname_out))
    
            agg_tbl = (
                df_w.group_by(key)
                    .agg([
                        pl.col("txn_amount").max().alias("max_amt"),
                        pl.col("txn_amount").min().alias("min_amt"),
                        pl.col("txn_amount").mean().alias("avg_amt"),
                    ])
            )
    
            out = base.join(agg_tbl, on=key, how="left")
    
            # Apply ratio overrides
            out = out.with_columns(
                apply_ratio_overrides(
                    (pl.col("max_amt") - pl.col("min_amt")) / pl.col("avg_amt"),
                    (pl.col("max_amt") - pl.col("min_amt")),
                    pl.col("avg_amt"),
                    is_count_amount=True
                ).alias(fname_out)
            ).drop(["max_amt", "min_amt", "avg_amt"])
    
            return out.select([key, fname_out])
    
        # --- Feature 228: range/avg in 30d ---
        feats_228_229 = feats_228_229.join(
            range_ratio(windows["0_30"], "A11_PDAY4544"),
            on=key, how="left"
        )
    
        # --- Feature 229: range/avg in 90d ---
        feats_228_229 = feats_228_229.join(
            range_ratio(windows["0_90"], "A11_PDAY4543"),
            on=key, how="left"
        )
    
        feats_228_229 = feats_228_229.select([key, "A11_PDAY4544", "A11_PDAY4543"])

    #print(feats_228_229)

##################################################################################################
#                               Feats 230-231
# ===========================================
# FEATURE FAMILY: 230–231 (CV of Paycheck Amounts)
# ===========================================

# Definition:
#   • Feature 230 → CV of paycheck amounts in last 30d → A11_PDAY4554
#   • Feature 231 → CV of paycheck amounts in last 90d → A11_PDAY4553
#   • CV = std / mean

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – BOTH0 → if std = 0 AND mean = 0
#     – DEN0  → if std > 0 AND mean = 0
#     – NUM0  → if std = 0 but mean > 0 (via apply_ratio_overrides)
#     – Else  → std / mean

# Notes:
#   • Rank‑agnostic: all valid ranks included (rank > 0)
#   • Uses central window masks (windows dict)
#   • Override logic applied via apply_ratio_overrides(expr, num, den, is_count_amount=True)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 230–231
###############################################

    if group_type == "A":
        feats_230_231 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4554": [override_value],  # CV in 30d
            "A11_PDAY4553": [override_value],  # CV in 90d
        })
    
    else:
        feats_230_231 = df_groupB_txn.select(key).unique()
    
        # --- Helper: CV = std / mean ---
        def cv_amount(window_mask, fname_out):
            base = feats_230_231
            df_w = df_groupB_txn.filter(window_mask & (pl.col("rank") > 0))
    
            # No txns → BOTH0
            if df_w.height == 0:
                return base.select([key]).with_columns(pl.lit(override["BOTH0"]).alias(fname_out))
    
            agg_tbl = (
                df_w.group_by(key)
                    .agg([
                        pl.col("txn_amount").std().alias("std_amt"),
                        pl.col("txn_amount").mean().alias("avg_amt"),
                    ])
            )
    
            out = base.join(agg_tbl, on=key, how="left")
    
            # Apply ratio overrides
            out = out.with_columns(
                apply_ratio_overrides(
                    pl.col("std_amt") / pl.col("avg_amt"),
                    pl.col("std_amt"),
                    pl.col("avg_amt"),
                    is_count_amount=True
                ).alias(fname_out)
            ).drop(["std_amt", "avg_amt"])
    
            return out.select([key, fname_out])
    
        # --- Feature 230: CV in 30d ---
        feats_230_231 = feats_230_231.join(
            cv_amount(windows["0_30"], "A11_PDAY4554"),
            on=key, how="left"
        )
    
        # --- Feature 231: CV in 90d ---
        feats_230_231 = feats_230_231.join(
            cv_amount(windows["0_90"], "A11_PDAY4553"),
            on=key, how="left"
        )
    
        feats_230_231 = feats_230_231.select([key, "A11_PDAY4554", "A11_PDAY4553"])

    #print(feats_230_231)

#######################################################################################
#                        Feats 232-235
# ===========================================
# FEATURE FAMILY: 232–235 (Ratio of Total/Avg Paycheck Amounts)
# ===========================================

# Definition:
#   • Feature 232 → sum(0–30) / sum(31–60) → A11_PDAY4563
#   • Feature 233 → sum(0–30) / sum(61–90) → A11_PDAY4573
#   • Feature 234 → avg(0–30) / avg(31–60) → A11_PDAY4583
#   • Feature 235 → avg(0–30) / avg(61–90) → A11_PDAY4593

# Overrides:
#   • Group A → override_value
#   • Group B:
#     – 0 → if no txns in numerator window
#     – BOTH0 → if num = 0 AND den = 0
#     – DEN0  → if denominator is null or 0
#     – Else → num / den

# Notes:
#   • Rank‑agnostic: all valid ranks included (rank > 0)
#   • Uses central window masks (windows dict)
#   • Override logic applied via apply_ratio_overrides(expr, num, den, is_count_amount=True)
# ===========================================

###############################################
# GROUP A / GROUP B HANDLING FOR FEATURES 232–235
###############################################
    
    if group_type == "A":
        feats_232_235 = pl.DataFrame({
            key: [df_txn_with_ranks[0, key]],
            "A11_PDAY4563": [override_value],  # sum(0–30)/sum(31–60)
            "A11_PDAY4573": [override_value],  # sum(0–30)/sum(61–90)
            "A11_PDAY4583": [override_value],  # avg(0–30)/avg(31–60)
            "A11_PDAY4593": [override_value],  # avg(0–30)/avg(61–90)
        })
    
    else:
        feats_232_235 = df_groupB_txn.select(key).unique()
    
        # --- Helper: ratio with overrides ---
        def ratio(num_mask, den_mask, agg_type, fname_out):
            base = feats_232_235
            df_num = df_groupB_txn.filter(num_mask & (pl.col("rank") > 0))
            df_den = df_groupB_txn.filter(den_mask & (pl.col("rank") > 0))
    
            # Build correct aggregation expression
            if agg_type == "sum":
                num_expr = pl.col("txn_amount").sum().alias("num_val")
                den_expr = pl.col("txn_amount").sum().alias("den_val")
            elif agg_type == "mean":
                num_expr = pl.col("txn_amount").mean().alias("num_val")
                den_expr = pl.col("txn_amount").mean().alias("den_val")
            else:
                raise ValueError("agg_type must be 'sum' or 'mean'")
    
            num_tbl = df_num.group_by(key).agg(num_expr)
            den_tbl = df_den.group_by(key).agg(den_expr)
    
            out = base.join(num_tbl, on=key, how="left")
            out = out.join(den_tbl, on=key, how="left")
    
            # Apply ratio overrides
            out = out.with_columns(
                pl.when(pl.col("num_val").is_null())
                  .then(0)  # no txns in numerator → 0
                .otherwise(
                    apply_ratio_overrides(
                        pl.col("num_val") / pl.col("den_val"),
                        pl.col("num_val"),
                        pl.col("den_val"),
                        is_count_amount=True
                    )
                ).alias(fname_out)
            ).drop(["num_val", "den_val"])
    
            return out.select([key, fname_out])
    
        # --- Feature 232: sum(0–30)/sum(31–60) ---
        feats_232_235 = feats_232_235.join(
            ratio(windows["0_30"], windows["31_60"], "sum", "A11_PDAY4563"),
            on=key, how="left"
        )
    
        # --- Feature 233: sum(0–30)/sum(61–90) ---
        feats_232_235 = feats_232_235.join(
            ratio(windows["0_30"], windows["61_90"], "sum", "A11_PDAY4573"),
            on=key, how="left"
        )
    
        # --- Feature 234: avg(0–30)/avg(31–60) ---
        feats_232_235 = feats_232_235.join(
            ratio(windows["0_30"], windows["31_60"], "mean", "A11_PDAY4583"),
            on=key, how="left"
        )
    
        # --- Feature 235: avg(0–30)/avg(61–90) ---
        feats_232_235 = feats_232_235.join(
            ratio(windows["0_30"], windows["61_90"], "mean", "A11_PDAY4593"),
            on=key, how="left"
        )
    
        feats_232_235 = feats_232_235.select([
            key,
            "A11_PDAY4563", "A11_PDAY4573", "A11_PDAY4583", "A11_PDAY4593"
        ])

    #print(feats_232_235)
######################################################################################################################################

    # Initialize an empty list to collect per-customer feature dataframes


    feature_blocks = [
        df_demography,
        feats_10_15,
        feats_16_21,
        feats_22_27,
        feats_28_33,
        feats_34_39,
        feats_40_45,
        feats_46_63,
        feats_64_69,
        feats_70_75,
        feats_76_81,
        feats_82_87,
        feats_88_93,
        feats_94_99,
        feats_100_108,
        feats_109_111,
        feats_112_114,
        feats_115_120,
        feats_121_126,
        feats_127_132,
        feats_133_138,
        feats_139_144,
        feats_145_150,
        feats_151_156,
        feats_157_162,
        feats_163_174,
        feats_175_180,
        feats_181_198,
        feats_199_200,
        feats_201_202,
        feats_203_208,
        feats_209_210,
        feats_211_212,
        feats_213_216,
        feats_217,
        feats_218_221,
        feats_222_225,
        feats_226_227,
        feats_228_229,
        feats_230_231,
        feats_232_235
    ]

    
    # --- Combine all feature blocks into one dataframe for this customer ---
    combined_feats = feature_blocks[0]
    for fb in feature_blocks[1:]:
        combined_feats = combined_feats.join(fb, on="experian_consumer_key", how="left")

    # --- Append to master list ---
    all_customers_feats.append(combined_feats)
    end2 = time.perf_counter()
    count = count + 1
    #print(feats_181_198)
    #print(f"Feature creation for customer finished in: {end2 - start2:.4f} seconds")
    if end2-start2 > 0.1 :
        count_ping_break = count_ping_break + 1    
    
    attributes_creation_time = attributes_creation_time + (end2-start2)
    
    # if count > 0:
    #     break

    if count % 1000 == 0:
        print(count,"customers completed")
        print("Ping Break",count_ping_break, "out of", count, "times")
        print("Total Clustering Time: ",clustering_time, "seconds")
        print("Total feature creation time: ",attributes_creation_time, "seconds")
        clustering_time = 0
        attributes_creation_time = 0
    
    if count % 10000 == 0:
        final_features_df = cast_and_concat_customer_list(all_customers_feats)
        final_features_df.write_csv('C:/Users/C26779E/OneDrive - EXPERIAN SERVICES CORP/Desktop/Projects/1. Payday Attributes/Corrected_Logic/Feature_Stamping/Checkpoint_3.csv')
        print(count,"customers checkpoint saved to directory")
    
    
#--- Concatenate all customers into one master dataframe ---
# for i, df in enumerate(all_customers_feats): 
#     print(i, df.schema)

final_features_df = cast_and_concat_customer_list(all_customers_feats, how="vertical")
print("Total Clustering time: ",clustering_time, "seconds")
print("Total feature creation time: ",attributes_creation_time, "seconds")
final_features_df.write_csv("C:/Users/C26779E/OneDrive - EXPERIAN SERVICES CORP/Desktop/Projects/1. Payday Attributes/Datasets/Partitions/200k_Payday_Attributes_Stamped.csv")
#print("Ping Break ",count_ping_break, "out of", count, "times")
print(final_features_df)
#print(final_features_df[['A11_PDAY1113','A11_PDAY2113','A11_PDAY3113','A11_PDAY1123','A11_PDAY2123','A11_PDAY3123']]
    
    
    
    
    
    
    
    
    
    
    
    
    
    



