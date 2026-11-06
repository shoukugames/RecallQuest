"""Random silly stories, written in English and Japanese at the same time, with questions.

A story is planned as a list of events (find, go, meet, give, eat, wear, play...).
Every event is rendered into both languages and records facts. Questions are built
only from facts that have exactly one right answer, and every answer is a picture.
Everything runs offline from the word lists in entities.py.
"""
import hashlib
import random
from dataclasses import dataclass, field

from . import entities as E

DIFFICULTIES = ("easy", "medium", "hard")
LEVELS = 10


# ------------------------------------------------------------------- results
@dataclass
class Option:
    art: str
    color: str = None
    count: int = 0
    en: str = ""
    ja: str = ""

    def key(self):
        return (self.art, self.color, self.count)


@dataclass
class Question:
    en: str
    ja: str
    kind: str
    options: list
    answer: int

    def text(self, lang):
        return self.ja if lang == "ja" else self.en


@dataclass
class Story:
    difficulty: str
    level: int
    title_en: str
    title_ja: str
    paragraphs: list          # list of paragraphs, each a list of (en, ja) sentences
    questions: list
    signature: str
    words: int = 0
    mentions: set = field(default_factory=set)

    def title(self, lang):
        return self.title_ja if lang == "ja" else self.title_en

    def text(self, lang):
        """Paragraphs as strings in one language."""
        if lang == "ja":
            return ["".join(ja for _, ja in para) for para in self.paragraphs]
        return [" ".join(en for en, _ in para) for para in self.paragraphs]


# ----------------------------------------------------------------- settings
def params(difficulty, level):
    lv = max(1, min(LEVELS, int(level)))
    if difficulty == "easy":
        return dict(cast=1 if lv <= 2 else 2, events=3 + (lv - 1) // 3, fillers=(lv - 1) // 4,
                    options=3 if lv <= 4 else 4, named=lv >= 5, colors=lv >= 3, counts=lv >= 4,
                    traps=0, reasons=False, fancy=False, quirks=False,
                    tiers={1: 3, 2: 1 if lv >= 4 else 0, 3: 0}, shuffle=False)
    if difficulty == "medium":
        return dict(cast=2 if lv <= 5 else 3, events=4 + (lv - 1) // 2, fillers=1 + (lv - 1) // 4,
                    options=4 if lv <= 5 else 5, named=True, colors=True, counts=True,
                    traps=1 if lv >= 5 else 0, reasons=lv >= 7, fancy=True, quirks=lv >= 3,
                    tiers={1: 2, 2: 2, 3: 1 if lv >= 4 else 0}, shuffle=False)
    return dict(cast=3 if lv <= 4 else 4, events=6 + (lv - 1) * 2 // 3, fillers=2 + (lv - 1) // 3,
                options=6, named=True, colors=True, counts=True, traps=1 + (lv >= 6), reasons=True,
                fancy=True, quirks=True, tiers={1: 1, 2: 2, 3: 3}, shuffle=True)


# --------------------------------------------------------------- word banks
OPENERS_EASY = [("Then,", "それから、"), ("Next,", "つぎに、"), ("One day,", "ある日、"), ("", ""), ("", "")]
OPENERS_FANCY = [("A little later,", "しばらくして、"), ("Just before lunch,", "お昼ごはんの少し前に、"),
                 ("All of a sudden,", "とつぜん、"), ("As the sun went down,", "夕日がしずむころ、"),
                 ("After a short nap,", "少しお昼ねをしたあと、"), ("That afternoon,", "その日の午後、")]
FIND_OPENERS = [("One morning,", "ある朝、"), ("After breakfast,", "朝ごはんのあと、"), ("One day,", "ある日、")]
SPOTS = [("under a rock", "岩の下で"), ("inside a cardboard box", "ダンボール箱の中で"),
         ("behind the sofa", "ソファーのうしろで"), ("in a puddle", "水たまりの中で"),
         ("on top of a cloud", "雲の上で"), ("in the fridge", "れいぞうこの中で"), ("under the bed", "ベッドの下で"),
         ("in a pile of leaves", "落ち葉の山の中で"), ("inside a hollow log", "木のうろの中で")]
REASONS = [("look for a singing cloud", "歌う雲をさがす"), ("practice yodeling", "ヨーデルの練習をする"),
           ("count the clouds", "雲の数をかぞえる"), ("find the world's biggest bubble", "世界一大きなシャボン玉を見つける"),
           ("teach a worm to whistle", "ミミズに口笛を教える"), ("take a bubble bath", "あわあわのおふろに入る"),
           ("win a staring contest", "にらめっこ大会で勝つ")]
