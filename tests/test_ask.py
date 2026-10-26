from types import SimpleNamespace

from app import ask


def test_print_usage_includes_model_and_token_counts(monkeypatch, capsys):
    monkeypatch.setattr(ask, "MODEL", "gemini-test")
    response = SimpleNamespace(
        usage_metadata=SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=34,
        )
    )

    ask.print_usage(response, 1.25)

    assert capsys.readouterr().out.splitlines() == [
        "[使用モデル] gemini-test",
        "[応答時間] 1.25秒",
        "[トークン数] 入力: 12 / 出力: 34",
    ]


def test_run_conversation_uses_a_new_chat_for_each_question(monkeypatch):
    class Chats:
        def __init__(self):
            self.created = []

        def create(self, model):
            chat = object()
            self.created.append((model, chat))
            return chat

    chats = Chats()
    client = SimpleNamespace(chats=chats)
    initial_chat = object()
    sent = []
    questions = iter(["次の質問", ""])

    monkeypatch.setattr(ask, "ask", lambda chat, question: sent.append((chat, question)))
    monkeypatch.setattr("builtins.input", lambda _: next(questions))

    ask.run_conversation(client, initial_chat, "最初の質問")

    assert sent == [
        (initial_chat, "最初の質問"),
        (chats.created[0][1], "次の質問"),
    ]
