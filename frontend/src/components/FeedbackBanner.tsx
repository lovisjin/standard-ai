import { useState } from "react";

interface FeedbackBannerProps {
  onFeedback: (isPositive: boolean, text?: string) => Promise<void>;
}

export const FeedbackBanner = ({ onFeedback }: FeedbackBannerProps) => {
  const [showTextInput, setShowTextInput] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleFeedback = async (isPositive: boolean) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      await onFeedback(isPositive, feedbackText);
      setIsSubmitted(true);
      setShowTextInput(false);
    } catch (error) {
      console.error("피드백 제출 실패:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center justify-center space-x-2">
        <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
        </svg>
        <span className="text-green-700">피드백이 기록되었습니다!</span>
      </div>
    );
  }

  return (
    <div className="bg-white border rounded-lg p-4 space-y-4">
      <p className="text-center text-gray-700">이 요약이 도움이 되었나요?</p>
      
      <div className="flex justify-center space-x-4">
        <button
          onClick={() => handleFeedback(true)}
          disabled={isSubmitting}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg border hover:bg-gray-50 transition-colors"
        >
          <span className="text-2xl">👍</span>
          <span>좋아요</span>
        </button>
        
        <button
          onClick={() => handleFeedback(false)}
          disabled={isSubmitting}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg border hover:bg-gray-50 transition-colors"
        >
          <span className="text-2xl">👎</span>
          <span>아쉬워요</span>
        </button>
      </div>

      {showTextInput && (
        <div className="space-y-2">
          <textarea
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="피드백을 남겨주세요 (선택사항)"
            className="w-full p-2 border rounded-lg resize-none h-24"
            disabled={isSubmitting}
          />
        </div>
      )}

      {isSubmitting && (
        <div className="text-center text-sm text-gray-500">
          피드백 처리 중...
        </div>
      )}
    </div>
  );
};
