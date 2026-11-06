import random

import pytest

from recallquest import entities as E
from recallquest import story


@pytest.mark.parametrize("difficulty", story.DIFFICULTIES)
def test_every_level_makes_valid_bilingual_stories(difficulty):
    rng = random.Random(difficulty)
    for level in range(1, story.LEVELS + 1):
        for _ in range(40):
            s = story.generate(difficulty, level, rng)
            en, ja = " ".join(s.text("en")), "".join(s.text("ja"))
            assert en and ja and "{" not in en + ja and "}" not in en + ja
            assert s.title_en and s.title_ja
            assert len(s.questions) == 3
            for q in s.questions:
                keys = [o.key() for o in q.options]
                assert len(keys) == len(set(keys)), q.en
                assert 0 <= q.answer < len(q.options)
                assert q.en.endswith("?") and q.ja.endswith("？")
                for o in q.options:
                    assert o.art in E.ALL


def test_stories_grow_with_level_and_difficulty():
    rng = random.Random(1)

    def avg(d, lv):
        return sum(story.generate(d, lv, rng).words for _ in range(60)) / 60

    assert avg("easy", 1) < avg("easy", 10) < avg("hard", 10)
    assert avg("medium", 1) < avg("medium", 10)
    assert avg("hard", 1) < avg("hard", 10)


def test_no_story_repeats():
    rng = random.Random(9)
    seen = set()
    for i in range(1500):
        story.generate(story.DIFFICULTIES[i % 3], i % 10 + 1, rng, seen)
    assert len(seen) == 1500


def test_not_in_story_answer_is_really_absent():
    rng = random.Random(3)
    for _ in range(400):
        s = story.generate("hard", rng.randint(1, 10), rng)
        for q in s.questions:
            if q.kind == "not_in":
                assert q.options[q.answer].art not in s.mentions
                assert all(o.art in s.mentions for i, o in enumerate(q.options) if i != q.answer)


def test_hard_uses_six_pictures_easy_starts_with_three():
    rng = random.Random(4)
    assert all(len(q.options) == 3 for q in story.generate("easy", 1, rng).questions)
    assert all(len(q.options) in (5, 6) for q in story.generate("hard", 5, rng).questions)
