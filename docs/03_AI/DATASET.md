# Dataset

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Nguồn, chia tập, schema và provenance dữ liệu.

## Phạm vi

Nguồn, chia tập, schema và provenance dữ liệu. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

VSL400 là dataset chính; Multi-VSL chỉ mở rộng khi đủ tài nguyên; tập con được phép cho pipeline ban đầu.

## Luồng hoạt động

Acquire/license -> manifest -> split signer-aware -> extract landmark -> validate -> version.

## Ví dụ

Mỗi sample lưu sample_id,label,signer,split,frames,source,license.

## Ghi chú triển khai

Không có dataset trong repository; cần xác minh quyền sử dụng và mapping nhãn.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [PREPROCESSING.md](PREPROCESSING.md)
- [TRAINING.md](TRAINING.md)