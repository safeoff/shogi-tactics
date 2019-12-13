import sys
sys.path.append('../Ayane/source/shogi')
import Ayane
sys.path.append('../csa2moves')
import Csa2moves

if __name__ == "__main__":
	# エンジン起動
	usi = Ayane.UsiEngine()
	# usi.debug_print = True
	usi.connect("../YaneuraOu478/YaneuraOu-by-gcc")

	# 棋譜読み込み
	wars = '        receiveMove("+7968GI,L600	-3142GI,L599	+5756FU,L599	-5354FU,L598	+6857GI,L599	-4253GI,L597	+8879KA,L598	-8384FU,L595	+2726FU,L598	-8485FU,L594	+6978KI,L596	-5364GI,L593	+5766GI,L593	-2231KA,L591	+7957KA,L587	-4132KI,L580	+2625FU,L584	-7162GI,L570	+2524FU,L555	-2324FU,L569	+2824HI,L553	-0023FU,L567	+2425HI,L548	-6253GI,L565	+3736FU,L542	-5344GI,L558	+3948GI,L533	-3334FU,L540	+2937KE,L504	-2133KE,L534	+2526HI,L503	-8252HI,L528	+5969OU,L494	-5455FU,L521	+5655FU,L491	-3345KE,L484	+3745KE,L479	-4445GI,L483	+6979OU,L422	-6455GI,L432	+6655GI,L410	-5255HI,L427	+5766KA,L400	-5552HI,L418	+6611UM,L397	-3122KA,L404	+1121UM,L383	-0058GI,L383	+2132UM,L366	-5849NG,L373	+0053FU,L331	SENTE_WIN_TORYO");'
	kif = Csa2moves.csa2moves(wars)

	# 検討開始
	for i, _ in enumerate(kif):
		usi.usi_position("startpos moves " + " ".join(kif[0:i]))
		usi.usi_go_and_wait_bestmove("byoyomi 500")
		print("=== UsiThinkResult ===\n" + usi.think_result.to_string())

	# エンジン切断
	usi.disconnect()
