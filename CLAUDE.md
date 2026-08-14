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

サーバーは Claude のバックグラウンドタスクではなく、**herdr の `sd-webui`
という名前の Pane で動かす**。ユーザーがログを直接見られる場所に置き、
セッションをまたいで生き残らせるため。

### 手順

前提として `HERDR_ENV=1` であること。そうでなければ herdr の外にいるので
操作しない。

1. 既存の Pane を探す。`herdr pane list --workspace "$HERDR_WORKSPACE_ID"`
   の結果から `label` が `sd-webui` のものを拾う。
2. 無ければ用意する。同じタブに未使用のシェル Pane（`revision` が 0 で
   エージェントが乗っていないもの）があればそれを使い、無ければ
   `herdr pane split --current --direction down --cwd "$PWD" --no-focus`
   で作る。いずれの場合も `herdr pane rename <pane_id> sd-webui` で命名する。
3. `herdr pane run <pane_id> './webui-user.sh'` で起動する。
4. `herdr pane wait-output <pane_id> --regex "Running on local URL|Traceback|error:|Killed"`
   で起動完了を待つ。成功時の目印は `Running on local URL:  http://[::]:7860`。

### 停止と再起動

Pane 内のフォアグラウンドプロセスなので `herdr pane send-keys <pane_id> ctrl+c`
で止める。再起動は手順3から。ポートが空いたことは `ss -ltn | grep 7860` で
確認できる。

Pane を作り直す必要はない。`sd-webui` Pane は使い回す。

## 環境ファイル

`.tool-versions` は追跡しない。コミット対象に含めないこと。
