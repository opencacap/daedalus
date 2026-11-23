# Giải lựa chọn phong cách khi chưa rõ hoặc pha chức năng

Chỉ đọc khi bảng mục đích của core chưa đủ, tức là khi ngữ cảnh thiếu/mâu thuẫn hoặc tài liệu pha chức năng.
Không đọc file này như điều kiện bắt buộc trước mọi câu sửa. Core sở hữu quyền sửa, dữ liệu,
vùng bảo toàn và năm chốt; resolver chỉ chọn cách viết giữa các lựa chọn còn hợp lệ.

## Giải năm chiều

1. Mục đích: kể, phối hợp, giải thích, thuyết phục, hướng dẫn, vận hành hay phân tích học thuật?
2. Người đọc/quan hệ: ai đọc, cần làm gì, đại từ nào có bằng chứng? Không tự đoán vai vế.
3. Thanh ngữ vực: thân mật, nghề nghiệp, trung tính hay trang trọng; xét cả phần thay vì một từ.
4. Kênh và quy ước: chat, bài công khai, marketing, tra cứu, SOP hay bài học thuật?
5. Bằng chứng giọng: yêu cầu hiện tại, mẫu/hồ sơ được giao đúng phạm vi; không tự tìm/lưu memory.

Yêu cầu cụ thể hiện tại đứng trước nhãn chung hoặc hồ sơ cũ. Core và cổng thể loại là bất biến;
mẫu đúng phạm vi đứng trước card, card trước mặc định profile. Chỉ đưa mẫu không bật chuyển giọng.
Thân mật/chuyên nghiệp là nhãn gợi chọn, không phủ quyết mô tả cụ thể. Bộ tham chiếu chuyên môn
không tự là giọng cá nhân; rút nét theo guide mẫu nếu có mẫu, không nạp mọi phương án để chọn sau.

## Chia phần và chọn card

Giữ vùng bảo toàn trước. Chia khi mục đích, người đọc hoặc người nói đổi; heading/độ dài không tự
chia phần. Vai trò nhỏ như định nghĩa hoặc đối chiếu trong cùng phần không tạo profile mới.
Chọn một card tương thích mỗi phần; không đem nhịp/đại từ/CTA của phần này sang phần khác.
Blog công nghệ có tác giả vẫn thuộc blog; README/SOP/tra cứu giữ kỹ thuật dù mẫu thân mật.
Typography-only không có card. Đọc thêm rules B/K chỉ khi có nghi vấn phụ thuộc thể loại, không
vì đã chọn một card mà tự nạp toàn profile. Không cần cài đủ nét của card vào bài.

Giữ tóm tắt ngắn trong quá trình làm, gồm phần, mục đích/người đọc, giọng đích/chế độ, card, nét có
bằng chứng và điều phải giữ. Không in phân tích định tuyến vào bài. Đủ căn cứ thì làm; thiếu chỉ
ảnh hưởng lựa chọn nhỏ thì giữ cách phù hợp đang có; thiếu làm đổi quan hệ/giọng đáng kể mới hỏi
đúng một điểm và dừng phần phụ thuộc. Đại từ đã nhất quán không cần hỏi lại để đổi.
Mẫu khác kênh không được trộn thành giọng trung bình; hồ sơ không đúng người/phạm vi thì không dùng.

## Họ thể loại

| Họ | Phạm vi | Catalog chẩn đoán |
|---|---|---|
| `personal-blog` | Có tác giả/chat/marketing | Pattern B1–B17 ở profiles/personal-blog/rules.md |
| `enterprise-technical` | Tra cứu/vận hành/học thuật | Pattern K1–K7 ở profiles/enterprise-technical/rules.md |

## Registry card

| Style card | Base profile | File |
|---|---|---|
| `personal-narrative` | `personal-blog` | `profiles/personal-blog/styles/personal-narrative.md` |
| `work-coordination` | `personal-blog` | `profiles/personal-blog/styles/work-coordination.md` |
| `public-expertise` | `personal-blog` | `profiles/personal-blog/styles/public-expertise.md` |
| `persuasive-marketing` | `personal-blog` | `profiles/personal-blog/styles/persuasive-marketing.md` |
| `technical-guide` | `enterprise-technical` | `profiles/enterprise-technical/styles/technical-guide.md` |
| `business-operations` | `enterprise-technical` | `profiles/enterprise-technical/styles/business-operations.md` |
| `academic-analysis` | `enterprise-technical` | `profiles/enterprise-technical/styles/academic-analysis.md` |

Đọc đúng card được chọn, không đọc các card khác chỉ để so. Card chỉ hỗ trợ nhịp, xưng hô,
thuật ngữ và cách kết trong phạm vi hợp lệ, không sở hữu pattern hoặc thêm quyền sửa. Metadata
card giữ tám mục Dùng khi/Thanh ngữ vực/Xưng hô/Nhịp/Thuật ngữ/Cách kết/Không tự thêm/Ca kiểm thử;
đó là hợp đồng bảo trì, không phải checklist bắt mỗi bài mang đủ tám nét. Không tạo card cá nhân/công ty.
