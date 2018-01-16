#!/usr/bin/env python3 -tt
"""
File: wallscraper.py
--------------------
Course: CS 41
Name: Kiko Ilagan
SUNet: ilaganf

This program allows a user to connect to reddit.com and download images from the "hot" page
of the user's chosen subreddit.
"""
import wallscraperutils
import requests
import math
import re
import os

# Constants
REASONABLE_NAME_LENGTH = 50
REDDIT = "http://www.reddit.com/r/"
FOLDER = wallscraperutils.WALLPAPER_FOLDER
IMAGE_FORMATS = ['.jpg', '.jpe', '.png', '.bmp', '.gif']
HEADER = {'User-Agent': 'Wallscraper Script by ilaganf'}


def query(subreddit):
    '''
    Grabs the json information from the given subreddit, raises an error if anything
    other than an ok response happens
    '''

    try:
        response = requests.get(REDDIT+subreddit+'.json', headers=HEADER)
        response.raise_for_status()
    except:
        print("An error occurred trying to connect to Reddit")

    return response.json()


def extract_posts(json):
    '''
    Reddit returns its json data in a super nested dictionary, this just grabs all
    'post' structures from that data and puts them in a list
    '''

    # should be a list of dictionaries  
    return [json['data']['children'][x]['data'] for x in range(len(json['data']['children']))]


def convert_to_posts(data):
    '''
    When used in conjunction with query, user can get a neat list of RedditPost objects
    from a given subreddit page
    '''

    return [RedditPost(post) for post in extract_posts(data)]


def get_yes_or_no():
    '''
    Simple little helper for getting a yes or no answer from the user
    '''

    answer = input("Enter Y/N: ").strip().upper()
    while not answer or answer not in ['Y','N']:
        answer = input("Input not recognized. Please enter Y/N: ").strip().upper()
    return answer


class RedditPost:
    '''
    Defines the RedditPost class, which contains the pertinent pieces of information
    from any given "real-world" reddit post's data
    '''

    def __init__(self, data):
        self.subreddit = data.get('subreddit')
        self.is_self = data.get('is_self')
        self.ups = data.get('ups')
        self.post_hint = data.get('post_hint') # "image", "video", etc.
        self.title = data.get('title') # user given title
        self.downs = data.get('downs')
        self.score = data.get('score')
        self.url = data.get('url')
        self.domain = data.get('domain')
        self.permalink = data.get('permalink')
        self.created_utc = data.get('created_utc') # time code of post's creation
        self.num_comments = data.get('num_comments')
        self.preview = data.get('preview')
        self.name = data.get('name') # unique name
        self.over_18 = data.get('over_18') # boolean telling if the post is nsfw
        self.gilded = data.get('gilded')


    def _get_extension(self):
        '''
        For simplicity, assert that the last 4 characters of the url needs to
        be of the form ".[file format]"
        '''

        if self.url:
            # get last 4 characters
            return self.url[-1:-5:-1][::-1]


    def _process_title(self):
        '''
        Uses regular expressions to transform any post titles that don't play well with
        file systems into a nice, short, readable file name
        '''

        filename = re.sub(r'\[.*\]', '', self.title.strip()) # remove anything in [brackets]
        filename = re.sub(r"[',./!@#$%^&*{}|?<>~`+=:;\-\\\"]", '', filename) # omit non alphanumeric characters
        filename = re.sub(r' ', '_', filename) # replace spaces with underscores
        if len(filename) > REASONABLE_NAME_LENGTH:
            return filename[:REASONABLE_NAME_LENGTH - 1]
        return filename     


    def _get_dimensions(self):
        '''
        Dimensions of an image post are stored in the post preview dictionary, as a dictionary
        that is within a few nested structures

        Returns a tuple containing the aspect ratio, the width, and the height
        '''

        # self.preview is a dictionary containing the info about the post's content.
        # the desired dimensions are in 'images', which is a list of dictionaries that
        # details the various properties of the images in the post. The first entry in that
        # list contains a dictionary of the size data for each image. The image we want is
        # always entitled 'source'
        if (self.preview.get('images')):
            source = self.preview.get('images')[0].get('source') # self.preview is a dictionary
            height = source.get('height')
            width = source.get('width')
            return wallscraperutils.get_aspect_ratio(width, height), width, height


    def download(self):
        '''
        Can download a reddit post if it is a direct link to an image. Supported formats
        are .jpg, .png, .jpe, .bmp, and .gif

        Creates a new file per image in the "wallpapers" folder in the current directory
        '''

        # Check if the given link is a link to an image
        extension = self._get_extension()
        if not self.url or extension not in IMAGE_FORMATS:
            print("ERROR: {post} either didn't link to an image or its format isn't supported".format(post=self.title))
            return

        # Use the post's info to create a directory path and unique file name
        filename = self._process_title() + extension
        aspect_ratio, width, height = self._get_dimensions()
        ratio = "{width}x{height}".format(width=str(aspect_ratio[0]), height=str(aspect_ratio[1]))
        size = "{width}x{height}".format(width=str(width), height=str(height))

        # Check to see if the directory for that size exists, make it if not
        path = str(FOLDER/ratio/size)
        if not os.path.exists(path):
            os.makedirs(path)

        # Write by bytes into the proper directory
        with open(path + '/' + filename, 'wb+') as file:
            image = requests.get(self.url, headers=HEADER)
            byte_array = bytearray(image.content)
            file.write(byte_array)


    def __str__(self):
        return "{title} (score: {score}): {url}".format(title=self.title, score=self.score, url=self.url)


