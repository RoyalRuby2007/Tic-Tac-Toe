"""Trang web kiểm tra trực quan cho BTL AI (chạy trên máy, không cần Internet).

    uv run python web/server.py          # tự mở http://localhost:8000

Ba chức năng:
  * Chơi:      người / Random / MCTS / Minimax / Alpha-Beta trên 3x3, 9x9, 15x15;
               sau mỗi nước của MCTS hiện bảng N, W, W/N, UCT và bản đồ nhiệt N.
  * Kiểm tra:  chạy toàn bộ pytest, hiện từng test xanh/đỏ.
  * Đấu thử:   cho 2 agent đấu N ván (dùng Arena nếu đã có), hiện thắng/hoà/thua.

Trang tự phát hiện module nào đã có trong repo, nên dùng được ở mọi mốc:
module chưa merge sẽ hiện "chưa có" thay vì làm hỏng trang.
API không lưu trạng thái: trình duyệt gửi lịch sử nước đi mỗi lần.
"""
import importlib
import json
import math
import os
import random
import re
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, "web", "static")
sys.path.insert(0, ROOT)

from uctlab.games.base import ONGOING, DRAW          # noqa: E402
from uctlab.games.mnk import MNKState                 # noqa: E402

BOARDS = {"3x3": (3, 3), "9x9": (9, 5), "15x15": (15, 5)}
LOCK = threading.Lock()


# ------------------------------------------------------------ phát hiện module
def try_import(module, name):
    try:
        return getattr(importlib.import_module(module), name)
    except Exception:
        return None


def available():
    """Agent / module nào đã có trong repo. Sau khi git pull, tắt và mở lại server."""
    return {
        "random": try_import("uctlab.agents.random_agent", "RandomAgent"),
        "mcts": try_import("uctlab.agents.mcts", "MCTSAgent"),
        "fast_mcts": try_import("uctlab.agents.fast_mcts", "FastMCTSAgent"),
        "minimax": try_import("uctlab.agents.minimax", "MinimaxAgent"),
        "alphabeta": try_import("uctlab.agents.minimax", "AlphaBetaAgent"),
        "arena": try_import("uctlab.arena", "play_match"),
    }


# ------------------------------------------------------------ trò chơi
def build_state(size, history):
    n, k = BOARDS[size]
    s = MNKState(n, n, k)
    for mv in history:
        s.play(int(mv))
    return s


def describe(size, history):
    """Dựng bàn cờ từ lịch sử (không phụ thuộc cách MNKState lưu bên trong)."""
    s = build_state(size, history)
    n, k = BOARDS[size]
    board = [0] * (n * n)
    for i, mv in enumerate(history):
        board[int(mv)] = 1 if i % 2 == 0 else 2
    res = s.result()
    return {"size": n, "k": k, "board": board, "player": s.player,
            "result": None if res == ONGOING else int(res),
            "legal": [int(m) for m in s.legal_moves()],
            "names": [s.move_str(i) for i in range(n * n)]}


def make_agent(spec, seed=None):
    av = available()
    kind = spec.get("type")
    it = int(spec.get("iterations", 2000))
    c = float(spec.get("c", 1.4))
    depth = spec.get("depth")
    depth = None if depth in (None, "", "full") else int(depth)
    if kind == "random":
        try:
            return av["random"](seed=seed)
        except TypeError:
            return av["random"]()
    if kind == "mcts":
        return av["mcts"](iterations=it, c=c, seed=seed)
    if kind == "fast_mcts":
        return av["fast_mcts"](iterations=it, c=c, seed=seed)
    if kind == "minimax":
        return av["minimax"](depth=depth)
    if kind == "alphabeta":
        return av["alphabeta"](depth=depth)
    raise ValueError(f"agent không hợp lệ: {kind}")


def root_table(agent, c):
    """Bảng thống kê gốc của MCTS: đọc thẳng agent.root (nếu có)."""
    root = getattr(agent, "root", None)
    kids = getattr(root, "children", None) if root is not None else None
    if not kids:
        return None
    total = max(getattr(root, "N", sum(ch.N for ch in kids)), 1)
    rows = []
    for ch in kids:
        q = ch.W / ch.N if ch.N else 0.0
        u = q + c * math.sqrt(math.log(total) / ch.N) if ch.N else float("inf")
        rows.append({"move": int(ch.move), "N": int(ch.N), "W": round(float(ch.W), 2),
                     "Q": round(q, 3), "UCT": round(u, 3)})
    rows.sort(key=lambda r: -r["N"])
    return rows


