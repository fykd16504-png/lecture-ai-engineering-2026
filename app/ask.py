"""第1回: 素のLLMと会話履歴を保って質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 講座に固有の質問から会話を始める

ツールは使わず、同じチャットで会話履歴を保つ「素の」呼び出し。
回答のあとに質問を続けられ、空行を入力すると終了する。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat, question: str) -> None:
    response = chat.send_message(question)
    print(response.text)

    # prompt_token_count は入力、candidates_token_count は生成した回答のトークン数。
    # 利用量情報や個々の数値がない場合もあるため、そのときは「不明」と表示する。
    usage = response.usage_metadata
    if usage is None:
        print("[トークン数] 入力: 不明 / 出力: 不明")
    else:
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count
        input_display = input_tokens if input_tokens is not None else "不明"
        output_display = output_tokens if output_tokens is not None else "不明"
        print(f"[トークン数] 入力: {input_display} / 出力: {output_display}")


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)
        question = args.question
        while True:
            print(f"[質問] {question}\n")
            ask(chat, question)
            try:
                question = input("次の質問 (終了するには空行): ").strip()
            except EOFError:
                print()
                break
            if not question:
                break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
