# CLAUDE.md

このリポジトリは上流 `Haoming02/sd-webui-forge-classic` のフォーク
`yuanying/sd-webui-forge-neo` である。チェックアウトは
`~/src/github.com/yuanying/sd-webui-forge-neo` に置く。

| remote | 指す先 |
| --- | --- |
| `origin` | フォーク `git@github.com:yuanying/sd-webui-forge-neo.git` |
| `upstream` | 上流 `git@github.com:Haoming02/sd-webui-forge-classic.git` |

## ブランチ運用

| ブランチ | 役割 |
| --- | --- |
| `upstream/neo` | 上流の開発ブランチ。読み取り専用 |
| `neo` | 上流のミラー。`upstream/neo` を早送りするのみ。独自コミットを載せない |
| `local/neo` | **フォークのデフォルトブランチ。独自の修正はすべてここに積む**。追跡ブランチは `origin/local/neo` |

`local/neo` は `upstream/neo` の上に独自コミットを重ねた形を常に保つ。
マージコミットは作らず、上流を取り込むときはリベースする。

```
upstream/neo ──●──●──● (上流最新)
                      └─●──● local/neo (独自コミット)
```

### 変更の入れ方

変更は作業ブランチを切ってフォークへ push し、フォークの `local/neo` 向けに
PR を出す。

```bash
git push -u origin <作業ブランチ>
gh pr create --repo yuanying/sd-webui-forge-neo --base local/neo
```

PR のマージはユーザーの承認を得てから行う。マージ後はローカルの `local/neo` を
`git pull --ff-only` で `origin/local/neo` に早送りする。

### 上流の取り込み

```bash
git fetch upstream
git rebase upstream/neo
```

`neo` をミラーとして更新したい場合は `git fetch upstream neo:neo` で早送りする。

リベースすると `local/neo` の履歴が書き換わるので、フォークへの反映には
force push が要る。これは勝手に行わず、ユーザーの承認を得てから行う。

### 禁止事項

- `upstream` へ push しない。差分の確認は `git log upstream/neo..local/neo` で行う。
- `gh pr create` で `--repo yuanying/sd-webui-forge-neo --base local/neo` を省略しない。
  省略するとフォークの親（上流）に PR が飛ぶ。
- `local/neo` へ直接 push しない。変更は PR を経由させる（例外は上記の、
  承認を得たリベース後の force push のみ）。

## 独自コミットの性格

`local/neo` に積まれているものは、上流へ還元する意図のないローカル専用の変更。

- **ローカル起動設定** — `webui-user.sh` の `COMMANDLINE_ARGS`（モデル配置先、
  待ち受けアドレス、API 有効化）と、起動スクリプトの実行ビット。
  このマシン固有の設定なので上流には出さない。
  常駐しているサーバーはこれを読まない（下記「起動方法」）。効くのは
  devbox から手で `./webui-user.sh` を叩いたときだけである。
- **バグ修正** — 上流にも存在する不具合への修正。上流へ PR を出す場合は
  `upstream/neo` から別ブランチを切り、該当コミットだけを cherry-pick すること。
  `local/neo` をそのまま PR の元にしない（ローカル設定が混入する）。

## 起動方法

サーバーはこのリポジトリからは起動しない。dotfiles の `devbox/apps` で、
devbox の隣に `sd-webui` コンテナとして常駐している（`restart: always`）。
起動・再起動・ログの見方・ソース変更の反映方法は dotfiles の
`devbox/apps/README.md` にまとめてあるので、そちらを見ること。

コンテナは `webui.sh` も `webui-user.sh` も使わない。このチェックアウト
（`~/src/github.com/yuanying/sd-webui-forge-neo`）の `venv/` の python で
`launch.py` を直接起動し、起動引数（`--listen`、`--api`、`--model-ref` など）は
dotfiles の compose ファイルが渡す。起動引数を変えたいときは、`webui-user.sh`
ではなく compose ファイルを直す。

## 環境ファイル

`.tool-versions` は追跡しない。コミット対象に含めないこと。
