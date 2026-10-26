# Jordan Matondo — Portfolio

A responsive personal portfolio built with FastAPI, Jinja2, HTML, CSS, and vanilla JavaScript. Project cards and profile artwork are local CSS placeholders; replace them with your real work when ready.

## Requirements

- Python 3.10 or newer
- Visual Studio Code

The project runs inside a virtual environment (`.venv`) so its dependencies never touch the system-wide Python installation. `.venv/` is git-ignored and is recreated from `requirements.txt` on any machine.

## Install and run on Windows

Open **PowerShell** in VS Code using **Terminal → New Terminal**, then run the one-time setup from the project folder:

```powershell
cd "C:\Users\Programming\Desktop\my-portfolio"
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

`setup.ps1` creates `.venv`, upgrades `pip`, installs `requirements.txt`, and verifies that the app imports. It is safe to re-run — an existing `.venv` is reused.

Start the site (and stop it with **Ctrl+C**):

```powershell
.\run.ps1
```

Use `run.ps1 -Port 8001` if port 8000 is busy. The launcher uses `.venv` directly, so no activation step is required and it works even when script execution is restricted.

### Manual alternative

If you prefer to run the steps yourself:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

If PowerShell blocks virtual-environment activation, allow it for this terminal session and activate again:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

To reproduce the exact versions that were tested here, use the lock file instead of `requirements.txt`:

```powershell
pip install -r requirements.lock.txt
```

Open the website at <http://127.0.0.1:8000/>. FastAPI's interactive API documentation is at <http://127.0.0.1:8000/docs>.

You can stop the development server with **Ctrl+C**.

## Personalize the portfolio

- **Introduction, skills, projects, services, and contact copy:** edit `templates/index.html`.
- **Shared page shell and navigation:** edit `templates/base.html`.
- **Colors, layout, and responsive styling:** edit `static/css/style.css`. The main blue accent is defined by the `--color-accent` variable near the top.
- **Mobile navigation and small interactions:** edit `static/js/script.js`.
- **Profile/project images:** add optimized images under `static/images/` and update the corresponding HTML in `templates/index.html`. Until then, the CSS illustrations are intentional placeholders.
- **Contact destination and social links:** configure the environment variables described below. No personal phone number, address, or social URL is included by default.
- **Project details:** select any project image or arrow button to open its accessible detail dialog. Update each card's title, description, tools, and illustration in `templates/index.html`; replace a sample with a real project URL there when you have one.

## Configure contact delivery (optional)

The form validates submissions in the browser and on the server, then reports delivery status inline without reloading the page. It sends email only when an SMTP server is configured; without it, the form clearly reports that delivery is unavailable. The application does not silently store messages or claim an email was sent.

Create a `.env` file from the provided template and fill in your values:

```powershell
Copy-Item .env.example .env
```

`run.ps1` detects `.env` and passes it to Uvicorn automatically. `.env` is git-ignored, so credentials are never committed.

Alternatively, set the variables in the current PowerShell session before starting Uvicorn:

```powershell
$env:CONTACT_EMAIL = "your-inbox@example.com"
$env:SMTP_HOST = "smtp.example.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "your-smtp-username"
$env:SMTP_PASSWORD = "your-smtp-password"
$env:SMTP_FROM_EMAIL = "portfolio@example.com"
$env:SMTP_USE_TLS = "true"
$env:SMTP_USE_SSL = "false"
$env:SOCIAL_LINKEDIN = "https://www.linkedin.com/in/your-profile"
$env:SOCIAL_GITHUB = "https://github.com/your-username"
$env:SOCIAL_BEHANCE = "https://www.behance.net/your-profile"
uvicorn main:app --reload
```

Use the SMTP settings supplied by your email provider. Port 587 normally uses STARTTLS (`SMTP_USE_TLS=true`, `SMTP_USE_SSL=false`); port 465 normally uses implicit TLS (`SMTP_USE_SSL=true`, `SMTP_USE_TLS=false`). Do not put real credentials in source code or commit them. Remove optional social variables you do not want to display. These settings are read from the process environment when the app starts.

## Project structure

```text
my-portfolio/
├── main.py
├── requirements.txt
├── requirements.lock.txt
├── setup.ps1
├── run.ps1
├── .env.example
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    └── images/
        └── .gitkeep
```

## Troubleshooting

- **`py` is not recognized:** install Python from <https://www.python.org/downloads/> and enable the launcher / PATH option, then restart VS Code. `setup.ps1` accepts `python` on PATH as well, so the launcher is optional.
- **Activation is blocked:** run the process-scoped `Set-ExecutionPolicy` command above; it does not change the machine-wide policy.
- **`No module named ...`:** ensure `.venv` is active in the current terminal and run `pip install -r requirements.txt` from this folder, or simply re-run `setup.ps1`.
- **`No .venv found`:** run `setup.ps1` first; `run.ps1` requires the environment it creates.
- **Scripts are blocked:** run them as `powershell -ExecutionPolicy Bypass -File .\setup.ps1`, which bypasses the policy for that one invocation only.
- **Port 8000 is busy:** run `uvicorn main:app --reload --port 8001` and open <http://127.0.0.1:8001/>.
- **Contact delivery unavailable:** configure the SMTP environment variables, restart Uvicorn, and check the terminal logs if the provider rejects delivery.
- **Changes do not appear:** hard-refresh the browser with **Ctrl+F5**. Uvicorn reloads Python code; refresh the browser for HTML, CSS, and JavaScript changes.

## Deploy online

For production, deploy this folder to a Python-capable host (for example, a managed application platform or a server you administer). Install `requirements.txt` and use a production ASGI command such as `uvicorn main:app --host 0.0.0.0 --port $PORT` (adapt the port variable to the host). Set contact and SMTP values through the host's secret/environment settings, configure HTTPS and a domain, and do not enable `--reload` in production. Test the contact flow with the provider's SMTP settings before publishing. Keep dependencies updated and use the hosting provider's process manager or deployment configuration to keep the application running.
