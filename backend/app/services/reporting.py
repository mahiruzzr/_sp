import re
from pathlib import Path

from app.core.config import Settings


class ReportService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def summarize(self, markdown_report: str, limit: int = 240) -> str:
        plain_text = re.sub(r"#+\s*", "", markdown_report)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()
        return plain_text[:limit] + ("..." if len(plain_text) > limit else "")

    def persist(self, task_id: str, markdown_report: str, report_title: str | None) -> Path:
        slug = self._slugify(report_title or "agent-orchestrator-report")
        report_path = self.settings.reports_dir / f"{task_id}-{slug}.md"
        report_path.write_text(markdown_report, encoding="utf-8")
        return report_path

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
        return normalized or "report"
