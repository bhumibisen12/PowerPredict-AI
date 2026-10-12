"""
PowerPredict AI - Enterprise Authentication & Verification Service
Implements Complete User Registration, 24-Hour Cryptographic Email Verification,
Resend Rate-Limiting, SMTP Dispatcher (Resend/SendGrid/SES), and Admin Notifications.
"""

import os
import sqlite3
import hashlib
import secrets
import smtplib
from email.message import EmailMessage
from email.header import Header
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from backend.config import BASE_DIR

AUTH_DB_PATH = BASE_DIR / "sample_data" / "powerpredict_auth.db"

# Environment Variables for SMTP & Administration
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "PowerPredict AI <no-reply@powerpredict.ai>")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@powerpredict.ai")
site_url_env = os.environ.get("SITE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("RAILWAY_STATIC_URL") or "http://localhost:8000"
if site_url_env and not site_url_env.startswith("http://") and not site_url_env.startswith("https://"):
    SITE_URL = f"https://{site_url_env}"
else:
    SITE_URL = site_url_env


def get_db_connection():
    os.makedirs(AUTH_DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        organization TEXT NOT NULL,
        role TEXT NOT NULL,
        is_verified INTEGER DEFAULT 0,
        verification_token TEXT,
        token_expiry TEXT,
        created_at TEXT,
        verified_at TEXT,
        last_resend_at TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        recipient TEXT NOT NULL,
        subject TEXT NOT NULL,
        content TEXT NOT NULL,
        dispatched_at TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    conn.commit()

    # Pre-seed verified enterprise demo roles if not present
    seed_users = [
        ("Dr. Arvind Sharma", "director@powerpredict.ai", "Director@2026", "Ministry of Power / CEA", "Project Director"),
        ("Er. Priya Patel", "discom@powerpredict.ai", "Discom@2026", "State Electricity Board", "State Power Board"),
        ("Col. Rajesh Varma", "epc@powerpredict.ai", "Epc@2026", "L&T Infrastructure Projects", "Lead EPC Contractor"),
        ("Smt. Sunita Rao", "auditor@powerpredict.ai", "Auditor@2026", "Central Electricity Authority", "Regulatory Auditor")
    ]
    for name, email, pwd, org, role in seed_users:
        c.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
        if not c.fetchone():
            salt = secrets.token_hex(16)
            pwd_hash = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
            now_iso = datetime.now(timezone.utc).isoformat()
            c.execute("""
                INSERT INTO users (full_name, email, password_hash, salt, organization, role, is_verified, created_at, verified_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (name, email.lower(), pwd_hash, salt, org, role, now_iso, now_iso))
    conn.commit()
    conn.close()

# Initialize DB on module import
init_auth_db()

def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return pwd_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    calc_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(calc_hash, stored_hash)

def log_email_dispatch(event_type: str, recipient: str, subject: str, content: str, status: str = "DELIVERED"):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO audit_logs (event_type, recipient, subject, content, dispatched_at, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (event_type, recipient, subject, content, datetime.now(timezone.utc).isoformat(), status))
    conn.commit()
    conn.close()

def send_system_email(to_email: str, subject: str, text_content: str, html_content: Optional[str] = None) -> bool:
    """
    Dispatches real email via Resend API or SMTP if configured.
    Always logs to audit_logs and console for flawless dev & production visibility.
    """
    resend_key = os.environ.get("RESEND_API_KEY", "") or (SMTP_PASSWORD if SMTP_PASSWORD.startswith("re_") else "")
    from_addr = os.environ.get("SMTP_FROM", "PowerPredict AI <onboarding@resend.dev>")

    # Priority 1: High-Speed Resend HTTPS API (Delivers Real Emails to User Inboxes)
    if resend_key:
        try:
            import requests
            payload = {
                "from": from_addr,
                "to": [to_email],
                "subject": subject,
                "text": text_content,
            }
            if html_content:
                payload["html"] = html_content

            res = requests.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "PowerPredict-AI/2.1"
                },
                timeout=12
            )
            if res.status_code in [200, 201]:
                print(f"[RESEND_SUCCESS] Real email delivered to {to_email}! Response: {res.text}")
                log_email_dispatch("RESEND_API_SENT", to_email, subject, text_content, "DELIVERED")
                return True
            else:
                print(f"[RESEND_API_ERROR] Status {res.status_code}: {res.text}")
                log_email_dispatch("RESEND_ERROR", to_email, subject, f"Error {res.status_code}: {res.text}", "FAILED")
        except Exception as e:
            print(f"[RESEND_EXCEPTION] {e}")

    # Priority 2: Standard SMTP Fallback
    if SMTP_HOST and SMTP_USERNAME and SMTP_PASSWORD:
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = from_addr
            msg["To"] = to_email
            msg.set_content(text_content)
            if html_content:
                msg.add_alternative(html_content, subtype="html")

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            print(f"[SMTP_SUCCESS] Real email dispatched via SMTP to {to_email}")
            log_email_dispatch("SMTP_SENT", to_email, subject, text_content, "DELIVERED")
            return True
        except Exception as e:
            print(f"[AUTH_SMTP_WARNING] Failed to send SMTP message to {to_email}: {e}")
            log_email_dispatch("SMTP_ERROR", to_email, subject, f"Error: {e}\n\n{text_content}", "FAILED")

    # Priority 3: Local Simulation Log
    print("=" * 60)
    print(f"[EMAIL SIMULATION] To: {to_email} | Subject: {subject}")
    print(text_content)
    print("=" * 60)
    log_email_dispatch("LOCAL_DEV_LOG", to_email, subject, text_content, "SIMULATED_LOCAL")
    return True


def send_admin_signup_notification(user_info: Dict[str, Any], status: str = "Verification pending"):
    """
    Notifies Admin/Team about a new registration.
    """
    now_str = datetime.now().strftime("%d %B %Y, %I:%M %p")
    subject = "New PowerPredict AI Signup"
    body = f"""New user registered:
Name: {user_info.get('full_name')}
Email: {user_info.get('email')}
Organization: {user_info.get('organization')}
Role: {user_info.get('role')}
Signup time: {now_str}
Email status: {status}
"""
    send_system_email(ADMIN_EMAIL, subject, body)

def send_admin_verified_notification(user_info: Dict[str, Any]):
    """
    Notifies Admin/Team when an organization completes email verification.
    """
    subject = "New verified organization joined"
    body = f"""New verified organization joined:
Name: {user_info.get('full_name')}
Email: {user_info.get('email')}
Organization: {user_info.get('organization')}
Role: {user_info.get('role')}
"""
    send_system_email(ADMIN_EMAIL, subject, body)

def send_user_verification_email(user_info: Dict[str, Any], token: str, site_url: str = SITE_URL):
    """
    Sends the 24-hour verification link to the newly registered user.
    """
    verify_url = f"{site_url}/#verify?token={token}"
    subject = "Welcome to PowerPredict AI - Verify Your Email"
    body = f"""Hi {user_info.get('full_name')},

Thank you for signing up for PowerPredict AI.

Your account has been created successfully. Please verify your email address by clicking the button below:

[Verify My Email]
{verify_url}

After verification, you can log in and access your dashboard.

If you did not create this account, please ignore this email.

Regards,
Team PowerPredict AI
"""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #ffffff;">
        <h2 style="color: #0f172a; margin-bottom: 8px;">PowerPredict <span style="color: #0284c7;">AI</span></h2>
        <p style="color: #334155; font-size: 15px;">Hi {user_info.get('full_name')},</p>
        <p style="color: #334155; font-size: 15px;">Thank you for signing up for PowerPredict AI.</p>
        <p style="color: #334155; font-size: 15px;">Your account has been created successfully. Please verify your email address by clicking the button below:</p>
        <div style="margin: 24px 0;">
            <a href="{verify_url}" style="background-color: #0284c7; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Verify My Email</a>
        </div>
        <p style="color: #64748b; font-size: 13px;">Or copy and paste this link into your browser:<br><a href="{verify_url}" style="color: #0284c7;">{verify_url}</a></p>
        <p style="color: #64748b; font-size: 13px;">After verification, you can log in and access your dashboard.</p>
        <p style="color: #94a3b8; font-size: 12px;">If you did not create this account, please ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="color: #94a3b8; font-size: 12px;">Regards,<br>Team PowerPredict AI</p>
    </div>
    """
    send_system_email(user_info.get("email"), subject, body, html)
    return verify_url

def send_user_welcome_email(user_info: Dict[str, Any], site_url: str = SITE_URL):
    """
    Sends the welcome email after successful email confirmation.
    """
    dashboard_url = f"{site_url}/#dashboard"
    subject = "Your PowerPredict AI account is verified"
    body = f"""Hi {user_info.get('full_name')},

Your email has been successfully verified. You can now log in to PowerPredict AI and create or monitor your projects.

[Go to Dashboard]
{dashboard_url}

Regards,
Team PowerPredict AI
"""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #0f172a; margin-bottom: 8px;">PowerPredict <span style="color: #0284c7;">AI</span></h2>
        <p style="color: #334155; font-size: 15px;">Hi {user_info.get('full_name')},</p>
        <p style="color: #334155; font-size: 15px;">Your email has been successfully verified. You can now log in to PowerPredict AI and create or monitor your projects.</p>
        <div style="margin: 24px 0;">
            <a href="{dashboard_url}" style="background-color: #10b981; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Go to Dashboard</a>
        </div>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="color: #94a3b8; font-size: 12px;">Regards,<br>Team PowerPredict AI</p>
    </div>
    """
    send_system_email(user_info.get("email"), subject, body, html)

class AuthService:
    """Manages User Identity, 24h Verification Lifecycle, and Authentication Security."""

    @staticmethod
    def register_user(full_name: str, email: str, password: str, organization: str, role: str, site_url: str = SITE_URL) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        conn = get_db_connection()
        c = conn.cursor()

        c.execute("SELECT id, is_verified FROM users WHERE email = ?", (email_clean,))
        existing = c.fetchone()
        if existing:
            if existing["is_verified"]:
                conn.close()
                return {
                    "success": False,
                    "error": "Email is already registered. Please sign in.",
                    "code": "EMAIL_ALREADY_REGISTERED"
                }
            else:
                # Refresh existing unverified account with updated credentials & new 24h token
                pwd_hash, salt = hash_password(password)
                token = secrets.token_urlsafe(32)
                now = datetime.now(timezone.utc)
                expiry = (now + timedelta(hours=24)).isoformat()
                now_iso = now.isoformat()

                c.execute("""
                    UPDATE users
                    SET full_name = ?, password_hash = ?, salt = ?, organization = ?, role = ?, verification_token = ?, token_expiry = ?, last_resend_at = ?
                    WHERE id = ?
                """, (full_name.strip(), pwd_hash, salt, organization.strip(), role.strip(), token, expiry, now_iso, existing["id"]))
                conn.commit()
                conn.close()

                user_info = {
                    "id": existing["id"],
                    "full_name": full_name.strip(),
                    "email": email_clean,
                    "organization": organization.strip(),
                    "role": role.strip()
                }

                verify_url = send_user_verification_email(user_info, token, site_url)
                send_admin_signup_notification(user_info, status="Verification pending")

                return {
                    "success": True,
                    "message": "Account created. Please check your email and verify your account.",
                    "email": email_clean,
                    "verification_link": verify_url,
                    "expires_in_hours": 24
                }


        # Generate cryptographic salt, password hash, and 24h verification token
        pwd_hash, salt = hash_password(password)
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expiry = (now + timedelta(hours=24)).isoformat()
        now_iso = now.isoformat()

        c.execute("""
            INSERT INTO users (full_name, email, password_hash, salt, organization, role, is_verified, verification_token, token_expiry, created_at, last_resend_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)
        """, (full_name.strip(), email_clean, pwd_hash, salt, organization.strip(), role.strip(), token, expiry, now_iso, now_iso))
        conn.commit()
        user_id = c.lastrowid
        conn.close()

        user_info = {
            "id": user_id,
            "full_name": full_name.strip(),
            "email": email_clean,
            "organization": organization.strip(),
            "role": role.strip()
        }

        # 1. Send verification link to user
        verify_url = send_user_verification_email(user_info, token, site_url)

        # 2. Dispatch admin notification
        send_admin_signup_notification(user_info, status="Verification pending")

        return {
            "success": True,
            "message": "Account created. Please check your email and verify your account.",
            "email": email_clean,
            "verification_link": verify_url,
            "expires_in_hours": 24
        }

    @staticmethod
    def verify_email_token(token: str, site_url: str = SITE_URL) -> Dict[str, Any]:
        if not token:
            return {"success": False, "error": "Invalid verification token.", "code": "INVALID_TOKEN"}

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, full_name, email, organization, role, is_verified, token_expiry
            FROM users WHERE verification_token = ?
        """, (token.strip(),))
        row = c.fetchone()

        if not row:
            conn.close()
            return {"success": False, "error": "Verification token is invalid or has already been used.", "code": "TOKEN_NOT_FOUND"}

        # Check 24-hour expiration
        expiry_dt = datetime.fromisoformat(row["token_expiry"])
        if datetime.now(timezone.utc) > expiry_dt:
            conn.close()
            return {
                "success": False,
                "error": "Verification link has expired (24-hour limit exceeded). Please request a new verification link.",
                "code": "TOKEN_EXPIRED",
                "email": row["email"]
            }

        # Mark account as verified
        now_iso = datetime.now(timezone.utc).isoformat()
        c.execute("""
            UPDATE users
            SET is_verified = 1, verification_token = NULL, verified_at = ?
            WHERE id = ?
        """, (now_iso, row["id"]))
        conn.commit()
        conn.close()

        user_info = {
            "id": row["id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "organization": row["organization"],
            "role": row["role"]
        }

        # 1. Send Welcome Email to verified user
        send_user_welcome_email(user_info, site_url)

        # 2. Dispatch Admin Verified Notification
        send_admin_verified_notification(user_info)

        return {
            "success": True,
            "message": "Email verified successfully! You can now log in.",
            "user": user_info
        }

    @staticmethod
    def resend_verification_email(email: str, site_url: str = SITE_URL) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, full_name, email, organization, role, is_verified, last_resend_at
            FROM users WHERE email = ?
        """, (email_clean,))
        row = c.fetchone()

        if not row:
            conn.close()
            return {"success": False, "error": "No account registered with this email.", "code": "USER_NOT_FOUND"}

        if row["is_verified"]:
            conn.close()
            return {"success": False, "error": "Your account is already verified. You can log in directly.", "code": "ALREADY_VERIFIED"}

        # Enforce 60-second cooldown
        now = datetime.now(timezone.utc)
        if row["last_resend_at"]:
            last_resend = datetime.fromisoformat(row["last_resend_at"])
            elapsed = (now - last_resend).total_seconds()
            if elapsed < 60:
                remaining = int(60 - elapsed)
                conn.close()
                return {
                    "success": False,
                    "error": f"Please wait {remaining} seconds before requesting another email.",
                    "code": "COOLDOWN_ACTIVE",
                    "remaining_seconds": remaining
                }

        # Generate fresh token & reset 24h expiry
        token = secrets.token_urlsafe(32)
        expiry = (now + timedelta(hours=24)).isoformat()
        now_iso = now.isoformat()

        c.execute("""
            UPDATE users
            SET verification_token = ?, token_expiry = ?, last_resend_at = ?
            WHERE id = ?
        """, (token, expiry, now_iso, row["id"]))
        conn.commit()
        conn.close()

        user_info = {
            "id": row["id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "organization": row["organization"],
            "role": row["role"]
        }

        verify_url = send_user_verification_email(user_info, token, site_url)
        return {
            "success": True,
            "message": "A fresh verification link has been sent to your email.",
            "email": email_clean,
            "verification_link": verify_url
        }

    @staticmethod
    def login_user(email: str, password: str) -> Dict[str, Any]:
        email_clean = email.strip().lower()
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, full_name, email, password_hash, salt, organization, role, is_verified
            FROM users WHERE email = ?
        """, (email_clean,))
        row = c.fetchone()
        conn.close()

        if not row:
            return {"success": False, "error": "Invalid email or password.", "code": "INVALID_CREDENTIALS"}

        if not verify_password(password, row["password_hash"], row["salt"]):
            return {"success": False, "error": "Invalid email or password.", "code": "INVALID_CREDENTIALS"}

        # STRICT VERIFICATION CHECK: Block unverified users from accessing dashboard!
        if not row["is_verified"]:
            return {
                "success": False,
                "error": "Please verify your email before logging in.",
                "code": "EMAIL_NOT_VERIFIED",
                "email": email_clean,
                "allow_resend": True
            }

        return {
            "success": True,
            "message": "Authentication successful.",
            "user": {
                "id": row["id"],
                "name": row["full_name"],
                "email": row["email"],
                "organization": row["organization"],
                "role": row["role"]
            }
        }

auth_service = AuthService()
