from regex_explainer.core import analyze_regex, explain_regex, tokenize


def test_tokenize_simple():
    tokens = tokenize(r"^ab+c$")
    assert tokens[0].value == "^"
    assert tokens[1].value == "a"
    assert tokens[2].value == "b"
    assert tokens[2].quantifier == "+"


def test_explain_has_lines():
    lines = explain_regex(r"[A-Z]+\d{2,4}")
    assert any("Character class" in line for line in lines)


def test_warnings():
    warnings = analyze_regex("hello.*world")
    codes = {w.code for w in warnings}
    assert "missing_start_anchor" in codes
    assert "missing_end_anchor" in codes
    assert "greedy_dot" in codes
