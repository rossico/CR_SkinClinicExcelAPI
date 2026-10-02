from fastapi import FastAPI
import pandas as pd

# -------------------------------------------------
# Create FastAPI app
# -------------------------------------------------
app = FastAPI()

# -------------------------------------------------
# Health check endpoint
# -------------------------------------------------
@app.get("/health")
def health_check():
    return {"message": "Skin Clinic Campaign API is running"}

# -------------------------------------------------
# Campaign analysis function
# -------------------------------------------------
def generate_campaign_summary():

    df = pd.read_csv("skin_clinic_campaign.csv")

    # Convert response to 1/0 so the mean gives the response rate
    df["Response_to_Campaign"] = df["Response_to_Campaign"].map({"Yes": 1, "No": 0})

    # Product usage bands: 1-4, 5-8, >8
    df["Product_Group"] = pd.cut(
        df["Unique_Products_Purchased"],
        bins=[0, 4, 8, float("inf")],
        labels=["1-4", "5-8", ">8"]
    )

    # (column to group by, name of the analysis, display order)
    analyses = [
        ("Gender", "Gender", ["Female", "Male"]),
        ("AgeGroup", "Age Group", ["<30", "30-50", ">50"]),
        ("Purchase_Last_Quarter", "Purchase in Last Quarter", ["Yes", "No"]),
        ("Product_Group", "Products Purchased (Last Year)", ["1-4", "5-8", ">8"])
    ]

    tables = []
    for column, analysis_name, order in analyses:
        rate = df.groupby(column, observed=False)["Response_to_Campaign"].mean() * 100
        rate = rate.reindex(order).round(2)

        table = pd.DataFrame({
            "Analysis": analysis_name,
            "Category": order,
            "Response_Rate_%": rate.values
        })
        tables.append(table)

    summary_df = pd.concat(tables, ignore_index=True)

    return summary_df

# -------------------------------------------------
# API endpoint for Excel / external usage
# -------------------------------------------------
@app.get("/campaign-analysis")
def campaign_analysis():
    try:
        df = generate_campaign_summary()

        # Return JSON
        return df.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
