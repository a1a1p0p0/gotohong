import Link from "next/link";
import MobileLayout from "../components/MobileLayout";
import ReportCard from "../components/ReportCard";
import { apiGet } from "../lib/api";
import type { ApiEnvelope } from "../lib/types";
import "./home.css";

type WeekData = {
  period: {
    main_element: string;
    secondary_element: string;
    strength_score: number;
    description: string;
  };
};

type PeriodData = {
  period: {
    main_element: string;
    secondary_element: string;
    strength_score: number;
    description: string;
  };
};

export default async function HomePage() {
  const year = await apiGet<ApiEnvelope<PeriodData>>("/api/free/year");
  const month = await apiGet<ApiEnvelope<PeriodData>>("/api/free/period?period_type=month");
  const day = await apiGet<ApiEnvelope<PeriodData>>("/api/free/period?period_type=day");
  const week = await apiGet<ApiEnvelope<WeekData>>("/api/free/week");

  return (
    <MobileLayout>
      <header className="hero">
        <p>今日先看动能，再看行业</p>
        <h1>五行行业动能</h1>
      </header>

      <ReportCard title="当前时间五行">
        <div className="period-grid">
          <span>今年：{year.data.period.main_element} / {year.data.period.secondary_element}</span>
          <span>当月：{month.data.period.main_element} / {month.data.period.secondary_element}</span>
          <span>当日：{day.data.period.main_element} / {day.data.period.secondary_element}</span>
        </div>
      </ReportCard>

      <ReportCard title="?? / ????">
        <div className="momentum-split">
          <section>
            <strong>????</strong>
            <span>??{week.data.period.main_element}</span>
            <span>??{week.data.period.secondary_element}</span>
          </section>
          <section>
            <strong>????</strong>
            <span>??{day.data.period.main_element}</span>
            <span>??{day.data.period.secondary_element}</span>
          </section>
        </div>
        <p>{week.data.period.description}</p>
      </ReportCard>

      <div className="action-grid">
        <Link href="/free-year">年度免费分析</Link>
        <Link href="/free-week">本周免费分析</Link>
        <Link href="/categories">行业大类免费</Link>
        <Link href="/ranking">行业方案</Link>
      </div>

      <ReportCard title="付费入口">
        <p>解锁每日、细分行业和 TOP 5 方案。内容只做动能观察，不提供投资建议。</p>
        <Link className="primary-link" href="/payment">微信扫码支付</Link>
        <Link className="primary-link" href="/subcategory">解锁细分行业</Link>
      </ReportCard>
    </MobileLayout>
  );
}
