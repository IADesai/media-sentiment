DROP TABLE IF EXISTS sources;
DROP TABLE IF EXISTS reddit_article;
DROP TABLE IF EXISTS story_keyword_link;
DROP TABLE IF EXISTS reddit_keyword_link;
DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS stories;

CREATE TABLE sources(
    source_id INT GENERATED ALWAYS AS IDENTITY,
    source_name TEXT UNIQUE,
    PRIMARY KEY (source_id)
);

CREATE TABLE stories(
    story_id INT GENERATED ALWAYS AS IDENTITY,
    source_id INT,
    title TEXT,
    description TEXT,
    pub_date TIMESTAMP,
    media_sentiment FLOAT,
    PRIMARY KEY (story_id),
    FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE keywords(
    keyword_id INT GENERATED ALWAYS AS IDENTITY,
    keyword TEXT UNIQUE,
    PRIMARY KEY (keyword_id)
);

CREATE TABLE reddit_article(
    re_article_id INT GENERATED ALWAYS AS IDENTITY,
    re_domain TEXT,
    re_title TEXT,
    re_article_url TEXT,
    re_url TEXT,
    public_sentiment FLOAT,
    PRIMARY KEY (re_article_id)
);

CREATE TABLE reddit_keyword_link(
    re_link_id INT GENERATED ALWAYS AS IDENTITY,
    keyword_id INT,
    re_article_id INT,
    PRIMARY KEY (re_link_id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id),
    FOREIGN KEY (re_article_id) REFERENCES reddit_article(re_article_id)
);

CREATE TABLE story_keyword_link(
    link_id INT GENERATED ALWAYS AS IDENTITY,
    keyword_id INT,
    story_id INT,
    PRIMARY KEY (link_id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id),
    FOREIGN KEY (story_id) REFERENCES stories(story_id)
);