import sys
sys.path.append('../csa2moves')
import Csa2moves
import unittest
import Tactics
import create


class Testcreate(unittest.TestCase):

	# 結合テスト
	def test_create(self):
		# arrange
		id = "safeoff"
		# act
		create.create(id, "", True)
		# assert


	# 先手番判定
	def test_is_first1(self):
		# arrange
		kifuurl = "https://kif-pona.heroz.jp/games/safeoff-sei1226-20191210_103425"
		id = "safeoff"
		expected_value = True
		# act
		result = create.is_first(kifuurl, id)
		# assert
		self.assertEqual(expected_value, result)


	# 先手番判定（似たid）
	def test_is_first2(self):
		# arrange
		kifuurl = "https://kif-pona.heroz.jp/games/id0000-id00-20191210_103425"
		id = "id"
		expected_value = False
		# act
		result = create.is_first(kifuurl, id)
		# assert
		self.assertEqual(expected_value, result)


class TestTactics(unittest.TestCase):

	# ウォーズの棋譜を送って計算させるテスト（後手番）
	def test_create_tactics(self):
		# arrange
		wars = '        receiveMove("+2726FU,L599	-3142GI,L600	+7776FU,L599	-5354FU,L599	+2625FU,L598	-4253GI,L598	+3948GI,L598	-4132KI,L596	+7968GI,L596	-2231KA,L595	+6877GI,L595	-5141OU,L594	+6978KI,L592	-8384FU,L594	+5969OU,L592	-8485FU,L593	+5756FU,L590	-7374FU,L592	+8879KA,L588	-9394FU,L590	+7946KA,L586	-6364FU,L586	+6979OU,L584	-7162GI,L585	+4958KI,L582	-6273GI,L584	+6766FU,L581	-5344GI,L582	+5867KI,L579	-4445GI,L577	+4657KA,L577	-9495FU,L572	+3736FU,L561	-4536GI,L553	+2524FU,L559	-2324FU,L551	+2824HI,L558	-0023FU,L549	+2426HI,L554	-3645GI,L541	+0035FU,L542	-5455FU,L535	+5655FU,L541	-0056FU,L518	+5768KA,L538	-8586FU,L492	+7786GI,L525	-8252HI,L464	+4746FU,L518	-5255HI,L462	+4645FU,L516	-5545HI,L456	+0046FU,L511	-4535HI,L447	+0036FU,L500	-3555HI,L442	+2937KE,L492	-0085FU,L414	+8677GI,L490	-5552HI,L401	+2629HI,L478	-7384GI,L381	+2959HI,L477	-7475FU,L373	+7675FU,L469	-6465FU,L372	+6756KI,L463	-6566FU,L359	+7766GI,L462	-8475GI,L355	+6675GI,L461	-3175KA,L352	+0066GI,L453	-0058FU,L316	+5958HI,L448	-7566KA,L314	+0053FU,L444	-5253HI,L304	+3745KE,L443	-5351HI,L273	+0052FU,L441	-5152HI,L270	+0053FU,L438	-6648UM,L262	+5352TO,L434	-6152KI,L260	+5848HI,L434	-4131OU,L202	+0053FU,L428	-5242KI,L201	+0071HI,L422	-3122OU,L194	+7151RY,L405	-0037GI,L191	+4847HI,L401	-3738GI,L172	+4777HI,L399	-0058GI,L152	+7771RY,L394	-1314FU,L144	+5121RY,L391	-2213OU,L143	+0035KA,L386	SENTE_WIN_TORYO");'
		usi = Csa2moves.csa2moves(wars)
		# act
		result = Tactics.create_tactics("嬉野流", usi[0], usi[1], False)
		# assert
		print(result)

	# movesを日本語に直すテスト
	def test_convert_moves1(self):
		# arrange
		moves = 'S*3g 5c5b+ S*3a'
		sfen = 'ln2+R2nl/5ggk1/4Ppppp/9/pp3N3/4GPP2/PP6P/2GB1R3/LNK5L w BS3s6p 94 '
		# act
		result = Tactics.convert_moves(moves, sfen)
		# assert
		print(result)


	# bestmovesを日本語に直すテスト
	def test_convert_moves2(self):
		# arrange
		moves = 'P*6g 5c5b+ 6g6h+ 4h6h S*3a P*2d 2c2d 6h6a+ B*7c 5b4b 7c5a 4b3b 3a3b 6a5a P*7g 8i7g R*4i P*6i'
		sfen = 'ln2+R2nl/5ggk1/4Ppppp/9/pp3N3/4GPP2/PP6P/2GB1R3/LNK5L w BS3s6p 94 '
		# act
		result = Tactics.convert_moves(moves, sfen)
		# assert
		print(result)


	# premoveを日本語に直すテスト
	def test_convert_premove(self):
		# arrange
		moves = '7a5a+'
		sfen = 'ln2+R2nl/5ggk1/4Ppppp/9/pp3N3/4GPP2/PP6P/2GB1R3/LNK5L w BS3s6p 94 '
		# act
		result = Tactics.convert_premove(moves, sfen)
		# assert
		print(result)