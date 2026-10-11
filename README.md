# 📊 Business Metrics Monitor — Anomaly Detection & Alert System

An automated business monitoring system built with Python that analyzes e-commerce transaction data, detects unusual changes in sales and business performance, generates understandable anomaly summaries, and sends email alerts. It also maintains a persistent history of alerts using SQLite.

## 🚀 Project Overview

Businesses need to identify unexpected sales drops, unusual sales spikes, declining profit margins, and regional performance changes quickly.

The Business Metrics Monitor automates this process by analyzing historical transaction data, comparing daily performance against historical baselines, detecting potential anomalies, and presenting the findings through an interactive Streamlit dashboard.

## ✨ Key Features

- **Automated Anomaly Detection:** Detects unusual changes in overall sales, category sales, product sales, profit margins, and regional sales.
- **Six Detection Methods:** Identifies overall sales drops, overall sales spikes, category sales spikes, product sales spikes, profit margin drops, and regional sales drops.
- **Historical Baselines:** Compares business metrics with historical patterns to identify significant deviations.
- **Interactive Dashboard:** Explores business performance using charts, filters, tables, and investigation panels.
- **Business Impact Analysis:** Analyzes revenue, profit, orders, and performance across product categories and regions.
- **Automated Email Alerts:** Sends email notifications for selected detected anomalies through Gmail SMTP.
- **Persistent Alert History:** Stores alert records and their statuses in an SQLite database.
- **Duplicate Alert Prevention:** Prevents the same alert from being sent repeatedly.
- **Anomaly Investigation:** Provides event details and supporting business metrics to help investigate unusual patterns.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application and processing |
| Pandas & NumPy | Data manipulation and numerical operations |
| Scikit-learn | Machine learning and data analysis utilities |
| Streamlit | Interactive dashboard |
| Plotly | Interactive visualizations |
| SQLite | Persistent alert history |
| Matplotlib & Seaborn | Exploratory data analysis and visualization |
| OpenPyXL | Excel data handling |
| SMTP & Gmail | Email notifications |
| python-dotenv | Environment variable management |

## 📁 Project Structure

```text
DS-Proj-3/
├── data/
│   └── ecommerce_business_monitoring_dataset.xlsx
├── src/
│   ├── __init__.py
│   ├── alert_history.py
│   ├── anomaly_detector.py
│   ├── data_loader.py
│   ├── email_alert.py
│   ├── explainer.py
│   ├── preprocessing.py
│   └── summary_generator.py
├── app.py
├── main.py
├── evaluate_detector.py
├── test_email.py
├── test_alert_integration.py
├── EDA.ipynb
├── .env.example
├── .gitignore
└── README.md
```

*Note: `alert_history.db` is generated locally and is excluded from version control. The `.env` file containing credentials must never be committed.*

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/DS-Proj-3.git
cd DS-Proj-3
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the libraries used by the project:

```bash
pip install pandas numpy scikit-learn streamlit plotly matplotlib seaborn openpyxl python-dotenv
```

### 4. Configure email notifications (optional)

Create a `.env` file in the project root:

```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
RECEIVER_EMAIL=recipient_email@gmail.com
```

Use a Gmail App Password rather than your regular Gmail password. Keep `.env` private and never commit it to GitHub.

If email credentials are not configured, email notifications may not work. Configure and test them before relying on automated alerts.

### 5. Run the monitoring pipeline

```bash
python main.py
```

This executes the data processing, anomaly detection, alert generation, and alert-history workflow configured in the main script.

### 6. Launch the Streamlit dashboard

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal to explore the dashboard.

## 📈 Dashboard Sections

### Overview
Displays key business metrics, daily sales trends, and category and regional performance.

### Sales Analytics
Explores sales and profit trends, with category filters and transaction-level data.

### Anomaly Detection
Displays detected events across six anomaly types, with filters for anomaly type and severity and tools for investigating individual events.

### Business Impact
Examines revenue, profit, order volume, and performance by category and region.

### Alert History
Displays recorded alerts, their time periods, summaries, and stored statuses.

## 🔍 Anomaly Detection Methods

| Anomaly Type | Purpose |
|---|---|
| Overall Sales Drop | Identifies unusual declines in overall sales |
| Overall Sales Spike | Identifies unusual increases in overall sales |
| Category Sales Spike | Detects unusual sales increases within categories |
| Product Sales Spike | Detects unusual sales increases for individual products |
| Profit Margin Drop | Identifies declining category-level profit margins |
| Regional Sales Drop | Detects unusual sales declines across regions |

The system uses historical comparisons and detection rules to identify potential anomalies. Detected events are indicators for investigation, not proof of fraud, business failure, or a specific cause.

## 🗄️ Alert History & Email Notifications

The application uses SQLite to maintain alert records, including alert type, date range, summary, status, and creation time.

Before sending an alert, the system checks whether its alert key already exists. This helps prevent duplicate notifications when the monitoring pipeline runs repeatedly.

Email delivery and alert-history integration have been tested successfully in the development environment.

## 🧪 Testing

Test the email functionality:

```bash
python test_email.py
```

Test email delivery through the alert-history integration:

```bash
python test_alert_integration.py
```

**Important:** The integration test sends a real email and records a test alert in the local SQLite database. Run it only when you intend to perform that test.

Evaluate the anomaly detection logic:

```bash
python evaluate_detector.py
```

## 🔒 Security Notes

- Never commit `.env` or email credentials.
- Keep generated database files and Python cache files out of version control.
- Do not include private data or credentials in screenshots.
- Use environment variables for sensitive configuration.

## 🔮 Future Improvements

- Schedule automated monitoring at regular intervals.
- Add configurable anomaly thresholds.
- Expand automated alert coverage to more detected events.
- Add more advanced anomaly detection algorithms.
- Improve anomaly evaluation using reliable labeled data.
- Support additional data sources and configurable business metrics.

## 👨‍💻 Author

**Vedant Boddula**

Information Technology Engineering Student | Aspiring Data Scientist

GitHub: [VedantBoddula](https://github.com/VedantBoddula)

---

*Built as a data science project to explore business analytics, anomaly detection, automated notifications, and interactive data visualization.*