"use client";

import Link from "next/link";
import { getUserId } from "../lib/user";

export default function ReportLink({ id }: { id: number }) {
  return <Link className="primary-link" href={`/report/${id}?user_id=${getUserId()}`}>查看详情</Link>;
}
