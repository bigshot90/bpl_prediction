#import collections, itertools

from nltk.metrics import BigramAssocMeasures
import pymongo

client = pymongo.MongoClient()
db1 = client["team_results"]
db2 = client["n-grams"]
 
team_names = ['Man United', 'Man City','Arsenal','Chelsea','Liverpool','West Ham','Leicester','Everton','Swansea','Crystal Palace','Tottenham','West Brom','Southampton','Aston Villa','Stoke','Newcastle','Sunderland']
team_names = [team_name.lower().replace(" ", "_") for team_name in team_names]
n = 100
#pos_score = BigramAssocMeasures.chi_sq(n_ii, (n_ix, n_xi), n_xx)
# n_ii counts (w1, w2)
# n_ix counts (w1, *)
# n_xi counts (*, w2)
# n_xx counts (*, *)
def get_chi_sqr_values(word, clas, n_xx, col_win, col_lose, col_draw):
	n_ii = collection.find_one({"words": word})["count"]
	(n_ix, n_xi) = get_ns(word, clas, col_win, col_lose, col_draw)
	return BigramAssocMeasures.chi_sq(n_ii, (n_ix, n_xi), n_xx)


def get_ns(word, clas, col_win, col_lose, col_draw):
	n_ix = 0
	try:
		n_ix += col_win.find_one({"words": word})["count"]#sum([elem["count"] for elem in col_win.find_one({"words": word})])
	except:
		pass
	try:
		n_ix += col_draw.find_one({"words": word})["count"]
	except:
		pass
	try:
		n_ix += col_lose.find_one({"words": word})["count"]
	except:
		pass

	n_xi = 0
	if clas == 1:
		try:
			n_xi = sum([elem["count"] for elem in col_win.find()])
		except:
			pass
	elif clas == 0:
		try:
			n_xi = sum([elem["count"] for elem in col_draw.find()])
		except:
			pass
	elif clas == -1:
		try:
			n_xi = sum([elem["count"] for elem in col_lose.find()])
		except:
			pass
	else:
		print("class not available")

	return (n_ix, n_xi)

def get_n_xx(col_win, col_lose, col_draw):
	n_xx = 0
	try:
		n_xx += sum([elem["count"] for elem in col_win.find()])
	except:
		pass
	try:
		n_xx += sum([elem["count"] for elem in col_draw.find()])
	except:
		pass
	try:
		n_xx += sum([elem["count"] for elem in col_lose.find()])
	except:
		pass
	return n_xx

def get_word_scores(words, col_win, col_lose, col_draw):
	n_xx = get_n_xx(col_win, col_lose, col_draw)
	word_scores = {}
	for word in words:
		win_socre = 0
		lose_score = 0
		draw_score = 0
		if col_win.find_one({"words": word}):
			win_score = get_chi_sqr_values(word, 1, n_xx, col_win, col_lose, col_draw)
		if col_lose.find_one({"words": word}):
			lose_score = get_chi_sqr_values(word, -1, n_xx, col_win, col_lose, col_draw)
		if col_draw.find_one({"words": word}):
			draw_score = get_chi_sqr_values(word, 0, n_xx, col_win, col_lose, col_draw)
		word_scores[word] = win_score + lose_score + draw_score
	return word_scores

def get_best_words(words, n, col_win, col_lose, col_draw):
	word_scores = get_word_scores(words, col_win, col_lose, col_draw)
	best = sorted(word_scores.items(), key=operator.itemgetter(1), reverse=True)[:n]
	return set([w for w, s in best])

def read_from_file(file_name):
	f = open(file_name, "r")
	words = f.readlines()
	f.close()	
	return [word.strip() for word in words] 

def write_to_file(words, file_name):
	words = list(words)
	f = open(file_name, "w+")
	for word in words:

		try:
			f.write(str(word))
			f.write("\n") 
		except UnicodeEncodeError:
			print("couldn't write word, ecoding error")
	f.close()

def main(team_name):
	col_win = db2[team_name+"_win"]
	col_lose = db2[team_name+"_lose"]
	col_draw = db2[team_name+"_draw"]

	words = read_from_file("./popular_bigram/" +team_name+"_clean_1500.txt")
	words = [word.replace("'", "").split(",") for word in words]
	bestwords = get_best_words(words)

	write_to_file(words, "./best/" + team_name + "_best_bigram_" + str(n) + ".txt")


def get_ns_uni(word, clas, col_win, col_lose, col_draw):
	n_ix = 0
	try:
		n_ix += sum([1 for elem in col_win.find({"words": word})])
	except:
		pass
	try:
		n_ix += sum([1 for elem in col_draw.find({"words": word})])
	except:
		pass
	try:
		n_ix += sum([1 for elem in col_lose.find({"words": word})])
	except:
		pass

	n_xi = 0
	if clas == 1:
		try:
			n_xi = sum([len(elem["words"]) for elem in col_win.find()])
		except:
			pass
	elif clas == 0:
		try:
			n_xi = sum([len(elem["words"]) for elem in col_draw.find()])
		except:
			pass
	elif clas == -1:
		try:
			n_xi = sum([len(elem["words"]) for elem in col_lose.find()])
		except:
			pass
	else:
		print("class not available")

	return (n_ix, n_xi)

def get_chi_sqr_values_uni(word, clas, n_xx, col_win, col_lose, col_draw):
	n_ii = collection.find({"words": word}).count()
	(n_ix, n_xi) = get_ns_uni(word, clas, col_win, col_lose, col_draw)
	return BigramAssocMeasures.chi_sq(n_ii, (n_ix, n_xi), n_xx)

def get_n_xx_uni(col_win, col_lose, col_draw):
	n_xx = 0
	try:
		n_xx += sum([len(elem["words"]) for elem in col_win.find()])
	except:
		pass
	try:
		n_xx += sum([len(elem["words"]) for elem in col_draw.find()])
	except:
		pass
	try:
		n_xx += sum([len(elem["words"]) for elem in col_lose.find()])
	except:
		pass
	return n_xx

def get_word_scores_uni(words, col_win, col_lose, col_draw):
	n_xx = get_n_xx_uni(col_win, col_lose, col_draw)
	word_scores = {}
	for word in words:
		win_socre = 0
		lose_score = 0
		draw_score = 0
		if col_win.find_one({"words": word}):
			win_score = get_chi_sqr_values_uni(word, 1, n_xx, col_win, col_lose, col_draw)
		if col_lose.find_one({"words": word}):
			lose_score = get_chi_sqr_values_uni(word, -1, n_xx, col_win, col_lose, col_draw)
		if col_draw.find_one({"words": word}):
			draw_score = get_chi_sqr_values_uni(word, 0, n_xx, col_win, col_lose, col_draw)
		word_scores[word] = win_score + lose_score + draw_score
	return word_scores

def get_best_words_uni(words, n, col_win, col_lose, col_draw):
	word_scores = get_word_scores_uni(words, col_win, col_lose, col_draw)
	best = sorted(word_scores.items(), key=operator.itemgetter(1), reverse=True)[:n]
	return set([w for w, s in best])


def unigram_main(team_name):
	col_win = db1[team_name+"_win"]
	col_lose = db1[team_name+"_lose"]
	col_draw = db1[team_name+"_draw"]

	words = read_from_file("./popular_clean/" +team_name+"_clean_1500.txt")
	bestwords = get_best_words_uni(words)

	write_to_file(words, "./best/" + team_name + "_best_unigram_" + str(n) + ".txt")


if __name__=="__main__":
	for team_name in team_names:
		main(team_name)
