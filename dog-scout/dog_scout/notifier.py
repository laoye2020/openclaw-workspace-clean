from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

from dog_scout.config import Settings
from dog_scout.models import Candidate, ScoreTimeline

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class NotificationResult:
    sent: bool
    status: str


class TelegramNotifier:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()

    def send_message(self, message: str) -> NotificationResult:
        if self.settings.dry_run or not self.settings.telegram_enabled:
            print(message)
            return NotificationResult(sent=False, status="dry_run")

        if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
            logger.error("Telegram enabled but token/chat id missing")
            return NotificationResult(sent=False, status="config_error")

        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.settings.telegram_chat_id,
            "text": message,
            "disable_web_page_preview": True,
        }

        try:
            response = self.session.post(
                url,
                json=payload,
                timeout=self.settings.request_timeout_seconds,
            )
            response.raise_for_status()
            return NotificationResult(sent=True, status="sent")
        except requests.RequestException as exc:
            logger.warning("Telegram send failed: %s", exc)
            return NotificationResult(sent=False, status="send_failed")


def format_telegram_message(rank: int, candidate: Candidate) -> str:
    pair = candidate.pair
    score = candidate.score
    risk_flags = "、".join(candidate.risk.risk_flags) if candidate.risk.risk_flags else "无"
    price_move = "n/a" if pair.price_change_h1 is None else f"{pair.price_change_h1:.2f}%"
    txns_h1 = pair.txns_h1_buys + pair.txns_h1_sells
    timeline_line = format_score_timeline_line(
        ScoreTimeline(initial_score=score.rule_score or score.final_score)
    )

    if score.final_score >= 85:
        action = "高优先：可加入观察列表，等待回踩或放量确认"
    elif score.final_score >= 65:
        action = "中优先：继续观察，不追高"
    else:
        action = "低优先：仅记录，不建议出手"

    return (
        f"🎯 土狗雷达 Top{rank} | 综合分 {score.final_score:.2f}/100\n"
        f"代币：{pair.base_token_symbol} ({pair.base_token_address})\n"
        f"池子：{pair.pair_address} | DEX: {pair.dex_id}\n"
        f"流动性：${pair.liquidity_usd:,.0f} | 1H成交笔数：{txns_h1}\n"
        f"1H动量：{price_move} | 24H成交额：${pair.volume_h24:,.0f}\n"
        f"{timeline_line}\n"
        f"风险标记：{risk_flags}\n"
        f"建议：{action}\n"
        f"链接：https://dexscreener.com/{pair.chain_id}/{pair.pair_address}"
    )


def format_recheck_summary_message(
    candidate: Candidate,
    status: str,
    timeline: ScoreTimeline,
    delta_from_initial: float,
    delta_from_previous: float,
) -> str:
    pair = candidate.pair
    score = candidate.score
    risk_flags = "、".join(candidate.risk.risk_flags) if candidate.risk.risk_flags else "无"
    timeline_line = format_score_timeline_line(timeline)

    return (
        f"🔁 Recheck | {pair.base_token_symbol} | {status}\n"
        f"综合分：{score.final_score:.2f}/100 (较首发 {delta_from_initial:+.2f}, 较上次 {delta_from_previous:+.2f})\n"
        f"{timeline_line}\n"
        f"风险标记：{risk_flags}\n"
        f"链接：https://dexscreener.com/{pair.chain_id}/{pair.pair_address}"
    )


def format_score_timeline_line(timeline: ScoreTimeline) -> str:
    return (
        "首发分 -> 5m分 -> 15m分："
        f"{_fmt_score(timeline.initial_score)} -> {_fmt_score(timeline.score_5m)} -> {_fmt_score(timeline.score_15m)}"
    )


def _fmt_score(score: float | None) -> str:
    if score is None:
        return "--"
    return f"{score:.2f}"
