import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_triage_email(
    recipient,
    ticket_id,
    issue,
    category,
    subcategory,
    resolution,
    confidence,
    priority,
    incident_id,
    incident_name,
    similarity,
    previous_resolution,
):

    html = f"""
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Triage Agent</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f7fb; font-family:Arial, Helvetica, sans-serif; color:#172033;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; background-color:#f4f7fb; margin:0; padding:24px 12px;">
    <tr>
      <td align="center" style="padding:0;">
        <table role="presentation" width="680" cellpadding="0" cellspacing="0" border="0" style="width:100%; max-width:680px; background-color:#ffffff; border-radius:18px; overflow:hidden; box-shadow:0 10px 28px rgba(16, 24, 40, 0.12);">
          <tr>
            <td style="padding:0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; background-color:#0f5bd8; background-image:linear-gradient(135deg,#0052cc 0%,#0078d4 48%,#00a3ff 100%);">
                <tr>
                  <td style="padding:34px 34px 30px 34px;">
                    <div style="font-size:28px; line-height:34px; font-weight:700; letter-spacing:0.4px; color:#ffffff;">AI TRIAGE AGENT</div>
                    <div style="font-size:15px; line-height:22px; color:#dbeafe; margin-top:6px;">Intelligent IT Support Automation</div>
                    <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:24px;">
                      <tr>
                        <td style="width:34px; height:34px; border-radius:17px; background-color:#22c55e; color:#ffffff; font-size:20px; line-height:34px; text-align:center; font-weight:700;">✓</td>
                        <td style="padding-left:12px; font-size:18px; line-height:24px; color:#ffffff; font-weight:700;">Ticket Successfully Processed</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        <tr>
            <td style="padding:28px 24px 8px 24px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;">
                <tr>
                <td style="padding:0 0 18px 0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; background-color:#ffffff; border:1px solid #e5ebf3; border-radius:14px; box-shadow:0 6px 18px rgba(16,24,40,0.07);">
                    <tr>
                        <td style="padding:22px 24px;">
                        <div style="font-size:18px; line-height:24px; font-weight:700; color:#172033; margin-bottom:16px;">Ticket Summary</div>
                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;">
                            <tr>
                            <td style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:13px; line-height:18px; color:#64748b;">Ticket ID</td>
                            <td align="right" style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:14px; line-height:18px; color:#172033; font-weight:700;">{ticket_id}</td>
                            </tr>
                            <tr>
                            <td style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:13px; line-height:18px; color:#64748b;">Status</td>
                            <td align="right" style="padding:10px 0; border-bottom:1px solid #eef2f7;">
                                <span style="display:inline-block; padding:6px 12px; border-radius:999px; background-color:#dcfce7; color:#166534; font-size:12px; line-height:14px; font-weight:700;">Processed</span>
                            </td>
                            </tr>
                            <tr>
                            <td style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:13px; line-height:18px; color:#64748b;">Priority</td>
                            <td align="right" style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:14px; line-height:18px; color:#172033; font-weight:700;">{priority}</td>
                            </tr>
                            <tr>
                            <td style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:13px; line-height:18px; color:#64748b;">Confidence Score</td>
                            <td align="right" style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:14px; line-height:18px; color:#0052cc; font-weight:700;">{confidence}</td>
                            </tr>
                            <tr>
                            <td style="padding:10px 0 0 0; font-size:13px; line-height:18px; color:#64748b;">Generated Date</td>
                            <td align="right" style="padding:10px 0 0 0; font-size:14px; line-height:18px; color:#172033; font-weight:700;">{generated_date}</td>
                            </tr>
                        </table>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>

                <tr>
                <td style="padding:0 0 18px 0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; background-color:#ffffff; border:1px solid #e5ebf3; border-radius:14px; box-shadow:0 6px 18px rgba(16,24,40,0.07);">
                    <tr>
                        <td style="padding:22px 24px;">
                        <div style="font-size:18px; line-height:24px; font-weight:700; color:#172033; margin-bottom:16px;">Issue Details</div>
                        <div style="font-size:13px; line-height:18px; color:#64748b; margin-bottom:6px;">Issue Description</div>
                        <div style="font-size:15px; line-height:23px; color:#172033; margin-bottom:18px;">{issue}</div>
                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;">
                            <tr>
                            <td style="padding:12px 14px; background-color:#f8fafc; border-radius:10px; border:1px solid #eef2f7;">
                                <div style="font-size:12px; line-height:16px; color:#64748b;">Category</div>
                                <div style="font-size:15px; line-height:22px; color:#172033; font-weight:700; margin-top:4px;">{category}</div>
                            </td>
                            <td style="width:14px;"></td>
                            <td style="padding:12px 14px; background-color:#f8fafc; border-radius:10px; border:1px solid #eef2f7;">
                                <div style="font-size:12px; line-height:16px; color:#64748b;">Subcategory</div>
                                <div style="font-size:15px; line-height:22px; color:#172033; font-weight:700; margin-top:4px;">{subcategory}</div>
                            </td>
                            </tr>
                        </table>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>

                <tr>
                <td style="padding:0 0 18px 0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; background-color:#ffffff; border:1px solid #d7e7ff; border-radius:14px; box-shadow:0 8px 24px rgba(0,82,204,0.14);">
                    <tr>
                        <td style="padding:24px;">
                        <div style="font-size:19px; line-height:25px; font-weight:700; color:#172033; margin-bottom:16px;">AI Recommended Resolution</div>
                        <div style="background-color:#f0f7ff; border-left:5px solid #0078d4; border-radius:12px; padding:18px 18px 18px 20px; font-size:16px; line-height:25px; color:#102a43; font-weight:600;">{resolution}</div>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>

                <tr>
                <td style="padding:0 0 18px 0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; background-color:#ffffff; border:1px solid #e5ebf3; border-radius:14px; box-shadow:0 6px 18px rgba(16,24,40,0.07);">
                    <tr>
                        <td style="padding:22px 24px;">
                        <div style="font-size:18px; line-height:24px; font-weight:700; color:#172033; margin-bottom:16px;">Similar Historical Incident</div>
                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;">
                            <tr>
                            <td style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:13px; line-height:18px; color:#64748b;">Incident ID</td>
                            <td align="right" style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:14px; line-height:18px; color:#172033; font-weight:700;">{incident_id}</td>
                            </tr>
                            <tr>
                            <td style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:13px; line-height:18px; color:#64748b;">Issue Name</td>
                            <td align="right" style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:14px; line-height:18px; color:#172033; font-weight:700;">{incident_name}</td>
                            </tr>
                            <tr>
                            <td style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:13px; line-height:18px; color:#64748b;">Similarity Score</td>
                            <td align="right" style="padding:10px 0; border-bottom:1px solid #eef2f7; font-size:14px; line-height:18px; color:#0052cc; font-weight:700;">{similarity}</td>
                            </tr>
                        </table>
                        <div style="font-size:13px; line-height:18px; color:#64748b; margin-top:16px; margin-bottom:6px;">Previous Resolution</div>
                        <div style="font-size:15px; line-height:23px; color:#172033; background-color:#f8fafc; border:1px solid #eef2f7; border-radius:10px; padding:14px;">{previous_resolution}</div>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>

                <tr>
                <td style="padding:0 0 18px 0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; background-color:#ffffff; border:1px solid #e5ebf3; border-radius:14px; box-shadow:0 6px 18px rgba(16,24,40,0.07);">
                    <tr>
                        <td style="padding:22px 24px;">
                        <div style="font-size:18px; line-height:24px; font-weight:700; color:#172033; margin-bottom:16px;">Technology Stack</div>
                        <span style="display:inline-block; padding:8px 12px; margin:0 8px 8px 0; border-radius:999px; background-color:#eef6ff; color:#0052cc; font-size:12px; line-height:14px; font-weight:700;">LangGraph</span>
                        <span style="display:inline-block; padding:8px 12px; margin:0 8px 8px 0; border-radius:999px; background-color:#eef6ff; color:#0052cc; font-size:12px; line-height:14px; font-weight:700;">Gemini AI</span>
                        <span style="display:inline-block; padding:8px 12px; margin:0 8px 8px 0; border-radius:999px; background-color:#eef6ff; color:#0052cc; font-size:12px; line-height:14px; font-weight:700;">RAG</span>
                        <span style="display:inline-block; padding:8px 12px; margin:0 8px 8px 0; border-radius:999px; background-color:#eef6ff; color:#0052cc; font-size:12px; line-height:14px; font-weight:700;">Jira</span>
                        <span style="display:inline-block; padding:8px 12px; margin:0 8px 8px 0; border-radius:999px; background-color:#eef6ff; color:#0052cc; font-size:12px; line-height:14px; font-weight:700;">ServiceNow</span>
                        <span style="display:inline-block; padding:8px 12px; margin:0 8px 8px 0; border-radius:999px; background-color:#eef6ff; color:#0052cc; font-size:12px; line-height:14px; font-weight:700;">PostgreSQL</span>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <tr>
            <td style="padding:8px 32px 34px 32px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; border-top:1px solid #e5ebf3;">
                <tr>
                <td align="center" style="padding-top:22px;">
                    <div style="font-size:13px; line-height:20px; color:#64748b;">This recommendation was generated automatically by the AI Triage Agent using historical incidents and Large Language Models.</div>
                    <div style="font-size:13px; line-height:20px; color:#64748b; margin-top:8px;">Please do not reply to this automated email.</div>
                    <div style="font-size:12px; line-height:18px; color:#94a3b8; margin-top:18px;">© AI Triage Agent</div>
                </td>
                </tr>
            </table>
            </td>
        </tr>
        </table>
    </td>
    </tr>
    </table>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")

    msg["Subject"] = f"✅ AI Triage Report | Ticket {ticket_id}"
    msg["From"] = os.getenv("SMTP_EMAIL")
    msg["To"] = recipient

    msg.attach(
    MIMEText(html, "html")
    )

    try:

        server = smtplib.SMTP(
            os.getenv("SMTP_SERVER"),
            int(os.getenv("SMTP_PORT")),
        )

        server.starttls()

        server.login(
            os.getenv("SMTP_EMAIL"),
            os.getenv("SMTP_PASSWORD"),
        )

        server.send_message(msg)

        server.quit()

        print(
            f"Email sent successfully to {recipient}"
        )

    except Exception as e:

        print(
            f"Failed to send email: {e}"
        )