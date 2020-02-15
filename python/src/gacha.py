import math
import numpy as np
from functools import reduce
from enum import IntEnum, auto

#カードのレアリティ
class Rarity(IntEnum):
    N = auto()
    R = auto()
    SR = auto()
    SSR = auto()

#カードの5属性
class Element(IntEnum):
    Blaze = auto() #頭文字Forestと変えたいのでFireではない
    Water = auto()
    Forest = auto()
    Light = auto()
    Dark = auto()

#カードのリリース区分
class Series(IntEnum):
    Launch = auto() #初期リリース
    Olympus = auto() #追加パック
    Japanese = auto() #追加パック
    Nordic = auto() #追加パック
    Grimm = auto() #追加パック
    Festival = auto() #フェス限定

#要素に注目してカードリストを辞書化する
def classify_cards(cards, label):
    res = {}
    for card in sorted(cards, key=lambda x:x[label]):
        key = card[label]
        if key not in res:
            res[key] = []
        res[key].append(card)
    return res

#要素に注目してカード枚数を数える
def classify_counts(cards, label):
    res = {}
    for card in sorted(cards, key=lambda x:x[label]):
        key = card[label]
        if key not in res:
            res[key] = 0
        res[key] += 1
    return res

#カードリストを要素で絞り込む
def filter_cards(cards, label, values):
    return [card for card in cards if card[label] in values]

#カードリストから要素のみ抽出する
def card_values(cards, label):
    return [card[label] for card in cards]

#最小公倍数
def lcm(a, b):
    return a*b // math.gcd(a,b)

#実数を整数と10のN乗に因数分解する
def factorize_to_integer(number):
    s = str(number)
    i = s.find('.')
    mul10 = 10**(len(s)-i-1) if i != -1 else 1
    return int(number*mul10), mul10

#比率を整数に直す
def integerize_ratio(ratio):
    mul10 = max([factorize_to_integer(v)[1] for v in ratio.values()])
    return {k:int(v*mul10) for k,v in ratio.items()}

