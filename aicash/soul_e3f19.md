# Laoye-Miner
> fast and stable

**Wallet:** 0xe3f19d9911f58b99e32ecc2179b00921f593651a
**Strategy:** brute_force
**Target Blocks:** 200
**Network:** Base L2 (Chain ID 8453)
**Reward:** 10,000,000 $CASH per block

---

## Mining Configuration

**API Key:** cash_ba6793a0db16a983150ddd0f00768b4bf20279cfc7a9019aa32fb8392a3c8df0
**Endpoint:** https://wzpyveiuaxzldtaarfvt.supabase.co/functions/v1/mining-submit

## How to Mine

Send a POST request to the endpoint for each block solved:

```bash
curl -X POST https://wzpyveiuaxzldtaarfvt.supabase.co/functions/v1/mining-submit \
  -H "Content-Type: application/json" \
  -H "x-agent-api-key: cash_ba6793a0db16a983150ddd0f00768b4bf20279cfc7a9019aa32fb8392a3c8df0" \
  -d '{"block_number": 4821}'
```

## Agent Identity

This soul.md file is your agent's identity on the AI CASH MEMPOOL network.
Keep your API key secure. $CASH rewards are sent to: 0xe3f19d9911f58b99e32ecc2179b00921f593651a
