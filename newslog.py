#!/usr/bin/env python
from __future__ import division
import psycopg2
import webbrowser
import os


"""Database queries and functions(python2 with PostgreSQL and psycopg2)
   views: 1)create view author_id_views as
                select articles.author,
                count(log.path) as num
                from log
                right join articles on log.path
                like concat('%',articles.slug)
                and log.status = '200 OK'
                group by articles.author
                order by num desc;

          2)create view errors_by_date as
                select time ::timestamp::date,
                count(status) as errors
                from log
                where status = '404 NOT FOUND'
                group by time ::timestamp::date;

          3)create view status_by_date as
                select time ::timestamp::date,
                count(status) as status
                from log
                group by time ::timestamp::date;
"""


# Styles and scripting for the page
main_page_head = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Analysis</title>
    <style type="text/css" media="screen">
        p {
            white-space: pre-wrap;
            color: #4d4d4d;
        }

        h1 {
            color: #b74e40;
            font-family: Arial;
        }

        h2 {
            color: #999;
            font-family: Arial;
        }

        .root {
            max-width: 400px;
            margin: 0 auto;
        }
    </style>
    <script type="text/javascript" charset="utf-8">
    </script>
</head>
'''

# The main page layout and title bar
main_page_content = '''
  <body>
    <div class="root">
        <h1>Newspaper Log Analysis</h1>
        {result_content}
    </div>
  </body>
</html>
'''

result_content = '''
    <div id="main_container">
        <h2>3 most popular articles of all time</h2>
        <p>{most_popular_articles}</p>
        <h2>Most popular authors</h2>
        <p>{most_popular_authors}</p>
        <h2>Dates with more than 1% of bad requests</h2>
        <p>{bad_requests}</p>
    </div>
    '''


def create_result():
    # Create html content for results
    content = ''
    content += result_content.format(
            most_popular_articles=popular_articles(),
            most_popular_authors=popular_authors(),
            bad_requests=errors()
        )
    return content


def open_log():
    # Create or open the output file
    output_file = open('log_analysis.html', 'w')

    rendered_content = main_page_content.format(
        result_content=create_result())

    # Output the file
    output_file.write(main_page_head + rendered_content)
    output_file.close()

    # open the output file in the browser (in a new tab, if possible)
    url = os.path.abspath(output_file.name)
    webbrowser.open('file://' + url, new=2)


def popular_articles():
    """Queries database for 3 most popular articles
       of all time returns a single string with 3 titles and their views
    """
    db = psycopg2.connect(database="news")
    cursor = db.cursor()
    cursor.execute("""select articles.title,
                    count(log.path) as num
                    from log
                    right join articles on log.path
                    = concat('/article/',articles.slug)
                    and log.status = '200 OK'
                    group by articles.title
                    order by num desc limit 3""")
    logged_paths = cursor.fetchall()
    db.close()
    res = ''
    for article in logged_paths:
        res = res + article[0] + " has " + str(article[1]) + " views \n"
    return res


def popular_authors():
    """Queries database for authors and how many times their
       articles have been read with the help of view nr. 1
       returns a single string containing with
       authors and views sorted by descending views
    """
    db = psycopg2.connect(database="news")
    cursor = db.cursor()
    cursor.execute("""select name, num
                    from authors, author_id_views
                    where authors.id = author_id_views.author""")
    authors = cursor.fetchall()
    db.close()
    res = ''
    for author in authors:
        res = res + author[0] + " has " + str(author[1]) + " views \n"
    return res


def errors():
    """Queries database for percentage of bad requests by date
       with the hep of views nr. 2 and 3 returns single string
       with dates and percentages of bad requests
    """
    db = psycopg2.connect(database="news")
    cursor = db.cursor()
    cursor.execute("""select errors_by_date.time,
                    errors_by_date.errors::float / status_by_date.status * 100
                    from errors_by_date, status_by_date
                    where errors_by_date.time = status_by_date.time""")
    err = cursor.fetchall()
    db.close()
    res = ''
    for current_date in err:
        if current_date[1] >= 1:
            res = res + current_date[0].strftime('On %d, %b %Y there were ') \
                  + str(round(current_date[1], 2)) + "% of bad requests. \n"
    return res


open_log()
