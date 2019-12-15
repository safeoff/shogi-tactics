# shogi-tactics

Create shogi tactics from online match.  
& Add it to ankiweb.

## Usage
```
  create.py (--wars <wars_id> --rule <rule>) [--file --limit <limit_num>]
  create.py (-h | --help)
  create.py --version
```
  
## Options
```
  -h --help     Show this screen.
  --wars        ID of shogi wars you want to calculate.
  --rule        game rule[10m | 3m | 10s]
  --limit       Maximum number of game records to download [default:no limit].
  --file        Output to a file. It doesn't add to ankiweb.
  --version     Show version.
```


将棋ウォーズの棋譜から次の一手問題を自動生成します。  
生成した問題は、↓の2パターンで出力します。  

・AnkiWebにカード登録します。
こんなふうになります
![doc3](https://raw.githubusercontent.com/safeoff/shogi-tactics/master/doc3.png)
![doc4](https://raw.githubusercontent.com/safeoff/shogi-tactics/master/doc4.png)


・HTML形式のファイルに出力します。  

![doc1](https://raw.githubusercontent.com/safeoff/shogi-tactics/master/doc1.png)

  
termuxでcron実行すると楽です
![doc2](https://raw.githubusercontent.com/safeoff/shogi-tactics/master/doc2.png)

  
↓のリポジトリに依存しています。  
safeoff以下のやつはまだreadmeぜんぜん未整備です  

 safeoff/shogi_anki  
 safeoff/kifu-downloader  
 safeoff/csa2moves  
 kovetskiy/ankictl  
 yaneurao/Ayane  
