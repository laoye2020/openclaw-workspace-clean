from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

import requests


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class AnalyzerError(RuntimeError):
    """Raised when analyzer evaluation cannot return a valid payload."""


@dataclass(slots=True)
class AnalyzerInput:
    chain_id: str
    token_address: str
    token_symbol: str
    pair_address: str
    dex_id: str
    rule_score: float
    liquidity_usd: float
    txns_h1: int
    price_change_h1: float | None
    price_change_h24: float | None
    volume_h24: float
    risk_flags: list[str]
    market_snapshot: str


@dataclass(slots=True)
class AnalyzerOutput:
    narrative_score: float
    risk_comment: str
    action_hint: str
    confidence: float
    reasons: list[str]


class Analyzer(Protocol):
    provider: str
    model: str

    def analyze(self, payload: AnalyzerInput) -> AnalyzerOutput:
        ...


@dataclass(slots=True)
class MockAnalyzer:
    provider: str = "mock"
    model: str = "mock-v1"

    def analyze(self, payload: AnalyzerInput) -> AnalyzerOutput:
        txns_term = payload.txns_h1 // 8
        h1_change = int(payload.price_change_h1 or 0.0)
        seed = (
            int(payload.rule_score * 100)
            + txns_term
            + h1_change
            + len(payload.token_address)
            + len(payload.risk_flags) * 7
        )
        adjustment = (seed % 13) - 6
        narrative_score = _clamp(payload.rule_score + adjustment, 0.0, 100.0)
        confidence = _clamp(0.52 + ((seed % 38) / 100.0), 0.0, 1.0)
        risk_comment = "风险标记较多，注意流动性变化" if payload.risk_flags else "风险标记较少"
        if narrative_score >= 80:
            action_hint = "可继续跟踪，等待放量确认"
        elif narrative_score >= 60:
            action_hint = "谨慎观察，不追涨"
        else:
            action_hint = "优先回避，等待结构改善"
        reasons = [
            f"mock_seed={seed}",
            f"txns_h1={payload.txns_h1}",
            f"h1_change={payload.price_change_h1 if payload.price_change_h1 is not None else 'n/a'}",
        ]
        return AnalyzerOutput(
            narrative_score=round(narrative_score, 2),
            risk_comment=risk_comment,
            action_hint=action_hint,
            confidence=round(confidence, 2),
            reasons=reasons,
        )


class DeepSeekAnalyzer:
    provider = "deepseek"

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: int,
    ) -> None:
        if not api_key:
            raise AnalyzerError("DOG_SCOUT_LLM_API_KEY is required when LLM is enabled")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def analyze(self, payload: AnalyzerInput) -> AnalyzerOutput:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        request_payload = {
            "model": self.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a crypto momentum risk analyst. "
                        "Respond only valid JSON with keys: "
                        "narrative_score, risk_comment, action_hint, confidence, reasons."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_user_prompt(payload),
                },
            ],
        }

        try:
            response = self.session.post(
                url,
                headers=headers,
                json=request_payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise AnalyzerError(f"DeepSeek request failed: {exc}") from exc

        content = _extract_message_content(body)
        parsed = _parse_json_payload(content)
        return _normalize_output(parsed)


def build_market_snapshot(
    liquidity_usd: float,
    volume_h24: float,
    txns_h1: int,
    price_change_h1: float | None,
    price_change_h24: float | None,
    dex_id: str,
) -> str:
    h1_text = "n/a" if price_change_h1 is None else f"{price_change_h1:.2f}%"
    h24_text = "n/a" if price_change_h24 is None else f"{price_change_h24:.2f}%"
    return (
        f"DEX={dex_id}; liquidity=${liquidity_usd:,.0f}; volume24h=${volume_h24:,.0f}; "
        f"txns_h1={txns_h1}; change_h1={h1_text}; change_h24={h24_text}"
    )


def _build_user_prompt(payload: AnalyzerInput) -> str:
    risk_flags_text = ", ".join(payload.risk_flags) if payload.risk_flags else "none"
    return (
        "Evaluate this meme token candidate:\n"
        f"- chain: {payload.chain_id}\n"
        f"- token: {payload.token_symbol} ({payload.token_address})\n"
        f"- pair: {payload.pair_address} on {payload.dex_id}\n"
        f"- rule_score: {payload.rule_score:.2f}\n"
        f"- risk_flags: {risk_flags_text}\n"
        f"- market_snapshot: {payload.market_snapshot}\n"
        "Return JSON with:\n"
        "- narrative_score (0-100)\n"
        "- risk_comment (short string)\n"
        "- action_hint (short string)\n"
        "- confidence (0-1)\n"
        "- reasons (array of concise strings)\n"
    )


def _extract_message_content(body: dict[str, Any]) -> str:
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AnalyzerError("DeepSeek response missing choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise AnalyzerError("DeepSeek response missing message")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise AnalyzerError("DeepSeek response message content is empty")
    return content.strip()


def _parse_json_payload(content: str) -> dict[str, Any]:
    raw = content
    if "```" in raw:
        raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AnalyzerError(f"Invalid analyzer JSON payload: {exc}") from exc
    if not isinstance(parsed, dict):
        raise AnalyzerError("Analyzer payload must be a JSON object")
    return parsed


def _normalize_output(payload: dict[str, Any]) -> AnalyzerOutput:
    try:
        narrative_score = float(payload.get("narrative_score"))
        confidence = float(payload.get("confidence"))
    except (TypeError, ValueError) as exc:
        raise AnalyzerError("Analyzer payload must include numeric narrative_score/confidence") from exc

    reasons_raw = payload.get("reasons")
    reasons: list[str] = []
    if isinstance(reasons_raw, list):
        for item in reasons_raw:
            if isinstance(item, str) and item.strip():
                reasons.append(item.strip())

    risk_comment = str(payload.get("risk_comment") or "").strip() or "n/a"
    action_hint = str(payload.get("action_hint") or "").strip() or "n/a"
    if not reasons:
        reasons = ["analyzer_reason_unavailable"]

    return AnalyzerOutput(
        narrative_score=round(_clamp(narrative_score, 0.0, 100.0), 2),
        risk_comment=risk_comment,
        action_hint=action_hint,
        confidence=round(_clamp(confidence, 0.0, 1.0), 2),
        reasons=reasons[:5],
    )
