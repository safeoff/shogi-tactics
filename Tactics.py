import sys
sys.path.append('../Ayane/source/shogi')
import Ayane
import shogi


class Move:
	def __init__(self, *args):
		self.premove = args[0]
		self.move = args[1]
		self.bestmove = args[2]
		self.move_eval = args[3]
		self.bestmove_eval = args[4]
		self.sfen = args[5]


# 悪手かどうかの判定
def is_badmove(premove, move, bestmove):
	# 指した手による機会損失（最善手と指した手の評価値の差）を計算
	# 評価値は先後で符号が反転しているのでここで調整する
	premove_eval = -premove.pvs[0].eval
	move_eval = -move.pvs[0].eval
	bestmove_eval = bestmove.pvs[0].eval
	lost = abs(bestmove_eval - move_eval)

	# 疑問手含む問題ない手：採用しない
	if lost < 1000:
		return False
	# 形勢が極端に傾いている局面での・・・
	if abs(premove_eval) > 2500:
		# 悪手：採用しない
		if (lost > 1000) and (lost < 2000):
			return False
		# 詰み逃し：採用しない　（逆転は採用）
		if (abs(move_eval) > 9999) and (premove_eval*bestmove_eval >= 0):
			return False
		# 最善手も指した手も大差なし：採用しない
		if (abs(move_eval) > 2500) and (abs(bestmove_eval) > 2500):
			return False


	# 読み筋が少ない：採用しない
	splited_pv = bestmove.pvs[0].pv
	if len(splited_pv.split()) < 3:
		return False

	# 上記以外は悪手・頓死・詰み逃し・必死逃しと判定　採用
	return True


# 悪手を指した局面を抽出
def choice_badmove(think_results, sfens, is_first):
	badmoves = []
	for i, item in enumerate(think_results):
		# 2手目と最後の手ならcontinue
		if i==0 or i > len(think_results)-2:
			continue
		# 自分の手番のみ抽出する
		is_first_now = i%2 == 1
		if is_first_now != is_first:
			continue
		# 評価値がNoneならcontinue
		premove_eval = think_results[i-1][2].pvs[0].eval
		if premove_eval is None:
			continue
		# 指した手と最善手が同じならcontinue（読み筋の評価値だけ異なる場合がある）
		if item[1] == item[2].pvs[0].pv[0:4]:
			continue

		# 悪手なら保存
		if is_badmove(think_results[i-1][2], think_results[i+1][2], item[2]):
			move_eval = -think_results[i+1][2].pvs[0].eval
			bestmove_eval = item[2].pvs[0].eval
			# 先手番なら反転
			if i%2 == 0:
				move_eval = -move_eval
				bestmove_eval = -bestmove_eval
			bestmove = item[2].pvs[0].pv
			premove = item[0]
			move = item[1] + " " + think_results[i+1][2].pvs[0].pv
			badmove = Move(premove, move, bestmove, move_eval, bestmove_eval, sfens[i])
			badmoves.append(badmove)

	return badmoves


# 駒の種類を変換
def convert_piece(ay, ax, board):
	namemap = {
		"P": "歩", "p": "歩", "L": "香", "l": "香", "N": "桂", "n": "桂",
		 "S": "銀", "s": "銀", "G": "金", "g": "金", "B": "角", "b": "角",
		  "R": "飛", "r": "飛", "K": "玉", "k": "玉", "+P": "と", "+p": "と",
		   "+L": "成香", "+l": "成香", "+N": "成桂", "+n": "成桂", "+S": "成銀",
		    "+s": "成銀", "+B": "馬", "+b": "馬", "+R": "竜", "+r": "竜"
	}
	if ax == "*":
		return namemap[ay]
	y = int(ay)
	x = ord(ax)-96
	num = (x-1) * 9 + (9-y)
	name = board.piece_at(num)
	return namemap[str(name)]


# 駒の動きを日本語に変換
def convert_word(piece, move, board):
	word = ""
	# 先後を変換
	turn = "△" if board.move_number%2 == 1 else "▲"
	# 移動先を変換
	y = int(move[2])
	x = ord(move[3])-96
	xmap = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九"}
	xkanji = xmap[x]

	word = turn + str(y) + xkanji + piece
	# 打ちを変換
	if move[1] == "*":
		word += "打"
	# 成りを変換
	if len(move) == 5:
		word += "成"
	return word


# 読み筋を日本語に変換
def convert_moves(moves, sfen):
	board = shogi.Board(sfen)
	words = ""
	# 読み筋を9手までに制限
	saved_moves = moves.split()[:9]
	for move in saved_moves:
		piece = convert_piece(move[0], move[1], board)
		board.push_usi(move)
		words += convert_word(piece, move, board) + "　"

	return words


# 一つ前の動きを日本語に変換
def convert_premove(premove, sfen):
	board = shogi.Board(sfen)
	piece = convert_piece(premove[2], premove[3], board)

	# premoveが成り時の場合、名前を間違えてしまう
	# 竜成とかになるので、飛成とかに修正する
	if len(premove) == 5:
		piecemap = {"と": "歩", "成桂": "桂", "成香": "香", "成銀": "銀", "馬": "角", "竜": "飛"}
		piece = piecemap[piece]

	return convert_word(piece, premove, board)


# 棋譜から次の一手問題を生成
def create_tactics(battle_type, moves, sfens, is_first):
	# エンジン起動
	usi = Ayane.UsiEngine()
	# usi.debug_print = True
	usi.connect("../YaneuraOu/YaneuraOu-by-gcc")
#	usi.connect("../YaneuraOu479/YaneuraOu-arm64-x8a")

	# 検討開始
	think_results = []
	for i, _ in enumerate(moves):
		usi.usi_position("startpos moves " + " ".join(moves[0:i]))
		usi.usi_go_and_wait_bestmove("byoyomi 100")
		# 思考結果を記録　初手は記録しない
		if i > 0:
			think_results.append([moves[i-1], moves[i], usi.think_result])

	# エンジン切断
	usi.disconnect()

	# 悪手を指した局面を抽出
	sfens.pop(0)
	badmoves = choice_badmove(think_results, sfens, is_first)

	# 駒の動きを日本語に変換
	tactics = []
	for badmove in badmoves:
		map = {
			"sfen": badmove.sfen,
			"bestmove": convert_moves(badmove.bestmove, badmove.sfen),
			"bestmove_eval": badmove.bestmove_eval,
			"move": convert_moves(badmove.move, badmove.sfen),
			"move_eval": badmove.move_eval,
			"premove": convert_premove(badmove.premove, badmove.sfen),
			"battle_type": battle_type
		}
		tactics.append(map)

	return tactics