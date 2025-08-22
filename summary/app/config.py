import os


def get_secret(secret_name: str) -> str | None:
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    return os.environ.get(secret_name.upper())


_gemini_api_key = get_secret("gemini_api_key")
if _gemini_api_key is None:
    raise ValueError("GEMINI_API_KEY secret or environment variable not set.")
GEMINI_API_KEY: str = _gemini_api_key

MODEL: str = "gemini-2.5-flash"

PROMPT_VERSION = 2

PROMPT: str = """
下記要約テンプレートに従って要約してください。

## 要約テンプレート

```markdown
## 決議された事項

* （決議事項1）
* （決議事項2）
* ...

## 議論となった事項

（ここから下に、全ての質疑応答の要約を繰り返す）

---

### 【（質疑のテーマ）】

**質疑者:** 

（氏名） 分科員（所属）

**答弁者:** 

（氏名） 政府参考人（役職など）

#### 【質疑の要点】

*   （質疑のポイント1）
*   （質疑のポイント2）
*   ...

#### 【答弁の要点】

*   （答弁のポイント1）
*   （答弁のポイント2）
*   ...

#### 【議論の結論】

（議論が平行線で終わったのか、何らかの合意や進展があったのかなど、議論の結果を簡潔に記述）

---

### 【（質疑のテーマ）】（次のテーマ）

...（同様の構造を繰り返す）...
```
"""

_database_url = get_secret("database_url")
if _database_url is None:
    raise ValueError("DATABASE_URL secret or environment variable not set.")
DATABASE_URL: str = _database_url

# API呼び出し制限関連の定数
BATCH_SIZE: int = 1
