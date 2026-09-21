#!/usr/bin/env python3
"""Terminal FAQ bot for the rehearsal."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

UNKNOWN_ANSWER = "Не знаю"
STOP_WORDS = {
    "а", "без", "быть", "в", "во", "для", "до", "за", "и", "из", "как",
    "какая", "какие", "какой", "когда", "кто", "на", "нам", "не", "о", "об",
    "по", "под", "при", "про", "с", "со", "у", "что", "это", "мне", "можно",
    "ли", "есть", "будет", "где", "или", "пожалуйста",
}


@dataclass(frozen=True)
class FAQEntry:
    question: str
    answer: str


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[\w-]+", text.lower(), flags=re.UNICODE)
    return {
        _stem(word.strip("-"))
        for word in words
        if len(word.strip("-")) > 1 and word not in STOP_WORDS
    }


def _stem(word: str) -> str:
    """Small suffix normalizer, enough to compare common Russian inflections."""
    for suffix in ("иями", "ами", "ями", "ого", "ему", "ому", "ами", "ями", "ах", "ях", "ом", "ем", "ов", "ев", "ам", "ям", "ую", "юю", "ой", "ей", "ые", "ие", "ой", "ей", "у", "ю", "а", "я", "ы", "и", "е", "о"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word


def load_faq(path: str | Path) -> list[FAQEntry]:
    """Load FAQ entries from blocks with ``Q:`` and ``A:`` lines."""
    entries: list[FAQEntry] = []
    question: str | None = None
    answer: str | None = None
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("Q:"):
            if question is not None and answer is not None:
                entries.append(FAQEntry(question, answer))
            question, answer = line[2:].strip(), None
        elif line.startswith("A:") and question is not None:
            answer = line[2:].strip()
    if question is not None and answer is not None:
        entries.append(FAQEntry(question, answer))
    if not entries:
        raise ValueError(f"В файле {path} не найдено ни одной пары Q/A")
    return entries


def _score(query: str, question: str) -> float:
    query_tokens = _tokens(query)
    question_tokens = _tokens(question)
    if not query_tokens or not question_tokens:
        return 0.0
    overlap = query_tokens & question_tokens
    keyword_score = len(overlap) / len(query_tokens)
    fuzzy_score = difflib.SequenceMatcher(
        None, " ".join(sorted(query_tokens)), " ".join(sorted(question_tokens))
    ).ratio()
    return 0.8 * keyword_score + 0.2 * fuzzy_score


def answer_question(query: str, entries: Iterable[FAQEntry], threshold: float = 0.38) -> str:
    """Find the closest FAQ answer or return ``Не знаю``."""
    query = query.strip()
    if not query:
        return UNKNOWN_ANSWER
    ranked = sorted(
        ((_score(query, entry.question), entry) for entry in entries),
        key=lambda item: item[0],
        reverse=True,
    )
    if not ranked or ranked[0][0] < threshold:
        return UNKNOWN_ANSWER
    return ranked[0][1].answer


def main() -> None:
    entries = load_faq(Path(__file__).with_name("faq.txt"))
    print("FAQ-бот репетиции. Задайте вопрос или введите «выход».")
    while True:
        try:
            query = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.strip().lower() in {"выход", "exit", "quit"}:
            break
        print(answer_question(query, entries))


if __name__ == "__main__":
    main()