def download_specific(posts):
    '''
    Function that allows the user to try to download specific posts of the ones that wallscraper finds.
    '''

    print("\n\nOk, here are the posts I found:\n")
    for index in enumerate(posts):
        print("{index}: {post}\n".format(index=index[0], post=index[1]))

    while True:
        choice = input("\nWhich number would you like to download? (One at a time, q to quit): ").strip().lower()

        while not choice or choice not in ['q'] + list(map(str, range(len(posts)))):
            choice = input("Please enter a valid choice (q to quit): ").strip().lower()
        
        if choice == 'q': return

        print("Downloading {}...".format(posts[int(choice)]))
        posts[int(choice)].download()


def main():
    '''
    Handles user interaction and coordination of the different pieces of wallscraper.

    Allows the user to type in subreddits and download results based off of different criteria.
    '''
    
    print("\nHello! Welcome to Wallscraper! I can download images and gifs to be used as")
    print("wallpapers or to peruse offline from any subreddit that links directly to images! ")
    print("(If you don't know what a subreddit is, go to reddit.com and browse around)")
    print("\n ------------------------------------------------------------\n")

    while True:
        # Get user input
        print("What subreddit would you like to scrape from?")
        subreddit = input("Type a valid subreddit extension without r/ in front (ex: wallpapers, funny+pics): ").strip()
        while not subreddit:
            subreddit = input("Please enter a subreddit name: ")

        # Scrape, baby, scrape
        print("Attempting to connect to reddit...")
        posts = convert_to_posts(query(subreddit))

        # Filter out nsfw (Or don't. Naughty user.)
        print("Successful! Should I filter out posts tagged nsfw?")
        filter_nsfw = get_yes_or_no()
        if filter_nsfw == 'Y':
            posts = list(filter((lambda x: not x.over_18), posts))

        # Ask the user what they want to download
        print("\nI've managed to scrape " + str(len(posts)) + " posts from " + subreddit + "\n")
        print("\nI've managed to scrape {x} posts from {subreddit}".format(x=len(posts), subreddit=subreddit))
        print("Which ones should I download? ")
        print("0: all")
        print("1: gilded posts only")
        print("2: posts with a score greater than 500")
        print("3: posts with a score greater than 1000")
        print("4: posts with more than 100 comments")
        print("5: see/download specific post(s)")
        choice = input("Enter your choice (0-5): ")
        while not choice or choice not in ['0','1','2','3','4','5']:
            choice = input("Enter a number between 0 and 5, inclusive: ")

        # Filter the list of posts to try to download, dependent on above input
        if choice == '1':
            posts = list(filter((lambda x: x.gilded), posts))
        elif choice == '2':
            posts = list(filter((lambda x: x.score > 500), posts))
        elif choice == '3':
            posts = list(filter((lambda x: x.score > 1000), posts))
        elif choice == '4':
            posts = list(filter((lambda x: x.num_comments > 100), posts))
        elif choice == '5':
            download_specific(posts)

        # Download and save the posts (unless the user chose option 5, which handles its own dowloading)
        if choice != '5':
            for post in posts:
                print("Downloading {post}...".format(post=post.title))
                post.download()
        
        # I want to get off Mr. Bones's wild ride
        print("\n\nI've downloaded all the posts I could matching your choice! Again?")
        repeat = get_yes_or_no()
        
        if repeat == 'N':
            print("Enjoy your images!")
            break

if __name__ == '__main__':
    print("\nCS 41 final project: Wallscraper by Kiko Ilagan (credit to CS 41 staff for the idea and structure\n")
    main()