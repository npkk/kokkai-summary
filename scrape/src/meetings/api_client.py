from typing import Optional

import httpx
from pydantic import ValidationError

from .request_schema import SpeechRequestParams
from .response_schema import NdlApiResponse


class NdlApiClient:
    def __init__(self):
        self.base_url = "https://kokkai.ndl.go.jp/api/"

    async def fetch_meeting_records(
        self, params: SpeechRequestParams
    ) -> Optional[NdlApiResponse]:
        """
        国会会議録検索システムAPIから会議録データを取得します。
        """
        url = f"{self.base_url}meeting"
        # Pydanticモデルを辞書に変換。Noneの値は除外し、エイリアスを適用する。
        request_params = params.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        )
        print(request_params)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=request_params)
                with open("response.json", "w") as f:
                    f.write(response.text)
                response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
                return NdlApiResponse.model_validate(response.json())
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            raise exc
        except httpx.HTTPStatusError as exc:
            print(
                f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
            )
            raise exc
        except ValidationError as e:
            print(f"Validation error occurred: {e}")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e
