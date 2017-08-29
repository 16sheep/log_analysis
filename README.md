
# Log analysis


### This is an internal reporting tool that will use information from the database to discover what kind of articles the site's readers like. The database contains newspaper articles, as well as the web server log for the site. The tool will connect to that database, use PostgreSQL queries to analyze the log data, and print out the answers to some questions to an html file. The result can be seen from log.png file.


### Tools needed
+ [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
+ [Vagrant](https://www.vagrantup.com/)
+ Python 2
+ [Udacity FSND Virtual Machine configuration](https://github.com/udacity/fullstack-nanodegree-vm)
+ A browser


### How to run
1. Install Virtual Machine and Vagrant
2. Clone FSND-Virtual-Machine and cd into it
3. Run vagrant up, then vagrant ssh from command line
4. Download [data](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip), unzip newsdata.sql into vagrant folder
5. run psql -d news to connect to the database
6. Create views 
7. Run python newslog.py from command line
8. Open the generated log_analysis.html file from vagrant folder


### Views as PostgreSQL queries

          1.create view author_id_views as
                select articles.author,
                count(log.path) as num
                from log
                right join articles on log.path
                like concat('%',articles.slug)
                and log.status = '200 OK'
                group by articles.author
                order by num desc;

          2.create view errors_by_date as
                select time ::timestamp::date,
                count(status) as errors
                from log
                where status = '404 NOT FOUND'
                group by time ::timestamp::date;

          3.create view status_by_date as
                select time ::timestamp::date,
                count(status) as status
                from log
                group by time ::timestamp::date; 

