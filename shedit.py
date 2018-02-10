
import praw
import sys

def main():

	print("starting reddit...")
	reddit = praw.Reddit('bot1')
	print("opening shedit...")
	shedit = reddit.subreddit("shedit")
	

	# extract subs from list
	subs = []
	sub_list = open("subreddits.txt", "r")
	for line in sub_list:
		if len(line) >= 1:
			subs.append(reddit.subreddit(line.strip()))
	sub_list.close()

	if len(sys.argv) == 1:
		confirm = input("Are you sure you want to pull from all subs? (Y/n) ")
		if(confirm.lower() == "y" or confirm.lower() == "yes"):
			# pull all subs from file
			# pull from each sub in list
			for sub in subs:
				print("Pulling from " + (str)(sub) + "...")
				pull_sub(sub, shedit)

	elif len(sys.argv) == 2 and sys.argv[1] == "-c":
		confirm = input("Are you sure you want to remove all the posts from r/shedit? ")
		if(confirm.lower() == "y" or confirm.lower() == "yes"):
			#clear out sub
			for submission in shedit.submissions():
				submission.delete()
	elif len(sys.argv) == 2 and sys.argv[1] == "-cl":
		confirm = input("Are you sure you want to clear out the log file? ")
		if(confirm.lower() == "y" or confirm.lower() == "yes"):
			#clear out log file
			log = open("log.txt", "w")
			log.close

	elif (len(sys.argv) == 3 or len(sys.argv) == 4) and sys.argv[1] == "-s":
		sub = sys.argv[2]
		if(len(sys.argv) == 3):
			print("pulling 3 posts from " + sub + "...")
			pull_sub(reddit.subreddit(sub), shedit)
		elif(sys.argv[3].isdigit()):
			postnum = (int)(sys.argv[3])
			print("Pulling " + (str)(postnum) + " posts from " + sub + "...")
			pull_sub(reddit.subreddit(sub), shedit, postnum)
		else:
			print("Error: " + sys.argv[3] + " is not a number.")
	
	else:
		print("shedit.py -s [subreddit]")

# flair a post on r/shedit
def flair(submission, flair):
	flairchoices = submission.flair.choices()
	flairchoice = flairchoices[0]['flair_template_id']
	submission.flair.select(flairchoice, flair)


def pull_sub(subreddit, shedit, postnum=3):

	if subreddit == "askreddit":
		#pull top 3 posts from askreddit along with top 5 comments
		submissions = subreddit.hot(limit = postnum)
		for submission in submissions:
			if(log(submission.id_from_url(submission.shortlink))):
				# make post
				crosspost = shedit.submit(submission.title,"")
				flair(crosspost, "askreddit")
				comment_summary = "{:,}".format(submission.score) + " points | [link](" + submission.shortlink + ")\n\n"
				
				# copy top 5 top-level comments
				submission.comment_sort = 'top'
				comment_summary += "**Top 5 top-level comments:**\n\n"
				for i in range(0,5):
					comment = submission.comments[i]
					comment_summary += comment.body + "\n\n" + "{:,}".format(comment.score) + " points | [link](" + comment.permalink + ")"
					comment_summary += "\n***\n"
				crosspost.reply(comment_summary)
	
	elif is_image_sub(subreddit):
		pic_post(subreddit, shedit, postnum)

	else:
		print("Protocol for r/" + (str)(subreddit) + " does not yet exist")

# my best attempt at parsing images
def is_image(url):
	image_suffixes = [
		".jpg",
		".png"
	]
	image_prefixes = [
		"i.imgur",
		"i.redd.it",
		"imgur.com"
	]
	image_suffixes = "\t".join(image_suffixes)
	image_prefixes = "\t".join(image_prefixes)
	return url[len(url) - 4:] in image_suffixes or url.split("/")[2] in image_prefixes

# fix imgur links to play nicely with RES
def fix_link(url):
	if url.split("/")[2] == "imgur.com" and "gallery" not in url:
		url = url.replace("imgur.com","i.imgur.com")
		url = url + ".jpg"
	return url

# subs that host images almost entirely kinda all follow the same procedure
# skim the top 10 posts for image posts, crosspost the top 3
def pic_post(subreddit, shedit, postnum=3):
	submissions = subreddit.top("day", limit = 10)
	subnum = 0
	for submission in submissions:
		if(is_image(submission.url) and log(submission.id_from_url(submission.shortlink))):
			subnum += 1
			# make post
			url = fix_link(submission.url)
			crosspost = shedit.submit(submission.title, url=url)
			flair(crosspost, (str)(subreddit))
			crosspost.reply("{:,}".format(submission.score) + " points | [link](" + submission.shortlink + ")")
		if subnum == postnum:
			break

# check if a sub is mostly revolved around images
def is_image_sub(sub):
	image_subs = [
		"hmmm",
		"atbge",
		"programmerhumor",
		"2meirl4meirl",
		"assholedesign",
		"catsstandingup"
	]
	return (str)(sub) in image_subs

# check if post id is already posted, if not, add it
def log(url):
	log = open("log.txt", "r+")
	for line in log:
		if url == line.strip():
			log.close()
			return False
	log.write(url)
	log.write("\n")
	return True

main()

