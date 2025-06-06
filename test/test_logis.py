import pytest
from skills.logis_summarizer import call_gpt_summary, execute
from utils.sheet import save_to_sheet
from utils.slack import send_slack_notification

@pytest.fixture
def dummy_text():
    return "테스트를 위한 샘플 텍스트입니다."

def test_call_gpt_summary(monkeypatch, dummy_text):
    # GPT API 모킹: 실제 API 호출 없이 예측된 값 반환
    class DummyResponse:
        class Choice:
            def __init__(self, content):
                self.message = type("M", (), {"content": content})
        choices = [Choice("샘플 요약")]

    monkeypatch.setattr("openai.ChatCompletion.create", lambda **kwargs: DummyResponse())
    summary = call_gpt_summary(dummy_text)
    assert summary == "샘플 요약"

def test_save_to_sheet(monkeypatch, tmp_path, dummy_text):
    # gspread 모킹: 실제 API 호출 없이 예측된 시트 URL 반환
    class DummySheet:
        def __init__(self):
            self.url = "https://docs.google.com/dummy"
        def share(self, *args, **kwargs): pass
        def get_worksheet(self, idx): return None
        def add_worksheet(self, *args, **kwargs): return self
        def row_values(self, row): return []
        def append_row(self, row): pass

    class DummyClient:
        def __init__(self): pass
        def open_by_key(self, key): return DummySheet()
        def create(self, name): return DummySheet()

    monkeypatch.setattr("gspread.authorize", lambda creds: DummyClient())
    sheet_url = save_to_sheet("user1", dummy_text, "요약 결과")
    assert sheet_url.startswith("https://docs.google.com/")

def test_send_slack_notification(monkeypatch, dummy_text):
    # requests.post 모킹: 원하는 상태 코드로 응답
    class DummyResponse:
        status_code = 200
        text = ""
    monkeypatch.setattr("requests.post", lambda url, data, headers: DummyResponse())
    # 실제로 예외가 발생하지 않아야 함
    send_slack_notification("user1", "테스트 요약")

def test_execute_endpoint(client, monkeypatch, dummy_text):
    # FastAPI TestClient 사용 예시
    from fastapi.testclient import TestClient
    from api.main import app

    monkeypatch.setattr("skills.logis_summarizer.execute", lambda uid, txt: {"summary": "샘플", "sheet_url": "url"})
    test_client = TestClient(app)
    response = test_client.post("/execute", json={"skill":"logis_summarizer","user_id":"user1","text":dummy_text})
    assert response.status_code == 200
    assert response.json()["summary"] == "샘플"
    assert response.json()["sheet_url"] == "url"
