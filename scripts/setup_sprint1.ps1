# Tạo milestone, label, 11 issue của Sprint 1 và Project board (chạy 1 lần)
$ErrorActionPreference = "Stop"
$Repo  = "RoyalRuby2007/Tic-Tac-Toe"
$Owner = "RoyalRuby2007"
$TV1   = "RoyalRuby2007"
$TV2   = "ngtrthhg"    
$TV3   = "Sun-Coder-2812"   
$M1    = "M1: Lõi chạy đúng"

# 1) Label
gh label create "sprint-1" --repo $Repo --color "0E8A16" --force
gh label create "TV1" --repo $Repo --color "5319E7" --description "Thuật toán" --force
gh label create "TV2" --repo $Repo --color "1D76DB" --description "Trò chơi" --force
gh label create "TV3" --repo $Repo --color "D93F0B" --description "Hạ tầng" --force

# 2) Milestone M1, hạn 27/11
gh api "repos/$Repo/milestones" -f title="$M1" -f due_on="2026-11-27T16:59:59Z" `
  -f description="Mọi thuật toán bắt buộc qua checkpoint" | Out-Null

# 3) Project board
$proj = gh project create --owner $Owner --title "BTL AI - Sprint board" --format json | ConvertFrom-Json
$PN = $proj.number
gh project link $PN --owner $Owner --repo $Repo

# 4) Danh sách issue: tiêu đề | người làm | label | nội dung
$issues = @(
  @("Luật m,n,k bản Numba (is_winning_move O(k), play/undo)", $TV2, "TV2",
    "**Checkpoint:** 50 000 ván Random vs Random trên 3x3 ra X ~58.5%, O ~28.8%, hoà ~12.7%."),
  @("Minimax (negamax) + đếm nút", $TV2, "TV2",
    "**Checkpoint:** duyệt toàn cây 3x3 = 549 946 nút, giá trị 0 (hoà).`n**Hạn:** 24/11"),
  @("Alpha-Beta + sắp xếp nước + bảng chuyển vị + hàm lượng giá cửa sổ", $TV2, "TV2",
    "**Checkpoint:** cùng giá trị với Minimax trên thế cờ ngẫu nhiên; 3x3 còn ~1 083 nút."),
  @("MCTS bản Python (4 bước)", $TV1, "TV1",
    "**Checkpoint:** tổng N các con của gốc = số iteration; thế cờ ví dụ trong đề -> c1."),
  @("Bộ test MCTS", $TV1, "TV1",
    "Test: bảo toàn số lượt N, tìm nước thắng/chặn, thế cờ ví dụ, so sánh bản Python với Minimax/Alpha-Beta."),
  @("MCTS bản Numba (cây dạng mảng)", $TV1, "TV1",
    "**Checkpoint:** cùng nước đi với bản Python, tỉ lệ lượt thăm lệch < 5%; đo tốc độ (iterations/s)."),
  @("Tham số mở rộng cho Sprint 2 + spec agent cho arena", $TV1, "TV1",
    "Thêm sẵn formula / rollout / final / solver (tạm chỉ cài UCB1 + rollout ngẫu nhiên)."),
  @("Arena đầy đủ: song song, đổi lượt, khai cuộc ngẫu nhiên theo cặp, ghi JSON", $TV3, "TV3",
    "**Checkpoint:** 1 000 ván Random vs Random ra tỉ lệ gần 58.5/28.8/12.7; kết quả ghi vào results/."),
  @("plots.py dùng chung", $TV3, "TV3",
    "Đọc results/*.json, xuất hình PDF + PNG vào report/figures; một hàm cho đồ thị tỉ lệ thắng."),
  @("Dàn ý chi tiết các mục report + quản lý refs.bib", $TV3, "TV3",
    "Mỗi file sections/*.tex có dàn ý 3-5 dòng và người phụ trách; CI report xanh.`n**Hạn:** 27/11"),
  @("Họp tuần 27/11: demo checkpoint M1", $TV1, "TV1",
    "Mỗi người demo checkpoint của mình chạy thật trên máy. Chốt kế hoạch Sprint 2.`n**Hạn:** 27/11")
)

foreach ($it in $issues) {
  $url = gh issue create --repo $Repo --title $it[0] --body $it[3] `
    --assignee $it[1] --label "sprint-1" --label $it[2] --milestone "$M1"
  gh project item-add $PN --owner $Owner --url $url | Out-Null
  Write-Host "Đã tạo: $url"
}
Write-Host "Xong. Mở board: https://github.com/users/$Owner/projects/$PN"