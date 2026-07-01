import MobileLayout from "../../../components/MobileLayout";
import ReportCard from "../../../components/ReportCard";
import { apiGet } from "../../../lib/api";
import type { ApiEnvelope } from "../../../lib/types";

type ReportPayload = {
  title: string;
  date?: string;
  sections?: { title: string; content: string }[];
};

type ReportDetail = {
  report: {
    id: number;
    title: string;
    report_type: string;
    report_date: string;
  };
  payload: ReportPayload;
};

export default async function ReportDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ user_id?: string }>;
}) {
  const { id } = await params;
  const { user_id } = await searchParams;
  const result = await apiGet<ApiEnvelope<ReportDetail>>(`/api/user/report/${id}?user_id=${user_id || "local_user"}`);
  const payload = result.data.payload;

  return (
    <MobileLayout>
      <h1>{payload.title || result.data.report.title}</h1>
      <ReportCard title="报告信息">
        <p>类型：{result.data.report.report_type}</p>
        <p>日期：{payload.date || result.data.report.report_date}</p>
      </ReportCard>
      {(payload.sections || []).map((section) => (
        <ReportCard key={section.title} title={section.title}>
          <p>{section.content}</p>
        </ReportCard>
      ))}
      <p>{result.risk_notice}</p>
    </MobileLayout>
  );
}
