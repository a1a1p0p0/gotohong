"use client";

import { useEffect, useState } from "react";
import MobileLayout from "../../components/MobileLayout";
import ReportCard from "../../components/ReportCard";
import { apiPost } from "../../lib/api";
import type { ApiEnvelope } from "../../lib/types";
import { getUserId } from "../../lib/user";

function getTodayText() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

type RankingItem = {
  rank: number;
  industry_name: string;
  main_element: string;
  secondary_element: string;
  score: number;
  reason: string;
};

type RankingData = {
  preview_items?: RankingItem[];
  items?: RankingItem[];
  visible_count?: number;
  locked_count?: number;
};

export default function RankingPage() {
  const [periodType, setPeriodType] = useState("day");
  const [rankingType, setRankingType] = useState("favorable");
  const [unlockCode, setUnlockCode] = useState("");
  const [message, setMessage] = useState("");
  const [items, setItems] = useState<RankingItem[]>([]);
  const [lockedCount, setLockedCount] = useState(0);

  useEffect(() => {
    loadRanking("");
  }, [periodType, rankingType]);

  async function loadRanking(code: string) {
    const today = getTodayText();
    const result = await apiPost<ApiEnvelope<RankingData>>("/api/paid/ranking", {
      period_type: periodType,
      ranking_type: rankingType,
      date: today,
      user_id: getUserId(),
      unlock_code: code,
    });

    if (result.code === "PAYWALL_REQUIRED") {
      setItems(result.data.preview_items || []);
      setLockedCount(result.data.locked_count || 0);
      setMessage(result.paywall?.message || "解锁后查看 TOP 5。");
      return;
    }

    setItems(result.data.items || []);
    setLockedCount(0);
    setMessage("已解锁 TOP 5");
  }

  async function createMockOrder() {
    const today = getTodayText();
    const accessTypeMap: Record<string, string> = {
      month: "PAID_MONTH_RANKING",
      week: "PAID_WEEK_RANKING",
      day: "PAID_DAY_RANKING",
    };
    const result = await apiPost<ApiEnvelope<{ unlock_code: { code: string } }>>("/api/payment/create_mock_order", {
      access_type: accessTypeMap[periodType],
      target_key: `${periodType}:${rankingType}:${today}`,
      amount: 990,
      payment_channel: "WECHAT",
      max_use_count: 1,
    });
    setUnlockCode(result.data.unlock_code.code);
    setMessage("已生成本地解锁码。");
  }

  return (
    <MobileLayout>
      <h1>行业方案</h1>
      <ReportCard title="Daily ranking">
        <select value={periodType} onChange={(event) => setPeriodType(event.target.value)}>
          <option value="month">当月</option>
          <option value="week">当周</option>
          <option value="day">当日</option>
        </select>
        <select value={rankingType} onChange={(event) => setRankingType(event.target.value)}>
          <option value="favorable">最有利</option>
          <option value="balanced">最平衡</option>
        </select>
        <input value={unlockCode} onChange={(event) => setUnlockCode(event.target.value)} placeholder="输入解锁码" />
        <button onClick={createMockOrder}>生成模拟订单</button>
        <button onClick={() => loadRanking(unlockCode)}>查看 TOP 5</button>
        {message && <p>{message}</p>}
        {lockedCount > 0 && <p>还有 {lockedCount} 个行业待解锁。</p>}
      </ReportCard>

      {items.map((item) => (
        <ReportCard key={item.rank} title={`${item.rank}. ${item.industry_name}`}>
          <p>主五行：{item.main_element}</p>
          <p>副五行：{item.secondary_element}</p>
          <p>分数：{item.score}</p>
          <p>{item.reason}</p>
        </ReportCard>
      ))}
    </MobileLayout>
  );
}
