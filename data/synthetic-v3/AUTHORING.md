# v0.3 出題指引（給撰寫題目的 Claude）

依據：[docs/protocol-v0.3.md](../../docs/protocol-v0.3.md) §3（已凍結）、[analysis-plan.json](analysis-plan.json)、jevlike `data/HARD_GUIDE.md`。
本檔是交給每位撰寫者的完整說明，凍結時一併存檔。

## 1. 題目長什麼樣

每段文字是某個專案的一段紀錄，例如週報、ADR、工單、會議紀錄或 PRD 里程碑。模型讀到的內容如下：

```
今天：2026-11-12            ← 英文題為 "Today: 2026-11-12"；這一行由程式加上，不要寫進 state
<state>
```

題目（instructions）與四個選項固定如下，撰寫者不能改：

- zh 題目：依據目前文字，專案現在最符合下列哪一種狀態？判斷規則：以最新的明確狀態陳述為準；條件尚未發生時，判斷目前的狀態；只有本專案被終止才算取消，其他專案或子項目被取消不算；已經排除的阻礙不算卡關；日期以第一行的「今天」為準。
- en 題目：Based on the current text, which project status is best supported? Rules: the latest explicit status statement wins; if a condition has not happened yet, judge the current status; only termination of this project counts as cancelled, not other projects or sub-items; a blocker that has been resolved is not blocked; dates are judged against the "Today" line.

| gold | zh 選項 | en 選項 |
|---|---|---|
| A | 專案按計畫進行，進度符合時程，預計如期交付。 | The project is on track and progressing as planned. Delivery is expected on schedule. |
| B | 專案進度落後，交付日期延後，無法依原定時程完成。 | The project is delayed and behind schedule. Delivery will miss the original deadline. |
| C | 專案遭遇阻礙，工作卡關，需要先排除問題才能繼續。 | The project is blocked by an unresolved dependency. Work cannot proceed until it is resolved. |
| D | 專案已取消，不再繼續執行，也不會交付原定成果。 | The project has been cancelled. Work will not resume and the planned deliverable will not be shipped. |

## 2. 每段只能符合一個選項（最重要）

gold 必須只靠「今天、state、題目裡的規則、選項文字」就能唯一判定。寫完每段，自己檢查一次：換一個細心的讀者，會不會選另一個選項？

**邊界的判定方式**（寫題時遵守；這些都是選項文字本身的意思，不是另外的規則）：

- **A 與 B**：
  - 預計交付日（或可完成的日期）**不晚於**原定期限 → A，就算中間有小延遲或用掉了緩衝。
  - 會**晚於**原定期限 → B。
- **B 與 C**：
  - B：工作還能繼續推進，只是會晚交，**而且有新的預計日期**或明確「會晚」。
  - C：有一個尚未解決的問題，**讓工作無法往下做**，必須先排除。
  - 寫 C 時**不要**同時給出新的交付日期；寫 B 時要寫出工作仍在進行。
- **C 與 D**：
  - 暫停、凍結、等決策、「先擱著」都是 C，因為之後還可能恢復。
  - 只有明確終止本專案、不再交付，才是 D。
- **D 的範圍**：只有「本專案」被終止才算。子功能被砍、另一個專案被取消、舊方案被廢棄，都不算 D。
- **條件式**：「若下週沒回覆就延期」在條件發生前，判斷目前狀態。
- **已排除的阻礙**：不算 C。

**不准留下與 gold 衝突、又沒有被規則化解的狀態句**。v2 的錯誤就是改了一個詞，卻留著「目前進度領先」。

例外是 H-tmp（多段更新）、H-res（已排除的阻礙）、H-dis（其他專案的事）這幾型。它們故意放入看似衝突的句子，但規則必須能清楚化解，例如「最新的一則」要有明確日期，或寫在最後並標示時間。

## 3. 寫法規範

1. **先定 gold，再寫情境**。每段附一句 `rationale`，說明為什麼是這個 gold，以及關鍵事實是哪一句。
2. **state 只放證據，不放結論**。不得出現選項句子，也不得出現「專案已取消」「專案狀態：延後」「The project is on track」這類總結句（validator 會擋）。
   - 可以描述事實，例如「客戶來信終止合約」「整合測試要等對方 API 開放」「預計 12/3 交付，原訂 11/28」。
   - 一般用詞可以出現在敘述中，例如「延期」「blocked」「暫停」，但不要只靠一個關鍵字就能答對，要讓讀者必須理解句子。
3. **手寫，不用模板**。同一型裡，句型、專案名、人名、產品、日期、骨架都要變化。不要所有題都用同一個專案名或同一個開頭。
   - 專案名請自創，例如「北極星計畫」「Orion billing revamp」「P-217 倉儲盤點 App」。
   - 人名中英都可以。
