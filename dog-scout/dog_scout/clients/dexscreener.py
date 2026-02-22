from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import requests

from dog_scout.models import PairSnapshot

logger = logging.getLogger(__name__)


class DexscreenerClient:
    """Thin Dexscreener client for latest tokens + token pairs."""

    base_url = "https://api.dexscreener.com"

    def __init__(self, timeout_seconds: int = 10) -> None:
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def _get_json(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.warning("Dexscreener request failed: %s (%s)", url, exc)
            return None
        except ValueError as exc:
            logger.warning("Dexscreener JSON decode failed: %s (%s)", url, exc)
            return None

    def fetch_latest_base_tokens(self, max_tokens: int) -> list[str]:
        payload = self._get_json("/token-profiles/latest/v1")
        if not isinstance(payload, list):
            return []

        token_addresses: list[str] = []
        seen: set[str] = set()
        for item in payload:
            if not isinstance(item, dict):
                continue
            chain_id = str(item.get("chainId", "")).lower()
            token_address = str(item.get("tokenAddress", "")).strip()
            if chain_id != "base" or not token_address:
                continue
            token_address_lc = token_address.lower()
            if token_address_lc in seen:
                continue
            seen.add(token_address_lc)
            token_addresses.append(token_address)
            if len(token_addresses) >= max_tokens:
                break
        return token_addresses

    def fetch_token_pairs(self, chain_id: str, token_address: str) -> list[PairSnapshot]:
        payload = self._get_json(f"/token-pairs/v1/{chain_id}/{token_address}")
        if not isinstance(payload, list):
            return []

        parsed: list[PairSnapshot] = []
        for pair in payload:
            parsed_pair = self._parse_pair(pair)
            if parsed_pair is not None:
                parsed.append(parsed_pair)
        return parsed

    def fetch_new_pairs(self, chain_id: str, max_tokens: int) -> list[PairSnapshot]:
        if chain_id.lower() != "base":
            logger.warning("Day-1 client is Base-focused; requested chain=%s", chain_id)

        token_addresses = self.fetch_latest_base_tokens(max_tokens=max_tokens)
        if not token_addresses:
            logger.warning("No latest base token profiles returned from Dexscreener")
            return []

        output: list[PairSnapshot] = []
        for token_address in token_addresses:
            pairs = self.fetch_token_pairs(chain_id=chain_id, token_address=token_address)
            if not pairs:
                continue
            newest = sorted(
                pairs,
                key=lambda p: p.pair_created_at or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True,
            )[0]
            output.append(newest)
        return output

    @staticmethod
    def _parse_pair(payload: Any) -> PairSnapshot | None:
        if not isinstance(payload, dict):
            return None

        try:
            chain_id = str(payload.get("chainId", "")).lower()
            pair_address = str(payload.get("pairAddress", "")).strip()
            dex_id = str(payload.get("dexId", "")).strip() or "unknown"
            base = payload.get("baseToken") or {}
            quote = payload.get("quoteToken") or {}
            liquidity = payload.get("liquidity") or {}
            txns = payload.get("txns") or {}
            txns_h1 = txns.get("h1") or {}
            price_change = payload.get("priceChange") or {}

            if not pair_address:
                return None

            pair_created = payload.get("pairCreatedAt")
            created_dt: datetime | None = None
            if isinstance(pair_created, (int, float)):
                created_dt = datetime.fromtimestamp(pair_created / 1000.0, tz=timezone.utc)

            return PairSnapshot(
                chain_id=chain_id,
                pair_address=pair_address,
                dex_id=dex_id,
                base_token_address=str(base.get("address", "")).strip(),
                base_token_symbol=str(base.get("symbol", "")).strip() or "UNKNOWN",
                quote_token_symbol=str(quote.get("symbol", "")).strip() or "UNKNOWN",
                price_usd=float(payload.get("priceUsd") or 0.0),
                liquidity_usd=float(liquidity.get("usd") or 0.0),
                volume_h24=float(payload.get("volume", {}).get("h24") or 0.0),
                txns_h1_buys=int(txns_h1.get("buys") or 0),
                txns_h1_sells=int(txns_h1.get("sells") or 0),
                price_change_h1=(
                    float(price_change["h1"])
                    if price_change.get("h1") is not None
                    else None
                ),
                price_change_h24=(
                    float(price_change["h24"])
                    if price_change.get("h24") is not None
                    else None
                ),
                pair_created_at=created_dt,
                raw=payload,
            )
        except (TypeError, ValueError, KeyError):
            logger.debug("Failed to parse pair payload", exc_info=True)
            return None
