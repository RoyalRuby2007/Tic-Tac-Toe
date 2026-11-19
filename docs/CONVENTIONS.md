## Quy ước
- Bàn m×n lưu thành mảng 1 chiều np.int8; ô (r, c) ở chỉ số r*n + c; 0 = trống, 1 = X, 2 = O
- Nước đi của trò chơi m,n,k là chỉ số ô (int); của cờ tướng là from*90 + to
- Kết quả thí nghiệm: results/<tên>.json, mỗi cấu hình ghi
  {"config": {...}, "win": .., "draw": .., "loss": .., "score": .., "n": .., "a_time_per_move": ..}
- Agent khai báo bằng dict để chạy được trong tiến trình con:
  {"type": "mcts" | "fast" | "minimax" | "random", ...tham số}
- Tên nhánh: feat/<việc>, fix/<lỗi>; commit viết tiếng Việt hoặc tiếng Anh đều được, nhưng rõ nghĩa