4. **骨架**（`skeleton`）：`weekly`（週報）、`adr`、`ticket`（工單）、`meeting`（會議紀錄）、`prd`（PRD 里程碑）。每型至少用到 4 種，盡量平均。
5. **語言**：中英各半。zh 用台灣正體中文，可以夾雜英文術語；en 用自然的英文。
6. **今天**（`today`）：2026 年的日期，可以變化，不必都是 11-12。若 state 有日期，要和 today 一致、合理。
7. **長度**：非 H-lng 的題目，加上今天這一行後不得超過 480 個 GLiNER token（中文約 300 字、英文約 250 個詞，validator 會檢查）。一般 40–250 字即可。
8. **gold 分布**：每型 A、B、C、D 都要有。60 段的型每類至少 10 段，90 段的型每類至少 15 段；A 不得超過 40%。
9. **孿生題**：60 段的型至少 15 對，90 段的型至少 20 對。
   - 同一對兩段的 lang、skeleton 相同，**只改一個事實**，就讓 gold 不同。
   - 兩段共用 `pair_id`，id 連號。
   - 其餘題目的 `pair_id` 填 `null`。

## 4. 欄位

一行一筆 JSON，UTF-8：

```json
{"id": "s-h-imp-001", "task": "status", "hard_type": "H-imp", "lang": "zh", "skeleton": "weekly",
 "today": "2026-11-12", "state": "……", "gold": "C", "pair_id": "s-h-imp-p01",
 "rationale": "測試環境要等資安審查，審查排在下個月，目前無法往下做"}
```

- `id`：`s-<代號小寫>-001`…，例如 `s-h-noi-001`。
- `pair_id`：`s-<代號小寫>-p01`… 或 `null`。
- H-dat 另加 `state_precomputed`，見 §5。

## 5. 十個題型

| 代號 | 段數 | 要寫成什麼樣 |
|---|---|---|
| H-noi | 60 | **雜訊**：錯字、注音文或火星文、口語、縮寫、中英夾雜、多餘符號、聊天語氣（如 Slack 訊息）。雜訊不能影響 gold 的唯一性。 |
| H-dis | 60 | **干擾**：混入與本專案無關的資訊，例如其他組的阻礙、別的專案被取消、已關閉的舊工單、無關數字、子功能被砍。必須讓讀者清楚知道哪個是「本專案」，gold 由本專案的事實決定。 |
| H-inv | 60 | **倒裝與否定敘述**：先講結果再講原因；「不是 X，是 Y」；「並沒有延期，只是……」；雙重否定。題目本身仍是肯定形，否定只出現在 state 裡。 |
| H-inc | 60 | **資訊不完整**：短、缺欄位、沒頭沒尾的訊息，但仍有足夠線索唯一判定，例如「vendor 說 Q1 才能給 SDK，我們的上線日是 12/15」→ B。 |
| H-bor | 60 | **邊界**：落在兩個選項之間，由一個關鍵事實決定，照 §2 的邊界判定。例如用掉緩衝但仍不晚於期限 → A；暫停待決策 → C 而非 D；能做但會晚 → B 而非 C。孿生題特別適合這一型。 |
| H-imp | 60 | **沒有狀態關鍵字**：不出現延期、卡住、取消、如期、blocked、delayed、on track 等詞，要從事實推論。例如「法務還沒簽，簽了才能開帳號，開帳號才能開始整合」→ C。 |
| H-res | 60 | **聽起來負面其實沒事**（或反過來）：描述過去的阻礙或風險，但已經排除或不影響。gold 不一定是 A：例如阻礙已排除但交付日已經改晚 → B，舊阻礙排除後又出現新的 → C。 |
| H-tmp | 60 | **多段更新**：同一段裡有 2–4 則帶日期或時間順序的更新，彼此矛盾，以最新的明確狀態為準。最新的那則不一定在最後，要靠日期判斷；但日期必須清楚。 |
| H-dat | 90 | **日期比較**：gold 要靠比較今天、預計日、期限才能判定，例如預計 11-25、期限 11-20 → B；期限已過但尚未交付 → B；預計早於期限 → A。也可以用相對日期，例如「下週五」配合今天推算。C、D 題也要放日期，讓日期不能當作答案提示。<br>**另加 `state_precomputed`**：同樣的 state，在關鍵日期旁用括號寫出程式算好的比較結果，例如「（預計交付日晚於期限 5 天：是）」「（期限已過：是）」。只寫比較結果，不寫結論（不寫「所以延期」）。 |
| H-lng | 90 | **長文件**：加上今天這一行後**至少 520 個 GLiNER token**（中文約 600 字以上、英文約 420 詞以上）。例如完整會議紀錄、跨團隊週報，包含多個議題或多個專案。決定 gold 的關鍵句埋在中段，不在開頭或結尾。第一行要寫清楚「本專案」是哪一個。 |

## 6. 驗證

寫完執行下列指令，必須零錯誤：

```bash
.mpvenv/bin/python -m src.v3_validate <代號>
```

validator 只檢查格式與分布，不評分，也不顯示規則基線。撰寫時**不要**拿任何模型或規則去測自己的題目，也不要刻意針對某個 arm 出題。
