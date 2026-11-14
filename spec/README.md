# KDE Window Size Screenshot — Specification

本資料夾保存 KDE Window Size Screenshot 的產品需求、技術約束、驗收條件與已確認決策。所有文件均以目前已確認的使用者決策為準。

## 文件索引

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md)：產品目標、GUI、Profile、快捷鍵、輸出、通知與操作流程。
- [TECHNICAL-SPEC.md](TECHNICAL-SPEC.md)：系統架構、X11 工作階段、虛擬顯示可行性閘門、視窗狀態保存與復原、打包方式。
- [ACCEPTANCE.md](ACCEPTANCE.md)：Kubuntu 24.04 KDE X11 實機人工驗收清單。
- [DECISIONS.md](DECISIONS.md)：第 1 至 48 項設計決策及後續修正紀錄。

## 規格優先順序

1. 使用者在專案討論中最後確認的決策。
2. 本資料夾中的產品與技術規格。
3. 實作時提出、但尚未經使用者確認的工程細節。

若早期決策與後續修正衝突，以後續修正為準。特別是 Profile 編輯方式：早期曾選擇獨立 Dialog 與齒輪入口，後來已明確改為在 Settings 的 Profiles 頁面直接編輯，舊方案不得實作。

## 開發原則

- 直接在 GitHub 的 main 分支開發，不建立 PR 或開發分支。
- 第一版目標平台為 Kubuntu 24.04、KDE Plasma、X11。
- Wayland 第一版不支援；偵測到 Wayland 時必須明確提示並禁止截圖。
- 最優先工作是驗證隔離式虛擬顯示方案是否能在不干擾主要桌面的前提下操作既有視窗。
- 若無法證明安全，必須停止，不得改用會改變主要桌面配置的替代方案。
- 最終 PNG 必須在擷取時即符合指定尺寸，且包含視窗標題列與邊框；不得以事後縮放冒充精確尺寸截圖。
- 截圖成功、失敗、取消及異常復原都必須納入桌面狀態保護。
- 正式驗收採 Kubuntu 24.04 KDE X11 實機人工測試。

## 實作階段

1. 將本規格落實為可追蹤的工程任務。
2. 完成隔離式虛擬顯示技術可行性驗證。
3. 通過安全閘門後才實作 Capture Backend。
4. 實作 PySide6 GUI 與 KDE 整合。
5. 製作 AppImage。
6. 在指定實機環境完成人工驗收。

技術可行性尚未驗證的項目必須標示為待驗證，不得在文件或 README 中宣稱已支援。
