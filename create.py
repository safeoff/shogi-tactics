"""Create shogi tactics from online match.
& Add it to ankiweb.

Usage:
  create.py (--wars <wars_id> --rule <rule>) [--file --limit <limit_num>]
  create.py (-h | --help)
  create.py --version

Options:
  -h --help     Show this screen.
  --wars        ID of shogi wars you want to calculate.
  --rule        game rule[10m | 3m | 10s]
  --limit       Maximum number of game records to download [default:no limit].
  --file        Output to a file. It doesn't add to ankiweb.
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
# front: 局面、一つ前の手、最善手の評価値、次善手の評価値、本譜の評価値
# back: 最善手の読み筋、次善手の読み筋、本譜の読み筋
def convert_tactics_anki(tactics):
	board = convert_board(tactics["sfen"], tactics["premove"])
	premove = tactics["premove"] + "まで　"
	bestmove_eval = "最善手：" + str(tactics["bestmove_eval"]) + "<br>"
	bettermove_eval = "次善手：" + str(tactics["bettermove_eval"]) + "　"
	move_eval = "指した手：" + str(tactics["move_eval"]) + "　"

	front = board + premove + bestmove_eval + bettermove_eval + move_eval

	bestmove = "最善手：" + tactics["bestmove"]
	bettermove = "<br>次善手：" + tactics["bettermove"]
	move = "<br>指した手：" + tactics["move"]

	back = bestmove + bettermove + move
	return front, back


# 計算結果をHTML形式に変換
# front: 戦法、局面、一つ前の手、最善手の評価値、次善手の評価値、本譜の評価値
# back: 最善手の読み筋、次善手の読み筋、本譜の読み筋
def convert_tactics_text(tactics, qnum):
	battle_type = "【問題" + qnum + "】" + tactics["battle_type"] + "<br>"
	board = convert_board(tactics["sfen"], tactics["premove"]) + "<br>"
	premove = tactics["premove"] + "まで<br>"
	bestmove_eval = "最善手の評価値：　" + str(tactics["bestmove_eval"]) + "<br>"
	bettermove_eval = "次善手の評価値：　" + str(tactics["bettermove_eval"]) + "<br>"
	move_eval = "指した手の評価値：　" + str(tactics["move_eval"]) + "<br>"

	front = battle_type + board + premove + bestmove_eval + bettermove_eval + move_eval

	button ="<input type=\"button\" value=\"解答\" onclick=\"document.getElementById(\'" + qnum + "\').style.visibility = \'visible\';\">"
	div = "<div id=\"" + qnum + "\" style=\"visibility:hidden\">"
	bestmove = "最善手+CPUの読み筋：　" + tactics["bestmove"] + "<br>"
	bettermove = "次善手+CPUの読み筋：　" + tactics["bettermove"] + "<br>"
	move = "指した手+CPUの読み筋：　" + tactics["move"] + "<br>"

	back = button + div + bestmove + bettermove + move + "</div><hr>\n"

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


# 棋譜から次の一手問題を自動生成
def create(id, gt, is_fileonly, limit_num):
	# ウォーズの棋譜を取得する
	kifus = kifuDownloader.download_warskifu(id, gt, limit_num)
	msg = "downloaded " + str(len(kifus)) + " game records."
	print(msg)

	# ウォーズの棋譜を送って計算させる
	tacticss = []
	for kifu in kifus:
		usi, times = Csa2moves.csa2moves(kifu["kifu"])
		moves = usi[0]
		sfens = usi[1]

		calculation_result = Tactics.create_tactics(kifu["battle_type"], moves, sfens, times, is_first(kifu["kifuurl"], id))
		tacticss[len(tacticss):len(tacticss)] = calculation_result

	# カードを登録
	# ファイルなら下準備
	if is_fileonly and len(tacticss)>0:
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
			deck = "学習::C::将棋::実践次の一手::" + id + "::" + tactics["battle_type"]
			anki_result = AddAnki.addAnki(front, back, deck)
			is_success = "1" in str(anki_result)

		if is_success:
			battle_types.append(tactics["battle_type"])

	# カード生成数を戦法ごとに出力
	c = collections.Counter(battle_types)
	for k, v in c.items():
		msg = "created " + str(v) + " " + k + " tactics."
		print(msg)
	if not battle_types:
		print("no tactics.")


if __name__ == "__main__":
	args = docopt(__doc__, version='0.1')
	limit = None
	if args["<limit_num>"] is not None:
		limit = int(args["<limit_num>"])
	if not args["<rule>"] in ["10m", "3m", "10s"]:
		print("rule: wrong value.")
		exit()
	else:
		gtmap = {"10m": "", "3m": "sb", "10s": "s1"}
		gt = gtmap[args["<rule>"]]

	if args["<wars_id>"] is not None:
		create(args["<wars_id>"], gt, args["--file"], limit)