def ai_move(size, history, spec):
    if spec["type"] in ("minimax", "alphabeta") and size != "3x3" and not spec.get("depth"):
        return {"error": "Bàn lớn không duyệt hết cây được: hãy nhập độ sâu (ví dụ 2)."}
    s = build_state(size, history)
    if s.result() != ONGOING:
        return {"error": "Ván đã kết thúc."}
    agent = make_agent(spec, seed=int(spec.get("seed", random.randrange(10**6))))
    t0 = time.perf_counter()
    with LOCK:
        mv = agent.select_move(s.clone())
    dt = time.perf_counter() - t0
    info = getattr(agent, "info", {}) or {}
    out = {"move": int(mv), "time": round(dt, 3), "agent": getattr(agent, "name", spec["type"]),
           "nodes": info.get("nodes", getattr(agent, "nodes", None)),
           "value": info.get("value")}
    if spec["type"] in ("mcts", "fast_mcts"):
        out["table"] = root_table(agent, float(spec.get("c", 1.4)))
        out["iterations"] = int(spec.get("iterations", 0))
    return out


# ------------------------------------------------------------ kiểm tra & đấu thử
def run_pytest(target):
    target = target if re.fullmatch(r"[\w/\\.\-]*", target or "") else ""
    cmd = [sys.executable, "-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider", target or "tests"]
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600,
                           encoding="utf-8", errors="replace")
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return {"error": "Quá 10 phút, đã dừng."}
    tests = []
    for line in out.splitlines():
        m = re.match(r"^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\s+(\S+)(?:\s+-\s+(.*))?", line)
        if m:
            tests.append({"status": m.group(1), "name": m.group(2), "msg": m.group(3) or ""})
    summary = out.strip().splitlines()[-1] if out.strip() else ""
    return {"tests": tests, "summary": summary, "time": round(time.perf_counter() - t0, 1),
            "output": out[-6000:]}


def run_match(size, spec_a, spec_b, n_games):
    n_games = max(2, min(int(n_games), 400))
    make_game = lambda: build_state(size, [])                  # noqa: E731
    make_a = lambda sd: make_agent(spec_a, seed=sd)            # noqa: E731
    make_b = lambda sd: make_agent(spec_b, seed=sd)            # noqa: E731
    av = available()
    t0 = time.perf_counter()
    if av["arena"]:
        r = av["arena"](make_game, make_a, make_b, n_games, seed=0, workers=1)
        res = {"a_wins": r["a_wins"], "draws": r["draws"], "a_losses": r["a_losses"],
               "x_wins": r.get("x_wins"), "o_wins": r.get("o_wins"), "via": "uctlab.arena"}
    else:                                                       # Arena chưa merge: vòng lặp đơn giản
        w = d = l = 0
        for i in range(n_games):
            a, b = make_a(i), make_b(10**6 + i)
            x, o = (a, b) if i % 2 == 0 else (b, a)
            s = make_game()
            while s.result() == ONGOING:
                s.play((x if s.player == 1 else o).select_move(s.clone()))
            a_col = 1 if i % 2 == 0 else 2
            if s.result() == DRAW:
                d += 1
            elif s.result() == a_col:
                w += 1
            else:
                l += 1
        res = {"a_wins": w, "draws": d, "a_losses": l, "via": "vòng lặp tạm (Arena chưa có)"}
    res["n_games"] = n_games
    res["time"] = round(time.perf_counter() - t0, 2)
    return res


# ------------------------------------------------------------ HTTP
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=STATIC, **kw)

    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/modules":
            av = available()
            return self.send_json({k: v is not None for k, v in av.items()})
        return super().do_GET()

    def do_POST(self):
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/api/state":
                return self.send_json(describe(body["size"], body.get("history", [])))
            if self.path == "/api/move":
                return self.send_json(ai_move(body["size"], body.get("history", []), body["agent"]))
            if self.path == "/api/pytest":
                return self.send_json(run_pytest(body.get("target", "")))
            if self.path == "/api/match":
                return self.send_json(run_match(body["size"], body["a"], body["b"], body.get("n", 20)))
            self.send_json({"error": "không có API này"}, 404)
        except Exception as e:                                  # lỗi hiện lên trang, không làm sập server
            self.send_json({"error": f"{type(e).__name__}: {e}",
                            "trace": traceback.format_exc()[-2500:]}, 200)


def main():
    port = int(os.environ.get("PORT", 8000))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"Mở {url}  (Ctrl + C để tắt)")
    if not os.environ.get("NO_BROWSER"):
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã tắt.")


if __name__ == "__main__":
    main()
