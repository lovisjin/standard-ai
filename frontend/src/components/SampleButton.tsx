import { Button } from "@/components/ui/button";
import { useState } from "react";

interface SampleButtonProps {
  onClick: () => void;
  isLoading: boolean;
}

export const SampleButton = ({ onClick, isLoading }: SampleButtonProps) => {
  const [hasClicked, setHasClicked] = useState(false);

  const handleClick = () => {
    setHasClicked(true);
    onClick();
  };

  return (
    <div className="text-center space-y-4">
      <Button
        onClick={handleClick}
        disabled={isLoading}
        size="lg"
        className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-8 py-3 rounded-lg shadow-lg transform transition hover:scale-105"
      >
        {isLoading ? (
          <span className="flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            처리 중...
          </span>
        ) : (
          "👀 샘플 데이터로 먼저 체험해보기"
        )}
      </Button>
      {hasClicked && !isLoading && (
        <p className="text-sm text-gray-600">
          * 실제 데이터는 저장되지 않습니다
        </p>
      )}
    </div>
  );
};
