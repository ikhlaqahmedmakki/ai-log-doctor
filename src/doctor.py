"""Diagnose the latest ERROR snapshot with a chat-completions API."""

import json
import logging
import os
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.db import init_db, finding_exists, insert_finding
from src.discord import send_discord_alert

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = ROOT / "reports" / "latest_snapshot.txt"
ENV_PATH = ROOT / ".env"
MODEL = "gpt-4o-mini"
REQUEST_TIMEOUT_SECONDS = 60

logger = logging.getLogger("doctor")


class DoctorError(Exception):
    """A problem the user can fix without a stack trace."""


def load_env(path: Path) -> None:
    """Load KEY=VALUE lines into the environment. Existing variables win."""
    if not path.is_file():
        raise DoctorError(f"Environment file not found: {path}")

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise DoctorError(f"Could not read environment file: {path}") from exc

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key.startswith("export "):
            key = key.removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def require_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise DoctorError(f"Missing {name}. Set it in {ENV_PATH}.")
    return value


def read_snapshot(path: Path) -> str:
    if not path.is_file():
        raise DoctorError(f"Snapshot not found: {path}")
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise DoctorError(f"Could not read snapshot: {path}") from exc
    if not text:
        raise DoctorError(f"Snapshot is empty: {path}")
    return text


def request_diagnosis(snapshot: str, api_key: str, api_base_url: str) -> str:
    url = api_base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": MODEL,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You diagnose application ERROR logs. "
                    "Reply with JSON only, using this shape: "
                    '{"severity":"low|medium|high|critical",'
                    '"summary":"one short paragraph",'
                    '"fixes":["first fix","second fix","third fix"]}'
                ),
            },
            {
                "role": "user",
                "content": "Diagnose these ERROR lines:\n\n" + snapshot,
            },
        ],
    }
    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception("REST request failed: %s", url)
        raise DoctorError(f"LLM request failed: {url}") from exc

    try:
        body = response.json()
        return body["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise DoctorError("LLM response did not include a message.") from exc


def parse_diagnosis(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DoctorError("LLM response was not valid JSON.") from exc

    severity = data.get("severity")
    summary = data.get("summary")
    fixes = data.get("fixes")
    if not isinstance(severity, str) or not severity.strip():
        raise DoctorError("LLM response is missing severity.")
    if not isinstance(summary, str) or not summary.strip():
        raise DoctorError("LLM response is missing summary.")
    if (
        not isinstance(fixes, list)
        or len(fixes) != 3
        or not all(isinstance(item, str) and item.strip() for item in fixes)
    ):
        raise DoctorError("LLM response must include exactly 3 fixes.")

    return {
        "severity": severity.strip(),
        "summary": summary.strip(),
        "fixes": [item.strip() for item in fixes],
    }


def print_diagnosis(diagnosis: dict) -> None:
    print(f"Severity: {diagnosis['severity']}")
    print(f"Summary: {diagnosis['summary']}")
    print("Fixes:")
    for index, fix in enumerate(diagnosis["fixes"], start=1):
        print(f"{index}. {fix}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        init_db()
        snapshot = read_snapshot(SNAPSHOT_PATH)
        load_env(ENV_PATH)
        api_key = require_setting("LLM_API_KEY")
        api_base_url = require_setting("API_BASE_URL")
        content = request_diagnosis(snapshot, api_key, api_base_url)
        diagnosis = parse_diagnosis(content)
        
        # Generate unique fingerprint from snapshot lines
        fingerprint = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
        
        if finding_exists(fingerprint):
            print("Duplicate error ignored")
        else:
            timestamp = datetime.now(timezone.utc).isoformat()
            severity = diagnosis["severity"]
            summary = diagnosis["summary"]
            insert_finding(
                timestamp=timestamp,
                fingerprint=fingerprint,
                severity=severity,
                summary=summary
            )
            print_diagnosis(diagnosis)

            if severity.lower() in ("high", "critical"):
                alert_msg = f"🚨 **AI Log Doctor Alert** [Severity: {severity}]\nSummary: {summary}"
                send_discord_alert(alert_msg)
    except DoctorError as exc:
        logger.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
