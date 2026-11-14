# Design Decision Log

本文件整理 GUI 設計與技術規劃過程中確認的 48 項決策。若後續修正與早期選擇衝突，以最新修正為準。

## Round 1 — Capture Interaction

| ID | Decision | Specification |
|---|---|---|
| 1b | Hotkey capture | Shift + Print Screen 直接截取滑鼠所在視窗，不需要再次點擊。 |
| 2a | Hotkey completion | 自動還原視窗並顯示 KDE 通知，不開啟圖片預覽。 |
| 3a | GUI capture | 按下 GUI 截圖按鈕後隱藏 GUI，使用滑鼠點選目標視窗。 |
| 4b | Capture area | 包含視窗標題列與邊框。 |
| 5b | GUI completion | GUI 發起的截圖完成後重新顯示小型主畫面。 |

## Round 2 — Basic GUI

| ID | Decision | Specification |
|---|---|---|
| 6a | Profiles | 支援多組自訂尺寸、儲存常用尺寸及設定預設值。 |
| 7a | Window picker feedback | 滑鼠移入視窗時顯示高亮邊框，點擊確認。 |
| 8b | Capture result UI | GUI 不顯示圖片預覽，維持原設定畫面。 |
| 9b | Capture history | 不保存截圖歷史，只顯示最近一次截圖資訊。 |
| 10a | Resize failure | 無法調整視窗尺寸時停止截圖、還原環境並顯示原因。 |
| 11a | Filename | 使用視窗名稱、日期與時間自動命名。 |
| 12a | Progress | GUI 顯示處理階段；快捷鍵使用非干擾式通知。 |

## Round 3 — Window and Output Behavior

| ID | Decision | Specification |
|---|---|---|
| 13b | Close | 關閉 GUI 視窗時直接結束程式。 |
| 14a | Tray interaction | 系統匣左鍵開啟 GUI，右鍵顯示功能選單。 |
| 15a | Shortcut conflict | 偵測快捷鍵衝突並提示使用者修改。 |
| 16c | Autostart | 不提供登入 KDE 後自動啟動。 |
| 17a | Settings persistence | 設定保存於 KDE 使用者設定目錄，重啟後載入。 |
| 18a | Output directory | 預設 ~/Pictures/Screenshots，允許修改。 |

## Round 4 — Window Controls and Profile Management

| ID | Decision | Specification |
|---|---|---|
| 19b | Minimize | 一般最小化到工作列，不縮至系統匣。 |
| 20a | Profile management | 新增、修改、刪除、重新命名及設定預設值。 |
| 21a | Filename collision | 同名檔案自動附加流水號，絕不覆蓋。 |
| 22a | Output independence | 剪貼簿與 PNG 儲存可分別啟用。 |
| 23a | Esc cancellation | 選取階段按 Esc 立即取消、恢復 GUI，不修改視窗。 |
| 24a | Unsupported windows | 不支援調整尺寸的視窗停止操作、還原環境並顯示原因。 |

## Round 5 — GUI Layout

| ID | Decision | Specification |
|---|---|---|
| 25 | Compact quick window | 啟動只顯示小型、不擋路的快速操作視窗；完整設定另開較大的 Settings 視窗。 |
| 26a — superseded | Original Profile editing | 早期選擇獨立 Dialog 編輯名稱、寬度、高度。此方案已被後續決策取代。 |
| 27a | Profile selector | 下拉選單顯示 Profile 名稱與解析度。 |
| 28a | Shortcut customization | Settings 可自訂快捷鍵，預設 Shift + Print Screen。 |
| 29a | Tray menu | 包含 Capture、Select Profile 子選單、Open GUI、Quit。 |
| 30a | GUI progress | 選取視窗後顯示獨立小型進度視窗，顯示處理階段，完成後返回主畫面。 |

### Quick Window visual corrections

使用者明確要求移除小視窗中的：

- CAPTURE PROFILE 標籤。
- Settings → Open full settings window 提示文字。

小視窗應有明確 Capture Window 按鈕，並盡量節省空間。小視窗右上角齒輪只負責開啟完整 Settings。

## Round 6 — Platform and Technical Architecture

| ID | Decision | Specification |
|---|---|---|
| 31a | Platform scope | 第一版優先支援 X11；Wayland 自動偵測並提示尚未支援。 |
| 32a | Virtual display | 優先研究獨立虛擬顯示區，必須保證不干擾主要桌面，否則中止。 |
| 33a | Exact dimensions | 最終 PNG 精確符合指定尺寸，標題列與邊框包含在尺寸內。 |
| 34a | State restoration | 完整保存與恢復位置、尺寸、最大化、全螢幕、所在桌面及螢幕。 |
| 35a | Concurrency | 單一程式實例，同一時間只允許一個截圖工作。 |
| 36b | Distribution | 第一版使用 AppImage。 |

## Round 7 — Settings Window

| ID | Decision | Specification |
|---|---|---|
| 37a | Settings layout | 左側垂直分類選單，右側設定內容。 |
| 38a | Apply behavior | 修改先暫存；Apply 正式保存；Cancel 放棄變更。 |
| 39a — superseded | Original Profile management entry | 早期選擇 Profiles 頁面以齒輪開啟獨立管理 Dialog。此方案已被後續決策取代。 |
| 40a | Shortcut recording | 使用 Record Shortcut，再按下想使用的組合鍵。 |
| 41a | Folder selection | 路徑欄位搭配 Browse，使用 KDE 原生資料夾選擇器。 |
| 42a | Diagnostics page | 提供環境檢查、截圖引擎檢查及複製診斷報告。 |

### Final Profile editing correction

後續使用者明確修正：

- Settings 的 Profiles 頁面選擇 Profile 後，直接在同一頁修改名稱、寬度與高度。
- 不使用齒輪管理 Profile。
- 不顯示 Manage Profiles 按鈕。
- 不開啟獨立 Profile 管理 Dialog。
- 早期 26a 與 39a 的獨立 Dialog / 齒輪方案正式失效。

## Round 8 — Final Acceptance and Distribution

| ID | Decision | Specification |
|---|---|---|
| 43a | AppImage dependencies | Python、PySide6、應用程式打包；X11/KDE 系統工具由主機提供，啟動檢查依賴。 |
| 44a | Startup checks | 啟動自動檢查 X11、必要指令及虛擬顯示能力；不符合條件禁止截圖。 |
| 45a | Restore failure | 自動執行復原程序，保留狀態快照，提供修復指引及診斷報告。 |
| 46a | Execution logs | 保留最近五次執行技術紀錄，不保存截圖內容。 |
| 47a | Updates | 從 GitHub Releases 手動下載新版，不提供程式內更新。 |
| 48c | Formal test method | 只做 Kubuntu 24.04 KDE X11 實機人工測試。 |

## Decision precedence

- 所有未被明確取代的決策持續有效。
- 26a 與 39a 的原始獨立 Dialog / 齒輪管理方案已被後續 Profile inline editing 修正取代。
- 小型快速操作視窗的齒輪仍保留，僅用來開啟完整 Settings；Settings 的 Profiles 頁面不使用齒輪。
- 若未來需要變更已確認決策，應新增修訂紀錄，不應靜默改寫歷史決策。
