import argparse
import time

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key


DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def create_chat():
    """クライアントを保持し、設定されたモデルでチャットを作成する。"""
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    return client, chat


def print_usage(response, elapsed_time: float) -> None:
    """使用モデル、応答時間、トークン数を表示する。"""
    usage = response.usage_metadata

    if usage is None:
        input_display = "不明"
        output_display = "不明"
    else:
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count

        input_display = (
            input_tokens if input_tokens is not None else "不明"
        )
        output_display = (
            output_tokens if output_tokens is not None else "不明"
        )

    print(f"[使用モデル] {MODEL}")
    print(f"[応答時間] {elapsed_time:.2f}秒")
    print(f"[トークン数] 入力: {input_display} / 出力: {output_display}")


def ask(chat, question: str) -> None:
    """質問を送り、回答と計測結果を表示する。"""
    start_time = time.perf_counter()

    response = chat.send_message(question)

    elapsed_time = time.perf_counter() - start_time

    print(response.text)
    print_usage(response, elapsed_time)


def run_conversation(client, chat, first_question: str) -> None:
    """質問ごとに新しいchatを使い、会話履歴を引き継がず質問する。"""
    question = first_question

    while True:
        print(f"[質問] {question}\n")

        # 同じchatを毎回渡すため、会話履歴が維持される
        ask(chat, question)

        try:
            question = input(
                "次の質問 (終了するには空行): "
            ).strip()
        except EOFError:
            print()
            break

        if not question:
            break

        chat = client.chats.create(model=MODEL)


def main() -> None:
    """コマンドライン引数を受け取り、会話を開始する。"""
    parser = argparse.ArgumentParser(
        description="素のLLMに質問する"
    )
    parser.add_argument(
        "question",
        nargs="?",
        default=DEFAULT_QUESTION,
    )
    args = parser.parse_args()

    try:
        client, chat = create_chat()
        run_conversation(client, chat, args.question)
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()