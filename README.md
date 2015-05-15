# crabby_crawl
A database driven web crawler that searches for swag for you.

The project is written in Python and uses the Scrapy framework and SQLite3 package.

![alt tag](https://raw.github.com/smartsystems4u/crabby_crawl/master/crabby_crawl_overview.png)

This overview sketches the architecture of crabby_crawl. All the important parameters for your search are put in the database. They consist of

* URL's : The sites where the crawler will search your swag
* Objectives: The search terms that describe your target product
* Parsers: Each url has it's own xpath patterns that yield product desciptions, prices, etc.
* Criteria: Each objective is associated with criteria upon which each result is assigned a score. The criteria are simple python statements and therefore incredibly expressive (use with care).

Current objectives:
- Create the criteria / scoring system
- Create a search term recommender that learns which missing keywords can improve the average score of search results
