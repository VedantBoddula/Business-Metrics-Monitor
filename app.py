
import streamlit as st
import pandas as pd
from pathlib import Path

from src.preprocessing import (
    create_daily_data,
    create_region_data,
    create_product_data,
    create_category_data
)

from src.anomaly_detector import (
    detect_overall_sales_drops,
    detect_overall_sales_spikes,
    detect_category_sales_spikes,
    detect_product_sales_spikes,
    detect_profit_margin_drops,
    detect_regional_sales_drops
)

# Page configuration
st.set_page_config(
    page_title="Business Metrics Monitor",
    page_icon="📊",
    layout="wide"
)

# Dashboard styling
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Business Metrics Anomaly Monitor")
st.caption(
    "Monitor business performance, investigate anomalies, "
    "and review automated alerts."
)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Sales Analytics",
        "Anomaly Detection",
        "Alert History"
    ]
)

# Load transaction data
DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "ecommerce_business_monitoring_dataset.xlsx"
)

@st.cache_data
def load_transactions(path):
    return pd.read_excel(path, sheet_name="Transactions")

try:
    df = load_transactions(DATA_PATH)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

    df = df.dropna(subset=["Date", "Sales", "Profit", "Quantity"])

except Exception as error:
    st.error(f"Could not load transaction data: {error}")
    st.stop()

