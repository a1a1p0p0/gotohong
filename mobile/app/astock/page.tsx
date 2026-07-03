"use client";

import { useEffect, useState } from "react";
import MobileLayout from "../../components/MobileLayout";
import ReportCard from "../../components/ReportCard";
import { apiGet } from "../../lib/api";
import type { ApiEnvelope } from "../../lib/types";

type BoardItem = {
  board_code: string;
  board_name: string;
  board_type: string;
  category: string;
  subcategory: string;
  main_element: string;
  secondary_element: string;
  confidence: number;
  need_review: string;
};

export default function AstockPage() {
  const [result, setResult] = useState<ApiEnvelope<{ items: BoardItem[]; count: number }> | null>(null);

  useEffect(() => {
    apiGet<ApiEnvelope<{ items: BoardItem[]; count: number }>>("/api/industry/astock-boards")
      .then(setResult)
      .catch(() => setResult(null));
  }, []);

  if (!result) {
    return (
      <MobileLayout>
        <h1>A stock boards</h1>
        <ReportCard title="Loading">
          <p>Loading data...</p>
        </ReportCard>
      </MobileLayout>
    );
  }

  return (
    <MobileLayout>
      <h1>A 股板块五行</h1>
      {result.data.items.map((item) => (
        <ReportCard key={item.board_code} title={item.board_name}>
          <p>类型：{item.board_type}</p>
          <p>主五行：{item.main_element}</p>
          <p>副五行：{item.secondary_element}</p>
          <p>置信度：{item.confidence}</p>
          {item.need_review === "true" && <p>需要人工复核</p>}
        </ReportCard>
      ))}
      <p>{result.risk_notice}</p>
    </MobileLayout>
  );
}
