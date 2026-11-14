# Technical Specification

## 1. 技術狀態與限制

本文件描述目標架構與安全約束，不代表所有技術路徑已經實機驗證。

目前最高風險是：能否建立不干擾主要 KDE 桌面的隔離式虛擬顯示環境，並在其中操作已存在於使用者桌面上的目標視窗。

在技術驗證通過前，不得宣稱此能力已實作，也不得以一般 RandR 畫面延伸或改變主螢幕排列的方式冒充隔離顯示。

若無法證明安全，必須停止後續截圖流程。

## 2. 目標技術堆疊

- 語言：Python。
- GUI：PySide6 / Qt。
- 第一版桌面工作階段：KDE Plasma on X11。
- 發行格式：AppImage。
- 設定：KDE 使用者設定目錄中的應用程式設定檔。
- 日誌：本機輪替紀錄，最多保留最近五次執行。
- 全域快捷鍵：使用與 KDE Plasma 相容的整合方式，必須處理衝突。
- 剪貼簿：透過 Qt / KDE 可用的影像剪貼簿介面。

Python、PySide6 與應用程式程式碼打包進 AppImage。X11/KDE 系統工具由主機提供，啟動時檢查工具是否存在及是否可用。

## 3. 建議模組邊界

建議程式分為以下責任區：

### 3.1 Application Layer

負責：

- 程式生命週期。
- 單一實例鎖定。
- 啟動環境檢查。
- 設定載入。
- 小型 GUI 與 Settings 視窗管理。
- 系統匣註冊。

### 3.2 UI Layer

建議元件：

- QuickWindow：小型快速操作視窗。
- SettingsWindow：獨立設定視窗。
- ProfilesPage：同頁直接編輯 Profile。
- ShortcutPage：快捷鍵錄製與衝突提示。
- OutputPage：輸出選項與目錄。
- ApplicationPage：應用程式行為資訊。
- SystemPage：環境檢查與診斷報告。
- CaptureProgressDialog：小型進度視窗。
- WindowPicker：視窗懸停高亮與點擊選取。

UI 不直接執行顯示器或視窗管理命令。所有工作透過 Capture Controller 或相應 service。

### 3.3 Core Layer

建議元件：

- CaptureController：統一 GUI 與快捷鍵的截圖工作入口。
- ProfileStore：Profile 與設定的載入、暫存、驗證及保存。
- StateSnapshot：截圖前保存視窗及桌面狀態。
- RestoreManager：負責還原視窗、螢幕與桌面狀態。
- DiagnosticsService：環境檢查與診斷報告。
- ExecutionLog：最近五次執行紀錄管理。

### 3.4 X11 Backend

建議責任：

- EnvironmentChecker：確認 X11 工作階段及必要工具。
- WindowInspector：取得 Window ID、視窗幾何與狀態。
- WindowPickerBackend：定位滑鼠所在視窗、排除不應選取的視窗。
- VirtualDisplayBackend：建立、驗證及移除隔離顯示資源。
- WindowPlacement：在已驗證的隔離環境中安排目標視窗。
- ScreenshotBackend：擷取完整視窗影像。
- RestoreBackend：恢復原始視窗與桌面狀態。

實際使用哪些 X11/RandR/X server 工具，必須由可行性實驗決定，不得在未驗證前固定假設。

## 4. 安全工作流程

所有截圖請求必須由單一 CaptureController 管理。

### 4.1 工作狀態

建議狀態：

1. IDLE
2. PREFLIGHT
3. TARGET_LOCKED
4. SNAPSHOT_SAVED
5. ISOLATED_DISPLAY_READY
6. WINDOW_PREPARED
7. CAPTURING
8. OUTPUT_WRITING
9. RESTORING
10. COMPLETED
11. FAILED
12. RECOVERY_REQUIRED
13. CANCELLED

每次狀態轉換必須可記錄，且失敗時不得略過必要復原步驟。

### 4.2 Preflight

執行任何桌面變更之前：

- 確認目前工作階段為 X11。
- 檢查必要系統指令。
- 檢查虛擬顯示能力。
- 確認目標視窗仍存在。
- 確認目標 Profile 尺寸合法。
- 確認至少啟用一種輸出方式。
- 確認目前沒有其他截圖工作。

任何必要條件不符合，立即中止，且不修改桌面。

### 4.3 Target Lock

快捷鍵模式必須在快捷鍵事件發生時取得滑鼠所在視窗的 Window ID。取得後鎖定該 ID，後續焦點改變不得使目標被替換。

GUI 模式由 WindowPicker 顯示懸停高亮，使用者點擊後鎖定 Window ID。

WindowPicker 必須排除自身視窗、進度視窗、系統匣 popup 及其他工具 UI，避免選到程式自己的視窗。

### 4.4 Snapshot

在任何視窗或顯示環境變更前，保存至少以下資訊：

- 目標 Window ID。
- 原始位置與尺寸。
- 原始最大化狀態。
- 原始全螢幕狀態。
- 所在虛擬桌面。
- 所在螢幕或 monitor assignment。
- 原始顯示配置資訊。
- 本次截圖使用的 Profile。
- 本次工作識別資訊。

狀態快照必須先成功保存，才允許進入可能改變桌面狀態的步驟。

### 4.5 Isolated Display Gate

隔離式虛擬顯示是第一版核心技術閘門。

必須證明：

