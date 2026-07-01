import MobileLayout from "../../components/MobileLayout";
import ReportCard from "../../components/ReportCard";
import { apiGet } from "../../lib/api";
import type { ApiEnvelope } from "../../lib/types";

type YearData = {
  title: string;
  period: {
    main_element: string;
    secondary_element: string;
    strength_score: number;
    description: string;
  };
  summary: string;
};

export default async function FreeYearPage() {
  const result = await apiGet<ApiEnvelope<YearData>>("/api/free/year");

  return (
    <MobileLayout>
      <h1>年度免费分析</h1>
      <ReportCard title={result.data.title}>
        <p>主五行：{result.data.period.main_element}</p>
        <p>副五行：{result.data.period.secondary_element}</p>
        <p>强度：{result.data.period.strength_score}</p>
        <p>{result.data.period.description}</p>
      </ReportCard>
      <p>{result.risk_notice}</p>
    </MobileLayout>
  );
}
