from typing import Optional  # Optionalをインポート

from google.genai.errors import APIError
from pytimeparse import parse
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_combine,
    wait_exponential,
)
from tenacity.wait import wait_base


def _is_retriable(e: BaseException) -> bool:
    return isinstance(e, APIError) and e.code in [503, 429]

def _calc_retry_delay(exception: Optional[BaseException]) -> float: # Optionalを追加
    if exception is None:
        return 60
    if isinstance(exception, APIError): # APIErrorであることを明示的にチェック
        if exception.code == 503:
            return 60
        if exception.code == 429:
            try:
                retry_delay = parse(
                    [
                        rd
                        for d in exception.details["error"]["details"]
                        if (rd := d.get("retryDelay"))
                    ][0]
                )
                if retry_delay:
                    return retry_delay + 5
            except (IndexError, KeyError):
                # retryDelayが取得できない場合はデフォルト値にフォールバック
                return 60
    return 60

class wait_from_exception(wait_base):
    def __init__(self):
        pass

    def __call__(self, retry_state: RetryCallState) -> float: # 型ヒントを修正
        if retry_state.outcome is None:
            return 0
        exception = retry_state.outcome.exception()
        return _calc_retry_delay(exception)

# リトライデコレータ
gemini_retry = retry(
    wait=wait_combine(
        wait_from_exception(), wait_exponential(multiplier=2, min=10, max=300)
    ),
    retry=retry_if_exception(_is_retriable),
    stop=stop_after_attempt(10),
)