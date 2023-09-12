# Media Sentiment Project

Despite reporting on the same topics, different media organisations can have wildly different coverage/messages. Collecting and analysing data on how coverage differs between different organisations will help us understand the media landscape and bias.

## The Team

[Isaac Van Bueren](https://github.com/isaac-vb) - Engineer/Project Manager  
[Remi Khalif](https://github.com/rk145lr) - Engineer/Architect  
[Ramiz Ali](https://github.com/ramiz76) - Engineer/Quality Assurance  
[Ibrahim Ayub Desai](https://github.com/IADesai) - Engineer/Quality Assurance

## About the Project

This project extracts UK news articles from different RSS feeds and finds related articles from other news feeds as well as comments about that story/topic on Reddit. Sentiment analysis is then applied to these news articles and social media comments and scores them depending on how positive/negative they are (-1 being the most negative, 1 being the most positive). The articles then have their topic keywords extracted using ChatGPT, this allows for articles/social media posts talking about the same news story/topic can be linked together. All of this information is then loaded onto an RDS which is running PostgreSQL. From the RDS, we visualise the wide variety of information we have gathered via a Tableau dashboard and also send out an email report with a PDF attached showing the most popular stories of the day amongst other key insights.  

## About the Repo

For more detailed setup, check the individual README files within each folder.

`rss_pipeline` - Extracts relevant information from the news feeds, transforms it and loads it onto the database.  
`public_sentiment_pipeline` - Extracts relevant information from Reddit pages, transforms it and loads it onto the database.  
`terraform` - Contains the code to setup/remove AWS resources effectively using Terraform.  
`setup.sql` - SQL file which sets up the database used within the pipelines.  
`.github/workflows` - Contains the workflows which run `pytest` and `pylint` for every pull request opened with `main` as the target branch.

## Architecture Diagram

<img src="architecture-diagram.svg" alt="Architecture Diagram" width="1000"/>
