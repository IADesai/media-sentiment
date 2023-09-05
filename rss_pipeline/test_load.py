from load import extract_source_from_url


def test_extract_source_from_url_returns_valid_source_for_bbc():
    url = "https://www.bbc.co.uk/news/uk-northern-ireland-66715623"
    assert extract_source_from_url(url) == 'bbc'


def test_extract_source_from_url_returns_valid_source_for_dailymail():
    url = "https://www.dailymail.co.uk/news/uk-northern-ireland-66715623"
    assert extract_source_from_url(url) == 'dailymail'


def test_extract_source_from_url_returns_valid_source_for_independent():
    url = "https://www.independent.co.uk/life-style/royal-family/prince-andrew-files-royal-family-b2404639.html?utm_source=reddit.com"
    assert extract_source_from_url(url) == 'independent'


def test_extract_source_from_url_returns_valid_source_for_guardian():
    url = "https://www.theguardian.com/society/2023/sep/05/birmingham-city-council-financial-distress-budget-section-114?CMP=Share_AndroidApp_Other"
    assert extract_source_from_url(url) == 'theguardian'


def test_extract_source_from_url_returns_valid_source_for_mirror():
    url = "https://www.mirror.co.uk/news/uk-news/rare-proof-copy-first-harry-30865794"
    assert extract_source_from_url(url) == 'mirror'