- 建立隔離顯示不會改變主要螢幕解析度。
- 不會改變主要桌面排列。
- 不會使使用者桌面跳動。
- 不會改變其他視窗的位置或尺寸。
- 能在隔離環境中操作本次目標視窗。
- 完成後能完整移除新增資源。

不可假設獨立 X Server 可以直接操作另一個 X Server 中已存在的 Window ID。不可假設建立 RandR monitor 就等於建立獨立顯示伺服器。這些方案必須分別驗證其實際隔離能力。

若無法滿足以上條件，停止 Phase 1，不得繼續使用會改動主要桌面的方案。

### 4.6 Capture

擷取範圍包含標題列與邊框。最終 PNG 的寬高必須精確等於 Profile。

禁止以事後縮放來修正不符合尺寸的影像。

若目標視窗拒絕調整、裝飾無法納入指定尺寸、擷取範圍不完整或輸出尺寸不符，必須視為失敗。

### 4.7 Restore

復原必須在成功、失敗、輸出失敗及使用者取消等情境中執行。

復原目標：

- 視窗位置。
- 視窗尺寸。
- 最大化狀態。
- 全螢幕狀態。
- 虛擬桌面。
- 螢幕指派。
- 暫時顯示資源。

復原順序必須由實機驗證決定。應避免在恢復幾何之前就移除仍被視窗使用的顯示資源。

只有復原驗證成功，才能將工作標記為正常完成。

### 4.8 Recovery

若一般復原失敗：

- 進入 RECOVERY_REQUIRED。
- 使用先前保存的狀態快照執行復原程序。
- 不刪除必要診斷資料。
- 保留人工修復所需的狀態資訊。
- 顯示清楚的修復指引。
- 提供可複製的診斷報告。

不可只顯示錯誤後就直接退出。

## 5. Exact Output Validation

截圖完成後檢查：

- PNG 可正常解碼。
- 寬度等於 Profile width。
- 高度等於 Profile height。
- 影像包含標題列及邊框。
- 未經事後縮放。
- 寫檔成功或剪貼簿寫入成功。

若輸出不符合條件，不得回報成功。

## 6. Output Safety

檔名由視窗名稱與日期時間組成。檔名清理必須處理路徑分隔符、控制字元與作業系統不允許字元。

檔案已存在時使用流水號建立新檔案。應採用不覆蓋既有檔案的建立方式，避免檢查與寫入之間的競態條件。

剪貼簿與 PNG 儲存各自獨立。若其中一種輸出失敗，通知必須說明實際成功與失敗的輸出項目。

## 7. Single Instance and Concurrency

- 使用單一實例鎖。
- 同一時間只允許一個 CaptureController 工作。
- 第二次觸發截圖時不得建立第二套顯示變更。
- 若正在截圖，應以非干擾式方式提示工作進行中。
- GUI 與快捷鍵不可各自啟動獨立截圖流程。

## 8. Settings Persistence

設定保存於 KDE 使用者設定目錄。

建議保存：

- Profiles。
- Default profile ID。
- Current profile ID。
- Global shortcut。
- Clipboard enabled。
- PNG enabled。
- Output directory。
- Notification preference。

Settings 使用 working copy：

- 開啟時載入目前已保存設定。
- 使用者修改只更新 working copy。
- Apply 驗證並原子化保存。
- Cancel 捨棄 working copy。
- 保存失敗時保留原設定並顯示錯誤。

Profile 切換不得讓尚未 Apply 的修改意外遺失。

## 9. Global Shortcut and KDE Integration

快捷鍵必須在 KDE X11 工作階段可用，且需偵測衝突。

優先使用 KDE 支援的全域快捷鍵整合方式。實際 API 或註冊機制應在實機環境驗證。

若快捷鍵衝突：

- 顯示衝突狀態。
- 不覆寫其他應用程式設定。
- 允許使用者重新錄製。
- Apply 前再次檢查。

系統匣左鍵開啟 QuickWindow；右鍵顯示 Capture、Select Profile、Open GUI、Quit。

## 10. Diagnostics and Logging

保留最近五次執行的技術紀錄，不保存截圖影像、剪貼簿內容或截圖像素資料。

建議記錄：

- 執行時間。
- 工作階段類型。
- Profile 名稱與尺寸。
- 目標視窗識別資訊（避免記錄不必要的視窗內容）。
- 狀態轉換。
- 依賴檢查結果。
- 虛擬顯示建立與清理結果。
- 截圖輸出尺寸。
- 復原結果。
- 錯誤類型與訊息。

日誌應限制權限並輪替，最多保留五次執行所需紀錄。

## 11. AppImage Packaging

打包：

- Python runtime。
- PySide6。
- Application modules。
- UI resources。

由主機提供 X11/KDE 系統工具。啟動時檢查必要命令、共享函式庫與工作階段環境。

不提供內建更新器。版本發布於 GitHub Releases，使用者手動下載新版 AppImage。

## 12. Open Technical Questions

以下項目不可由文件直接視為已解決：

1. 能否在不改變主要桌面的情況下建立隔離顯示區？
2. 如何讓既有 X11 視窗在隔離顯示環境中呈現與操作？
3. KDE 視窗裝飾與指定最終尺寸如何精確協調？
4. 哪種 X11 工具組合能可靠保存及恢復 monitor、desktop 與 window state？
5. 快捷鍵衝突如何透過 KDE 支援的機制可靠偵測？
6. AppImage 所需的系統端 X11/KDE 依賴清單為何？

每個問題都必須透過 Kubuntu 24.04 KDE X11 實機驗證後才能定案。
