# セッションログ 010 — Sprint 3（第3部・拡張）／skills 化

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv`（ruff/mypy/pytest）+ mcp 1.28.1
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

第3部の **skills**。このセッションで繰り返した「出荷手順」を skill に切り出し、
CLAUDE.md（常時）から**必要時読込**へ移す。

## やったこと

- [`.claude/skills/ship-change/SKILL.md`](../../.claude/skills/ship-change/SKILL.md) —
  出荷手順（branch → 検証網 → 1コミット=1意味 → PR → CI → マージ → main 確認）。
- [`docs/concepts/04-skills.md`](../concepts/04-skills.md) — 必要時読込 / CLAUDE.md との線引き / skill の形。
- `CLAUDE.md` から skill を**軽く参照**（常時 → 必要時の分離を実演）。

## 判断（採用/棄却）

| 判断点 | 採用 | 理由 | 棄却 |
|--------|------|------|------|
| 何を skill 化するか | 8回繰り返した出荷手順 | 最も反復・手順が明確・CLAUDE.md 肥大の主因 | 規約そのもの（常時＝CLAUDE.md が適切） |
| CLAUDE.md との関係 | CLAUDE.md は原則／skill は手順詳細／CLAUDE.md から軽く指す | 常時文脈を軽く保つ | 手順を CLAUDE.md に全部書く（肥大・読まれない） |

## 検証結果

`ruff` / `mypy app experiments` / `pytest`（**11 passed**・コード変更なし）すべて緑。

## 未処理 → Sprint 3 の残り

- **sub-agents**（委譲・並列・コスト比較。「分割は常に得ではない」）→ これで Sprint 3 締め。

## レトロ（速報）

- **Keep**: 4層記憶モデルが実物で揃った
  （CLAUDE.md＝常時 / `ship-change`＝必要時 / 会話＝揮発 / `session-logs`＝永続）。
- **Try**: sub-agents はコスト／時間／質を数字で比較し「分割が損な場合」も示す。
