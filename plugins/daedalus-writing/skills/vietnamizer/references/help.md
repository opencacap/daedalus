# Hướng dẫn dùng và thiết lập giọng

Đọc khi người dùng hỏi Vietnamizer làm được gì, hỏi cách dùng Vietnamizer, gõ `/daedalus-writing:vietnamizer hướng dẫn` (Claude
Code), hoặc nói “bắt đầu dùng Vietnamizer”, “thiết lập giọng”. Yêu cầu sửa hay viết có chữ “giúp” hoặc
“hướng dẫn” (“sửa giúp email này”, “viết hướng dẫn cài đặt”) vẫn là việc biên tập hay viết, không vào
file này. Phần hướng dẫn không đọc file của người dùng, không tìm hồ sơ và không lưu gì. Trả
lời bằng tiếng Việt, gọn trong một màn hình.

## 1. Hướng dẫn một màn hình

Trình bốn ý, mỗi ý kèm một câu yêu cầu mẫu, rồi mời bắt đầu:

1. **Biên tập và viết.** Sửa bản nháp, bản dịch hay bài AI còn gượng; giữ nghĩa và giọng hiện có. Viết
   mới từ ý hoặc dàn ý. Ví dụ: “Sửa giúp email này cho tự nhiên hơn.”
2. **Chọn giọng.** Mặc định giữ giọng của chính người viết. Có thể gọi bằng tên một hồ sơ giọng cá nhân
   hoặc một hồ sơ giọng thương hiệu; mỗi lần chỉ dùng một hồ sơ. Gọi lại hồ sơ đã lưu bằng
   `/daedalus-writing:vietnamizer <tên>` (Claude Code cài qua plugin; cài skill riêng thì `/vietnamizer <tên>`),
   `$vietnamizer <tên>` (Codex) hoặc câu “theo hồ sơ <tên>”; cùng lệnh ấy với `cá nhân` hay câu “theo giọng của tôi” dùng hồ sơ cá nhân mặc định. Sau mỗi lần lưu, skill
   in đúng câu cần gõ. Trên Chat không có file (claude.ai bản web, Desktop, Mobile và Cowork chạy trên cloud), hồ sơ lưu được dưới dạng bản gọn trong
   bộ nhớ của Chat. Ví dụ: “Viết lại bài này theo hồ sơ `giong-cong-viec`.”
3. **Học giọng.** Dán 10–20 bài tự viết, đưa file export LinkedIn hoặc Facebook, hoặc để Vietnamizer
   đọc trang của chính bạn qua trình duyệt nếu host có công cụ đó (có cảnh báo điều khoản của LinkedIn và Facebook).
   Giọng thương hiệu học từ bộ quy chuẩn, bài đã đăng và tài liệu nội bộ người dùng đưa, hoặc đọc fanpage,
   trang công ty LinkedIn hay blog của thương hiệu qua trình duyệt từ URL người dùng đưa. Ví dụ: “Học
   giọng viết LinkedIn của tôi.”
4. **Kiểm giọng.** Chấm vài đoạn mẫu theo bốn mức Kém, Trung bình, Khá, Tốt để sửa hồ sơ; đó là đánh giá
   của người dùng, skill không tự tính điểm giống giọng. Ví dụ: “Cho tôi chấm 3 đoạn mẫu của hồ sơ này.”

Kết bằng: “Muốn bắt đầu thiết lập giọng không? Không bắt buộc. Không có hồ sơ thì Vietnamizer vẫn sửa và viết
theo giọng sẵn có của bài.” Người dùng không muốn thì dừng ở đây.

## 2. Thiết lập giọng từng bước

Chạy khi người dùng nhận lời mời trên, hoặc nói “bắt đầu dùng Vietnamizer”, “thiết lập giọng”. Mỗi lựa chọn hỏi qua
công cụ câu hỏi của host khi có, lựa chọn đề xuất đứng đầu; không có thì hỏi bằng chữ. Riêng câu chấm ở
bước 5 không có lựa chọn đề xuất. Quy tắc chấm ở `references/voice-profile.md` mục 7 thắng. Người dùng có thể dừng
ở bất kỳ bước nào; không lưu gì nếu người dùng dừng, và không đọc gì ngoài phần họ đã đồng ý cho đọc.

