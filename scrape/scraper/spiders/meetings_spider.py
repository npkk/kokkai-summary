from urllib.parse import urlencode

import scrapy
from pydantic import ValidationError
from scrapy.exceptions import CloseSpider

from scraper.items import MeetingItem, SpeechItem
from scraper.schemas import NdlApiResponse, SpeechRequestParams


class MeetingsSpider(scrapy.Spider):
    name = "meetings_spider"
    allowed_domains = ["kokkai.ndl.go.jp"]
    base_url = "https://kokkai.ndl.go.jp/api/meeting?"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            # スパイダー引数をPydanticモデルで検証
            self.request_params = SpeechRequestParams(**kwargs)
        except ValidationError as e:
            self.logger.error(f"Invalid spider arguments: {e}")
            # エラーが発生した場合、スパイダーを停止させる
            raise CloseSpider(reason=f"Invalid spider arguments: {e}")

    async def start(self):
        # Pydanticモデルから辞書を生成し、Noneの値を除外
        params = self.request_params.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        )
        url = self.base_url + urlencode(params)
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        try:
            # レスポンスをPydanticモデルで検証
            data = NdlApiResponse.model_validate_json(response.body)
        except ValidationError as e:
            self.logger.error(f"Response validation failed: {e} URL: {response.url}")
            return

        for meeting_record in data.meetingRecord:
            meeting_item = MeetingItem()
            # PydanticオブジェクトからItemへデータをコピー
            for field in meeting_item.fields:
                if hasattr(meeting_record, field):
                    meeting_item[field] = getattr(meeting_record, field)

            speeches = []
            for speech_record in meeting_record.speechRecord:
                speech_item = SpeechItem()
                for field in speech_item.fields:
                    if hasattr(speech_record, field):
                        speech_item[field] = getattr(speech_record, field)
                speeches.append(speech_item)

            meeting_item["speechRecord"] = speeches
            yield meeting_item

        # 次のページの処理
        if data.nextRecordPosition:
            self.request_params.startRecord = data.nextRecordPosition
            params = self.request_params.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            )
            url = self.base_url + urlencode(params)
            yield scrapy.Request(url, self.parse)
