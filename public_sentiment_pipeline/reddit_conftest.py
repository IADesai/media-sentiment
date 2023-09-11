"""Contains useful properties for the unit tests"""

# pylint: skip-file

import pytest


class FakeGet:
    def __init__(self) -> None:
        self.status_code = 200

    def json(self):
        return {"success": True}


class FakePost:
    def __init__(self) -> None:
        self.status_code = 200

    def json(self):
        return {"success": True, "access_token": "this is an access token"}


@pytest.fixture
def fake_subreddit_json():
    return {
        "data": {
            "children": [
                {"data": {
                    "title": "a",
                    "permalink": "b",
                    "url": "c",
                    "domain": "d",
                    "score": 100,
                    "upvote_ratio": 0.6,
                    "num_comments": 10,
                    "created_utc": 1693809634.0
                }},
                {"data": {
                    "title": "e",
                    "permalink": "f",
                    "url": "g",
                    "domain": "h",
                    "score": 200,
                    "upvote_ratio": 0.35,
                    "num_comments": 125,
                    "created_utc": 1693809635.0
                }},
                {"data": {
                    "title": "i",
                    "permalink": "j",
                    "url": "k",
                    "domain": "l",
                    "score": 15,
                    "upvote_ratio": 0.12345,
                    "num_comments": 12345,
                    "created_utc": 1693809636.0
                }}
            ]
        }
    }


@pytest.fixture
def fake_subreddit_json_missing_entries():
    return {
        "data": {
            "children": [
                {"data": {
                    "title": "a",
                    "permalink": "b",
                    "url": "c",
                    "domain": "d",
                    "score": 100,
                    "upvote_ratio": 0.6,
                    "num_comments": 10,
                    "created_utc": 1693809634.0
                }},
                {"data": {
                    "title": "e",
                    "url": "g",
                    "domain": "h",
                    "score": 100,
                    "upvote_ratio": 0.6,
                    "num_comments": 10,
                    "created_utc": 1693809634.0
                }},
                {"data": {
                    "permalink": "j",
                    "url": "k",
                    "domain": "l",
                    "score": 100,
                    "upvote_ratio": 0.6,
                    "num_comments": 10,
                    "created_utc": 1693809634.0
                }},
                {"data": {
                    "title": "m",
                    "permalink": "o",
                    "domain": "p",
                    "score": 100,
                    "upvote_ratio": 0.6,
                    "num_comments": 10,
                    "created_utc": 1693809634.0
                }},
                {"data": {
                    "title": "q",
                    "permalink": "r",
                    "url": "s",
                    "score": 100,
                    "upvote_ratio": 0.6,
                    "num_comments": 10,
                    "created_utc": 1693809634.0
                }},
                {"data": {
                    "title": "t",
                    "permalink": "u",
                    "url": "v",
                    "domain": "w",
                    "score": 100,
                    "upvote_ratio": 0.6,
                    "num_comments": 10,
                    "created_utc": 1693809634.0
                }}
            ]
        }
    }


@pytest.fixture
def fake_json_content_1():
    return ['                        "awarders": [],",',
            '                        "banned_at_utc": null,',
            '                        "banned_by": null,',
            '                        "body": "This is the first comment.",',
            '                        "body_html": "&lt;div class=\"md\"&gt;&lt;p&gt;This is the first comment.&lt;/p&gt;\n&lt;/div&gt;",',
            '                        "can_gild": true,',
            '                        "can_mod_post": false,',
            '                        "collapsed": false,',
            '                        "awarders": [],"',
            '                        "banned_at_utc": null,',
            '                        "banned_by": null,',
            '                        "body": "This is the second comment.",',
            '                        "body_html": "&lt;div class=\"md\"&gt;&lt;p&gt;This is the second comment.&lt;/p&gt;\n&lt;/div&gt;",',
            '                        "can_gild": true,',
            '                        "can_mod_post": false,',
            '                        "collapsed": false,']


@pytest.fixture
def fake_json_content_2():
    return ['                        "awarders": [],",',
            '                        "banned_at_utc": null,',
            '                        "banned_by": null,',
            '                        "body": "This is the third comment.",',
            '                        "body_html": "&lt;div class=\"md\"&gt;&lt;p&gt;This is the first comment.&lt;/p&gt;\n&lt;/div&gt;",',
            '                        "can_gild": true,',
            '                        "body": "[removed]",',
            '                        "collapsed": false,',
            '                        "body": "[deleted]",',
            '                        "banned_at_utc": null,',
            '                        "body": "**Removed/tempban**",',
            '                        "body": "This is the fourth comment.",',
            '                        "body_html": "&lt;div class=\"md\"&gt;&lt;p&gt;This is the second comment.&lt;/p&gt;\n&lt;/div&gt;",',
            '                        "can_gild": true,',
            '                        "body": "**Removed/warning**",',
            '                        "collapsed": false,']


@pytest.fixture
def fake_page_response_list():
    return [{"title": "a", "subreddit_url": "b", "article_url": "c", "article_domain": "d", "comments": ["a", "b"]}, {"title": "e", "subreddit_url": "f", "article_url": "g", "article_domain": "h", "comments": ["c", "d"]}]
