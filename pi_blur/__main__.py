from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
from dotenv import load_dotenv
from requests import post, get
import os
from datetime import datetime
from io import BytesIO
import base64

load_dotenv()

API_PREFIX = 'https://www.newsblur.com/'

USER_NAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
FEED_ID = os.getenv('FEED_ID')


inky_display = InkyPHAT("black")
inky_display.set_border(inky_display.WHITE)
font = ImageFont.truetype(
    "/usr/share/fonts/truetype/darkergrotesque/DarkerGrotesque-Bold.ttf", 20)

def wrap_text(text, width, font):
    text_lines = []
    text_line = []
    text = text.replace('\n', ' [br] ')
    words = text.split()
    font_size = font.getsize(text)

    for word in words:
        if word == '[br]':
            text_lines.append(' '.join(text_line))
            text_line = []
            continue
        text_line.append(word)
        w, h = font.getsize(' '.join(text_line))
        if w > width:
            text_line.pop()
            text_lines.append(' '.join(text_line))
            text_line = [word]

    if len(text_line) > 0:
        text_lines.append(' '.join(text_line))

    return text_lines

def get_newsblur_cookies(user, password = ''):
  data = {'username': user}

  if(password):
    data.password = password

  response = post(API_PREFIX + 'api/login', data=data)
  return response.cookies

def fetch_recent_story(cookies, feed_id):
  response = post(API_PREFIX + '/reader/feed/' + str(feed_id), cookies=cookies, data={'include_story+content': False}).json()
  favicons = get(API_PREFIX + 'reader/favicons?feed_ids=' + str(feed_id), cookies=cookies).json()
  recent_story = list(response.get('stories'))[0]
  return {
    'date': datetime.fromtimestamp(int(recent_story.get('story_timestamp'))),
    'headline': recent_story.get('story_title'),
    'favicon': favicons.get(feed_id)
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

def main():
  cookies = get_newsblur_cookies(USER_NAME, PASSWORD)
  feeds = get_newsblur_feed_list(cookies)
  stories = list(map(lambda feed: fetch_recent_story(cookies, feed), feeds))
  sorted_stories = sorted(stories, key=lambda k: k['date'])[::-1]
  most_recent = sorted_stories[0]
  img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
  draw = ImageDraw.Draw(img)
  lines = wrap_text(most_recent.get('headline'), inky_display.WIDTH, font)
  y_text = 0

  for line in lines:
    width, height = font.getsize(line)
    draw.text((0, y_text), line, inky_display.BLACK, font)
    y_text += height

  favicon = Image.open(BytesIO(base64.b64decode(most_recent.get('favicon')))
  img.paste(favicon, (0, y_text))
  inky_display.set_image(img)
  inky_display.show()
  print(most_recent.get('headline') + ' ' + most_recent.get('date').strftime('%b %-d, %Y %-I:%M %p'))

if __name__ == '__main__':
  main()
