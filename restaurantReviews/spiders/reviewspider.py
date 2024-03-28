import scrapy
from restaurantReviews.items import BookItem
from datetime import datetime, timedelta
import re

class ReviewSpider(scrapy.Spider):
    name = "reviewspider"
    allowed_domains = ["www.opentable.com"]
    start_urls = ["https://www.opentable.com/michael-jordans-steak-house-mohegan-sun?page=1"]

    def convert_date(self, text, reference_date):
        # Patterns for "X days ago" and exact dates
        days_ago_pattern = re.compile(r"Dined (\d+) days ago")
        exact_date_pattern = re.compile(r"Dined on (\w+ \d{1,2}, \d{4})")
        
        days_ago_match = days_ago_pattern.search(text)
        exact_date_match = exact_date_pattern.search(text)
        
        if days_ago_match:
            days = int(days_ago_match.group(1))
            new_date = reference_date - timedelta(days=days)
        elif exact_date_match:
            new_date = datetime.strptime(exact_date_match.group(1), "%B %d, %Y")
        else:
            return "Invalid date format"
        
        return new_date.strftime("%m/%d/%Y")

    def parse(self, response):
        reviews = response.css('li.afkKaa-4T28-')
        today = datetime.now()  # Use current date as reference

        for review in reviews:
            raw_date = review.css('p.iLkEeQbexGs-::text').get()
            converted_date = self.convert_date(raw_date, today)
            
            book_item = BookItem()
        
            book_item['name'] = review.css('p._1p30XHjz2rI-::text').get(),
            book_item['review'] = review.css('div._6rFG6U7PA6M- > span::text').get(),
            book_item['rating'] = review.css('div.tSiVMQB9es0-::text').get(),
            book_item['date'] = converted_date
            
            yield book_item

        # Handling pagination
        current_page_number = response.url.split('page=')[1]
        next_page_number = int(current_page_number) + 1

        if next_page_number <= 179:  # Example limitation for demonstration
            next_page_url = f'https://www.opentable.com/michael-jordans-steak-house-mohegan-sun?page={next_page_number}'
            yield response.follow(next_page_url, callback=self.parse)
