from __future__ import annotations

import os
import logging
import traceback
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai_tools import TavilySearchTool

from app.core.config import Settings
from app.models.schemas import TaskRunRequest

logger = logging.getLogger(__name__)


class PromptLibrary:
    def build_research_prompt(self, request: TaskRunRequest) -> str:
        return f"""
You are the Researcher for AgentOrchestrator.

Primary instruction:
{request.instruction}

Additional context:
{request.context or "No additional context provided."}

Requirements:
- Use Tavily search to gather recent and relevant external information.
- Prefer current signals, credible sources, concrete facts, and notable trend lines.
- Separate verified facts from informed inferences.
- End with a concise handoff section for the Analyst.
""".strip()

    def build_analysis_prompt(self, request: TaskRunRequest, research_brief: str) -> str:
        return f"""
You are the Analyst for AgentOrchestrator.

Original instruction:
{request.instruction}

Additional context:
{request.context or "No additional context provided."}

Research brief:
{research_brief}

Requirements:
- Synthesize the research into themes, tradeoffs, opportunities, and risks.
- Highlight where the research is strong and where assumptions remain.
- Produce a structured analytical brief that the Writer can convert into a polished report.
""".strip()

    def build_writer_prompt(
        self,
        request: TaskRunRequest,
        task_id: str,
        research_brief: str,
        analysis_brief: str,
    ) -> str:
        report_title = request.report_title or "AgentOrchestrator Report"
        return f"""
You are the Writer for AgentOrchestrator.

Task ID: {task_id}
Report title: {report_title}
Original instruction:
{request.instruction}

Additional context:
{request.context or "No additional context provided."}

Research brief:
{research_brief}

Analysis brief:
{analysis_brief}

Write a professional Markdown report with these sections in order:
1. Executive Summary
2. Task Framing
3. Research Findings
4. Analysis
5. Recommendations
6. Risks and Assumptions
7. Next Steps

Requirements:
- Use clean Markdown headings and concise paragraphs.
- Call out inferences explicitly.
- Include a brief source recap in the Research Findings section when available.
- Finish with a short conclusion tied to the original instruction.
""".strip()


