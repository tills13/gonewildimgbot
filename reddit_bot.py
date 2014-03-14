import praw, datetime, random, pyimgur, re, time, sys, os, exceptions, string




POST_LIMIT = 500
MIN_SCORE = 500
MAX_SCORE = 4000
MIN_AGE = 365 # days
time_slept = 0

avoid_subreddits = ['suicidewatch', 'gaymers', 'olympics', 'golf', 'cringepics', 'gonewild', 'steamdeals', 'cosplay', 'nba']
avoid_phrases = ['today', 'married', 'sister', 'sisters', 'wife', 'wifes', 'husband', 'husbands', 
				 'dad', 'dads', 'uncle', 'uncles', 'brother', 'brothers', 'halloween', 
				 'christmas', 'mom', 'moms']
posted = []

reddit = praw.Reddit("idgaf")
imgur = pyimgur.Imgur(IMGUR_CLIENT_ID)

def login():
	global imgur

	print ('logging into reddit as'),
	account = random.choice(accounts)
	print (account[0], '...',
	reddit.login(account[0], account[1])
	print 'done'

	print ('hooking up imgur... '),
	imgur = pyimgur.Imgur(IMGUR_CLIENT_ID)
	print ('done')

def run():
	subreddit = reddit.get_random_subreddit()
		
	print ('trying /r/%s ...' % subreddit.display_name),
	if subreddit.subscribers < 25000: 
		print '\rskipping /r/%s, not enough subscribers ... ' % subreddit.display_name # get a valid subreddit...
		run()
	elif subreddit.display_name.lower() in avoid_subreddits: 
		print '\ravoiding /r/%s ...' % subreddit.display_name
		run()
	else:
		print
		post = random.choice(find_post_candidates(subreddit.get_top_from_all(limit = POST_LIMIT)))

		print 'suitable post found: redd.it/%s...' % post.name.split('_')[1]
		imgur_url = get_imgur_url(post.url)
		image = imgur.get_image(imgur_url).download()
		uploaded_image = imgur.upload_image(image)
		os.remove(image)

		submitted_post = subreddit.submit(title = post.title, text = None, url = uploaded_image.link)	
		posted.append(submitted_post.name)

		print("submitted \'%s\' @ redd.it/%s in /r/%s from redd.it/%s" % (post.title, submitted_post.name.split('_')[1], subreddit.display_name, post.name.split('_')[1]))

def find_post_candidates(posts):
	results = []
	for post in posts:
		if not post.is_self and post.score > MIN_SCORE and post.score < MAX_SCORE and post.name and days_between(posted = datetime.date.fromtimestamp(post.created_utc)) > MIN_AGE and 'imgur' in post.url: 
			if not title_contains_avoided_words(post.title): results.append(post)

	return results

def title_contains_avoided_words(post_title):
	return len(list(set([word.lower().replace("\'s", "").strip(string.punctuation) for word in post_title.split(' ')]).intersection(set(avoid_phrases)))) != 0

def days_between(posted, today=datetime.date.today()):
	return (today - posted).days

def get_imgur_url(full_url):
	groups = re.match(r'https?://(?:(?:i|www)\.)?imgur.com/(?:a/)?([^\.]*)(\?.*)?', full_url)
	return groups.group(1)

def sleep(minutes):
	global time_slept

	if ((time_slept / 20) >= 1): 
		print_summary()
		time_slept = 0

	length = 120
	for i in range(length + 1):
		sys.stdout.write("\rwating... [{0}{1}] {2}s/{3}s".format("=" * i, " " * (length - i), int(i * (60 * (float(minutes) / length))), int(minutes * 60)))
		sys.stdout.flush()
		time.sleep(60 * (float(minutes) / length))
	
	time_slept += minutes	
	print

def print_summary():
	print '\nsummary of %d posts in this session: ' % len(posted)
	for mpost in posted:
		post = reddit.get_submission(submission_id = mpost.split('_')[1])
		
		print 'post %s in /r/%s (%d up|%d down), %d comments' % (mpost, post.subreddit.display_name, post.ups, post.downs, post.num_comments)

def main():
	while True:
		try:
			run()
			sleep(5)
		except praw.errors.RateLimitExceeded as rate_e:
			print 'RateLimitExceeded: sleeping for %d minutes' % (int(rate_e.sleep_time / 60))
			sleep(int(rate_e.sleep_time / 60))
		except praw.errors.APIException as api_e:
			sleep_time = 5
			if api_e.error_type == 'QUOTA_FILLED': 
				print 'API limit reached, switching users...'
				login()
			else: 
				if api_e.error_type == 'NO_LINKS': sleep_time = 2
				print 'APIException (%s): sleeping for %d minutes' % (api_e, sleep_time)
				sleep(sleep_time)
		except praw.errors.ClientException as client_e:
			print 'ClientException (%s): sleeping for %d minutes' % (rate_e, 1)
			sleep(1)
		except exceptions.IndexError as index_e:
			print 'IndexError: no suitable post found in subreddit'
		except exceptions.KeyboardInterrupt:
			print_summary()
			break
		except Exception as http_e:
			print http_e

login()
main()