USES = [("pillow", "まくら"), ("tiny boat", "小さな船"), ("spaceship", "宇宙船"), ("hat for my goldfish", "金魚の帽子"),
        ("very fancy bathtub", "とてもごうかなおふろ"), ("birthday present for the moon", "月へのたんじょう日プレゼント")]
EFFECTS = [("the windows wiggled", "窓がガタガタゆれました"), ("a cloud woke up and yawned", "雲が目をさましてあくびをしました"),
           ("all the fish started to dance", "魚たちがおどりだしました"),
           ("the trees clapped their branches", "木々が枝をたたいて拍手しました"),
           ("a passing bird forgot how to fly", "通りかかった鳥が飛び方をわすれてしまいました")]
QUIRKS = [("loved to sing opera in the bath", "おふろでオペラを歌うのが大好きでした"),
          ("could burp the whole alphabet", "ゲップでアルファベットを全部言えました"),
          ("always wore polka-dot pajamas", "いつも水玉もようのパジャマを着ていました"),
          ("told the worst jokes in the world", "世界一つまらないジョークを言うのが得意でした"),
          ("snored louder than a thunderstorm", "かみなりよりも大きないびきをかきました"),
          ("collected shiny pebbles", "ピカピカの小石を集めていました"),
          ("was scared of butterflies", "チョウチョがこわくてたまりませんでした")]
FILLERS = [  # (en, ja, mentions); {A} is an actor, {Aj} the Japanese
    ("The sky was the color of strawberry milk.", "空はいちごミルクのような色でした。", {"strawberry"}),
    ("Somewhere far away, a cloud sneezed.", "どこか遠くで、雲がくしゃみをしました。", set()),
    ("Nobody knew why, but the trees were humming a song.", "なぜかわからないけれど、木々が歌を口ずさんでいました。", set()),
    ("A grumpy snail watched everything from a leaf.", "葉っぱの上から、きげんの悪いカタツムリがじっと見ていました。", set()),
    ("The wind smelled a little bit like pancakes.", "風は少しだけパンケーキのにおいがしました。", set()),
    ("It was so windy that hats were flying everywhere.", "風が強くて、あちこちで帽子が飛んでいました。", {"hat"}),
    ("{A} laughed so hard that the hiccups lasted ten minutes.", "{Aj}は笑いすぎて、十分間しゃっくりが止まりませんでした。", set()),
    ("{A} thought it was the best day ever.", "{Aj}は「今日は最高の日だ！」と思いました。", set()),
    ("{A} did a funny little dance.", "{Aj}はおかしな小さいダンスをおどりました。", set()),
    ("{A} said, \"Wow! This is amazing!\"", "{Aj}は「わあ！すごい！」と言いました。", set()),
    ("{A} wondered if fish ever get bored.", "{Aj}は「魚もたいくつするのかな」と考えました。", set()),
    ("{A} hummed a tune about socks.", "{Aj}はくつ下の歌を口ずさみました。", {"sock"}),
]
ENDINGS = [("In the end, everyone took a big, happy nap.", "最後に、みんなでぐっすりお昼ねをしました。"),
           ("And that was the silliest day ever.", "こうして、世界一へんてこな一日が終わりました。"),
           ("Everyone laughed until the stars came out.", "みんなは星が出るまで笑いました。"),
           ("Then everyone went home for pancakes.", "それから、みんなでパンケーキを食べに家へ帰りました。")]


KIND_WEIGHT = {"name": 0.4, "home": 0.6, "go_who": 0.8}


def cap(text):
    return text[:1].upper() + text[1:] if text else text


def title_case(text):
    small = {"of", "the", "and", "a", "an"}
    words = text.split()
    return " ".join(w if (i and w in small) else cap(w) for i, w in enumerate(words))


# -------------------------------------------------------------------- actors
class Actor:
    def __init__(self, ent, name=None):
        self.ent = ent
        self.name = name          # (en, ja) or None
        self.introduced = False
        self.place = None
        self.holding = []
        self.block = -1           # block index where introduced

    def ref(self):
        if self.name:
            return self.name
        return "the " + self.ent.en, self.ent.ja

    def first(self):
        if self.name:
            return f"{E.article(self.ent.en)} named {self.name[0]}", f"{self.name[1]}という名前の{self.ent.ja}"
        return E.article(self.ent.en), self.ent.ja


