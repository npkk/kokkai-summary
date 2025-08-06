import scrapy


class SpeechItem(scrapy.Item):
    speechID = scrapy.Field()
    speechOrder = scrapy.Field()
    speaker = scrapy.Field()
    speakerYomi = scrapy.Field()
    speakerGroup = scrapy.Field()
    speakerPosition = scrapy.Field()
    speakerRole = scrapy.Field()
    speech = scrapy.Field()
    startPage = scrapy.Field()
    createTime = scrapy.Field()
    updateTime = scrapy.Field()
    speechURL = scrapy.Field()


class MeetingItem(scrapy.Item):
    issueID = scrapy.Field()
    imageKind = scrapy.Field()
    searchObject = scrapy.Field()
    session = scrapy.Field()
    nameOfHouse = scrapy.Field()
    nameOfMeeting = scrapy.Field()
    issue = scrapy.Field()
    date = scrapy.Field()
    closing = scrapy.Field()
    speechRecord = scrapy.Field()  # List of SpeechItem
    meetingURL = scrapy.Field()
    pdfURL = scrapy.Field()

class SessionItem(scrapy.Item):
    session = scrapy.Field()
    name = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
