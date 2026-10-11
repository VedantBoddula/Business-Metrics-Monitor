
from datetime import date
from src.alert_history import send_alert_once

result = send_alert_once(
    alert_key="integration_test_20261011_01",
    alert_type="Integration Test",
    start_date=date.today(),
    end_date=date.today(),
    subject="Business Monitor - Integration Test",
    summary="Testing email delivery through send_alert_once and alert history."
)

print("Integration test result:", result)
