README

Dependencies:
requests.py: http://docs.python-requests.org/en/master/
Python Standard Library (wallscraper.py was written using Python 3.4.3, all other versions are untested)
working internet connection

Installation:
Install requests (easy if you have PyPI, just type the command "pip requests" in the command line)
Make sure that wallscraper.py and wallscraperutils.py are both in the current working directory

Execution:
Simple! Just run the main script, wallscraper.py, from the command line: python3 wallscraper.py

Technical details:

wallscraper.py: harnessing the power of requests, this script connects to reddit and scrapes images from a given subreddit.
    - Asks user for subreddit to scrape from
    - Attempts to connect to reddit and navigates to that subreddit's "hot" page
    - Once the connection is established and relevant data retrieved, prompts the user to tell it which posts to download
    - Attempts to download those posts and creates a folder in the working directory to save them to
        - Organizes pictures by aspect ratio, then actual size
Note that as of the current version, wallscraper can only download reddit posts if they directly link to a .jpg, .png, .jpe, .bmp, or .gif formatted image. 
The centerpiece of this code is the RedditPost class, which takes "post" structures from reddit's super nested json dictionary and contains the following pieces of information:
    - subreddit: what subreddit the post is from (string)
    - is_self: whether or not the post is a self post, which is entirely text (0 or 1)
    - ups: the number of upvotes this post has (integer)
    - downs: the number of downvotes this post has (integer)
    - score: this post's overall score
    - post_hint: Reddit's guess about what the post is (string)
    - title: the title given to the post by the original poster (string)
    - url: the url that the post links to, where the content is (string)
    - domain: the domain of the url (string)
    - permalink: a permanent link to the reddit post (string)
    - created_utc: time code of the post's creation (double)
    - num_comments: the current number of comments the post has (integer)
    - preview: dictionary containing the image previews (dict)
    - name: unique name Reddit gives the post (string)
    - over_18: tells whether or not the post is nsfw (0 for safe, 1 for unsafe)
    - gilded: whether or not the post has been awareded Reddit gold (0 or 1)
Additionally, the RedditPost class supports the following functions:
    - download(): the only public function in the class, attempts to download whatever the post's url links to
    - _get_extension(): gets whatever file extension is at the end of the url
    - _process_title(): turns the post's title into something more friendly for filesystems
    - _get_dimensions(): if the post is an image, gets its aspect ratio, width, and height
    - __str__(): magic method that allows a RedditPost to be represented as a string
There are also a few one-off functions that handle a few miscellaneous things:
    - query(subreddit): retrieves the json information from the entered subreddit from Reddit
    - extract_posts(json): given raw json data from a Reddit page, puts all the "post" structures in a list
    - convert_to_posts(data): given a raw list of posts from extract_posts, then turns them all into RedditPost objects
    - get_yes_or_no(): helper function for getting a yes or no answer from the user for interaction


wallscraperutils.py: contains a few tools for use with wallscraper.
    - get_aspect_ratio(width, height): given an image's dimensions, finds the closest aspect ratio that matches the image's format
    - WALLPAPER_FOLDER: a constant that gets the current working directory path so that wallscraper can create a folder in the right place

For other technical questions, I direct you to the source code itself. It's all well-commented and easy to read

Acknowledgements:
Thanks to the CS41 course staff for the idea for wallscraper, and for telling me how Reddit organizes its data.
