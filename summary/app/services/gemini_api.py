from google import genai
from google.genai.errors import APIError
from google.genai.types import GenerateContentResponse

from app.config import GEMINI_API_KEY, MODEL, PROMPT
from app.utils.retry import gemini_retry


class GeminiAPIClient:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    @gemini_retry
    async def generate_content_from_file(self, file_path: str) -> GenerateContentResponse:
        """
        ファイルの内容を元にGemini APIでコンテンツを生成する
        """
        try:
            file = await self.client.aio.files.upload(file=file_path)
            response = await self.client.aio.models.generate_content(
                model=MODEL, contents=[PROMPT, file]
            )
            return response
        except APIError as e:
            print(f"APIError occurred in GeminiAPIClient: {e.code}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred in GeminiAPIClient: {e}")
            raise
