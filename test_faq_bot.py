import tempfile
import unittest
from pathlib import Path

from faq_bot import FAQEntry, UNKNOWN_ANSWER, answer_question, load_faq


class FAQBotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.entries = load_faq(Path(__file__).with_name("faq.txt"))

    def test_faq_has_five_pairs(self) -> None:
        self.assertEqual(len(self.entries), 5)

    def test_matches_paraphrased_questions(self) -> None:
        self.assertIn("18:00", answer_question("Во сколько встречаемся?", self.entries))
        self.assertIn("Алиса", answer_question("Кто у нас в команде", self.entries))
        self.assertIn("FAQ-бот", answer_question("Что за трек", self.entries))
        self.assertIn("GitHub", answer_question("Куда сдавать проект", self.entries))
        self.assertIn("призы", answer_question("Что получат победители", self.entries))

    def test_unknown_question(self) -> None:
        self.assertEqual(answer_question("Какая сегодня погода?", self.entries), UNKNOWN_ANSWER)
        self.assertEqual(answer_question("", self.entries), UNKNOWN_ANSWER)

    def test_load_faq_rejects_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.txt"
            path.write_text("# no entries\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_faq(path)

    def test_custom_entry(self) -> None:
        entries = [FAQEntry("Какая у нас команда?", "Команда теста")]
        self.assertEqual(answer_question("Расскажи про команду", entries), "Команда теста")


if __name__ == "__main__":
    unittest.main()
