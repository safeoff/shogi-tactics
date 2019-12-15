"""create shogi tactics from online match.
& add it to ankiweb.

Usage:
  create.py (-w | --wars) <wars_id>
  create.py (-w | --wars) <wars_id> --file
  create.py (-h | --help)
  create.py --version

Options:
  -h --help     Show this screen.
  -w --wars     ID of shogi wars you want to calculate.
  --file        output to a file. it doesn't add to ankiweb.
  --version     Show version.

"""
from docopt import docopt
import datetime
import os
import sys
import collections
import urllib
import re
sys.path.append('../kifu-downloader')
import kifuDownloader
sys.path.append('../csa2moves')
import Csa2moves
sys.path.append('../shogi_anki')
import AddAnki
import Tactics


# 一つ前の手を強調表示するための数字を得る　sfenreader用
def calc_move_num(move):
	nummap = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
	chars = list(move)
	num = chars[1] + str(nummap[chars[2]])
	return num


# sfen文字列を、局面のpng画像URLに変換
def convert_board(sfen, premove):
	api = "http://sfenreader.appspot.com/sfen"
	sfen = "?sfen=" + urllib.parse.quote(sfen)
	lm = "&lm=" + calc_move_num(premove)
	board = "<img src=\'" + api + sfen + lm + "\'>"

	return board


# 計算結果をAnki形式に変換
# front: 局面、一つ前の手、最善手の評価値、本譜の評価値
# back: 最善手の読み筋、本譜の読み筋
def convert_tactics_anki(tactics):
	board = convert_board(tactics["sfen"], tactics["premove"])
	premove = tactics["premove"] + "まで　"
	bestmove_eval = "最善手の評価値：　" + str(tactics["bestmove_eval"]) + "　"
	move_eval = "指した手の評価値：　" + str(tactics["move_eval"]) + "　"

	front = board + premove + bestmove_eval + move_eval

	bestmove = "最善手+CPUの読み筋：　" + tactics["bestmove"] + "　"
	move = "指した手+CPUの読み筋：　" + tactics["move"] + "　"

	back = bestmove + move
	return front, back


# 計算結果をHTML形式に変換
# front: 戦型、局面、一つ前の手、最善手の評価値、本譜の評価値
# back: 最善手の読み筋、本譜の読み筋
def convert_tactics_text(tactics, qnum):
	battle_type = "【問題" + qnum + "】" + tactics["battle_type"] + "<br>"
	board = convert_board(tactics["sfen"], tactics["premove"]) + "<br>"
	premove = tactics["premove"] + "まで<br>"
	bestmove_eval = "最善手の評価値：　" + str(tactics["bestmove_eval"]) + "<br>"
	move_eval = "指した手の評価値：　" + str(tactics["move_eval"]) + "<br>"

	front = battle_type + board + premove + bestmove_eval + move_eval

	button ="<input type=\"button\" value=\"解答\" onclick=\"document.getElementById(\'" + qnum + "\').style.visibility = \'visible\';\">"
	div = "<div id=\"" + qnum + "\" style=\"visibility:hidden\">"
	bestmove = "最善手+CPUの読み筋：　" + tactics["bestmove"] + "<br>"
	move = "指した手+CPUの読み筋：　" + tactics["move"] + "<br>"

	back = button + div + bestmove + move + "</div><hr>\n"

	return front + back


# プレイヤーが先手かどうか
def is_first(kifuurl, id):
	match = re.search(r"games/(.+)", kifuurl).group(1)
	first_player = match[0:len(id)]

	# 先手: id0000, 後手: id00 みたいなケースに対応
	# -の位置で判別できる
	if first_player == id:
		return match[len(id)] == "-"
	return False


# 棋譜から次の一手問題を自動生成してAnkiに登録
def create(id, gt, is_fileonly):
	# ウォーズの棋譜を取得する
	kifus = kifuDownloader.download_warskifu(id, gt)

	# ウォーズの棋譜を送って計算させる
	tacticss = []
	for kifu in kifus:
		item = Csa2moves.csa2moves(kifu["kifu"])
		moves = item[0]
		sfens = item[1]

		calculation_result = Tactics.create_tactics(kifu["battle_type"], moves, sfens, is_first(kifu["kifuurl"], id))
		tacticss[len(tacticss):len(tacticss)] = calculation_result

	# カードを登録
	# ファイルなら下準備
	if is_fileonly:
		dirname = "tactics/" + id
		os.makedirs(dirname, exist_ok=True)
		filename = datetime.datetime.now().strftime("%Y%m%d%H%M")
		filename += tacticss[0]["battle_type"] + "ほか" + str(len(tacticss)) + "問.html"

	battle_types = []
	for tactics in tacticss:
		is_success = False
		# ファイル
		if is_fileonly:
			with open(dirname + "/" + filename, "a") as f:
				msg = convert_tactics_text(tactics, str(len(battle_types)+1))
				f.write(msg)
				is_success = True
		# Anki
		else:
			front, back = convert_tactics_anki(tactics)
			deck = "学習::将棋::実践次の一手::" + id + "::" + tactics["battle_type"]
			anki_result = AddAnki.addAnki(front, back, deck)
			is_success = "1" in str(anki_result)

		if is_success:
			battle_types.append(tactics["battle_type"])

	# カード生成数を戦法ごとに出力
	c = collections.Counter(battle_types)
	for k, v in c.items():
		msg = "created " + str(v) + " " + k + " tactics.\n"
		print(msg)


if __name__ == "__main__":
	args = docopt(__doc__, version='0.1')
	if args["--wars"]:
		create(args["<wars_id>"], "", args["--file"])