class Builder:
    def __init__(self, rng, difficulty, level):
        self.rng = rng
        self.difficulty = difficulty
        self.level = level
        self.p = params(difficulty, level)
        self.blocks = []          # each: dict(kind, sents=[(en, ja)], sig=str)
        self.mentions = set()
        self.facts = []
        self.used = set()
        self.colors = {}          # thing id -> colour name
        self.actors = []
        self.homes = set()
        self.used_fillers = set()
        self.used_meets = set()

    # -- helpers
    def opener(self):
        if not self.blocks or self.rng.random() < 0.35:
            return "", ""
        bank = OPENERS_EASY + (OPENERS_FANCY if self.p["fancy"] else [])
        return self.rng.choice(bank)

    def add(self, kind, sents, sig, mentions=()):
        self.blocks.append({"kind": kind, "sents": sents, "sig": sig})
        self.mentions.update(mentions)
        return len(self.blocks) - 1

    @staticmethod
    def join(op, en, ja):
        return cap((op[0] + " " if op[0] else "") + en), op[1] + ja

    def pick(self, pool, avoid=()):
        choices = [k for k in pool if k not in self.used and k not in avoid]
        if not choices:
            return None
        key = self.rng.choice(sorted(choices))
        self.used.add(key)
        return key

    def thing_first(self, ent, color):
        if color:
            en_col, ja_col, _ = E.COLOR_NAMES[color]
            return E.article(f"{en_col} {ent.en}"), f"{ja_col}{ent.ja}"
        return E.article(ent.en), ent.ja

    def maybe_color(self, ent):
        if "colorable" in ent.tags and self.p["colors"] and self.rng.random() < 0.85:
            color = self.rng.choice(sorted(E.COLOR_NAMES))
            self.colors[ent.id] = color
            return color
        return None

    # -- events
    def intro(self, a):
        place = E.PLACES[self.pick(E.PLACES)]
        a.place, a.introduced = place, True
        self.homes.add(place.id)
        fe, fj = a.first()
        sents = [self.rng.choice([
            (f"Once upon a time, {fe} lived {place.at_en} {place.en}.", f"むかしむかし、{place.ja}に{fj}が住んでいました。"),
            (f"There once was {fe} who lived {place.at_en} {place.en}.", f"{place.ja}に、{fj}が住んでいました。"),
        ])]
        if self.p["quirks"] and self.rng.random() < 0.5:
            q = self.rng.choice(QUIRKS)
            sents.append((f"{cap(a.ref()[0])} {q[0]}.", f"{a.ref()[1]}は{q[1]}。"))
        a.block = self.add("intro", sents, f"intro:{a.ent.id}:{place.id}", {a.ent.id, place.id})
        self.facts.append({"t": "home", "a": a, "place": place, "i": a.block})

    def meet(self, a, b):
        pl = a.place
        b.place, b.introduced = pl, True
        A, Aj = a.ref()
        bf, bfj = b.first()
        templates = [
            (f"{cap(pl.at_en if pl.at_en != 'near' else 'at')} {pl.en}, {A} met {bf}.", f"{pl.ja}で、{Aj}は{bfj}に会いました。"),
            (f"{A} bumped into {bf} {pl.at_en if pl.at_en != 'near' else 'at'} {pl.en}.",
             f"{Aj}は{pl.ja}で{bfj}にばったり出会いました。"),
            (f"{A} made a new friend {pl.at_en if pl.at_en != 'near' else 'at'} {pl.en}: {bf}.",
             f"{pl.ja}で、{Aj}に新しい友だちができました。{bfj}です。"),
            (f"{cap(pl.at_en if pl.at_en != 'near' else 'at')} {pl.en}, {A} met {bf}, who was waving hello.",
             f"{pl.ja}で、{Aj}は手をふっている{bfj}に会いました。"),
        ]
        fresh = [i for i in range(len(templates)) if i not in self.used_meets] or list(range(len(templates)))
        pick = self.rng.choice(fresh)
        self.used_meets.add(pick)
        en, ja = templates[pick]
        sents = [(cap(en), ja)]
        if self.p["quirks"] and self.rng.random() < 0.5:
            q = self.rng.choice(QUIRKS)
            sents.append((f"{cap(b.ref()[0])} {q[0]}.", f"{b.ref()[1]}は{q[1]}。"))
        b.block = self.add("meet", sents, f"meet:{a.ent.id}:{b.ent.id}:{pl.id}", {a.ent.id, b.ent.id, pl.id})
        self.facts.append({"t": "meet", "a": a, "b": b, "place": pl, "i": b.block})

    def find(self, a):
        pool = [k for k, e in E.THINGS.items() if "instrument" not in e.tags]
        key = self.pick(pool)
        if not key:
            return False
        ent = E.THINGS[key]
        color = self.maybe_color(ent)
        of, ofj = self.thing_first(ent, color)
        spot = self.rng.choice(SPOTS)
        A, Aj = a.ref()
        op = self.rng.choice(FIND_OPENERS) if self.rng.random() < 0.5 else self.opener()
        verb = self.rng.choice([("found", "見つけました"), ("discovered", "発見しました")])
        en, ja = self.join(op, f"{A} {verb[0]} {of} {spot[0]}.", f"{Aj}は{spot[1]}{ofj}を{verb[1]}。")
        a.holding.append(ent)
        i = self.add("find", [(en, ja)], f"find:{a.ent.id}:{key}:{color}", {a.ent.id, key})
        self.facts.append({"t": "find", "a": a, "obj": ent, "color": color, "i": i})
        return True

    def go(self, a, partner=None):
        options = [k for k in E.PLACES if k != a.place.id and k not in self.used]
        if not options:
            return False
        pl = E.PLACES[self.rng.choice(sorted(options))]
        self.used.add(pl.id)
        A, Aj = a.ref()
        op = self.opener()
        if partner:
            B, Bj = partner.ref()
            en, ja = self.join(op, f"{A} and {B} went to {pl.en} together.", f"{Aj}と{Bj}は、いっしょに{pl.ja}へ行きました。")
            partner.place = pl
        elif self.p["reasons"] and self.rng.random() < 0.5:
            r = self.rng.choice(REASONS)
            en, ja = self.join(op, f"{A} {a.ent.move_en} to {pl.en} to {r[0]}.",
                               f"{Aj}は{r[1]}ために、{a.ent.move_ja}{pl.ja}へ行きました。")
        else:
            en, ja = self.join(op, f"{A} {a.ent.move_en} to {pl.en}.", f"{Aj}は{a.ent.move_ja}{pl.ja}へ行きました。")
        a.place = pl
        ids = {a.ent.id, pl.id} | ({partner.ent.id} if partner else set())
        i = self.add("go", [(en, ja)], f"go:{a.ent.id}:{pl.id}:{partner.ent.id if partner else ''}", ids)
        self.facts.append({"t": "go", "a": a, "place": pl, "i": i})
        if partner:
            self.facts.append({"t": "go", "a": partner, "place": pl, "i": i})
            self.facts.append({"t": "with", "a": a, "b": partner, "place": pl, "i": i})
        return True

    def give(self, a, b):
        obj = a.holding.pop(0)
        b.holding.append(obj)
        A, Aj = a.ref()
        B, Bj = b.ref()
        op = self.opener()
        en, ja = self.join(op, f"{A} gave the {obj.noun} to {B}.", f"{Aj}は{Bj}にその{obj.ja}をあげました。")
        sents = [(en, ja)]
        if self.rng.random() < 0.7:
            use = self.rng.choice(USES)
            sents.append((f"{cap(B)} said, \"Thank you! I will use it as a {use[0]}!\"",
                          f"{Bj}は「ありがとう！{use[1]}にするね！」と言いました。"))
        i = self.add("give", sents, f"give:{a.ent.id}:{b.ent.id}:{obj.id}", {a.ent.id, b.ent.id, obj.id})
        self.facts.append({"t": "give", "a": a, "b": b, "obj": obj, "i": i})

    def eat(self, a):
        key = self.pick(E.FOODS)
        if not key:
            return False
        food = E.FOODS[key]
        n = self.rng.randint(2, 6)
        A, Aj = a.ref()
        num, numj = E.NUM_EN[n], E.NUM_JA[n]
        choice = self.rng.randrange(3)
        if choice == 0:
            en, ja = self.join(self.opener(), f"{A} was very hungry and ate {num} {food.en_pl}.",
                               f"{Aj}はおなかがペコペコだったので、{food.ja}を{numj}食べました。")
        elif choice == 1:
            en, ja = self.join(self.opener(), f"{A} gobbled up {num} {food.en_pl} in one big bite.",
                               f"{Aj}は{food.ja}を{numj}、ひと口でぺろりと食べました。")
        else:
            en, ja = f"For a snack, {A} ate {num} {food.en_pl}.", f"おやつに、{Aj}は{food.ja}を{numj}食べました。"
        i = self.add("eat", [(en, ja)], f"eat:{a.ent.id}:{key}:{n}", {a.ent.id, key})
        self.facts.append({"t": "eat", "a": a, "obj": food, "n": n, "i": i})
        return True

    def wear(self, a):
        key = self.pick([k for k, e in E.THINGS.items() if "wearable" in e.tags])
        if not key:
            return False
        ent = E.THINGS[key]
        color = self.maybe_color(ent)
        of, ofj = self.thing_first(ent, color)
        A, Aj = a.ref()
        en, ja = self.join(self.opener(), f"{A} {ent.wear_en.format(x=of)}.", f"{Aj}は{ofj}{ent.wear_ja}。")
        sents = [(en, ja)]
        if self.rng.random() < 0.5:
            sents.append(self.rng.choice([("Everyone thought it looked wonderful.", "みんなは「すてき！」と言いました。"),
                                          ("It looked very silly.", "それはとてもへんてこに見えました。")]))
        i = self.add("wear", sents, f"wear:{a.ent.id}:{key}:{color}", {a.ent.id, key})
        self.facts.append({"t": "wear", "a": a, "obj": ent, "color": color, "i": i})
        return True

    def play(self, a):
        key = self.pick([k for k, e in E.THINGS.items() if "instrument" in e.tags])
        if not key:
            return False
        ent = E.THINGS[key]
        eff = self.rng.choice(EFFECTS)
        A, Aj = a.ref()
        en, ja = self.join(self.opener(), f"{A} played the {ent.en} so loudly that {eff[0]}.",
                           f"{Aj}がとても大きな音で{ent.ja}をえんそうしたので、{eff[1]}。")
        i = self.add("play", [(en, ja)], f"play:{a.ent.id}:{key}", {a.ent.id, key})
        self.facts.append({"t": "play", "a": a, "obj": ent, "i": i})
        return True

    # -- filler and traps (inserted after the main plan; they add no facts)
    def filler_block(self, a):
        fresh = [f for f in FILLERS if f[0] not in self.used_fillers] or FILLERS
        en, ja, ments = self.rng.choice(fresh)
        self.used_fillers.add(en)
        A, Aj = a.ref()
        en = cap(en.replace("{A}", A))
        ja = ja.replace("{Aj}", Aj)
        self.mentions.update(ments)
        return {"kind": "filler", "sents": [(en, ja)], "sig": "f"}

    def trap_block(self, a):
        A, Aj = a.ref()
        kind = self.rng.choice(["food", "thing", "place"])
        if kind == "food":
            key = self.pick(E.FOODS)
            if key:
                f = E.FOODS[key]
                self.mentions.add(key)
                return {"kind": "trap", "sig": f"t:{key}", "sents": [
                    (f"{cap(A)} did not like {f.en_pl} at all.", f"{Aj}は{f.ja}が大きらいでした。")]}
        if kind == "thing":
            key = self.pick([k for k, e in E.THINGS.items() if "instrument" not in e.tags])
            if key:
                t = E.THINGS[key]
                self.mentions.add(key)
                return {"kind": "trap", "sig": f"t:{key}", "sents": [
                    (f"{cap(A)} wanted to find {E.article(t.en)}, but never found one.",
                     f"{Aj}は{t.ja}をさがしていましたが、見つかりませんでした。")]}
        key = self.pick(E.PLACES)
        if key:
            pl = E.PLACES[key]
            self.mentions.add(key)
            return {"kind": "trap", "sig": f"t:{key}", "sents": [
                (f"{cap(A)} had always wanted to visit {pl.en}, but never did.",
                 f"{Aj}はずっと{pl.ja}に行ってみたいと思っていましたが、行けませんでした。")]}
        return None

    # -- the plan
    def build(self):
        p, rng = self.p, self.rng
        species = rng.sample(sorted(E.ACTORS), p["cast"])
        names = rng.sample(E.NAMES, p["cast"]) if p["named"] else [None] * p["cast"]
        self.actors = [Actor(E.ACTORS[s], n) for s, n in zip(species, names)]
        for a in self.actors:
            self.used.add(a.ent.id)
        self.intro(self.actors[0])
        pending = self.actors[1:]
        steps = p["events"]
        for step in range(steps):
            left = steps - step
            live = [a for a in self.actors if a.introduced]
            if pending and (rng.random() < 0.55 or left <= len(pending)):
                self.meet(rng.choice(live), pending.pop(0))
                continue
            a = rng.choice(live)
            mates = [b for b in live if b is not a and b.place is a.place]
            choices = [("find", 3), ("go", 2.5), ("eat", 2), ("wear", 1.5), ("play", 1)]
            if a.holding and mates:
                choices.append(("give", 3))
            if mates and len(self.actors) > 1:
                choices.append(("together", 1.2))
            for _ in range(6):
                kind = rng.choices([c[0] for c in choices], [c[1] for c in choices])[0]
                if kind == "give":
                    self.give(a, rng.choice(mates))
                    break
                if kind == "together":
                    if self.go(a, rng.choice(mates)):
                        break
                    continue
                if getattr(self, kind)(a):
                    break
        # fillers and traps go anywhere after the actor they mention appears
        extras = [("filler", None)] * p["fillers"] + [("trap", None)] * p["traps"]
        for kind, _ in extras:
            a = rng.choice(self.actors)
            block = self.filler_block(a) if kind == "filler" else self.trap_block(a)
            if not block:
                continue
            pos = rng.randint(a.block + 1, len(self.blocks))
            self.blocks.insert(pos, block)
            for f in self.facts:
                if f["i"] >= pos:
                    f["i"] += 1
            for other in self.actors:
                if other.block >= pos:
                    other.block += 1
        end = rng.choice(ENDINGS)
        self.blocks.append({"kind": "end", "sents": [end], "sig": "e"})

    # -- questions
    def label(self, ent):
        if ent.kind == "place":
            return cap(ent.en[4:] if ent.en.startswith("the ") else ent.en), ent.ja
        return cap(ent.noun), ent.ja

    def opt(self, ent, color=None, count=0):
        en, ja = self.label(ent)
        if color:
            en, ja = cap(E.COLOR_NAMES[color][0]), E.COLOR_NAMES[color][2]
        if count:
            en, ja = str(count), f"{count}"
        return Option(ent.id, color, count, en, ja)

    def options_from(self, answer, traps, pool, k):
        """answer: Entity; traps: entities named in the story (preferred wrong answers)."""
        rng = self.rng
        wrong = list({t.id: t for t in traps if t.id != answer.id}.values())
        rng.shuffle(wrong)
        others = [e for e in pool if e.id != answer.id and e not in wrong]
        rng.shuffle(others)
        picks = (wrong[: max(1, (k - 1) // 2 + 1)] + others)[: k - 1]
        if len(picks) < k - 1:
            return None
        opts = [self.opt(answer)] + [self.opt(e) for e in picks]
        return self.finish(opts)

    def finish(self, opts):
        right = opts[0]
        self.rng.shuffle(opts)
        return opts, opts.index(right)

    def actor_opts(self, a, k):
        return self.options_from(a.ent, [x.ent for x in self.actors], list(E.ACTORS.values()), k)

    def story_ents(self, kind_filter):
        return [E.ALL[m] for m in sorted(self.mentions) if m in E.ALL and kind_filter(E.ALL[m])]

    def candidates(self):
        k = self.p["options"]
        facts = self.facts
        by = {}
        for f in facts:
            by.setdefault((f["t"], f["a"]), []).append(f)
        goers = {}
        for f in facts:
            if f["t"] == "go":
                goers.setdefault(f["place"].id, set()).add(f["a"])
        meet_at = {}
        for f in facts:
            if f["t"] == "meet":
                meet_at.setdefault((f["a"], f["place"].id), []).append(f)
        things = lambda: self.story_ents(lambda e: e.kind == "thing")  # noqa: E731
        out = []

        def q(tier, fact, en, ja, kind, built):
            if built:
                out.append((tier, fact["i"], kind, Question(en, ja, kind, built[0], built[1])))

        for f in facts:
            t, a = f["t"], f["a"]
            A, Aj = a.ref()
            if t == "home":
                q(1, f, f"Where did {A} live?", f"{Aj}はどこに住んでいましたか？", "home",
                  self.options_from(f["place"], self.story_ents(lambda e: e.kind == "place"),
                                    list(E.PLACES.values()), k))
            elif t in ("find", "wear"):
                obj, color = f["obj"], f["color"]
                pool = [e for e in E.THINGS.values() if "instrument" not in e.tags]
                if t == "wear":
                    pool = [e for e in E.THINGS.values() if "wearable" in e.tags]
                same = by[(t, a)]
                if len(same) == 1:
                    if t == "find":
                        q(1, f, f"What did {A} find?", f"{Aj}は何を見つけましたか？", "find_what",
                          self.options_from(obj, things(), pool, k))
                    else:
                        q(1, f, f"What did {A} put on?", f"{Aj}が身につけたものは何ですか？", "wear_what",
                          self.options_from(obj, things(), pool, min(k, len(pool))))
                elif t == "find" and same[0] is f:
                    q(3, f, f"What did {A} find first?", f"{Aj}が最初に見つけたものは何ですか？", "find_first",
                      self.options_from(obj, [x["obj"] for x in same] + things(), pool, k))
                verb = ("found", "見つけた") if t == "find" else ("put on", "身につけた")
                q(1, f, f"Who {verb[0]} the {obj.noun}?", f"{obj.ja}を{verb[1]}のはだれですか？", f"{t}_who",
                  self.actor_opts(a, k))
                if color:
                    names = sorted(E.COLOR_NAMES)
                    others = [c for c in names if c != color]
                    self.rng.shuffle(others)
                    opts = [self.opt(obj, color)] + [self.opt(obj, c) for c in others[: min(k, 6) - 1]]
                    q(2, f, f"What color was the {obj.noun} that {A} {verb[0]}?",
                      f"{Aj}が{verb[1]}{obj.ja}は何色でしたか？", "color", self.finish(opts))
            elif t == "go":
                same = by[(t, a)]
                pl = f["place"]
                places = self.story_ents(lambda e: e.kind == "place")
                if len(same) == 1:
                    q(1, f, f"Where did {A} go?", f"{Aj}はどこへ行きましたか？", "go_where",
                      self.options_from(pl, places, list(E.PLACES.values()), k))
                elif same[0] is f:
                    q(3, f, f"Where did {A} go first?", f"{Aj}が最初に行った場所はどこですか？", "go_first",
                      self.options_from(pl, places, list(E.PLACES.values()), k))
                elif same[-1] is f:
                    q(3, f, f"Where did {A} go last?", f"{Aj}が最後に行った場所はどこですか？", "go_last",
                      self.options_from(pl, places, list(E.PLACES.values()), k))
                if len(goers[pl.id]) == 1 and pl.id not in self.homes:
                    q(1, f, f"Who went to {pl.en}?", f"{pl.ja}へ行ったのはだれですか？", "go_who",
                      self.actor_opts(a, k))
            elif t == "with":
                pl = f["place"]
                q(3, f, f"Who went to {pl.en} with {A}?", f"{Aj}といっしょに{pl.ja}へ行ったのはだれですか？",
                  "with_who", self.actor_opts(f["b"], k))
            elif t == "meet":
                pl = f["place"]
                if len(meet_at[(a, pl.id)]) == 1:
                    q(2, f, f"Who did {A} meet {pl.at_en if pl.at_en != 'near' else 'at'} {pl.en}?",
                      f"{Aj}が{pl.ja}で会ったのはだれですか？", "meet_who", self.actor_opts(f["b"], k))
            elif t == "give":
                obj, b = f["obj"], f["b"]
                B, Bj = b.ref()
                q(2, f, f"Who did {A} give the {obj.noun} to?", f"{Aj}は{obj.ja}をだれにあげましたか？", "give_who",
                  self.actor_opts(b, k))
                if sum(1 for g in facts if g["t"] == "give" and g["a"] is a and g["b"] is b) == 1:
                    q(2, f, f"What did {A} give to {B}?", f"{Aj}は{Bj}に何をあげましたか？", "give_what",
                      self.options_from(obj, things(), [e for e in E.THINGS.values()
                                                        if "instrument" not in e.tags], k))
            elif t == "eat":
                food, n = f["obj"], f["n"]
                foods = self.story_ents(lambda e: e.kind == "food")
                if len(by[(t, a)]) == 1:
                    q(1, f, f"What did {A} eat?", f"{Aj}は何を食べましたか？", "eat_what",
                      self.options_from(food, foods, list(E.FOODS.values()), k))
                q(1, f, f"Who ate the {food.en_pl}?", f"{food.ja}を食べたのはだれですか？", "eat_who",
                  self.actor_opts(a, k))
                if self.p["counts"]:
                    near = [c for c in range(1, 9) if c != n]
                    near.sort(key=lambda c: (abs(c - n), self.rng.random()))
                    counts = near[: min(k, 5) - 1]
                    opts = [self.opt(food, count=n)] + [self.opt(food, count=c) for c in counts]
                    q(2, f, f"How many {food.en_pl} did {A} eat?", f"{Aj}は{food.ja}をいくつ食べましたか？",
                      "eat_count", self.finish(opts))
            elif t == "play":
                inst = f["obj"]
                pool = [e for e in E.THINGS.values() if "instrument" in e.tags]
                filler = [e for e in E.THINGS.values() if "instrument" not in e.tags]
                self.rng.shuffle(filler)
                q(1, f, f"What did {A} play?", f"{Aj}がえんそうしたのは何ですか？", "play_what",
                  self.options_from(inst, pool, pool + filler, k))
                q(1, f, f"Who played the {inst.en}?", f"{inst.ja}をえんそうしたのはだれですか？", "play_who",
                  self.actor_opts(a, k))
            if (t == "home" and a.name) or (t == "meet" and f["b"].name):
                who = a if t == "home" else f["b"]
                q(2, f, f"Which picture shows {who.name[0]}?", f"{who.name[1]}はどれですか？", "name",
                  self.actor_opts(who, k))
        # One that was never mentioned anywhere in the story
        mentioned = [E.ALL[m] for m in sorted(self.mentions) if m in E.ALL]
        unmentioned = [e for e in E.ALL.values() if e.id not in self.mentions]
        if len(mentioned) >= k - 1 and unmentioned:
            ans = self.rng.choice(unmentioned)
            picks = self.rng.sample(mentioned, k - 1)
            opts = [self.opt(ans)] + [self.opt(e) for e in picks]
            out.append((3, len(self.blocks), "not_in",
                        Question("Which one was NOT in the story?", "お話に出てこなかったのはどれですか？", "not_in",
                                 *self.finish(opts))))
        return out

    def choose(self):
        tiers = self.p["tiers"]
        cands = [c for c in self.candidates() if tiers.get(c[0], 0) > 0]
        chosen, used_blocks, used_kinds = [], set(), set()
        rng = self.rng
        while cands and len(chosen) < 3:
            weights = [tiers[c[0]] * KIND_WEIGHT.get(c[2], 1.0) * (0.35 if c[2] in used_kinds else 1.0)
                       for c in cands]
            c = rng.choices(cands, weights)[0]
            cands = [x for x in cands if x is not c and x[1] != c[1]]
            if c[1] in used_blocks:
                continue
            used_blocks.add(c[1])
            used_kinds.add(c[2])
            chosen.append(c)
        if len(chosen) < 3:
            return None
        if not self.p["shuffle"]:
            chosen.sort(key=lambda c: c[1])
        else:
            rng.shuffle(chosen)
        return [c[3] for c in chosen]

    def title(self):
        a = self.actors[0]
        A, Aj = a.ref()
        main = next((f for f in self.facts if f["t"] in ("find", "wear", "play", "eat")), None)
        if not main:
            pl = next(f["place"] for f in self.facts if f["t"] == "home")
            return title_case(f"{A} of {pl.en}"), f"{pl.ja}の{Aj}"
        obj = main["obj"]
        noun = obj.en_pl if main["t"] == "eat" else obj.noun
        return title_case(f"{A} and the {noun}"), f"{Aj}と{obj.ja}"


def _paragraphs(blocks, size):
    paras, cur = [], []
    for b in blocks:
        cur.extend(b["sents"])
        if len(cur) >= size and b["kind"] != "intro":
            paras.append(cur)
            cur = []
    if cur:
        if paras and len(cur) == 1:
            paras[-1].extend(cur)
        else:
            paras.append(cur)
    return paras


def generate(difficulty, level, rng=None, seen=None, tries=300):
    """Make a new story. `seen` is a set of signatures that must not repeat."""
    rng = rng or random.Random()
    seen = seen if seen is not None else set()
    for _ in range(tries):
        b = Builder(rng, difficulty, level)
        b.build()
        questions = b.choose()
        if not questions:
            continue
        sig_text = "|".join(x["sig"] for x in b.blocks if x["sig"] not in ("f", "e"))
        sig_text += "|" + ",".join(a.name[0] if a.name else "-" for a in b.actors)
        signature = hashlib.sha1(sig_text.encode()).hexdigest()[:16]
        if signature in seen:
            continue
        seen.add(signature)
        size = 3 if difficulty == "easy" else 4
        paras = _paragraphs(b.blocks, size)
        title_en, title_ja = b.title()
        words = sum(len(en.split()) for para in paras for en, _ in para)
        return Story(difficulty, level, title_en, title_ja, paras, questions, signature, words, set(b.mentions))
    raise RuntimeError("could not make a new story")
