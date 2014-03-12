import praw, pyimgur, re, os, random, sys, string

from twython import Twython
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from config import config

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
	li = []
	posts = reddit.get_subreddit('gonewild').get_top_from_month(limit = post_limit)
	for post in posts: li.append(post)
	return random.choice(li)

def fetch_earthporn_image():
	print('fetching earthporn image')
	posts = reddit.get_subreddit('earthporn').get_top_from_month(limit = post_limit)
	post = random.choice([post for post in posts if 'imgur' in post.url]) 
	imgur_url = get_imgur_url(post.url)
	return imgur.get_image(imgur_url).download()

def get_imgur_url(full_url):
	return re.match(r'https?://(?:(?:i|www)\.)?imgur.com/(?:a/)?([^\.]*)(\?.*)?', full_url).group(1)

def upload_image(image):
	uploaded_image = imgur.upload_image(image)

def draw_text(image, title, top_comment):
	global title_font_size, subtitle_font_size, padding_vert2
	draw = ImageDraw.Draw(image)
	image_width, image_height = image.size

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

	twidth, theight = draw.textsize(title, font = ImageFont.truetype(font_path, title_font_size))
	stwidth, stheight = draw.textsize(top_comment, font = ImageFont.truetype(font_path, subtitle_font_size))

	print (twidth, theight, stwidth, stheight)

	vert = random.random() # top or bottom
	horiz = random.random() # left of right

	if vert > 0.5: # top
		title_pos_y = padding_vert
		subtitle_pos_y = title_pos_y + theight + padding_vert2
	else: # bottom
		subtitle_pos_y = image_height - padding_vert - stheight
		title_pos_y = subtitle_pos_y - padding_vert2 - theight

	if horiz > 0.5: # left
		title_pos_x, subtitle_pos_x = padding_horiz, padding_horiz
	else: # right
		title_pos_x = image_width - padding_horiz - twidth
		subtitle_pos_x = image_width - padding_horiz - stwidth

	draw_stroke(draw, title_pos_x, title_pos_y, subtitle_pos_x, subtitle_pos_y, title, top_comment)
	draw.text((title_pos_x, title_pos_y), title, font = ImageFont.truetype(font_path, title_font_size), fill = 'white')
	draw.text((subtitle_pos_x, subtitle_pos_y), top_comment, font = ImageFont.truetype(font_path, subtitle_font_size), fill = 'white')
	return image

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

def generate_image():
	post = fetch_gonewild_post()
	original_image = fetch_earthporn_image()
	image = Image.open(original_image)

	title = post.title
	top_comment = post.comments[0].body

	image = draw_text(image, title, top_comment)
	
	f_name = '%s.jpg' % (os.path.splitext(image.filename)[0].strip(string.punctuation + ' '))
	image.save(f_name)

	uploaded_image = imgur.upload_image(path = os.path.realpath(f_name), title = f_name)
	twitter.update_status(status = ('%s: %s' % (f_name, uploaded_image.link)))
	os.remove(original_image)

for i in range(int(sys.argv[1])): generate_image()
