import praw, random

reddit = praw.Reddit("idgaf")
post_limit = 500

def fetch_image():
	print('fetching image')
	post = fetch_earthporn_post() if random.random() > 0.5 else fetch_spaceporn_post()

	print post


def fetch_earthporn_post():
	posts = reddit.get_subreddit('earthporn').get_top_from_month(limit = post_limit)
	return random.choice([post for post in posts if 'imgur' in post.url])

def fetch_spaceporn_post():
	posts = reddit.get_subreddit('spaceporn').get_top_from_month(limit = post_limit)
	return random.choice([post for post in posts if 'imgur' in post.url])

fetch_image()
