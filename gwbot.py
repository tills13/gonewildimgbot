import praw, pyimgur, re, os, random, sys, string

from twython import Twython
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from config import config
#from Image.draw import textsize

post_limit = 500
font_path = os.path.join('fonts', 'OpenSans-Light.ttf')
title_font_size = 90
subtitle_font_size = 60

padding_vert = 30
padding_vert2 = 30
padding_horiz = 30

twitter = Twython(config['twitter_app_key'], config['twitter_app_secret'], config['twitter_oauth_token_key'], config['twitter_oauth_token_secret'])
imgur = pyimgur.Imgur(config['imgur_id'])
reddit = praw.Reddit("idgaf")

def fetch_gonewild_post():
	print('fetching gonewild post')
	posts = reddit.get_subreddit('gonewild').get_top_from_month(limit = post_limit)

	return random.choice([post for post in posts])

def fetch_image():
	print('fetching image')
	post = fetch_earthporn_post() if random.random() > 0.5 else fetch_spaceporn_post()
	return imgur.get_image(get_imgur_url(post.url)).download(), post.title


def fetch_earthporn_post():
	posts = reddit.get_subreddit('earthporn').get_top_from_month(limit = post_limit)
	return random.choice([post for post in posts if 'imgur' in post.url])

def fetch_spaceporn_post():
	posts = reddit.get_subreddit('spaceporn').get_top_from_month(limit = post_limit)
	return random.choice([post for post in posts if 'imgur' in post.url])

def get_imgur_url(full_url):
	return re.match(r'https?://(?:(?:i|www)\.)?imgur.com/(?:a/)?([^\.]*)(\?.*)?', full_url).group(1)

def draw_text(image, title, top_comment):
	global title_font_size, subtitle_font_size, padding_vert2
	draw = ImageDraw.Draw(image)

	image_width, image_height = image.size
	set_text_size(draw, title, top_comment, image_width, image_height)

	twidth, theight = draw.textsize(title, font = ImageFont.truetype(font_path, title_font_size))
	stwidth, stheight = draw.textsize(top_comment, font = ImageFont.truetype(font_path, subtitle_font_size))

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

def draw_stroke(draw, title_pos_x, title_pos_y, subtitle_pos_x, subtitle_pos_y, title, subtitle):
	# thin border
	draw.text((title_pos_x - 1, title_pos_y - 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((title_pos_x + 1, title_pos_y - 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((title_pos_x - 1, title_pos_y - 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((title_pos_x + 1, title_pos_y + 1), title, font = ImageFont.truetype(font_path, title_font_size), fill='black')
	draw.text((subtitle_pos_x - 1, subtitle_pos_y - 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')
	draw.text((subtitle_pos_x + 1, subtitle_pos_y - 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')
	draw.text((subtitle_pos_x - 1, subtitle_pos_y - 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')
	draw.text((subtitle_pos_x + 1, subtitle_pos_y + 1), subtitle, font = ImageFont.truetype(font_path, subtitle_font_size), fill='black')

def generate_image()
	post = fetch_gonewild_post()
	original_image, original_title = fetch_image()
	image = Image.open(original_image)

	title = post.title
	top_comment = post.comments[0].body

	image = draw_text(image, title, top_comment)
	
	f_name = '%s.jpg' % (os.path.splitext(image.filename)[0].strip(string.punctuation + ' '))
	image.save(f_name)

	uploaded_image = imgur.upload_image(path = os.path.realpath(f_name), title = f_name)
	print ('uploaded image at: %s' % uploaded_image.link)
	photo = open(os.path.realpath(f_name), 'rb')
	twitter.update_status_with_media(media = photo, status = ('%s [larger: %s]' % (original_title[:min(string.find(original_title, '['),100 - len(uploaded_image.link) - 10)], uploaded_image.link)))

for i in range(int(sys.argv[1])): generate_image()
