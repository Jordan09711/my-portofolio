import logging
import os
import re
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Jordan Matondo | Portfolio",
    description="Portfolio of Jordan Matondo, software developer and freelancer.",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_LENGTHS = {
    "name": 100,
    "email": 254,
    "subject": 150,
    "message": 5000,
}


def get_site_settings() -> dict[str, object]:
    """Read public contact and social settings from the environment."""
    social_links = [
        {"label": "LinkedIn", "url": os.getenv("SOCIAL_LINKEDIN", "").strip()},
        {"label": "GitHub", "url": os.getenv("SOCIAL_GITHUB", "").strip()},
        {"label": "Behance", "url": os.getenv("SOCIAL_BEHANCE", "").strip()},
    ]
    return {
        "contact_email": os.getenv("CONTACT_EMAIL", "").strip(),
        "social_links": [link for link in social_links if link["url"]],
    }


def validate_contact_form(
    name: str, email: str, subject: str, message: str
) -> tuple[dict[str, str], list[str]]:
    values = {
        "name": name.strip(),
        "email": email.strip(),
        "subject": subject.strip(),
        "message": message.strip(),
    }
    errors: list[str] = []

    for field, value in values.items():
        if not value:
            errors.append(f"Please enter your {field}.")
        elif len(value) > MAX_LENGTHS[field]:
            errors.append(
                f"Your {field} must be no more than {MAX_LENGTHS[field]} characters."
            )
        elif any(ord(character) < 32 and character not in "\t\n\r" for character in value):
            errors.append(f"Your {field} contains unsupported characters.")

    if values["email"] and not EMAIL_PATTERN.fullmatch(values["email"]):
        errors.append("Please enter a valid email address.")

    return values, errors


def send_contact_email(name: str, sender_email: str, subject: str, message: str) -> None:
    """Deliver a validated message through an explicitly configured SMTP server."""
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    recipient = os.getenv("CONTACT_EMAIL", "").strip()
    sender = os.getenv("SMTP_FROM_EMAIL", "").strip() or os.getenv(
        "SMTP_USERNAME", ""
    ).strip()

    if not smtp_host or not recipient or not sender:
        raise RuntimeError(
            "Contact delivery is not configured. Set SMTP_HOST, CONTACT_EMAIL, "
            "and SMTP_FROM_EMAIL (or SMTP_USERNAME)."
        )

    email_message = EmailMessage()
    email_message["Subject"] = f"Portfolio contact: {subject}"
    email_message["From"] = sender
    email_message["To"] = recipient
    email_message["Reply-To"] = sender_email
    email_message.set_content(
        f"Name: {name}\nEmail: {sender_email}\n\n{message}"
    )

    port = int(os.getenv("SMTP_PORT", "587"))
    use_ssl = os.getenv("SMTP_USE_SSL", "false").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    timeout = 15

    if use_ssl:
        with smtplib.SMTP_SSL(
            smtp_host, port, timeout=timeout, context=ssl.create_default_context()
        ) as smtp:
            _authenticate_and_send(smtp, email_message)
    else:
        with smtplib.SMTP(smtp_host, port, timeout=timeout) as smtp:
            if use_tls:
                smtp.starttls(context=ssl.create_default_context())
            _authenticate_and_send(smtp, email_message)


def _authenticate_and_send(smtp: smtplib.SMTP, email_message: EmailMessage) -> None:
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    if username:
        smtp.login(username, password)
    smtp.send_message(email_message)


def render_home(
    request: Request,
    *,
    form_values: dict[str, str] | None = None,
    errors: list[str] | None = None,
    success_message: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "site": get_site_settings(),
            "year": date.today().year,
            "form_values": form_values or {},
            "errors": errors or [],
            "success_message": success_message,
        },
        status_code=status_code,
    )


@app.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request) -> HTMLResponse:
    return render_home(request)


@app.post("/contact", response_class=HTMLResponse, name="contact")
def contact(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    subject: str = Form(""),
    message: str = Form(""),
) -> HTMLResponse:
    values, errors = validate_contact_form(name, email, subject, message)
    if errors:
        return render_home(request, form_values=values, errors=errors, status_code=422)

    try:
        send_contact_email(
            values["name"], values["email"], values["subject"], values["message"]
        )
    except RuntimeError as exc:
        return render_home(
            request,
            form_values=values,
            errors=[str(exc)],
            status_code=503,
        )
    except (OSError, smtplib.SMTPException, ValueError):
        logger.exception("Contact form email delivery failed.")
        return render_home(
            request,
            form_values=values,
            errors=[
                "Your message could not be delivered right now. Please try again later."
            ],
            status_code=502,
        )

    return render_home(
        request,
        success_message="Your message was sent successfully. Thank you for reaching out!",
    )