#排出率に従って抽選箱を作成する
def create_lottery_box(cards, source_ratio):
    counts = classify_counts(cards, 'rarity')
    counts_lcm = reduce(lcm, counts.values())
    ratio = integerize_ratio(source_ratio)
    ratio_gcd = reduce(math.gcd, ratio.values())
    return [card for card in cards if card['rarity'] in ratio
        for i in range(ratio[card['rarity']]//ratio_gcd * counts_lcm//counts[card['rarity']])]

#特定レアリティの排出率をN倍にして、その分最低レアリティの排出率を下げる
def rarity_up(source_ratio, rarity, source_rate):
    ratio = integerize_ratio(source_ratio)
    rate, mul10 = factorize_to_integer(source_rate)
    before_ratio_val = ratio[rarity]*mul10
    ratio = {k:v*(rate if k == rarity else mul10) for k,v in ratio.items()}
    ratio[min(ratio.keys())] -= ratio[rarity] - before_ratio_val
    return ratio

#特定カードの排出率をN倍にする
def pickup(cards, ids, source_rate):
    pickup_cards = filter_cards(cards, 'id', ids)
    pickup_rarities = set(card_values(pickup_cards, 'rarity'))
    rarities = set(card_values(cards, 'rarity'))
    rarity_card_dict = classify_cards(cards, 'rarity')
    res = []
    for rarity in rarities:
        if rarity in pickup_rarities:
            rarity_cards = rarity_card_dict[rarity]
            total = len(rarity_cards)
            pickup = len(filter_cards(pickup_cards, 'rarity', [rarity]))
            rate, mul10 = factorize_to_integer(source_rate)
            #ピックアップ対象の排出率x、対象外の排出率y
            # x = 1/total * source_rate ...元の排出率をN倍にする
            # y = (1 - x * pickup) / (total - pickup) ...確率アップ対象を除外した排出率を分配する
            # ↓ 式の整理
            x = rate * total - rate * pickup
            y = mul10 * total - rate * pickup
            assert x > 0 and y > 0, "ピックアップ排出率がオーバーフローします。"
            xy_gcd = math.gcd(x, y)
            x = x // xy_gcd
            y = y // xy_gcd
            res += [card for card in rarity_cards for i in range(x if card['id'] in ids else y)]
        else:
            res += rarity_card_dict[rarity]
    return res

def create_card(seq, rarity, series, element):
    id = seq.next()
    return {'id':id, 'rarity':rarity, 'series':series, 'element':element,
        'name':"%03s-%s-%s-%s"%(id,series.name,rarity.name,element.name)}

class Sequence:
    def __init__(self):
        self.value = 0
    def next(self):
        self.value += 1
        return self.value

def test():

    #カードリスト作成
    seq = Sequence()
    all_cards = [create_card(seq, Rarity.N, Series.Launch, e) for i in range(8) for e in Element] +\
        [create_card(seq, Rarity.R, Series.Launch, e) for i in range(8) for e in Element] +\
        [create_card(seq, Rarity.SR, Series.Launch, e) for i in range(4) for e in Element] +\
        [create_card(seq, Rarity.SSR, Series.Launch, e) for i in range(2) for e in Element] +\
        [create_card(seq, Rarity.SSR, Series.Olympus, e) for e in Element] +\
        [create_card(seq, Rarity.SSR, Series.Japanese, e) for e in Element] +\
        [create_card(seq, Rarity.SSR, Series.Nordic, e) for e in Element] +\
        [create_card(seq, Rarity.SSR, Series.Grimm, e) for e in Element] +\
        [create_card(seq, Rarity.SSR, Series.Festival, e) for e in Element]
    fes_cards = filter_cards(all_cards, 'series', [Series.Festival])
    cards = [card for card in all_cards if card not in fes_cards]
    grimm_cards = filter_cards(cards, 'series', [Series.Grimm])

    #確率設定
    free_ratio = {Rarity.N:79, Rarity.R:20, Rarity.SR:1}
    rare_ratio = {Rarity.R:79, Rarity.SR:20, Rarity.SSR:1}
    sr_ratio = {Rarity.SR:95, Rarity.SSR:5}
    for ratio in [free_ratio, rare_ratio, sr_ratio]:
        sum_ratio = float(sum(ratio.values()))
        assert sum_ratio==100, "排出率の合計が[%s%%]です。"%sum_ratio
    
    #排出テスト
    lottery_test("無料ガチャ", cards, free_ratio)
    lottery_test("レアガチャ", cards, rare_ratio)
    lottery_test("SSR確率アップガチャ", cards, rarity_up(rare_ratio, Rarity.SSR, 2))
    lottery_test("属性ガチャ", filter_cards(cards, 'element', [Element.Blaze]), rare_ratio)
    lottery_test("新シリーズ追加ガチャ", pickup(cards, card_values(grimm_cards, 'id'), 5), rare_ratio)
    lottery_test("限定フェスガチャ", pickup(cards + fes_cards, card_values(fes_cards, 'id'), 5), rare_ratio)
    lottery_test("SR以上確定ガチャ", cards, sr_ratio)

def lottery_test(title, cards, ratio):
    
    #確率表記
    box = create_lottery_box(cards, ratio)
    print_card_counts("%s 確率表記"%title, box)
    
    #抽選する
    res = np.random.choice(box, 5000000)
    print_card_counts("%s 排出テスト"%title, res)

def print_card_counts(title, cards):
    print(title)
    
    #レアリティごとの枚数と割合
    counts = classify_counts(cards, 'rarity')
    print(counts)
    lambda_rates = lambda counts: {k:"%.3f%%"%(v/sum(counts.values())*100) for k,v in counts.items()}
    print(lambda_rates(counts))

    #カード種類ごとの枚数と割合
    counts = classify_counts(cards, 'name')
    rates = lambda_rates(counts)
    for name in counts.keys():
        print("%6s枚"%counts[name], rates[name], name)
    print()

test()
