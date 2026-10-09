import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

# Load .env if present
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

def test_send_email(to_email=None):
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user)
    
    if not (smtp_host and smtp_user and smtp_pass):
        print("\n❌ SMTP Credentials Not Configured in .env file!")
        print("Please configure SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD in .env to send real emails.")
        print("\nQuick Example for Gmail:")
        print("SMTP_HOST=smtp.gmail.com")
        print("SMTP_PORT=587")
        print("SMTP_USERNAME=yourname@gmail.com")
        print("SMTP_PASSWORD=your_16_digit_app_password")
        print("SMTP_FROM=PowerPredict AI <yourname@gmail.com>")
        return False
        
    recipient = to_email or smtp_user
    print(f"\n[*] Connecting to {smtp_host}:{smtp_port} via STARTTLS...")
    try:
        msg = EmailMessage()
        msg["Subject"] = "Test Email: PowerPredict AI Real Verification System"
        msg["From"] = smtp_from
        msg["To"] = recipient
        msg.set_content(f"""Hi,

This is a real test email from your PowerPredict AI platform.
Your real email delivery system is working successfully!

Regards,
Team PowerPredict AI
""")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            
        print(f"✅ SUCCESS! Real email successfully delivered to: {recipient}")
        print("Check your inbox (or Spam/Promotions folder if testing for the first time).")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    test_send_email(target)
