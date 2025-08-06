import json
import re
from datetime import datetime

import scrapy
from scraper.items import SessionItem


class SessionsSpider(scrapy.Spider):
    name = "sessions_spider"
    allowed_domains = ["kokkai.ndl.go.jp"]
    
    async def start(self):
        url = "https://kokkai.ndl.go.jp/minutes/api/v1/name/kaijifp"
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        data = json.loads(response.body)
        date_pattern = re.compile(
            r"\((\d{4})\)年(\d+)月(\d+)日～.*\((\d{4})\)年(\d+)月(\d+)日"
        )

        for session_data in data.get("data", []):
            item = SessionItem()
            
            session_code = session_data.get("code")
            name_full = session_data.get("name", "")

            if not session_code or not name_full:
                continue

            item["session"] = int(session_code)
            
            # 会議名部分を抽出
            name_parts = name_full.split(" ")
            item["name"] = " ".join(name_parts[:2])

            # 日付を抽出
            date_match = date_pattern.search(name_full)
            if date_match:
                s_year, s_month, s_day, e_year, e_month, e_day = date_match.groups()
                try:
                    item["start_date"] = datetime(int(s_year), int(s_month), int(s_day)).date()
                    item["end_date"] = datetime(int(e_year), int(e_month), int(e_day)).date()
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Could not parse date for session {item['session']}: {e}")
                    item["start_date"] = None
                    item["end_date"] = None
            else:
                self.logger.warning(f"Could not find dates for session {item['session']}")
                item["start_date"] = None
                item["end_date"] = None

            yield item
