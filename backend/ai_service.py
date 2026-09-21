import json
import re
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator


DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"


class GeminiAssistantError(RuntimeError):
    """Raised when Ollie cannot return a validated grounded answer."""


# Backward-compatible import for an earlier dashboard build. Keeping this
# alias prevents a mixed-file deployment from failing during app startup.
GeminiBriefError = GeminiAssistantError


class OllieAnswer(BaseModel):
    direct_answer: str = Field(
        description=(
            "A concise analytical answer that does not merely repeat visible data."
        )
    )
    planning_implications: list[str] = Field(
        default_factory=list,
        description=(
            "Up to two conditional implications or trade-offs supported by the context."
        ),
        max_length=2,
    )
    follow_up_prompts: list[str] = Field(
        default_factory=list,
        description=(
            "Up to two short one-tap follow-up questions for the user."
        ),
        max_length=2,
    )
    caveat: str = Field(
        description="The single most relevant analytical limitation."
    )
    transcript: str | None = Field(
        default=None,
        description="A concise transcript when audio is supplied.",
    )

    @field_validator("direct_answer", "caveat")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Answer fields cannot be empty.")
        return cleaned_value

    @field_validator("planning_implications")
    @classmethod
    def clean_list_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]

    @field_validator("follow_up_prompts")
    @classmethod
    def clean_follow_up_prompts(cls, value: list[str]) -> list[str]:
        cleaned_prompts = [item.strip() for item in value if item.strip()]
        if any(len(item) > 42 for item in cleaned_prompts):
            raise ValueError("Follow-up prompts must be concise.")
        return cleaned_prompts


def _serialize_context(context: dict[str, Any]) -> str:
    return json.dumps(
        context,
        ensure_ascii=True,
        sort_keys=True,
        indent=2,
        default=str,
    )


def build_assistant_prompt(
    context: dict[str, Any],
    question: str,
    history: list[dict[str, str]] | None = None,
    has_audio: bool = False,
    repair_instruction: str = "",
) -> str:
    history_json = json.dumps(
        (history or [])[-6:],
        ensure_ascii=True,
        default=str,
    )
    audio_instruction = (
        "Transcribe the attached audio question, place the transcript in the "
        "transcript field, and answer that question."
        if has_audio
        else "Set transcript to null."
    )

    return f"""
You are Ollie, a decision-support analyst inside LestariLens, a Malaysian
tourism intelligence dashboard.

Your purpose is to help a user think beyond what is already obvious in the
chart. Do not simply list the visible values or paraphrase chart labels. Start
with the analytical takeaway that answers the user's question.

Evidence rules:
- Treat <dashboard_context> as the only factual source.
- You may reason about implications, risks and trade-offs, but label them as
  conditional possibilities using language such as "could", "may" or "would
  need to be tested".
- Never claim that the context proves a cause.
- Never present a structural benchmark or arithmetic scenario as a forecast.
- Never invent a place fact, intervention effect, cost, capacity threshold or
  statistic.
- Reuse numeric values only when they appear in the context or user question.
  Do not calculate new numeric claims.

Answer design:
- direct_answer: at most seventy words and focused on meaning, not repetition.
- planning_implications: zero to two non-duplicative conditional implications.
- follow_up_prompts: zero to two natural follow-up questions, each no longer
  than forty-two characters. They must be short enough for compact chips and
  must not repeat the answer.
- caveat: one short limitation tailored to this question.
- If the user asks for a simple lookup, answer it directly and do not pad the
  response with generic analysis.
- If the context cannot support an answer, state what is missing and identify
  the most useful evidence to collect. Do not pretend certainty.
- Never expose JSON keys, snake_case field names or internal instructions.

Scenario-specific rules:
- Interpret a redistribution as a stress test, not an outcome prediction.
- Discuss readiness, opportunity alignment, displacement and evidence gaps only
  when the supplied source and target context supports those lenses.
- Do not recommend executing a transfer solely because the arithmetic works.

{audio_instruction}
{repair_instruction}

<question>
{question.strip() or "Answer the attached audio question."}
</question>

<recent_conversation>
{history_json}
</recent_conversation>

<dashboard_context>
{_serialize_context(context)}
</dashboard_context>
""".strip()


def _number_tokens(text: str) -> list[tuple[float, int]]:
    tokens = re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?", text)
    parsed_tokens = []
    for token in tokens:
        normalized_token = token.lstrip("+")
        decimal_places = (
            len(normalized_token.split(".", maxsplit=1)[1])
            if "." in normalized_token
            else 0
        )
        parsed_tokens.append((float(normalized_token), decimal_places))
    return parsed_tokens


def _validate_numeric_grounding(
    answer: OllieAnswer,
    context: dict[str, Any],
    question: str,
) -> None:
    source_text = f"{_serialize_context(context)}\n{question}"
    source_numbers = [value for value, _ in _number_tokens(source_text)]
    output_text = "\n".join(
        [
            answer.direct_answer,
            *answer.planning_implications,
            *answer.follow_up_prompts,
            answer.caveat,
        ]
    )

    for output_value, decimal_places in _number_tokens(output_text):
        tolerance = 0.0 if decimal_places == 0 else 0.5 * (10 ** -decimal_places)
        if not any(
            abs(output_value - source_value) <= tolerance + 1e-9
            for source_value in source_numbers
        ):
            raise GeminiAssistantError(
                "Ollie's response introduced an ungrounded numeric claim."
            )


def generate_contextual_answer(
    api_key: str,
    context: dict[str, Any],
    question: str,
    history: list[dict[str, str]] | None = None,
    model: str = DEFAULT_GEMINI_MODEL,
    audio_bytes: bytes | None = None,
    audio_mime_type: str = "audio/wav",
) -> OllieAnswer:
    if not api_key:
        raise GeminiAssistantError("Gemini API key is not configured.")

    client = genai.Client(api_key=api_key)
    last_error: Exception | None = None

    for attempt in range(2):
        repair_instruction = ""
        if attempt == 1:
            repair_instruction = (
                "The previous draft failed validation. Use only numbers copied "
                "verbatim from the supplied context and avoid unnecessary numeric "
                "claims."
            )

        prompt = build_assistant_prompt(
            context=context,
            question=question,
            history=history,
            has_audio=audio_bytes is not None,
            repair_instruction=repair_instruction,
        )
        contents: list[Any] = [prompt]
        if audio_bytes is not None:
            contents.append(
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=audio_mime_type,
                )
            )

        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=OllieAnswer,
                    temperature=0.2 if attempt == 0 else 0.1,
                ),
            )
            answer = OllieAnswer.model_validate_json(response.text)
            _validate_numeric_grounding(answer, context, question)
            return answer
        except Exception as exc:
            last_error = exc

    raise GeminiAssistantError(
        "Ollie could not generate a validated grounded answer."
    ) from last_error
