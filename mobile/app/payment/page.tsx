"use client";

import { useState } from "react";
import MobileLayout from "../../components/MobileLayout";
import ReportCard from "../../components/ReportCard";
import { apiPost } from "../../lib/api";
import type { ApiEnvelope } from "../../lib/types";
import "./payment.css";

type MockOrderData = {
  order: { order_no: string; status: string };
  unlock_code: { code: string; access_type: string; target_key: string };
};

export default function PaymentPage() {
  const [unlockCode, setUnlockCode] = useState("");
  const [message, setMessage] = useState("");

  async function confirmLocalPayment() {
    const result = await apiPost<ApiEnvelope<MockOrderData>>("/api/payment/create_mock_order", {
      access_type: "PAID_SUBCATEGORY_SINGLE",
      target_key: "tech_semiconductor",
      amount: 990,
      payment_channel: "WECHAT",
      max_use_count: 1,
    });
    setUnlockCode(result.data.unlock_code.code);
    setMessage("本地解锁码已生成。");
  }

  return (
    <MobileLayout>
      <h1>微信扫码支付</h1>
      <ReportCard title="商家收款码">
        <img className="payment-qr" src="/payments/wechat-merchant-qr.png" alt="微信商家收款码" />
        <p>扫码付款后，点击下方按钮生成本地解锁码。</p>
        <button onClick={confirmLocalPayment}>我已支付，生成解锁码</button>
        {message && <p>{message}</p>}
        {unlockCode && <input readOnly value={unlockCode} />}
      </ReportCard>
    </MobileLayout>
  );
}
