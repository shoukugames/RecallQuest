from recallquest.storage import Store


def test_top10_and_history(tmp_path, monkeypatch):
    monkeypatch.setenv("RECALLQUEST_DATA", str(tmp_path))
    st = Store()
    for i in range(12):
        st.add_score(f"P{i}", 1000 * (i + 1), "easy", 3)
    assert len(st.scores) == 10 and st.scores[0]["score"] == 12000
    assert not st.qualifies(1500) and st.qualifies(50000)
    st.add_level({"difficulty": "hard", "level": 4, "read_time": 40, "total_time": 70, "score": 9000,
                  "errors": 1, "first_try": 2, "questions": 3})
    again = Store()
    assert again.summary()["progress"]["hard"] == 4
    assert again.summary()["levels"] == 1
    again.remember("abc")
    assert "abc" in Store().seen
    again.reset()
    assert Store().scores == []


def test_damaged_file_is_set_aside(tmp_path, monkeypatch):
    monkeypatch.setenv("RECALLQUEST_DATA", str(tmp_path))
    (tmp_path / "scores.json").write_text("{not json")
    assert Store().scores == []
    assert (tmp_path / "scores.json.corrupt").exists()
