# Navigation Android

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Graph và deep-link nội bộ.

## Phạm vi

Graph và deep-link nội bộ. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Start=Realtime; destinations: Realtime, ReverseCommunication, History, Device, Settings, Debug, ModelUpdate.

## Luồng hoạt động

Connection state là shared state, không phải navigation side effect.

## Ví dụ

Realtime -> History -> ConversationDetail.

## Ghi chú triển khai

Bốn top-level destination `Phụ đề`, `Trò chuyện`, `Lịch sử`, `Thiết bị` đã được triển khai bằng Navigation Compose với `launchSingleTop`, `saveState` và `restoreState`. Debug/model update vẫn là **Planned**.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [SCREEN_SPECIFICATIONS.md](SCREEN_SPECIFICATIONS.md)
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
