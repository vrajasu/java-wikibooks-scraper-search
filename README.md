# java-wikibooks-scraper-search

The application mainly has the following two parts.
1. Scraping Data using BeautifulSoup in Python
2. Using Solr to Index and search data for content based recommendation

## Scraping Data
I have written a simple scraper that can be found in the app.py file. The scraper makes use of the BeautifulSoup Library and scraps data from the Java WikiBooks tutorials. These pages are scraped section by section and the text, url, title and html are extracted.

## Solr to index data and search data for Content Based recommendation
I change the default Solr schema to add a field that automatically removes stop words and applies porter stemming before indexing the text data. While querying from the application I use a python's nltk library to remove stem words and apply stemming to make a better query. The query returns the html which is stored in the Solr Store. This html is then rendered on the screen to provide a decent recommendation. Extracting the html makes sure that the code formatting in the tutorials stays intact and provides for a pleasant reading experience to the user.

The application is made in Flask Python and the front end is made in vanilla HTML,CSS,JS(and JQuery)
