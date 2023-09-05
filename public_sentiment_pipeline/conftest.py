"""Contains useful properties for the unit tests"""

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
                    "domain": "d"
                }},
                {"data": {
                    "title": "e",
                    "permalink": "f",
                    "url": "g",
                    "domain": "h"
                }},
                {"data": {
                    "title": "i",
                    "permalink": "j",
                    "url": "k",
                    "domain": "l"
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
                    "domain": "d"
                }},
                {"data": {
                    "title": "e",
                    "url": "g",
                    "domain": "h"
                }},
                {"data": {
                    "permalink": "j",
                    "url": "k",
                    "domain": "l"
                }},
                {"data": {
                    "title": "m",
                    "permalink": "o",
                    "domain": "p"
                }},
                {"data": {
                    "title": "q",
                    "permalink": "r",
                    "url": "s",
                }},
                {"data": {
                    "title": "t",
                    "permalink": "u",
                    "url": "v",
                    "domain": "w"
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
