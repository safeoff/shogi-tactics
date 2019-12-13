import sys
sys.path.append('../Ayane/source/shogi')
import Ayane


# 棋譜から次の一手問題を生成
def create_tactics(moves):
	# エンジン起動
	usi = Ayane.UsiEngine()
	# usi.debug_print = True
	usi.connect("../YaneuraOu478/YaneuraOu-by-gcc")

	# 検討開始
	for i, _ in enumerate(moves):
		usi.usi_position("startpos moves " + " ".join(moves[0:i]))
		usi.usi_go_and_wait_bestmove("byoyomi 100")
		print("=== UsiThinkResult ===\n" + usi.think_result.to_string())

		# 思考結果を記録

	# エンジン切断
	usi.disconnect()

	# 悪手を指した局面を抽出
	# 最善手と悪手を比較
	# 次の一手問題を生成