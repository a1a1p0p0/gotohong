import MobileLayout from "../../components/MobileLayout";
import ReportCard from "../../components/ReportCard";
import { apiGet } from "../../lib/api";
import type { ApiEnvelope } from "../../lib/types";

type Category = {
  category_id: string;
  category_name: string;
  main_element: string;
  secondary_element: string;
  free_description?: string;
  paid_hint?: string;
};

type CategoriesData = {
  title: string;
  items: Category[];
  paid_hint: string;
};

export default async function CategoriesPage() {
  const result = await apiGet<ApiEnvelope<CategoriesData>>("/api/free/categories");

  return (
    <MobileLayout>
      <h1>行业大类</h1>
      {result.data.items.map((item) => (
        <ReportCard key={item.category_id} title={item.category_name}>
          <p>主五行：{item.main_element}</p>
          <p>副五行：{item.secondary_element}</p>
          <p>{item.free_description}</p>
          <p>{item.paid_hint || result.data.paid_hint}</p>
        </ReportCard>
      ))}
      <p>{result.risk_notice}</p>
    </MobileLayout>
  );
}
