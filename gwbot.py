import praw, re, os, io, random, string, imgurpython, urllib.request

from twython import Twython
from PIL import Image,ImageDraw,ImageFont
from sys import exit,argv
from os import environ

post_limit = 500
font_path = os.path.join('fonts', 'OpenSans-Regular.ttf')
title_font_size = 90
subtitle_font_size = 60

padding_vert = 30
padding_vert2 = 30
padding_horiz = 30

environ["twitter_app_key"] = "iLMVoNLQZBUrt7mjwfZMQ"
environ["twitter_app_secret"] = "NDbXTzkWiHrG59gL1zMVosU4AzhUNhlH4qyK5vYNk"
environ["twitter_oauth_token"] = "2384365692-VKnymNfB6wGhBps9obtM4yTxFiJa95JMWDMQYcc"
environ["twitter_oauth_token_secret"] = "kP4kwJk6XC2dm9y1HCD3a2JcRLbhPJOpUEGqwlipydkET"
environ["imgur_client_id"] = "21126a4485580a8"
environ["imgur_client_secret"] = "e22520024677935ca788bc1525318f23b128c047"

def login_to_twitter():
	twitter = Twython(environ["twitter_app_key"], environ["twitter_app_secret"], environ["twitter_oauth_token"], environ["twitter_oauth_token_secret"])
	return twitter

def login_to_reddit():
	reddit = praw.Reddit(user_agent="ayyyy lmaooo")
	return reddit

def login_to_imgur():
	imgur = imgurpython.ImgurClient(environ['imgur_client_id'],environ['imgur_client_secret'])
	return imgur

#==============

def upload_to_imgur(image_path):
	print ("uploading to imgur...")
	return imgur.upload_from_path(image_path)

def upload_to_twitter(image, status):
	print ("uploading to twitter...")

	media_id = twitter.upload_media(media=image)['media_id']
	print (media_id)
	twitter.update_status(media_ids = [media_id], status = status)

	image.close()

#==============

def fetch_post(subreddit, require_imgur):
	print ("fetching %s post" % subreddit)
	posts = reddit.get_subreddit(subreddit).get_top_from_week(limit = post_limit)
	return random.choice([post for post in posts if (True if not require_imgur else ('imgur' in post.url))])

def fetch_image_and_title():
	post = fetch_post(("earthporn" if (random.random() > 0.5) else "spaceporn"), True)
	if not post.url.endswith((".png",".jpeg",".jpg")): post.url += ".jpg"
	print ("fetching %s" % post.url)

	return Image.open(io.BytesIO(urllib.request.urlopen(post.url).read())), post.title

def get_random_comment(post):
	pauthor = post.author
	comments = post.comments

	if (len(comments) == 0): exit("\t >>>>> no comments on post; exiting")

	return random.choice([comment for comment in comments if comment.author != pauthor and comment.body != '[deleted]'])

def draw_text(image, title, top_comment):
	global title_font_size, subtitle_font_size, padding_vert2
	draw = ImageDraw.Draw(image)

	image_width, image_height = image.size
	set_text_size(draw, title, top_comment, image_width, image_height)

	twidth, theight = draw.textsize(title, font = ImageFont.truetype(font_path, title_font_size))
	stwidth, stheight = draw.textsize(top_comment, font = ImageFont.truetype(font_path, subtitle_font_size))
	set_padding_vert2(title)

	if random.random() > 0.5: # top
		title_pos_y = padding_vert
		subtitle_pos_y = title_pos_y + theight + padding_vert2
	else: # bottom
		subtitle_pos_y = image_height - padding_vert - stheight
		title_pos_y = subtitle_pos_y - padding_vert2 - theight

	if random.random() > 0.5: # left
		title_pos_x, subtitle_pos_x = padding_horiz, padding_horiz
	else: # right
		title_pos_x = image_width - padding_horiz - twidth
		subtitle_pos_x = image_width - padding_horiz - stwidth

	draw_stroke(draw, title_pos_x, title_pos_y, subtitle_pos_x, subtitle_pos_y, title, top_comment)
	draw.text((title_pos_x, title_pos_y), title, font = ImageFont.truetype(font_path, title_font_size), fill = 'white')
	draw.text((subtitle_pos_x, subtitle_pos_y), top_comment, font = ImageFont.truetype(font_path, subtitle_font_size), fill = 'white')

	return image

def set_padding_vert2(title):
	# (){}[]gypqj
	global padding_vert2
	if set(title).intersection(set(list('(){}[]gypqj'))): padding_vert2 = 35

def set_text_size(draw, title, top_comment, image_width, image_height):
	global title_font_size, subtitle_font_size

	orig_font_size = title_font_size
	twidth, theight = draw.textsize(title, font = ImageFont.truetype(font_path, orig_font_size)) # base values

	if twidth > image_width: 
		while draw.textsize(title, font = ImageFont.truetype(font_path, title_font_size))[0] > (image_width - 2 * padding_horiz): title_font_size -= 1
	else: 
		while draw.textsize(title, font = ImageFont.truetype(font_path, title_font_size))[0] < (image_width - 2 * padding_horiz): title_font_size += 1

	orig_font_size = subtitle_font_size
	stwidth, stheight = draw.textsize(top_comment, font = ImageFont.truetype(font_path, orig_font_size)) # base values
	
	if stwidth > image_width: 
		while draw.textsize(top_comment, font = ImageFont.truetype(font_path, subtitle_font_size))[0] > (image_width - 2 * padding_horiz): subtitle_font_size -= 1
	if stwidth < (image_width / 3.0):
		while draw.textsize(top_comment, font = ImageFont.truetype(font_path, subtitle_font_size))[0] > (image_width - 2 * padding_horiz): 
			subtitle_font_size += 1
			if subtitle_font_size > 100: break

def draw_stroke(draw, title_pos_x, title_pos_y, subtitle_pos_x, subtitle_pos_y, title, subtitle): # thick border
	draw.text((title_pos_x - 1, title_pos_y - 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((title_pos_x + 1, title_pos_y - 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((title_pos_x - 1, title_pos_y - 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((title_pos_x + 1, title_pos_y + 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((subtitle_pos_x - 1, subtitle_pos_y - 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')
	draw.text((subtitle_pos_x + 1, subtitle_pos_y - 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')
	draw.text((subtitle_pos_x - 1, subtitle_pos_y - 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')
	draw.text((subtitle_pos_x + 1, subtitle_pos_y + 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')

def generate_image():
	gw_post = fetch_post('gonewild', False)
	original_image, original_title = fetch_image_and_title()
	top_comment = get_random_comment(gw_post).body # slow as shit 'cause lazy objects

	image = draw_text(original_image, gw_post.title, top_comment)
	f_name = "images%s%s.jpg" % (os.sep,gw_post.name.split("_")[1])
	image.save(f_name)
	
	uploaded_image = upload_to_imgur(os.path.realpath(f_name))
	upload_to_twitter(open(os.path.realpath(f_name), 'rb'),
					  "%s [larger: %s]" % (original_title[:min(original_title.find('['),100 - len(uploaded_image['link']) - 10)], uploaded_image['link']))	

	print ('from: redd.it/%s, uploaded image at: %s' % (gw_post.name.split("_")[1], uploaded_image['link']))

twitter = login_to_twitter()
imgur = login_to_imgur()
reddit = login_to_reddit()

generate_image()