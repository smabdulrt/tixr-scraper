from scrapy import Spider, Request
from datetime import datetime
from bs4 import BeautifulSoup
import usaddress


def format_date_time(unix_datetime):
    datetime_sec = unix_datetime / 1000
    datetime_obj = datetime.fromtimestamp(datetime_sec)
    date = datetime_obj.strftime('%Y-%m-%d')
    time = datetime_obj.strftime('%H:%M %p')
    return date, time


class TixrCrawlSpider(Spider):
    name = "tixr_crawl"
    start_urls = ["https://domain.com"]
    custom_settings = {
        'FEED_URI': "Tixr_output.json",
        'FEED_FORMAT': 'json',
        'FEED_EXPORT_INDENT': 2,
        # 'RETRY_ENABLED': True,
        # 'RETRY_TIMES': 5,
    }
    page = 1
    all_tags = [
        "Clubs", "Lounge", "Pool Hall", "Sports Bar", "Dive Bars", "Hookah Lounge",
        "Karaoke", "Drag Queen Show", "Dinner Party", "Live Music", "Outdoor",
        "Industry Night", "18+", "21+",
        "Any", "Casual", "Upscale", "Beach Attire",
        "Gay Friendly", "Senior Friendly", "Budget Friendly", "Upscale", "Happy Hour",
        "Ladies Night", "Smoke Free", "Join a Group",
        "Pop", "Rock", "Hip Hop", "Electronic / Dance", "R&B", "Latin", "Country",
        "Jazz", "Classical", "Blues", "Metal", "Indei", "Punk", "Funk", "Soul", "Gospel",
        "Aventura", "Bal Harbour", "Brickell", "Coconut Grove", "Coral Gables",
        "Design District", "Downtown", "Edgewater", "Fisher Island", "Hallandale Beach",
        "Key Biscayne", "Miami Beach", "Midtown", "North Bay Village", "Park West",
        "South Beach", "South of Fifth", "Sunny Isles Beach", "Surfside", "Wynwood"
    ]
    headers = {
        'authority': 'www.tixr.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'queryParams={}; datadome=zgXTadaNPiR_Y6LtgILw93BSb2d2o3t~oUCXZw9aDZnFRwUH6AqWECxdXcuUOcUnn8V6omEu511K8riSu2IjfAymoM7AE0u2dU2kuyuOGbm8E2FYQe9_1YSIgiCUeumC',
        'referer': 'https://www.upwork.com/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        url = "https://www.tixr.com/"
        yield Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, **kwargs):
        data = response.css("script:contains('xpid')").get('').split("{xpid:")[-1].split(',')[0].replace('"', '')
        headers = {
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'X-NewRelic-ID': f'{data}',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.tixr.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-platform': '"Windows"',
            # 'Cookie': 'datadome=jXTySj1OerCIjTF84VwdApReyH1Kiec1ixm2QUaXibLhWazx4JnvgaLvAMHg8Lb7hIw8evv8_qhyy5l3Z2vs6b0d2~~pK960fxfWAHwGFc8YoB5DknlwofyyF1uN0pbC'
        }
        url = "https://www.tixr.com/api/events?eventName=miami&page=1&pageSize=20"

        yield Request(url=url, callback=self.parse_details, headers=headers, meta={"id": data})
        pass

    def parse_details(self, response):
        records = response.json()
        all_events_urls = []
        for record in records:
            details = dict()
            all_events_urls.append(record.get("id"))
        data_id = response.meta['id']
        headers = {
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'X-NewRelic-ID': f'{data_id}',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.tixr.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-platform': '"Windows"',
            # 'Cookie': 'datadome=jXTySj1OerCIjTF84VwdApReyH1Kiec1ixm2QUaXibLhWazx4JnvgaLvAMHg8Lb7hIw8evv8_qhyy5l3Z2vs6b0d2~~pK960fxfWAHwGFc8YoB5DknlwofyyF1uN0pbC'
        }
        for event_url in all_events_urls[:]:
            url = f'https://www.tixr.com/api/events/{event_url}'
            yield Request(url=url, callback=self.parse_details_page, headers=headers)
        if all_events_urls:
            self.page += 1
            url = f"https://www.tixr.com/api/events?eventName=miami&page={self.page}&pageSize=20"
            yield Request(url=url, callback=self.parse_details, headers=headers, meta={"id": data_id})
        pass

    def parse_details_page(self, response):
        data = response.json()
        details = dict()
        details['id'] = data.get("id")
        details['name'] = data['name']
        details['image'] = data.get('flyerUrl', '')
        details['venue'] = data.get('venue', {}).get("name", '')
        details['venue_id'] = data.get('venue', {}).get('id', '')
        start_date, start_time = format_date_time(data.get('startDate', ''))
        end_date, end_time = format_date_time(data.get('endDate', ''))
        create_tags = data['name'].split(" ")

        common_tags = list(set(create_tags).intersection(set(self.all_tags)))
        details['tags'] = common_tags
        details['date'] = f'{start_date} - {end_date}'
        details['hours'] = f'{start_time} - {end_time}'
        address = f'{data.get("venue", {}).get("address", {}).get("streetAddress")}, {data.get("venue", {}).get("address", {}).get("city")}, {data.get("venue", {}).get("address", {}).get("state")} {data.get("venue", {}).get("address", {}).get("postalCode")}'
        details['location'] = address
        min_price = 0
        max_price = 0
        try:
            for key, value in data['filterConfiguration'].items():
                min_price = value.get("filters", [])[0].get("range", {}).get("min")
                max_price = value.get("filters", [])[0].get("range", {}).get("max")
                break
        except:
            details['price'] = f"${int(min_price)}-${int(max_price)}"
        details['dressCode'] = ''
        details['music'] = ''
        soup = BeautifulSoup(data.get("description", ''), "html.parser")
        text = soup.get_text(separator="\n")
        details['description'] = text.replace("\n", '').replace('\xa0', ' ')
        details['saves'] = 0
        details["url"] = data['url']
        details['checkIns'] = 0
        yield details

    def parse_detail_api(self, response):
        data = response.json()
        details = dict()
        details['id'] = data['id']
        details['name'] = data['name']
        details['tags'] = []
        details['venue'] = data.get("venue", {}).get("name", '')
        details['date'] = data.get("formattedStartDate", '').split(" at ")[0]
        details['hours'] = data.get("formattedStartDate", '').split(" at ")[-1]
        price = [i for i in data.get("sales", []) if i['state'] == 'OPEN']
        details['price'] = price[0].get("tiers", [])[0].get("price", '')
        details['description'] = data.get("description", '')
        details['Dresscode'] = ''
        details['music'] = ''
        details['image_url'] = data.get('backgroundUrl', '')
        pass
