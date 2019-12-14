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
	sfen = "?sfen=" + urllib.parse.quote(tactics["sfen"])
	lm = "&lm=" + calc_move_num(premove)
	board = "<img src=\'" + api + sfen + lm + "\'>"

	return board


# 計算結果をAnki形式に変換
# front: 局面、戦法名、一つ前の手、最善手の評価値、本譜の評価値
# back: 最善手の読み筋、本譜の読み筋
def convert_tactics(tactics):
	board = convert_board(tactics["sfen"], tactics["premove"])
	battle_type = tactics["battle_type"] + "　"
	premove = tactics["premove"] + "まで　"
	bestmove_eval = "最善手の評価値：　" + str(tactics["bestmove_eval"]) + "　"
	move_eval = "本譜の評価値：　" + str(tactics["move_eval"]) + "　"

	front = board + battle_type + premove + bestmove_eval + move_eval

	bestmove = "最善手+CPUの読み筋：　" + tactics["bestmove"] + "　"
	move = "本譜+CPUの読み筋：　" + tactics["move"] + "　"

	back = bestmove + move
	return front, back


# プレイヤーが先手かどうか
def is_first(kifuurl, id):
	match = re.search(r"games/(.+)", kifuurl).group(1)
	first_player = match[0:len(id)]

	# 先手: id0000, 後手: id00 みたいなケースに対応
	# -の位置で判別できる
	if first_player == id:
		return match[len(id)] == "-"
	return False


# ウォーズの棋譜を取得する（10分切れ）
if __name__ == "__main__":
	id = "safeoff"
	gt = ""
	kifus = kifuDownloader.download_warskifu(id, gt)

	# ウォーズの棋譜を送って計算させる
	tacticss = []
	for kifu in kifus:
		item = Csa2moves.csa2moves(kifu["kifu"])
		moves = item[0]
		sfens = item[1]

		calculation_result = Tactics.create_tactics(kifu["battle_type"], moves, sfens)
		tacticss[len(tacticss):len(tacticss)] = calculation_result

	# Ankiにカードを登録
	battle_types = []
	for tactics in tacticss:
		front, back = convert_tactics(tactics)
		deck = "学習::将棋::実践次の一手::" + tactics["battle_type"]

		anki_result = AddAnki.addAnki(front, back, deck)

		if "1" in str(anki_result):
			battle_types.append(tactics["battle_type"])

	# カード生成数を戦法ごとに出力
	c = collections.Counter(battle_types)
	for k, v in c.items():
		msg = "created " + str(v) + " " + k + " tactics.\n"
		print(msg)