# Overview page
if page == "Overview":
    st.subheader("Business Overview")

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order_ID"].nunique()
    total_units = df["Quantity"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"₹{total_sales:,.0f}")
    col2.metric("Total Profit", f"₹{total_profit:,.0f}")
    col3.metric("Total Orders", f"{total_orders:,}")
    col4.metric("Units Sold", f"{total_units:,.0f}")

    st.divider()

    daily_sales = (
        df.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
    )

    st.subheader("Daily Sales Trend")
    st.line_chart(
        daily_sales.set_index("Date")["Sales"],
        x_label="Date",
        y_label="Sales (₹)"
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Sales by Category")
        category_sales = (
            df.groupby("Category")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(category_sales, horizontal=True)

    with right:
        st.subheader("Sales by Region")
        region_sales = (
            df.groupby("Region")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(region_sales)

# Sales Analytics page
elif page == "Sales Analytics":
    st.subheader("Sales Analytics")

    categories = ["All"] + sorted(
        df["Category"].dropna().unique().tolist()
    )
    selected_category = st.selectbox("Select Category", categories)

    filtered_df = df.copy()

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["Category"] == selected_category
        ]

    daily = (
        filtered_df.groupby("Date", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
        .sort_values("Date")
    )

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Sales", f"₹{filtered_df['Sales'].sum():,.0f}")
    metric2.metric("Profit", f"₹{filtered_df['Profit'].sum():,.0f}")
    metric3.metric("Units Sold", f"{filtered_df['Quantity'].sum():,.0f}")

    st.subheader("Sales Over Time")
    st.line_chart(daily.set_index("Date")["Sales"])

    st.subheader("Profit Over Time")
    st.line_chart(daily.set_index("Date")["Profit"])

    with st.expander("View transaction data"):
        st.dataframe(filtered_df, use_container_width=True)



# Anomaly Detection page
elif page == "Anomaly Detection":
    st.subheader("Anomaly Detection")
    st.caption(
        "Identify unusual business activity using historical sales patterns."
    )

    with st.spinner("Analyzing business data..."):
        daily_data = create_daily_data(df)
        region_daily = create_region_data(df)
        product_daily = create_product_data(df)
        category_daily = create_category_data(df)

        _, sales_drops = detect_overall_sales_drops(daily_data)
        _, sales_spikes = detect_overall_sales_spikes(daily_data)
        _, category_spikes = detect_category_sales_spikes(category_daily)
        _, product_spikes = detect_product_sales_spikes(product_daily)
        _, margin_drops = detect_profit_margin_drops(category_daily)
        _, regional_drops = detect_regional_sales_drops(region_daily)

    events = []

    def add_events(data, anomaly_type, scope_column=None):
        for _, event in data.iterrows():
            row = {
                "Anomaly Type": anomaly_type,
                "Start Date": pd.to_datetime(event["Start_Date"]),
                "End Date": pd.to_datetime(event["End_Date"]),
                "Duration (days)": int(event["Duration"]),
                "Scope": (
                    str(event[scope_column])
                    if scope_column and scope_column in event.index
                    else "Overall Business"
                )
            }

            if "Avg_Sales_Change" in event.index:
                row["Sales Change (%)"] = round(
                    event["Avg_Sales_Change"], 1
                )

            if "Avg_Quantity_Change" in event.index:
                row["Quantity Change (%)"] = round(
                    event["Avg_Quantity_Change"], 1
                )

            if "Avg_Margin_Drop_pp" in event.index:
                row["Margin Drop (pp)"] = round(
                    event["Avg_Margin_Drop_pp"], 1
                )

            events.append(row)

    add_events(sales_drops, "Overall Sales Drop")
    add_events(sales_spikes, "Overall Sales Spike")
    add_events(category_spikes, "Category Sales Spike", "Category")
    add_events(product_spikes, "Product Sales Spike", "Product_Name")
    add_events(margin_drops, "Profit Margin Drop", "Category")
    add_events(regional_drops, "Regional Sales Drop", "Region")


    
    # Assign severity using transparent, configurable rules
    def assign_severity(row):
        anomaly_type = row["Anomaly Type"]
        sales_change = row.get("Sales Change (%)")
        margin_drop = row.get("Margin Drop (pp)")

        if anomaly_type in [
            "Overall Sales Drop",
            "Regional Sales Drop"
        ] and pd.notna(sales_change):
            if sales_change <= -40:
                return "Critical"
            elif sales_change <= -30:
                return "High"
            return "Moderate"

        if anomaly_type == "Profit Margin Drop" and pd.notna(margin_drop):
            if margin_drop <= -15:
                return "Critical"
            elif margin_drop <= -8:
                return "High"
            return "Moderate"

        if pd.notna(sales_change):
            magnitude = abs(sales_change)
            if magnitude >= 200:
                return "Critical"
            elif magnitude >= 100:
                return "High"

        return "Moderate"


    if not events:
        st.success("No anomalies were detected with the current rules.")
    else:
        
        results = pd.DataFrame(events)

        results["Severity"] = results.apply(
            assign_severity, axis=1
        )

        results = results.sort_values(
            "Start Date", ascending=False
        )

        
        
        

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Detected Events", len(results))

        with col2:
            st.metric(
                "Anomaly Types",
                results["Anomaly Type"].nunique()
            )

        

        # Severity Summary
        st.markdown("### Severity Summary")
        
        critical_count = (results["Severity"] == "Critical").sum()
        high_count = (results["Severity"] == "High").sum()
        moderate_count = (results["Severity"] == "Moderate").sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔴 Critical", critical_count)
        
        with col2:
            st.metric("🟠 High", high_count)
        
        with col3:
            st.metric("🟡 Moderate", moderate_count)


        st.divider()
        
        
        

        anomaly_types = ["All"] + sorted(
            results["Anomaly Type"].unique().tolist()
        )

        selected_anomaly = st.selectbox(
            "Filter by anomaly type",
            anomaly_types
        )

        
        severity_options = ["All", "Critical", "High", "Moderate"]

        selected_severity = st.selectbox(
            "Filter by severity",
            severity_options
        )

        filtered_results = results.copy()

        if selected_severity != "All":
            filtered_results = filtered_results[
                filtered_results["Severity"] == selected_severity
            ]


        if selected_anomaly != "All":
            filtered_results = filtered_results[
                filtered_results["Anomaly Type"] == selected_anomaly
            ]

        st.caption(f"Showing {len(filtered_results)} detected event(s)")

        st.dataframe(
            filtered_results,
            use_container_width=True,
            hide_index=True
        )


        
        # Interactive anomaly investigation
        st.divider()
        st.subheader("🔎 Investigate an Anomaly")
        st.caption(
            "Select a detected event to inspect its metrics, "
            "historical baseline, and business impact."
        )

        if filtered_results.empty:
            st.info("No events available for investigation.")
        else:
            investigation_data = filtered_results.reset_index(drop=True)

            selected_index = st.selectbox(
                "Choose an event",
                options=investigation_data.index.tolist(),
                format_func=lambda i: (
                    f"{investigation_data.loc[i, 'Anomaly Type']} | "
                    f"{investigation_data.loc[i, 'Scope']} | "
                    f"{investigation_data.loc[i, 'Start Date']:%Y-%m-%d} "
                    f"to "
                    f"{investigation_data.loc[i, 'End Date']:%Y-%m-%d}"
                ),
                key="investigation_event"
            )

            event = investigation_data.loc[selected_index]

            anomaly_type = event["Anomaly Type"]
            scope = event["Scope"]
            severity = event["Severity"]
            start_date = event["Start Date"]
            end_date = event["End Date"]

            st.markdown("### Event Details")
            if severity == "Critical":
                st.error(f"🚨 Severity: {severity}")
            elif severity == "High":
                st.warning(f"⚠️ Severity: {severity}")
            else:
                st.info(f"ℹ️ Severity: {severity}")

            detail1, detail2, detail3 = st.columns(3)
            detail1.metric("Anomaly Type", anomaly_type)
            detail2.metric("Duration", f"{event['Duration (days)']} days")
            detail3.write(
                f"**Period**\n\n"
                f"{start_date:%d %b %Y} – {end_date:%d %b %Y}"
            )

            # Select the correct data and baseline for this event
            if anomaly_type in [
                "Overall Sales Drop",
                "Overall Sales Spike"
            ]:
                detail_data = daily_data[
                    (daily_data["Date"] >= start_date)
                    & (daily_data["Date"] <= end_date)
                ].copy()

                metric_column = "Sales"
                baseline_column = "Sales_4week_Avg"
                metric_label = "Sales"
                quantity_column = "Quantity"
                quantity_baseline = "Quantity_4week_Avg"

            elif anomaly_type == "Regional Sales Drop":
                detail_data = region_daily[
                    (region_daily["Region"] == scope)
                    & (region_daily["Date"] >= start_date)
                    & (region_daily["Date"] <= end_date)
                ].copy()

                metric_column = "Sales"
                baseline_column = "Same_Day_4week_Avg"
                metric_label = "Sales"
                quantity_column = None
                quantity_baseline = None

            elif anomaly_type == "Product Sales Spike":
                detail_data = product_daily[
                    (product_daily["Product_Name"] == scope)
                    & (product_daily["Date"] >= start_date)
                    & (product_daily["Date"] <= end_date)
                ].copy()

                metric_column = "Sales"
                baseline_column = "Same_Day_4week_Avg"
                metric_label = "Sales"
                quantity_column = "Quantity"
                quantity_baseline = "Quantity_4week_Avg"

            else:
                # Category sales spike or profit margin drop
                detail_data = category_daily[
                    (category_daily["Category"] == scope)
                    & (category_daily["Date"] >= start_date)
                    & (category_daily["Date"] <= end_date)
                ].copy()

                if anomaly_type == "Profit Margin Drop":
                    metric_column = "Profit_Margin_pct"
                    baseline_column = "Profit_Margin_4week_Avg"
                    metric_label = "Profit Margin (%)"
                else:
                    metric_column = "Sales"
                    baseline_column = "Same_Day_4week_Avg"
                    metric_label = "Sales"

                quantity_column = "Quantity"
                quantity_baseline = "Quantity_4week_Avg"

            if detail_data.empty:
                st.warning("No matching daily records were found for this event.")
            else:
                actual_total = detail_data[metric_column].sum()

                # Compare averages for percentage-based metrics,
                # and totals for sales/quantity metrics.
                if metric_column == "Profit_Margin_pct":
                    actual_value = detail_data[metric_column].mean()
                    baseline_value = detail_data[baseline_column].mean()
                    value_format = "{:.2f}%"
                else:
                    actual_value = detail_data[metric_column].sum()
                    baseline_value = detail_data[baseline_column].sum()
                    value_format = "₹{:,.0f}" if metric_column == "Sales" else "{:,.0f}"

                if pd.notna(baseline_value) and baseline_value != 0:
                    change_pct = (
                        (actual_value - baseline_value)
                        / abs(baseline_value)
                    ) * 100
                else:
                    change_pct = None

                st.markdown("### Actual vs Historical Baseline")

                metric1, metric2, metric3 = st.columns(3)

                metric1.metric(
                    f"Actual {metric_label}",
                    value_format.format(actual_value)
                )

                metric2.metric(
                    f"Baseline {metric_label}",
                    value_format.format(baseline_value)
                    if pd.notna(baseline_value)
                    else "Unavailable"
                )

                metric3.metric(
                    "Change vs Baseline",
                    f"{change_pct:+.1f}%"
                    if change_pct is not None
                    else "Unavailable"
                )

                # Plot the actual values against the historical baseline
                chart_columns = [metric_column, baseline_column]

                chart_data = detail_data[
                    ["Date"] + chart_columns
                ].copy()

                chart_data = chart_data.sort_values("Date")
                chart_data = chart_data.set_index("Date")

                chart_data = chart_data.rename(columns={
                    metric_column: f"Actual {metric_label}",
                    baseline_column: f"Historical Baseline ({metric_label})"
                })

                st.line_chart(
                    chart_data,
                    x_label="Date",
                    y_label=metric_label
                )

                # Show supporting business metrics
                if "Profit" in detail_data.columns:
                    total_profit = detail_data["Profit"].sum()
                    st.metric("Total Profit During Event", f"₹{total_profit:,.2f}")

                if (
                    quantity_column
                    and quantity_column in detail_data.columns
                    and quantity_baseline in detail_data.columns
                ):
                    actual_quantity = detail_data[quantity_column].sum()
                    baseline_quantity = detail_data[quantity_baseline].sum()

                    q1, q2 = st.columns(2)
                    q1.metric("Units Sold", f"{actual_quantity:,.0f}")
                    q2.metric(
                        "Baseline Units",
                        f"{baseline_quantity:,.1f}"
                    )

                # Break down overall business events by product and region
                if anomaly_type in [
                    "Overall Sales Drop",
                    "Overall Sales Spike"
                ]:
                    event_transactions = df[
                        (df["Date"] >= start_date)
                        & (df["Date"] <= end_date)
                    ]

                    left, right = st.columns(2)

                    with left:
                        st.markdown("#### Sales by Product")
                        product_breakdown = (
                            event_transactions.groupby("Product_Name")["Sales"]
                            .sum()
                            .sort_values(ascending=False)
                            .head(5)
                        )
                        st.bar_chart(product_breakdown, horizontal=True)

                    with right:
                        st.markdown("#### Sales by Region")
                        region_breakdown = (
                            event_transactions.groupby("Region")["Sales"]
                            .sum()
                            .sort_values(ascending=False)
                        )
                        st.bar_chart(region_breakdown)

                # Show the exact daily records used in the investigation
                with st.expander("View daily investigation data"):
                    st.dataframe(
                        detail_data,
                        use_container_width=True,
                        hide_index=True
                    )

                st.info(
                    "The historical baseline is a comparison reference, "
                    "not a guaranteed forecast. Review business context "
                    "before deciding whether an event requires action."
                )


        with st.expander("How does anomaly detection work?"):
            st.write(
                "The monitor compares business metrics with historical "
                "baselines and applies the detection rules defined in "
                "the anomaly detector module. Detected events are "
                "candidates for investigation, not proof of a business problem."
            )


# Alert History page

elif page == "Alert History":
    st.subheader("Alert History")

    DB_PATH = Path(__file__).parent / "alert_history.db"

    if not DB_PATH.exists():
        st.info("No alert history database found yet. Run the monitoring pipeline first.")
    else:
        try:
            import sqlite3

            with sqlite3.connect(DB_PATH) as connection:
                tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table'",
                    connection
                )["name"].tolist()

                if not tables:
                    st.info("The alert history database has no tables yet.")
                else:
                    history = pd.read_sql_query(
                        f'SELECT * FROM "{tables[0]}"',
                        connection
                    )

                    if history.empty:
                        st.info("No alerts recorded yet.")
                    else:
                        # Normalize column names for display
                        history.columns = [
                            column.replace("_", " ").title()
                            for column in history.columns
                        ]

                        st.metric("Total Recorded Alerts", len(history))

                        if "Alert Type" in history.columns:
                            alert_types = ["All"] + sorted(
                                history["Alert Type"].dropna().unique().tolist()
                            )
                            selected_type = st.selectbox(
                                "Filter by alert type",
                                alert_types
                            )

                            if selected_type != "All":
                                history = history[
                                    history["Alert Type"] == selected_type
                                ]

                        st.caption(f"Showing {len(history)} alert(s)")

                        for _, alert in history.iloc[::-1].iterrows():
                            alert_type = alert.get("Alert Type", "Alert")
                            start_date = str(alert.get("Start Date", "N/A"))[:10]
                            end_date = str(alert.get("End Date", "N/A"))[:10]
                            status = alert.get("Status", "Unknown")
                            summary = str(alert.get("Summary", "No summary available"))

                            with st.expander(
                                f"{alert_type} | {start_date} to {end_date}"
                            ):
                                st.write(f"**Status:** {status}")
                                st.write(f"**Alert ID:** {alert.get('Id', 'N/A')}")

                                st.markdown("**Business Summary**")
                                st.text(summary.replace("\\n", "\n"))

        except Exception as error:
            st.error(f"Could not read alert history: {error}")
