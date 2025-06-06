import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { SampleButton } from "./SampleButton";

interface FeedbackStats {
  total_feedbacks: number;
  positive_rate: number;
  negative_rate: number;
  recent_comments: Array<{
    text: string;
    is_positive: boolean;
    created_at: string;
  }>;
  start_date: string;
  end_date: string;
}

const API_URL = import.meta.env.VITE_API_URL || "";

const Dashboard = () => {
  const [startDate, setStartDate] = useState(
    format(new Date().setDate(new Date().getDate() - 30), "yyyy-MM-dd")
  );
  const [endDate, setEndDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [data, setData] = useState<FeedbackStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showSampleData, setShowSampleData] = useState(true);  // 초기 방문 시 샘플 데이터 표시

  const handleFetchClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    fetchStats();
  };

  const fetchStats = async (useSampleData: boolean = false) => {
    setLoading(true);
    setError("");
    try {
      const endpoint = useSampleData ? "/feedback/sample" :
        `/feedback/stats?${new URLSearchParams({
          start_date: startDate,
          end_date: endDate
        })}`;
        
      const res = await fetch(`${API_URL}${endpoint}`);
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "데이터를 불러오지 못했습니다.");
      }
      
      const result = await res.json();
      setData(result);
      
      if (useSampleData) {
        setShowSampleData(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.");
    }
    setLoading(false);
  };

  // 컴포넌트 마운트 시 초기 데이터 로드
  useEffect(() => {
    if (showSampleData) {
      fetchStats(true);
    } else {
      fetchStats(false);
    }
  }, []); // 컴포넌트 마운트 시 초기 데이터 로드

  const chartData = data ? [
    { 
      name: "긍정", 
      value: Math.round(data.positive_rate * 100),
      color: "#4ade80"
    },
    { 
      name: "부정", 
      value: Math.round(data.negative_rate * 100),
      color: "#f87171"
    }
  ] : [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold mb-6">피드백 통계 대시보드</h1>

      <div className="space-y-6">
        {showSampleData ? (
          <div className="text-center space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                👋 STANDARD-AI를 시작해보세요!
              </h3>
              <p className="text-blue-600 mb-4">
                샘플 데이터로 먼저 체험해보세요. <br />
                실제 사용 시에는 자동으로 기록이 누적됩니다.
              </p>
              <SampleButton
                onClick={() => {
                  setShowSampleData(false);
                  fetchStats();
                }}
                isLoading={loading}
              />
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-4 bg-white p-4 rounded-lg shadow">
            <div className="flex flex-col">
              <label className="text-sm text-gray-600">시작일</label>
              <Input 
                type="date" 
                value={startDate} 
                onChange={(e) => setStartDate(e.target.value)}
                className="w-40"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-sm text-gray-600">종료일</label>
              <Input 
                type="date" 
                value={endDate} 
                onChange={(e) => setEndDate(e.target.value)}
                className="w-40"
              />
            </div>
            <Button 
              onClick={handleFetchClick}
              disabled={loading}
              className="mt-6"
            >
              {loading ? "로딩 중..." : "조회"}
            </Button>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded-lg">
          {error}
        </div>
      )}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <h2 className="text-lg font-semibold text-gray-600">총 피드백</h2>
                <p className="text-4xl font-bold mt-2">{data.total_feedbacks}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="col-span-2">
            <CardContent className="pt-6">
              <h2 className="text-lg font-semibold text-gray-600 mb-4">피드백 분포</h2>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, value }) => `${name} ${value}%`}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => `${value}%`}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="col-span-full">
            <CardContent className="pt-6">
              <h2 className="text-lg font-semibold text-gray-600 mb-4">최근 피드백</h2>
              <div className="space-y-3">
                {data.recent_comments.map((item, idx) => (
                  <div 
                    key={idx} 
                    className={`p-3 rounded-lg ${
                      item.is_positive ? "bg-green-50" : "bg-red-50"
                    }`}
                  >
                    <p className="text-sm">{item.text}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {format(new Date(item.created_at), "PPP", { locale: ko })}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
