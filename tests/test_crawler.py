from src.crawler import CubaTravelCrawler


def test_crawler():
    crawler = CubaTravelCrawler()
    crawler.crawl(["https://www.cuba.travel/"])
    crawler.close()


if __name__ == "__main__":
    test_crawler()
