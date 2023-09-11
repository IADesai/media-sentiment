DROP TABLE IF EXISTS sources CASCADE;
DROP TABLE IF EXISTS reddit_article CASCADE;
DROP TABLE IF EXISTS story_keyword_link CASCADE;
DROP TABLE IF EXISTS reddit_keyword_link CASCADE;
DROP TABLE IF EXISTS keywords CASCADE;
DROP TABLE IF EXISTS stories CASCADE;

CREATE TABLE sources(
    source_id INT GENERATED ALWAYS AS IDENTITY,
    source_name TEXT UNIQUE,
    PRIMARY KEY (source_id)
);

CREATE TABLE stories(
    story_id BIGINT GENERATED ALWAYS AS IDENTITY,
    source_id SMALLINT,
    title TEXT,
    description TEXT,
    url TEXT UNIQUE,
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
    re_url TEXT UNIQUE,
    re_sentiment_mean FLOAT,
    re_sentiment_st_dev FLOAT,
    re_sentiment_median FLOAT,
    re_vote_score INT,
    re_upvote_ratio FLOAT,
    re_post_comments INT,
    re_processed_comments INT,
    re_created_timestamp TIMESTAMP,
    PRIMARY KEY (re_article_id)
);

CREATE TABLE reddit_keyword_link(
    re_link_id INT GENERATED ALWAYS AS IDENTITY,
    keyword_id INT,
    re_article_id INT,
    PRIMARY KEY (re_link_id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id),
    FOREIGN KEY (re_article_id) REFERENCES reddit_article(re_article_id),
    ADD CONSTRAINT re_unique_id_pairs UNIQUE (keyword_id, re_article_id)
);

CREATE TABLE story_keyword_link(
    link_id INT GENERATED ALWAYS AS IDENTITY,
    keyword_id INT,
    story_id INT,
    PRIMARY KEY (link_id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id),
    FOREIGN KEY (story_id) REFERENCES stories(story_id),
    ADD CONSTRAINT unique_id_pairs UNIQUE (keyword_id, story_id)
);

INSERT INTO sources (source_name) VALUES ('bbc');
INSERT INTO sources (source_name) VALUES ('dailymail');


