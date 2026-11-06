"""Everything a story can mention, with English and Japanese names and its picture."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Entity:
    id: str            # also the picture name in art.py
    kind: str          # animal, character, food, thing, place
    en: str            # singular noun phrase
    ja: str
    en_pl: str = ""    # plural (foods)
    short: str = ""    # short English noun used after first mention ("the cheese")
    tags: tuple = field(default_factory=tuple)  # colorable, wearable, instrument
    move_en: str = ""  # how an actor travels, past tense
    move_ja: str = ""  # te-form phrase
    wear_en: str = ""  # verb phrase with {x}
    wear_ja: str = ""  # verb phrase after を
    at_en: str = ""    # place preposition: in / on / at / near

    @property
    def noun(self):
        return self.short or self.en


def _a(*rows):
    return {r[0]: Entity(r[0], "animal", r[1], r[2], move_en=r[3], move_ja=r[4]) for r in rows}


ANIMALS = _a(
    ("cat", "cat", "ネコ", "tiptoed", "そっと歩いて"),
    ("dog", "dog", "イヌ", "ran", "走って"),
    ("frog", "frog", "カエル", "hopped", "ぴょんぴょん跳ねて"),
    ("penguin", "penguin", "ペンギン", "waddled", "よちよち歩いて"),
    ("rabbit", "rabbit", "ウサギ", "bounced", "ぴょこぴょこ跳ねて"),
    ("bear", "bear", "クマ", "lumbered", "のっしのっし歩いて"),
    ("pig", "pig", "ブタ", "trotted", "とことこ歩いて"),
    ("duck", "duck", "アヒル", "waddled", "ぺたぺた歩いて"),
    ("owl", "owl", "フクロウ", "flew", "パタパタ飛んで"),
    ("fox", "fox", "キツネ", "dashed", "さっと走って"),
    ("elephant", "elephant", "ゾウ", "stomped", "ドスンドスン歩いて"),
    ("monkey", "monkey", "サル", "swung on vines", "つるにぶら下がって"),
    ("turtle", "turtle", "カメ", "crawled slowly", "ゆっくりゆっくり歩いて"),
    ("octopus", "octopus", "タコ", "wiggled", "くねくね進んで"),
    ("lion", "lion", "ライオン", "strutted", "どうどうと歩いて"),
    ("mouse", "mouse", "ネズミ", "scurried", "ちょこちょこ走って"),
)

CHARACTERS = {e.id: e for e in (
    Entity("robot", "character", "robot", "ロボット", move_en="rolled", move_ja="ガタゴト転がって"),
    Entity("alien", "character", "alien", "宇宙人", move_en="zoomed in a flying saucer",
           move_ja="空飛ぶ円ばんに乗って"),
    Entity("ghost", "character", "ghost", "おばけ", move_en="floated", move_ja="ふわふわうかんで"),
    Entity("dinosaur", "character", "dinosaur", "きょうりゅう", move_en="thundered", move_ja="ドシンドシン歩いて"),
    Entity("snowman", "character", "snowman", "雪だるま", move_en="slid", move_ja="つるつるすべって"),
    Entity("wizard", "character", "wizard", "魔法使い", move_en="flew on a broom", move_ja="ほうきに乗って"),
    Entity("pirate", "character", "pirate", "海賊", move_en="sailed", move_ja="船に乗って"),
)}

ACTORS = {**ANIMALS, **CHARACTERS}

FOODS = {e.id: e for e in (
    Entity("banana", "food", "banana", "バナナ", "bananas"),
    Entity("pizza", "food", "pizza", "ピザ", "pizzas"),
    Entity("donut", "food", "donut", "ドーナツ", "donuts"),
    Entity("cupcake", "food", "cupcake", "カップケーキ", "cupcakes"),
    Entity("apple", "food", "apple", "りんご", "apples"),
    Entity("carrot", "food", "carrot", "にんじん", "carrots"),
    Entity("cheese", "food", "wedge of cheese", "チーズ", "wedges of cheese", "cheese"),
    Entity("icecream", "food", "ice cream cone", "アイスクリーム", "ice cream cones", "ice cream cone"),
    Entity("cookie", "food", "cookie", "クッキー", "cookies"),
    Entity("strawberry", "food", "strawberry", "いちご", "strawberries"),
)}

_PUT_ON = ("put on {x}", "をかぶりました")
_LIKE_HAT = ("wore {x} like a hat", "を帽子のようにかぶりました")

THINGS = {e.id: e for e in (
    Entity("hat", "thing", "hat", "帽子", tags=("colorable", "wearable"), wear_en=_PUT_ON[0], wear_ja=_PUT_ON[1]),
    Entity("sock", "thing", "sock", "くつ下", tags=("colorable", "wearable"),
           wear_en=_LIKE_HAT[0], wear_ja=_LIKE_HAT[1]),
    Entity("boot", "thing", "rain boot", "長ぐつ", short="boot", tags=("colorable", "wearable"),
           wear_en=_LIKE_HAT[0], wear_ja=_LIKE_HAT[1]),
    Entity("crown", "thing", "crown", "王かん", tags=("wearable",), wear_en=_PUT_ON[0], wear_ja=_PUT_ON[1]),
    Entity("sunglasses", "thing", "pair of sunglasses", "サングラス", short="sunglasses", tags=("wearable",),
           wear_en="put on {x}", wear_ja="をかけました"),
    Entity("umbrella", "thing", "umbrella", "かさ", tags=("colorable",)),
    Entity("balloon", "thing", "balloon", "風船", tags=("colorable",)),
    Entity("kite", "thing", "kite", "カイト", tags=("colorable",)),
    Entity("book", "thing", "book", "本", tags=("colorable",)),
    Entity("ball", "thing", "ball", "ボール", tags=("colorable",)),
    Entity("teapot", "thing", "teapot", "ティーポット", tags=("colorable",)),
    Entity("gift", "thing", "present", "プレゼント", tags=("colorable",)),
    Entity("key", "thing", "key", "カギ"),
    Entity("rocket", "thing", "toy rocket", "おもちゃのロケット", short="rocket"),
    Entity("guitar", "thing", "guitar", "ギター", tags=("instrument",)),
    Entity("drum", "thing", "drum", "たいこ", tags=("instrument",)),
    Entity("trumpet", "thing", "trumpet", "トランペット", tags=("instrument",)),
)}

PLACES = {e.id: e for e in (
    Entity("beach", "place", "the beach", "ビーチ", at_en="at"),
    Entity("castle", "place", "the castle", "お城", at_en="in"),
    Entity("moon", "place", "the moon", "月", at_en="on"),
    Entity("forest", "place", "the forest", "森", at_en="in"),
    Entity("volcano", "place", "the volcano", "火山", at_en="near"),
    Entity("island", "place", "the island", "島", at_en="on"),
    Entity("farm", "place", "the farm", "牧場", at_en="on"),
    Entity("bakery", "place", "the bakery", "パン屋さん", at_en="in"),
    Entity("mountain", "place", "the snowy mountain", "雪山", at_en="on"),
)}

ALL = {**ACTORS, **FOODS, **THINGS, **PLACES}

COLOR_NAMES = {  # name: (English, Japanese before a noun, Japanese answer label)
    "red": ("red", "赤い", "赤"),
    "blue": ("blue", "青い", "青"),
    "green": ("green", "緑の", "緑"),
    "yellow": ("yellow", "黄色い", "黄色"),
    "purple": ("purple", "むらさきの", "むらさき"),
    "pink": ("pink", "ピンクの", "ピンク"),
    "orange": ("orange", "オレンジ色の", "オレンジ"),
}

NAMES = [  # silly character names (English, Japanese)
    ("Bubbles", "バブルス"), ("Mr. Pickles", "ピクルスさん"), ("Captain Noodle", "ヌードル船長"),
    ("Princess Waffle", "ワッフル姫"), ("Sir Wiggles", "ウィグルス卿"), ("Dr. Muffin", "マフィン博士"),
    ("Professor Sprinkles", "スプリンクル教授"), ("Little Taco", "タコスくん"), ("Grandma Jelly", "ゼリーおばあちゃん"),
    ("Coco", "ココ"), ("Mochi", "モチ"), ("Pudding", "プリン"), ("Biscuit", "ビスケット"), ("Ziggy", "ジギー"),
    ("Lulu", "ルル"), ("Pom-Pom", "ポンポン"), ("Tofu", "トーフ"), ("Captain Fluff", "フラッフ船長"),
    ("Madame Marshmallow", "マシュマロ夫人"), ("Baron Burrito", "ブリトー男爵"), ("Noodles", "ヌードルス"),
    ("Peanut", "ピーナッツ"), ("Sergeant Snuggles", "スナッグルズ軍曹"), ("Wobbles", "ウォブルス"),
    ("King Kiwi", "キウイ王"), ("Queen Cupcake", "カップケーキ女王"), ("Gizmo", "ギズモ"), ("Pickle", "ピクル"),
]

NUM_EN = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight"]
NUM_JA = ["", "ひとつ", "ふたつ", "みっつ", "よっつ", "いつつ", "むっつ", "ななつ", "やっつ"]


def article(phrase):
    return ("an " if phrase[:1].lower() in "aeiou" else "a ") + phrase