1. **Loại giọng:** Cá nhân (đề xuất) hoặc Thương hiệu.
2. **Nguồn mẫu:**
   - Cá nhân: Dán bài (đề xuất), File export, hoặc Đọc trang qua trình duyệt. Chỉ đưa lựa chọn trình duyệt
     khi agent thấy có công cụ trình duyệt theo `references/voice-sources.md` mục 1. Trong cùng câu hỏi nguồn,
     trình duyệt tách hai lựa chọn: tài khoản cá nhân (mục 4a) hay Trang Facebook mang tên chính người
     dùng (trang người nổi tiếng, mục 4c). Tài khoản thì chỗ “nền tảng khi cần” hỏi LinkedIn hay Facebook;
     Trang thì chỗ đó hỏi URL Trang và tên người dùng khi chưa có.
     File export thì nêu các bước của nền tảng theo mục 3 của file đó. Trình duyệt thì cảnh báo điều
     khoản đi cùng câu đồng ý ở bước 3, theo `references/voice-profile.md` mục 2; không nhắc lại ở đây.
   - Thương hiệu: nhờ người dùng dán hoặc nêu tên bộ quy chuẩn và tài liệu nội bộ họ chọn đưa, theo
     `references/brand-voice.md` mục 1. Bài thương hiệu đã đăng: Dán bài (đề xuất), File export (file bài
     viết trong export của trang), hoặc Đọc trang qua trình duyệt, với cùng điều kiện có công cụ trình
     duyệt; không nêu các bước export tài khoản cá nhân. Trình duyệt thì hỏi URL trang và tên thương hiệu
     khi chưa có, theo `references/voice-sources.md` mục 4b; câu này dùng chỗ “nền tảng khi cần” của ngân
     sách.
3. **Đồng ý đọc:** đúng một câu theo `references/voice-profile.md` mục 2, nêu tên nguồn. Dán bài thì áp quy
   tắc tác giả ở mục đó (chỉ bài người dùng tự viết), không hỏi chủ tài khoản. File export hay trang thì
   hỏi luôn tài khoản có phải của chính người dùng; Trang Facebook (mục 4c) thì hỏi luôn đó có phải Trang
   của chính người dùng, kèm cảnh báo của mục đó. Thương hiệu thì hỏi luôn người dùng có được nói thay
   thương hiệu không, theo `references/brand-voice.md`; với trình duyệt, câu ấy nêu tên thương hiệu và
   URL, cảnh báo điều khoản chỉ cho Facebook và LinkedIn.
4. **Học:** soạn và trình toàn bộ hồ sơ theo `references/voice-profile.md` mục 3.
5. **Chấm:** mời chấm đoạn mẫu theo mục 7 của file đó; trả lời 0 là bỏ qua.
6. **Lưu:** hỏi có lưu không, rồi theo mục 4 của file đó (nơi lưu, tên, đường dẫn, câu hỏi ghi vào sổ hồ
   sơ và câu gọi lần sau). Không lưu thì hồ sơ chỉ ở lại trong hội thoại.

Ngân sách câu hỏi: tối đa 6 câu hỏi trước bước chấm, gồm loại giọng, nguồn, nền tảng khi cần, câu đồng ý
đọc và tối đa một câu hỏi làm rõ. Trang thứ hai và thứ ba trong cùng lượt, của mục 4b hay 4c, có câu
đồng ý riêng, không tính vào 6 câu. Khi mục 4b gặp Trang của một cá nhân, câu hỏi Trang ấy có phải của chính
người dùng không và câu đồng ý mục 4c theo sau cũng không tính vào 6 câu. Không hỏi thêm để lấp đủ hồ sơ; thiếu thì ghi thiếu như hướng dẫn phân
tích.

Thiết lập chỉ chạy khi người dùng yêu cầu; skill không tự phát hiện lần dùng đầu và không tạo file đánh
dấu.
