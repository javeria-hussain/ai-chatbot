from app.schemas.notification import NotificationPayload


def _row(label: str, value: str | None) -> str:
    display = value if value else "Not provided"
    return f"""
    <tr>
      <td style="padding:6px 12px;font-weight:bold;color:#333;white-space:nowrap;">{label}</td>
      <td style="padding:6px 12px;color:#333;">{display}</td>
    </tr>"""


def render_lead_notification(payload: NotificationPayload) -> tuple[str, str]:
    subject = f"New Website Lead: {payload.name or 'Unnamed visitor'}"

    rows = "".join(
        [
            _row("Name", payload.name),
            _row("Email", payload.email),
            _row("Contact Number", payload.contact_number),
            _row("Company", payload.company),
            _row("Service Interest", payload.service_interest),
            _row("Project Summary", payload.project_summary),
            _row("Timeline / Budget", payload.timeline_budget),
            _row("Source Page", payload.source_page),
            _row("Latest Question", payload.user_question),
            _row("Timestamp (UTC)", payload.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
        ]
    )

    conversation_html = payload.conversation_summary.replace("\n", "<br>")

    html_body = f"""
    <html>
      <body style="font-family:Arial,sans-serif;">
        <h2 style="color:#0b3d91;">New Lead from MoinSystems AI Website</h2>
        <table style="border-collapse:collapse;">{rows}</table>
        <h3 style="margin-top:24px;">Conversation Summary</h3>
        <div style="background:#f5f5f5;padding:12px;border-radius:6px;">
          {conversation_html}
        </div>
      </body>
    </html>"""

    return subject, html_body
