import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { postSummary } from "@/utils/api";

export default function Summarizer() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSummarize = async () => {
    if (!text.trim()) {
      setError("요약할 텍스트를 입력해주세요.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await postSummary(text);
      setSummary(result.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "요약 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">텍스트 요약</h1>
      
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              요약할 텍스트
            </label>
            <textarea
              className="w-full h-40 px-3 py-2 border rounded-md"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="요약할 텍스트를 입력하세요..."
            />
          </div>

          <Button
            onClick={handleSummarize}
            disabled={loading}
            className="w-full"
          >
            {loading ? "요약 중..." : "요약 실행"}
          </Button>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded-lg">
              {error}
            </div>
          )}

          {summary && (
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">요약 결과</h3>
              <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap">
                {summary}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
