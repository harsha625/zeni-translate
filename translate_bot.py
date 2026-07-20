"""English to Telugu Translation Bot in Python (Zeni Translate Bot).

Requirements:
    pip install googletrans==4.0.0rc1

Usage:
    1. Interactive Mode:
       python translate_bot.py

    2. Direct Translation Mode:
       python translate_bot.py "Hello, how are you?"
"""

from __future__ import annotations
import sys
import os

# Fix standard output encoding for Windows terminals printing Telugu characters
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from googletrans import Translator
except ImportError:
    print(
        "Missing dependency: googletrans.\n"
        "Please install it using:\n"
        "    pip install googletrans==4.0.0rc1",
        file=sys.stderr,
    )
    sys.exit(1)


class EnglishToTeluguBot:
    """Zeni Translation Bot for translating English text into Telugu."""

    def __init__(self) -> None:
        self.translator = Translator()

    def translate(self, text: str) -> str:
        """Translates an English string into Telugu.

        Args:
            text: The English input string.

        Returns:
            The translated Telugu string.
        """
        if not text or not text.strip():
            return ""

        # Translate from English (src='en') to Telugu (dest='te')
        result = self.translator.translate(text.strip(), src="en", dest="te")
        return result.text


def translate_english_to_telugu(text: str) -> str:
    """Convenience function to translate English text to Telugu."""
    bot = EnglishToTeluguBot()
    return bot.translate(text)


def run_interactive_mode(bot: EnglishToTeluguBot) -> None:
    """Runs the interactive translation bot loop."""
    print("=========================================================")
    print("  ✨ ZENI TRANSLATE - English to Telugu Bot ✨")
    print("=========================================================")
    print("Zeni Bot: 'Welcome! Type an English phrase to translate into Telugu.'")
    print("Type 'exit', 'quit', or 'bye' to exit.\n")

    while True:
        try:
            user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nZeni Bot: Thank you for using Zeni Translate! Goodbye! (సెలవు!)")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Zeni Bot: Thank you for using Zeni Translate! Goodbye! (సెలవు!)")
            break

        try:
            telugu_text = bot.translate(user_input)
            print(f"Zeni Translation > {telugu_text}\n")
        except Exception as error:
            print(f"Translation Error: {error}", file=sys.stderr)
            print("Please check your internet connection.\n")


def main() -> None:
    bot = EnglishToTeluguBot()

    # If arguments are passed from CLI (e.g. python translate_bot.py "Hello world")
    if len(sys.argv) > 1:
        text_to_translate = " ".join(sys.argv[1:])
        try:
            telugu_translation = bot.translate(text_to_translate)
            print(f"Input:  {text_to_translate}")
            print(f"Zeni Telugu Translation: {telugu_translation}")
        except Exception as error:
            print(f"Translation Error: {error}", file=sys.stderr)
            sys.exit(1)
    else:
        # Otherwise start interactive CLI bot
        run_interactive_mode(bot)


if __name__ == "__main__":
    main()


