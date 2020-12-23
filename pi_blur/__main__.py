from dotenv import load_dotenv
from requests import post
import os
from datetime import datetime

load_dotenv()

API_PREFIX = 'https://www.newsblur.com/'

USER_NAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
FEED_ID = os.getenv('FEED_ID')

def get_newsblur_cookies(user, password = ''):
  data = {'username': user}

  if(password):
    data.password = password

  response = post(API_PREFIX + 'api/login', data=data)
  return response.cookies

def fetch_recent_story(cookies, feed_id):
  response = post(API_PREFIX + '/reader/feed/' + str(feed_id), cookies=cookies).json()
  recent_story = list(response.get('stories'))[0]
  return {
    'date': datetime.fromtimestamp(int(recent_story.get('story_timestamp'))),
    'headline': recent_story.get('story_title')
  }

def find_folder(folders, feed_id):
  for folder in folders:
    if(type(folder) is dict and list(folder.keys())[0]==feed_id):
      return folder.get(feed_id)
    elif(folder == feed_id):
      return [folder]

def get_newsblur_feed_list(cookies):
  response = post(API_PREFIX + '/reader/feeds', cookies=cookies).json()
  feeds = find_folder(response.get('folders'), FEED_ID)
  if(not feeds):
    feeds = list([FEED_ID])
  return feeds

def print_story(story):
  print(story)


def main():
  cookies = get_newsblur_cookies(USER_NAME, PASSWORD)
  feeds = get_newsblur_feed_list(cookies)
  stories = list(map(lambda feed: fetch_recent_story(cookies, feed), feeds))
  sorted_stories = sorted(stories, key=lambda k: k['date'])[::-1]
  most_recent = sorted_stories[0]
  print(most_recent.get('headline') + ' ' + most_recent.get('date').strftime('%b %-d, %Y %-I:%M %p'))

if __name__ == '__main__':
  main()