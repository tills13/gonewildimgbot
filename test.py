import praw

reddit = praw.Reddit("asdklj")

for post in reddit.get_subreddit('gonewild').get_top_from_week(limit = 1):
	print ('from: redd.it/%s, uploaded image at: %s' % (post.name.split("_")[1], "sdlkas"))