"use client";

import { useEffect, useState } from "react";
import MobileLayout from "../../components/MobileLayout";
import ReportCard from "../../components/ReportCard";
import ReportLink from "../../components/ReportLink";
import { apiGet } from "../../lib/api";
import type { ApiEnvelope } from "../../lib/types";
import { getUserId } from "../../lib/user";

type ReportItem = {
  id: number;
  report_type: string;
  target_key: string;
  title: string;
  report_date: string;
  created_at: string;
};

type ReportsData = {
  items: ReportItem[];
  count: number;
};

export default function UserPage() {
  const [items, setItems] = useState<ReportItem[]>([]);
  const [userId, setUserId] = useState("");

  useEffect(() => {
    const currentUserId = getUserId();
    setUserId(currentUserId);
    apiGet<ApiEnvelope<ReportsData>>(`/api/user/reports?user_id=${currentUserId}`).then((result) => {
      setItems(result.data.items);
    });
  }, []);

  return (
    <MobileLayout>
      <h1>用户历史</h1>
      <p>用户：{userId}</p>
      {items.length === 0 ? (
        <ReportCard title="暂无报告">
          <p>生成付费报告后，会在这里显示历史记录。</p>
        </ReportCard>
      ) : (
        items.map((item) => (
          <ReportCard key={item.id} title={item.title || item.report_type}>
            <p>类型：{item.report_type}</p>
            <p>日期：{item.report_date || item.created_at}</p>
            <p>对象：{item.target_key}</p>
            <ReportLink id={item.id} />
          </ReportCard>
        ))
      )}
    </MobileLayout>
  );
}
