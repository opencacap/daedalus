---
type: vietnamizer-ai-error-lexicon
schema: 1
---

# Bảng dạng lỗi AI đã gặp

Bảng này ghi những dạng lỗi AI đã gặp nhiều lần, mỗi dòng một dạng, kèm pattern sở hữu, cách sửa và trường hợp giữ nguyên. Thấy một dạng trong bài chỉ có nghĩa là có một ứng viên cần xét, chưa phải chỗ phải sửa. Bảng không phải cách tìm lỗi. Lỗi cùng loại trong một bài mới thường mang dạng khác, nên bài không khớp dòng nào vẫn chưa chắc đã sạch và vẫn phải rà catalog như thường.

Trước khi sửa một ứng viên, đọc cột Không flag của dòng đó và mục Không flag của pattern sở hữu. Chỉ sửa khi cả hai đều không cho giữ.

Bảng chỉ áp cho văn xuôi ngoài nhánh chỉ rà soát T1–T6.

Cột Sau không là và Trước không là ghi những tiếng đứng ngay sau hoặc ngay trước dạng đó mà khi gặp thì dạng ấy là một phần của từ khác, nên không thành ứng viên. Dấu — nghĩa là không có tiếng nào bị loại. Cột Chữ hoa ghi `đầu câu` khi chỉ xét dạng viết hoa ở đầu câu, đầu dòng liệt kê, sau `>` hoặc sau dấu hai chấm, chấm phẩy, gạch ngang; ghi `mọi` khi xét ở mọi vị trí.

## Bảng

| ID | Dạng | Loại | Pattern | Sửa | Ngữ vực lỗi | Sau không là | Trước không là | Chữ hoa | Không flag | Ca |
|---|---|---|---|---|---|---|---|---|---|---|
| L01 | rườm | từ ghép bị cắt | V20 | rườm rà | Văn viết: bài đăng, báo cáo, hướng dẫn, bài chuyên môn | rà | — | mọi | Văn nói, chat và lời thoại trích nguyên văn | HF02, HF10, HF09 |
| L02 | bỡ | từ ghép bị cắt | V20 | bỡ ngỡ | Văn viết: bài đăng, báo cáo, hướng dẫn, bài chuyên môn | ngỡ | — | mọi | Văn nói, chat và lời thoại trích nguyên văn | HF10, HF09 |
| L03 | giữ nghĩa | từ ghép bị cắt | V20 | giữ ngữ nghĩa / giữ nguyên nghĩa | Giới thiệu sản phẩm, hướng dẫn, bài chuyên môn | vụ, tình, cử, khí | — | mọi | Câu trang trọng đã đủ ý, như *Bản dịch giữ nghĩa của nguyên tác.*; chat và văn nói | HF11, HF17 |
| L04 | giữ giọng | từ ghép bị cắt | V20 | giữ giọng văn | Giới thiệu sản phẩm, hướng dẫn, bài chuyên môn | văn, nói, điệu | — | mọi | Chat, văn nói và nhãn giao diện ngắn như nút *Giữ giọng* | HF11, HF12, HF16 |
| L05 | nghĩa và giọng | từ ghép bị cắt | V20 | ngữ nghĩa và giọng văn | Giới thiệu sản phẩm, hướng dẫn, bài chuyên môn | văn, nói, điệu | ngữ, ý | mọi | Chat và văn nói | HF11, HF12 |
| L06 | gọi tên | dịch sát | V9 | xác định / chỉ đích danh / nêu tên | Văn viết: bài đăng, báo cáo, hướng dẫn, bài chuyên môn | — | — | mọi | *Gọi tên* theo nghĩa đen, như *cô giáo gọi tên từng học sinh*; cách nói đã quen như *gọi tên cảm xúc* | HF11, HF14, HF13 |
| L07 | dịch sát | từ nghề hiểu sai | V19 | dịch thô | Văn bản cho người ngoài nghề: giới thiệu sản phẩm, hướng dẫn, bài đăng | nghĩa | — | mọi | Người đọc là người trong nghề, như ghi chú nội bộ cho biên tập viên | HF11, HF15 |
| L08 | đội | danh từ tập thể đứng trơ | V20 | đội ngũ / cả đội / tên đội cụ thể | Bài đăng công việc, bài giới thiệu, báo cáo | ngũ, trưởng, viên, hình, quân, tuyển, bóng, nhóm, tàu, xe, bay, lân, mũ, nón, ơn, lốt, sổ, vốn, giá | — | đầu câu | Đã có định ngữ hoặc ngữ cảnh đã cho biết đội nào, như *đội IT*, *đội của chị Lan*; *đội* là động từ, như *đội mũ*; chỉ dùng *cả đội* khi ngữ cảnh nói về toàn đội | HF07, HF08 |

## Thêm mục

Chỉ thêm dòng khi có bằng chứng. Trước hết ghi lỗi vào `calibration/LOG.md`, rồi thêm ít nhất một ca lỗi và một ca chống sửa quá tay vào `calibration/test-cases.md`, cùng fixture tương ứng trong `tests/fixtures/lexicon/fixtures.json`; sau đó mới thêm dòng. Mỗi dòng gắn với một pattern V hoặc T đã có, không tạo số pattern mới, và phải có cách sửa, ngữ vực lỗi và Không flag. Sở thích riêng của một người viết thuộc về hồ sơ giọng của người đó, không đưa vào bảng này.
