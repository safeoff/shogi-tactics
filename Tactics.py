import sys
sys.path.append('../Ayane/source/shogi')
import Ayane


class Move:
	def __init__(self, *args):
		self.i = args[0]
		self.premove = args[1]
		self.move = args[2]
		self.bestmove = args[3]
		self.move_eval = args[4]
		self.bestmove_eval = args[5]

# 悪手を指した局面を抽出
def choice_badmove(think_results):
	badmoves = []
	for i, item in enumerate(think_results):
		# 最初と最後の手ならcontinue
		if i==0 or i > len(think_results)-2:
			continue
		# 評価値がNoneならcontinue
		premove_eval = think_results[i-1][2].pvs[0].eval
		if premove_eval is None:
			continue

		# 指した手による機会損失（最善手と指した手の評価値の差）を計算
		# 評価値は先後で符号が反転しているのでここで調整する
		premove_eval = -premove_eval
		move_eval = -think_results[i+1][2].pvs[0].eval
		bestmove_eval = item[2].pvs[0].eval
		# 先手番なら反転
		if i%2 == 0:
			premove_eval = -premove_eval
			move_eval = -move_eval
			bestmove_eval = -bestmove_eval

		lost = abs(bestmove_eval - move_eval)
		# 疑問手含む問題ない手：採用しない
		if lost < 1000:
			continue
		# 形勢が極端に傾いている局面での・・・
		if abs(premove_eval > 2500):
			# 悪手：採用しない
			if (lost > 1000 and lost < 2000):
				continue
			# 詰み逃し：採用しない　（逆転は採用）
			if (abs(move_eval) > 9999 and premove_eval*bestmove_eval >= 0):
				continue
		# 読み筋が少ない：採用しない
		bestmove = item[2].pvs[0].pv
		if len(bestmove.split()) < 3:
			continue

		# 上記以外は悪手・頓死・詰み逃し・必死逃しと判定　採用
		premove = item[0]
		move = item[1] + " " + think_results[i+1][2].pvs[0].pv
		badmove = Move(i+2, premove, move, bestmove, move_eval, bestmove_eval)
		badmoves.append(badmove)

	return badmoves


# 駒の動きを日本語に変換
def convert_words(moves):

	r = ""
	for move in moves.split():
		# 先後を変換
		# 移動先を変換
		# move[2:3]
		# 駒の種類を変換
		# 打ちを変換
		# 成りを変換
		pass

	return r


# 棋譜から次の一手問題を生成
def create_tactics(battle_type, moves):
	# エンジン起動
	usi = Ayane.UsiEngine()
	# usi.debug_print = True
	usi.connect("../YaneuraOu/YaneuraOu-by-gcc")
#	usi.connect("../YaneuraOu479/YaneuraOu-arm64-x8a")

	# 検討開始
	think_results = []
	for i, _ in enumerate(moves):
		usi.usi_position("startpos moves " + " ".join(moves[0:i]))
		usi.usi_go_and_wait_bestmove("byoyomi 1000")
		# 思考結果を記録　初手は記録しない
		if i > 0:
			think_results.append([moves[i-1], moves[i], usi.think_result])
			# TODO この時点のSFENを記録しておけばいいのでは！

	# エンジン切断
	usi.disconnect()

	# 悪手を指した局面を抽出
	badmoves = choice_badmove(think_results)

	# 駒の動きを日本語に変換
	tactics = {}
	for badmove in badmoves:
		tactics.update([
			# TODO SFENの局面がまだ
			("board", "未実装"),
			("bestmove", convert_words(badmove.bestmove)),
			("bestmove_eval",badmove.bestmove_eval),
			("move", convert_words(badmove.move)),
			("move_eval", badmove.bestmove_eval),
			("premove", badmove.premove),
			("battle_type", battle_type)
		])

	print(tactics)
