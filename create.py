import sys
import collections
sys.path.append('../kifu-downloader')
import kifuDownloader
sys.path.append('../csa2moves')
import Csa2moves
sys.path.append('../shogi_anki')
import AddAnki
import Tactics


if __name__ == "__main__":
	# ウォーズの棋譜を取得する（10分切れ）
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
		front = tactics["board"] + tactics["battle_type"] + tactics["premove"]
		back = tactics["move"] + str(tactics["move_eval"]) + tactics["bestmove"] + str(tactics["bestmove_eval"])
		deck = "学習::将棋::実践次の一手"

		anki_result = AddAnki.addAnki(front, back, deck)

		if "1" in str(anki_result):
			battle_types.append(tactics["battle_type"])

	# カード生成数を戦法ごとに出力
	c = collections.Counter(battle_types)
	for k, v in c.items():
		msg = "created " + str(v) + " " + k + " tactics.\n"
		print(msg)