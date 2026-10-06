import pandas as pd


def get_field_insights(
    kharif_df: pd.DataFrame,
    state: str,
    district: str
):
    # ========================================================
    # DISTRICT DATA
    # ========================================================

    district_data = kharif_df[
        (kharif_df["State_Name"] == state)
        & (kharif_df["District_Name"] == district)
    ].copy()

    if district_data.empty:
        raise ValueError(
            "No historical data found for this district."
        )

    district_data["Area"] = pd.to_numeric(
        district_data["Area"],
        errors="coerce"
    )

    district_data["Production"] = pd.to_numeric(
        district_data["Production"],
        errors="coerce"
    )

    district_data = district_data[
        district_data["Area"].notna()
        & district_data["Production"].notna()
        & (district_data["Area"] > 0)
        & (district_data["Production"] >= 0)
    ].copy()

    if district_data.empty:
        raise ValueError(
            "No valid production records found for this district."
        )

    # ========================================================
    # DISTRICT YEAR-WISE DATA
    # ========================================================

    district_year = (
        district_data
        .groupby("Crop_Year", as_index=False)
        .agg(
            Area=("Area", "sum"),
            Production=("Production", "sum")
        )
    )

    district_year["Yield"] = (
        district_year["Production"]
        / district_year["Area"]
    )

    district_year = (
        district_year
        .sort_values("Crop_Year")
        .reset_index(drop=True)
    )

    # ========================================================
    # DISTRICT SUMMARY
    # ========================================================

    average_yield = float(
        district_year["Yield"].mean()
    )

    median_yield = float(
        district_year["Yield"].median()
    )

    best_row = district_year.loc[
        district_year["Yield"].idxmax()
    ]

    worst_row = district_year.loc[
        district_year["Yield"].idxmin()
    ]

    latest_row = district_year.iloc[-1]

    latest_year = int(
        latest_row["Crop_Year"]
    )

    # ========================================================
    # STATE DATA
    # ========================================================

    state_data = kharif_df[
        kharif_df["State_Name"] == state
    ].copy()

    state_data["Area"] = pd.to_numeric(
        state_data["Area"],
        errors="coerce"
    )

    state_data["Production"] = pd.to_numeric(
        state_data["Production"],
        errors="coerce"
    )

    state_data = state_data[
        state_data["Area"].notna()
        & state_data["Production"].notna()
        & (state_data["Area"] > 0)
        & (state_data["Production"] >= 0)
    ].copy()

    state_year = (
        state_data
        .groupby("Crop_Year", as_index=False)
        .agg(
            Area=("Area", "sum"),
            Production=("Production", "sum")
        )
    )

    state_year["Yield"] = (
        state_year["Production"]
        / state_year["Area"]
    )

    state_year = (
        state_year
        .sort_values("Crop_Year")
        .reset_index(drop=True)
    )

    # ========================================================
    # DISTRICT VS STATE
    # ========================================================

    state_latest = state_year[
        state_year["Crop_Year"] == latest_year
    ]

    state_yield_latest = None
    difference_percent = None

    if not state_latest.empty:
        state_yield_latest = float(
            state_latest.iloc[0]["Yield"]
        )

        district_latest_yield = float(
            latest_row["Yield"]
        )

        if state_yield_latest != 0:
            difference_percent = (
                (
                    district_latest_yield
                    - state_yield_latest
                )
                / state_yield_latest
            ) * 100

    # ========================================================
    # DISTRICT TREND
    # ========================================================

    district_trend = []

    for _, row in district_year.iterrows():
        district_trend.append(
            {
                "year": int(row["Crop_Year"]),
                "area_hectares": round(
                    float(row["Area"]),
                    2
                ),
                "production_tonnes": round(
                    float(row["Production"]),
                    2
                ),
                "yield_tonnes_per_hectare": round(
                    float(row["Yield"]),
                    3
                )
            }
        )

    # ========================================================
    # STATE TREND
    # ========================================================

    state_trend = []

    for _, row in state_year.iterrows():
        state_trend.append(
            {
                "year": int(row["Crop_Year"]),
                "yield_tonnes_per_hectare": round(
                    float(row["Yield"]),
                    3
                )
            }
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "location": {
            "state": state,
            "district": district
        },

        "crop": "Rice",
        "season": "Kharif",

        "historical_period": {
            "start_year": int(
                district_year["Crop_Year"].min()
            ),
            "end_year": int(
                district_year["Crop_Year"].max()
            ),
            "years_available": int(
                len(district_year)
            )
        },

        "summary": {
            "average_yield": round(
                average_yield,
                3
            ),

            "median_yield": round(
                median_yield,
                3
            ),

            "best_year": {
                "year": int(
                    best_row["Crop_Year"]
                ),
                "yield": round(
                    float(best_row["Yield"]),
                    3
                )
            },

            "worst_year": {
                "year": int(
                    worst_row["Crop_Year"]
                ),
                "yield": round(
                    float(worst_row["Yield"]),
                    3
                )
            },

            "latest_record": {
                "year": latest_year,
                "yield": round(
                    float(latest_row["Yield"]),
                    3
                ),
                "area_hectares": round(
                    float(latest_row["Area"]),
                    2
                ),
                "production_tonnes": round(
                    float(latest_row["Production"]),
                    2
                )
            }
        },

        "state_comparison": {
            "year": latest_year,

            "district_yield": round(
                float(latest_row["Yield"]),
                3
            ),

            "state_yield": (
                round(
                    state_yield_latest,
                    3
                )
                if state_yield_latest is not None
                else None
            ),

            "difference_percent": (
                round(
                    difference_percent,
                    2
                )
                if difference_percent is not None
                else None
            )
        },

        "district_trend": district_trend,
        "state_trend": state_trend,

        "note": (
            "Historical district-level analysis "
            "based on available Kharif rice "
            "area and production records."
        )
    }
