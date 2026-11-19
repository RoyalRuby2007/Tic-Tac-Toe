# Các quyết định của nhóm (chốt ngày 19/11)
| # | Vấn đề | Quyết định | Lý do |
|---|--------|------------|-------|
| 1 | Ngôn ngữ | Python 3.11–3.13 + Numba | Code dễ đọc khi vấn đáp; đủ nhanh cho hàng nghìn ván |
| 2 | Luật 5 quân | Bàn m×n, k=5, ≥5 quân liên tiếp là thắng (freestyle) | Đề không nói rõ |
| 3 | Kích thước bàn | Thí nghiệm 9×9, demo 15×15 | 15×15 chạy thí nghiệm quá chậm |
| 4 | Điểm của một ván | Thắng 1 / hoà 0.5 / thua 0 | Đúng giả thiết phần thưởng trong [0, 1] của UCB1 |
| 5 | Đấu nhiều ván | ≥100 ván, đổi người đi trước; khai cuộc ngẫu nhiên theo cặp | Tránh lặp lại cùng một ván |
| 6 | Bonus | Làm hết; thứ tự ưu tiên: toán UCT > biến thể > cờ tướng > Bài 2 | Phòng khi bị trễ |
| 7 | Hạn nộp nội bộ | 9/12 (hạn thật 10/12) | Giữ 1 ngày dự phòng |