import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from app.config import settings


class EmailService:
    """
    Service for sending emails using SMTP.
    """

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Optional plain text content

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject

            # Add plain text part if provided
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
            )

            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """
        Send email verification link.

        Args:
            to_email: User email address
            verification_token: Verification token

        Returns:
            True if email was sent successfully
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #3b82f6;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Verify Your Email Address</h1>
                <p>Thank you for registering with Telegram Lead Monitor!</p>
                <p>Please click the button below to verify your email address:</p>
                <a href="{verification_url}" class="button">Verify Email</a>
                <p>Or copy and paste this link into your browser:</p>
                <p><a href="{verification_url}">{verification_url}</a></p>
                <div class="footer">
                    <p>This link will expire in {settings.VERIFICATION_TOKEN_EXPIRE_HOURS} hours.</p>
                    <p>If you didn't create an account, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Verify Your Email Address

        Thank you for registering with Telegram Lead Monitor!

        Please click the link below to verify your email address:
        {verification_url}

        This link will expire in {settings.VERIFICATION_TOKEN_EXPIRE_HOURS} hours.

        If you didn't create an account, you can safely ignore this email.
        """

        return await self.send_email(
            to_email=to_email,
            subject="Verify Your Email - Telegram Lead Monitor",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset link.

        Args:
            to_email: User email address
            reset_token: Password reset token

        Returns:
            True if email was sent successfully
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #3b82f6;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Reset Your Password</h1>
                <p>We received a request to reset your password.</p>
                <p>Click the button below to reset your password:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                <p>Or copy and paste this link into your browser:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <div class="footer">
                    <p>This link will expire in {settings.VERIFICATION_TOKEN_EXPIRE_HOURS} hours.</p>
                    <p>If you didn't request a password reset, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Reset Your Password

        We received a request to reset your password.

        Click the link below to reset your password:
        {reset_url}

        This link will expire in {settings.VERIFICATION_TOKEN_EXPIRE_HOURS} hours.

        If you didn't request a password reset, you can safely ignore this email.
        """

        return await self.send_email(
            to_email=to_email,
            subject="Reset Your Password - Telegram Lead Monitor",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_new_lead_notification(
        self,
        to_email: str,
        user_name: str,
        lead_id: str,
        lead_score: float,
        lead_reasoning: str,
        rule_name: str,
        source_title: str,
        message_preview: str,
    ) -> bool:
        """
        Send notification about a new lead.

        Args:
            to_email: Recipient email
            user_name: User's full name
            lead_id: Lead UUID
            lead_score: Lead score (0.0-1.0)
            lead_reasoning: LLM reasoning
            rule_name: Rule name
            source_title: Source title
            message_preview: Message text preview

        Returns:
            True if email was sent successfully
        """
        dashboard_url = settings.FRONTEND_URL
        subject = f"🎯 New Lead Found! (Score: {int(lead_score * 100)}%)"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; }}
                .lead-info {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4F46E5; }}
                .score {{ font-size: 24px; font-weight: bold; color: #4F46E5; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #4F46E5;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{ color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Lead Found!</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>The monitoring system found a new lead matching your rules:</p>

                    <div class="lead-info">
                        <p><strong>Rule:</strong> {rule_name}</p>
                        <p><strong>Source:</strong> {source_title}</p>
                        <p><strong>Match Score:</strong> <span class="score">{int(lead_score * 100)}%</span></p>
                        <p><strong>LLM Analysis:</strong></p>
                        <p style="font-style: italic; color: #6b7280;">"{lead_reasoning}"</p>
                    </div>

                    <div class="lead-info">
                        <p><strong>Message Preview:</strong></p>
                        <p>{message_preview[:200]}{"..." if len(message_preview) > 200 else ""}</p>
                    </div>

                    <a href="{dashboard_url}/dashboard/leads?highlight={lead_id}" class="button">
                        View Lead in Dashboard
                    </a>

                    <div class="footer">
                        <p>This is an automated notification from Telegram Lead Monitor.</p>
                        <p>You can configure notifications in <a href="{dashboard_url}/dashboard/settings">settings</a>.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        New Lead Found!

        Rule: {rule_name}
        Source: {source_title}
        Score: {int(lead_score * 100)}%

        LLM Analysis: {lead_reasoning}

        Preview: {message_preview[:200]}

        View in Dashboard: {dashboard_url}/dashboard/leads?highlight={lead_id}
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_lead_status_change_notification(
        self,
        to_email: str,
        user_name: str,
        lead_id: str,
        old_status: str,
        new_status: str,
        rule_name: str,
    ) -> bool:
        """
        Send notification about lead status change.
        """
        dashboard_url = settings.FRONTEND_URL
        status_labels = {
            "new": "New",
            "in_progress": "In Progress",
            "processed": "Processed",
            "archived": "Archived"
        }

        subject = f"Lead Status Changed: {status_labels.get(old_status, old_status)} → {status_labels.get(new_status, new_status)}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; }}
                .status-change {{ background-color: white; padding: 15px; margin: 15px 0; text-align: center; }}
                .status {{ display: inline-block; padding: 8px 16px; border-radius: 4px; margin: 0 10px; }}
                .status-new {{ background-color: #dbeafe; color: #1e40af; }}
                .status-in_progress {{ background-color: #fef3c7; color: #92400e; }}
                .status-processed {{ background-color: #d1fae5; color: #065f46; }}
                .status-archived {{ background-color: #f3f4f6; color: #1f2937; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #4F46E5;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Lead Status Changed</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>The status of a lead for rule <strong>{rule_name}</strong> has changed:</p>

                    <div class="status-change">
                        <span class="status status-{old_status}">{status_labels.get(old_status, old_status)}</span>
                        <span style="font-size: 24px;">→</span>
                        <span class="status status-{new_status}">{status_labels.get(new_status, new_status)}</span>
                    </div>

                    <a href="{dashboard_url}/dashboard/leads?highlight={lead_id}" class="button">
                        View Lead
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_lead_assignment_notification(
        self,
        to_email: str,
        user_name: str,
        lead_id: str,
        rule_name: str,
        source_title: str,
    ) -> bool:
        """
        Send notification about lead assignment to user.
        """
        dashboard_url = settings.FRONTEND_URL
        subject = f"Lead Assigned to You: {rule_name}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; }}
                .lead-info {{ background-color: white; padding: 15px; margin: 15px 0; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #10b981;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Lead Assigned to You</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>A new lead has been assigned to you:</p>

                    <div class="lead-info">
                        <p><strong>Rule:</strong> {rule_name}</p>
                        <p><strong>Source:</strong> {source_title}</p>
                    </div>

                    <a href="{dashboard_url}/dashboard/leads?highlight={lead_id}" class="button">
                        View Lead
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)


# Global instance
email_service = EmailService()