class CrewAgentFactory:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_researcher(self) -> Agent:
        return Agent(
            role="Researcher",
            goal="Search the web for the latest, relevant evidence and signals.",
            backstory=(
                "You are a senior researcher who validates claims, monitors new developments, "
                "and prepares structured evidence for downstream decision-making."
            ),
            tools=[TavilySearchTool(search_depth="advanced", max_results=5, include_answer=True)],
            allow_delegation=False,
            verbose=True,
            llm=self._create_llm(),
        )

    def create_analyst(self) -> Agent:
        return Agent(
            role="Analyst",
            goal="Turn raw evidence into structured reasoning, tradeoffs, and insights.",
            backstory=(
                "You are a principal analyst who interprets signals, weighs uncertainties, "
                "and organizes findings into clear strategic thinking."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self._create_llm(),
        )

    def create_writer(self) -> Agent:
        return Agent(
            role="Writer",
            goal="Draft polished stakeholder-ready reports in clear professional Markdown.",
            backstory=(
                "You are an executive report writer who transforms analytical material into concise, "
                "high-signal documents for technical and business audiences."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self._create_llm(),
        )

    def _create_llm(self) -> LLM:
        kwargs: dict[str, Any] = {
            "model": self._resolve_model_name(),
            "temperature": 0.2,
        }
        api_version = self._resolve_google_api_version()
        if api_version:
            kwargs["api_version"] = api_version
        api_key = self._resolve_api_key()
        if api_key:
            kwargs["api_key"] = api_key

        return LLM(
            **kwargs,
        )

    def _resolve_model_name(self) -> str:
        model_name = self.settings.model.strip()
        if model_name.startswith("models/"):
            model_name = model_name.removeprefix("models/")
        if model_name.startswith("gemini/models/"):
            model_name = f"gemini/{model_name.removeprefix('gemini/models/')}"
        if model_name.startswith("google/models/"):
            model_name = f"gemini/{model_name.removeprefix('google/models/')}"
        if model_name == "gemini/gemini-3-flash":
            model_name = "gemini/gemini-3-flash-preview"
        if "/" in model_name:
            return model_name
        if model_name.startswith("gemini-"):
            return f"gemini/{model_name}"
        return model_name

    def _resolve_api_key(self) -> str | None:
        model_name = self._resolve_model_name()
        if model_name.startswith("gemini/") or model_name.startswith("google/"):
            if self.settings.google_api_key:
                return self.settings.google_api_key
            return None
        if model_name.startswith("groq/"):
            if self.settings.groq_api_key:
                return self.settings.groq_api_key
            return None
        return None

    def _resolve_google_api_version(self) -> str | None:
        model_name = self._resolve_model_name()
        if not model_name.startswith("gemini/") and not model_name.startswith("google/"):
            return None
        is_preview_model = "gemini-3-" in model_name or model_name.endswith("-preview") or "-preview-" in model_name
        configured_version = self.settings.google_api_version.strip()
        if configured_version:
            if is_preview_model and configured_version == "v1":
                logger.warning(
                    "MODEL=%s is a preview Gemini model and cannot use GOOGLE_API_VERSION=v1. "
                    "Overriding to v1beta.",
                    model_name,
                )
                return "v1beta"
            return configured_version
        if is_preview_model:
            return "v1beta"
        return "v1"


class CrewPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.prompt_library = PromptLibrary()
        self.agent_factory = CrewAgentFactory(settings)

    def validate_configuration(self) -> None:
        missing = []
        if not self.settings.tavily_api_key:
            missing.append("TAVILY_API_KEY")
        provider = self._provider_name()

        if provider == "unknown":
            raise ValueError(
                "Unsupported MODEL. Use a CrewAI-compatible provider prefix such as "
                "'gemini/gemini-3-flash-preview', 'gemini/gemini-2.5-flash', or 'groq/llama-3.1-8b-instant'."
            )

        if provider == "gemini" and not self.settings.google_api_key:
            missing.append("GOOGLE_API_KEY or GEMINI_API_KEY")
        if provider == "groq" and not self.settings.groq_api_key:
            missing.append("GROQ_API_KEY")
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        os.environ["TAVILY_API_KEY"] = self.settings.tavily_api_key
        if self.settings.google_api_key:
            os.environ["GOOGLE_API_KEY"] = self.settings.google_api_key
            os.environ["GEMINI_API_KEY"] = self.settings.google_api_key
        if self.settings.groq_api_key:
            os.environ["GROQ_API_KEY"] = self.settings.groq_api_key

        logger.info(
            "Validated LLM provider=%s model=%s google_api_version=%s google_api_key_loaded=%s groq_api_key_loaded=%s",
            provider,
            self._normalized_model_name(),
            self.agent_factory._resolve_google_api_version(),
            bool(self.settings.google_api_key),
            bool(self.settings.groq_api_key),
        )

    def _provider_name(self) -> str:
        model_name = self._normalized_model_name()
        if model_name.startswith("gemini/") or model_name.startswith("google/"):
            return "gemini"
        if model_name.startswith("groq/"):
            return "groq"
        return "unknown"

    def _normalized_model_name(self) -> str:
        return self.agent_factory._resolve_model_name()

    def run_research(self, request: TaskRunRequest) -> str:
        prompt = self.prompt_library.build_research_prompt(request)
        return self._run_stage(
            agent=self.agent_factory.create_researcher(),
            description=prompt,
            expected_output=(
                "A concise research brief with current facts, key trends, evidence, source references, "
                "uncertainties, and a clear analyst handoff."
            ),
        )

    def run_analysis(self, request: TaskRunRequest, research_brief: str) -> str:
        prompt = self.prompt_library.build_analysis_prompt(request, research_brief)
        return self._run_stage(
            agent=self.agent_factory.create_analyst(),
            description=prompt,
            expected_output=(
                "A structured analytical brief with major patterns, implications, tradeoffs, opportunities, "
                "risks, and decision criteria for the writer."
            ),
        )

    def run_writer(
        self,
        request: TaskRunRequest,
        task_id: str,
        research_brief: str,
        analysis_brief: str,
    ) -> str:
        prompt = self.prompt_library.build_writer_prompt(request, task_id, research_brief, analysis_brief)
        return self._run_stage(
            agent=self.agent_factory.create_writer(),
            description=prompt,
            expected_output="A complete professional Markdown report ready for presentation.",
        )

    def _run_stage(self, *, agent: Agent, description: str, expected_output: str) -> str:
        try:
            task = Task(description=description, expected_output=expected_output, agent=agent)
            crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
            result = crew.kickoff()
            return self._extract_text(result)
        except Exception as exc:
            logger.error(
                "Crew pipeline stage failed for agent=%s: %s\n%s",
                getattr(agent, "role", "unknown"),
                exc,
                traceback.format_exc(),
            )
            raise

    def _extract_text(self, result: Any) -> str:
        for attr in ("raw", "output"):
            value = getattr(result, attr, None)
            if isinstance(value, str) and value.strip():
                return value.strip()

        text_result = str(result).strip()
        if text_result:
            return text_result

        raise RuntimeError("CrewAI returned an empty response. Please verify your model and API configuration.")
