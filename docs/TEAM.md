# Phân công nhóm (cập nhật 22/11/2026)

Bản đầy đủ (mục tiêu, hạn, tiêu chí thành công): `docs/phan_cong.pdf`.

| | TV1 — Hoàng Gia | TV2 — Tiến Thành | TV3 — Thảo Hương |
|---|---|---|---|
| Vai trò | Thuật toán MCTS | Tìm kiếm đối kháng và cờ tướng | Tri thức trò chơi và bài toán thực tế |
| Thuật toán Bài 1 | MCTS (Python + Numba), UCT, chọn theo max N | Minimax, Alpha-Beta, sắp xếp nước, bảng chuyển vị | Luật m,n,k (Numba), hàm lượng giá, rollout heuristic |
| Bonus | Toán học UCT, biến thể UCT, value function | Cờ tướng | Bài 2: xếp lịch thi |
| Hạ tầng | — | Arena, web demo | `plots.py`, CI, tổng biên tập report |
| Thực nghiệm | E2, E3, E4, E5, E6 (chung) | E1, cờ tướng | E6 (chung), Bài 2 |
| Label | `TV1` | `TV2` | `TV3` |

## Thư mục / file thuộc ai

| Đường dẫn | Chủ sở hữu |
|---|---|
| `uctlab/agents/mcts.py`, `uctlab/agents/fast_mcts.py`, `uctlab/value_fn.py` | Hoàng Gia |
| `uctlab/agents/minimax.py`, `uctlab/arena.py`, `uctlab/games/xiangqi*`, `web/` | Tiến Thành |
| `uctlab/games/mnk*.py`, `uctlab/rollouts.py`, `uctlab/scheduling/`, `experiments/plots.py`, `.github/`, `report/main.tex` | Thảo Hương |
| `uctlab/games/base.py`, `uctlab/agents/base.py`, `docs/` | Cả nhóm (sửa phải có 2 người duyệt) |

## Phụ thuộc Sprint 1

| Giao | Nhận | Nội dung | Hạn |
|---|---|---|---|
| Thảo Hương | Hoàng Gia | `is_winning_move` Numba + rollout ngẫu nhiên | 23/11 |
| Thảo Hương | Tiến Thành | Hàm lượng giá cửa sổ k ô | 24/11 |
| Tiến Thành | Cả nhóm | Arena đầy đủ | 24/11 |
| Hoàng Gia | Tiến Thành, Thảo Hương | Agent MCTS đúng hợp đồng API | 26/11 |

## Review chéo

Hoàng Gia → Tiến Thành → Thảo Hương → Hoàng Gia (người bên phải review PR của người bên trái).
