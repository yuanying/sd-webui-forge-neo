# CLAUDE.md

このリポジトリは上流 `Haoming02/sd-webui-forge-classic` のクローンであり、
フォークではない。`origin` は上流そのものを指す。

## ブランチ運用

| ブランチ | 役割 |
| --- | --- |
| `origin/neo` | 上流の開発ブランチ。読み取り専用 |
| `neo` | 上流のミラー。早送りのみ。独自コミットを載せない |
| `local/neo` | **作業ブランチ。独自の修正はすべてここに積む** |

`local/neo` は `origin/neo` の上に独自コミットを重ねた形を常に保つ。
マージコミットは作らず、上流を取り込むときはリベースする。

```
origin/neo ──●──●──● (上流最新)
                    └─●──● local/neo (独自コミット)
```

### 上流の取り込み

```bash
git fetch origin
git rebase origin/neo
```

`neo` をミラーとして更新したい場合は `git fetch origin neo:neo` で早送りする。

### 禁止事項

- `local/neo` に upstream を設定しない。素の `git push` が `origin/neo`
  （＝上流本体）を狙う事故を防ぐため、追跡ブランチは意図的に未設定にしてある。
- `origin` へ push しない。差分の確認は `git log origin/neo..local/neo` で行う。

## 独自コミットの性格

`local/neo` に積まれているものは、上流へ還元する意図のないローカル専用の変更。

- **ローカル起動設定** — `webui-user.sh` の `COMMANDLINE_ARGS`（モデル配置先、
  待ち受けアドレス、API 有効化）と、起動スクリプトの実行ビット。
  このマシン固有の設定なので上流には出さない。
- **バグ修正** — 上流にも存在する不具合への修正。上流へ PR を出す場合は
  `origin/neo` から別ブランチを切り、該当コミットだけを cherry-pick すること。
  `local/neo` をそのまま PR の元にしない（ローカル設定が混入する）。

## 起動方法

`./webui.sh` ではなく **`./webui-user.sh`** を使う。前者を直接叩くと
`COMMANDLINE_ARGS` が渡らず、モデルパスなどの設定がすべて落ちる。

## 環境ファイル

`.tool-versions` は追跡しない。コミット対象に含めないこと。
