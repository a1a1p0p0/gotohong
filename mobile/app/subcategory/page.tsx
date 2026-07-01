"use client";

import { useEffect, useState } from "react";
import MobileLayout from "../../components/MobileLayout";
import ReportCard from "../../components/ReportCard";
import { apiGet, apiPost } from "../../lib/api";
import type { ApiEnvelope } from "../../lib/types";
import { getUserId } from "../../lib/user";
import "./subcategory.css";

type SubcategoryReport = {
  title: string;
  date: string;
  sections: { title: string; content: string }[];
};

type MockOrderData = {
  unlock_code: {
    code: string;
  };
};

type SubcategoryItem = {
  subcategory_id: string;
  subcategory_name: string;
};

export default function SubcategoryPage() {
  const [options, setOptions] = useState<SubcategoryItem[]>([]);
  const [subcategoryId, setSubcategoryId] = useState("tech_semiconductor");
  const [unlockCode, setUnlockCode] = useState("");
  const [message, setMessage] = useState("");
  const [report, setReport] = useState<SubcategoryReport | null>(null);

  async function loadOptions() {
    const result = await apiGet<ApiEnvelope<{ items: SubcategoryItem[] }>>("/api/industry/subcategories");
    setOptions(result.data.items);
    if (result.data.items[0]) setSubcategoryId(result.data.items[0].subcategory_id);
  }

  useEffect(() => {
    loadOptions();
  }, []);

  async function submit() {
    setMessage("正在验证...");
    setReport(null);
    const result = await apiPost<ApiEnvelope<SubcategoryReport>>("/api/paid/subcategory", {
      subcategory_id: subcategoryId,
      date: "2026-06-29",
      user_id: getUserId(),
      unlock_code: unlockCode,
    });

    if (result.code === "PAYWALL_REQUIRED") {
      setMessage(result.paywall?.message || "需要有效解锁码。");
      return;
    }

    setMessage("解锁成功");
    setReport(result.data);
  }

  async function createMockOrder() {
    setMessage("正在生成模拟订单...");
    const result = await apiPost<ApiEnvelope<MockOrderData>>("/api/payment/create_mock_order", {
      access_type: "PAID_SUBCATEGORY_SINGLE",
      target_key: subcategoryId,
      amount: 990,
      payment_channel: "WECHAT",
      max_use_count: 1,
    });
    setUnlockCode(result.data.unlock_code.code);
    setMessage("已生成本地解锁码，可直接生成报告。");
  }

  return (
    <MobileLayout>
      <h1>细分行业付费分析</h1>
      <ReportCard title="半导体">
        <p>选择细分行业，输入本地解锁码，查看完整动能报告。</p>
        <select value={subcategoryId} onChange={(event) => setSubcategoryId(event.target.value)}>
          {options.map((item) => (
            <option key={item.subcategory_id} value={item.subcategory_id}>
              {item.subcategory_name}
            </option>
          ))}
        </select>
        <input value={unlockCode} onChange={(event) => setUnlockCode(event.target.value)} placeholder="输入解锁码" />
        <button className="secondary-button" onClick={createMockOrder}>生成模拟订单</button>
        <button onClick={submit}>生成报告</button>
        {message && <p>{message}</p>}
      </ReportCard>

      {report && (
        <ReportCard title={report.title}>
          <p>日期：{report.date}</p>
          {report.sections.map((section) => (
            <section key={section.title}>
              <h3>{section.title}</h3>
              <p>{section.content}</p>
            </section>
          ))}
        </ReportCard>
      )}
    </MobileLayout>
  );
}
