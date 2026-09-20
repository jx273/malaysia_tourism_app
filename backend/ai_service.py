import json
import re
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator


DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"


class GeminiBriefError(RuntimeError):
    """Raised when a grounded Gemini brief cannot be generated safely."""


class GeminiAssistantError(RuntimeError):
    """Raised when Ollie cannot return a validated grounded answer."""


class TourismOpportunityBrief(BaseModel):
    headline: str = Field(description="A concise tourism opportunity headline.")
    interpretation: str = Field(description="A grounded context interpretation.")
    recommended_action: str = Field(description="One practical investigation.")
    caveat: str = Field(description="A concise analytical limitation.")

    @field_validator("headline", "interpretation", "recommended_action", "caveat")
    @classmethod
    def reject_generated_numbers(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Brief fields cannot be empty.")
        if re.search(r"\d", cleaned_value):
            raise ValueError("AI narrative must not introduce numeric claims.")
        return cleaned_value


class OllieAnswer(BaseModel):
    answer: str = Field(description="A direct answer grounded in the context.")
    evidence: list[str] = Field(
        default_factory=list,
        description="Up to three supporting facts from the context.",
        max_length=3,
    )
    caveat: str = Field(description="The most relevant analytical limitation.")
    transcript: str | None = Field(
        default=None,
        description="A concise transcript when audio is supplied.",
    )

    @field_validator("answer", "caveat")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Answer fields cannot be empty.")
        return cleaned_value

    @field_validator("evidence")
    @classmethod
    def clean_evidence(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


def _serialize_context(context: dict[str, Any]) -> str:
    return json.dumps(
        context,
        ensure_ascii=True,
        sort_keys=True,
        indent=2,
        default=str,
    )


def build_grounded_prompt(context: dict[str, Any]) -> str:
    return f"""
You are an evidence-grounded tourism policy analyst for Malaysia.

Use only the dashboard context inside <dashboard_context>. Do not use outside
knowledge, infer causes, invent facts, or add statistics. The dashboard will
display numeric evidence separately, so every response field must contain no
digits and no numeric claims.

Interpret a positive relative opportunity gap only as actual visitor share
being below the model-expected structural benchmark. It is not a forecast,
proof of unmet demand, or proof of a marketing problem.

Keep the headline under twelve words, the interpretation under forty-five
words, the recommended investigation under thirty words, and the caveat under
twenty-five words. Write concise professional English for a public-sector
dashboard.

<dashboard_context>
{_serialize_context(context)}
</dashboard_context>
""".strip()


def build_assistant_prompt(
    context: dict[str, Any],
    question: str,
    history: list[dict[str, str]] | None = None,
    has_audio: bool = False,
) -> str:
    history_json = json.dumps(
        (history or [])[-4:],
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
You are Ollie, the concise AI data assistant inside LestariLens, a Malaysian
tourism intelligence dashboard.

Answer only from <dashboard_context>. Never use outside knowledge, invent a
fact, infer a cause, or present the structural benchmark as a forecast. A
positive opportunity gap means actual visitor share is below the model-expected
share. Scenario outputs are illustrative arithmetic, not predicted outcomes.

If the context cannot answer the question, say what is unavailable and suggest
which dashboard page contains the closest evidence. Use at most eighty words in
the answer, up to three evidence bullets, and one short caveat. Reuse numeric
values only when they are explicitly present in the context or the user's
question. Do not calculate new statistics.

{audio_instruction}

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
    output_text = "\n".join([answer.answer, *answer.evidence, answer.caveat])

    for output_value, decimal_places in _number_tokens(output_text):
        tolerance = 0.0 if decimal_places == 0 else 0.5 * (10 ** -decimal_places)
        if not any(
            abs(output_value - source_value) <= tolerance + 1e-9
            for source_value in source_numbers
        ):
            raise GeminiAssistantError(
                "Ollie's response introduced an ungrounded numeric claim."
            )


def generate_tourism_brief(
    api_key: str,
    context: dict[str, Any],
    model: str = DEFAULT_GEMINI_MODEL,
) -> TourismOpportunityBrief:
    if not api_key:
        raise GeminiBriefError("Gemini API key is not configured.")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=build_grounded_prompt(context),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TourismOpportunityBrief,
                temperature=0.2,
            ),
        )
        return TourismOpportunityBrief.model_validate_json(response.text)
    except GeminiBriefError:
        raise
    except Exception as exc:
        raise GeminiBriefError(
            "Gemini could not generate a validated brief."
        ) from exc


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

    try:
        client = genai.Client(api_key=api_key)
        prompt = build_assistant_prompt(
            context=context,
            question=question,
            history=history,
            has_audio=audio_bytes is not None,
        )
        contents: list[Any] = [prompt]
        if audio_bytes is not None:
            contents.append(
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=audio_mime_type,
                )
            )

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OllieAnswer,
                temperature=0.15,
            ),
        )
        answer = OllieAnswer.model_validate_json(response.text)
        _validate_numeric_grounding(answer, context, question)
        return answer
    except GeminiAssistantError:
        raise
    except Exception as exc:
        raise GeminiAssistantError(
            "Ollie could not generate a validated grounded answer."
        ) from exc
