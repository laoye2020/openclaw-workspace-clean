#!/usr/bin/env python3
import json, time, requests, subprocess, os
from pathlib import Path

API_CUR = "https://api.agentcoin.site/api/problem/current"
API_MIN = "https://api.agentcoin.site/api/mining/status"
BASE = Path('/home/laoye/.openclaw/workspace/skills/agentcoin-mining')
STATE = BASE / 'daemon_state.json'
EVENTS = BASE / 'events.jsonl'

N = 6021
PK = os.getenv('AGC_PRIVATE_KEY','')


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"last_submitted_problem": None, "last_seen_problem": None}

def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False))

def log_event(obj):
    with EVENTS.open('a') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def ds(x):
    return sum(map(int, str(x)))

def solve(template):
    # A: sequence + inverse mod 101
    if 'a_1 = N mod 17' in template and '(a_k * 13 + 7) mod 19' in template:
        a = N % 17
        S = 0
        for _ in range(100):
            S += a
            a = (a * 13 + 7) % 19
        x = S % 101
        for m in range(1, 102):
            if (x * m) % 101 == 1:
                return m

    # B: divisible by 3/5 not both15, mod (N mod 100 + 1)
    if 'divisible by 3 or 5' in template and 'not divisible by 15' in template:
        total = sum(k for k in range(1, N + 1) if ((k % 3 == 0 or k % 5 == 0) and k % 15 != 0))
        return total % (N % 100 + 1)

    # C: digit sum condition + divisible by sum prime factors (6021 => 232)
    if 'sum of the digits of (N * {AGENT_ID})' in template:
        spf = 232
        for i in range(1, 2_000_000):
            v = i * spf
            if ds(v * N) == ds(v):
                return v

    # D: N! divisible by AGENT_ID^3 then post process
    if 'N! is divisible by AGENT_ID^3' in template:
        # 6021 = 3^3 * 223; need in N!: v3>=9 and v223>=3
        def vp_fact(n, p):
            s = 0
            while n:
                n //= p
                s += n
            return s
        n = 1
        while not (vp_fact(n, 3) >= 9 and vp_fact(n, 223) >= 3):
            n += 1
        r = ds(n) % 7
        if r % 2 == 0:
            return r + 2  # distinct prime factors of 6021: {3,223}
        else:
            return r + ds(N)

    # E: n<=1000 divisible by (N mod 17) xor (N mod 23)
    if 'n ≤ 1000' in template and 'AGENT_ID mod 17' in template and 'AGENT_ID mod 23' in template:
        a = N % 17 or 17
        b = N % 23 or 23
        s = 0
        for n in range(1, 1001):
            x = (n % a == 0)
            y = (n % b == 0)
            if x ^ y:
                s += n
        return s

    return None


def submit(problem_id, ans):
    cmd = f'cd {BASE} && AGC_PRIVATE_KEY="{PK}" python3 submit.py {problem_id} {ans}'
    out = subprocess.getoutput(cmd)
    return out


def main():
    if not PK:
        print('Missing AGC_PRIVATE_KEY')
        return
    st = load_state()
    while True:
        try:
            cur = requests.get(API_CUR + f'?t={int(time.time())}', timeout=8).json()
            pid = cur.get('problem_id')
            active = bool(cur.get('is_active'))
            tpl = cur.get('template_text', '')
            st['last_seen_problem'] = pid
            save_state(st)

            if active and pid != st.get('last_submitted_problem'):
                ans = solve(tpl)
                if ans is None:
                    log_event({"ts": int(time.time()), "problem": pid, "status": "unsolved"})
                else:
                    out = submit(pid, ans)
                    ok = "'status': 1" in out or '"status": 1' in out
                    log_event({"ts": int(time.time()), "problem": pid, "answer": ans, "ok": ok, "raw": out[:220]})
                    if ok:
                        st['last_submitted_problem'] = pid
                        save_state(st)
            time.sleep(5)
        except Exception as e:
            log_event({"ts": int(time.time()), "status": "error", "err": str(e)[:180]})
            time.sleep(5)

if __name__ == '__main__':
    main()
