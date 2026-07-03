import Link from "next/link";
import { notFound } from "next/navigation";
import MobileLayout from "../../../components/MobileLayout";
import { ElementBadge } from "../../../components/ElementBadge";
import { ReportSection } from "../../../components/ReportSection";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { getCategoryById, getSubcategoriesByCategoryId, industryCategoriesMock } from "../../../lib/mock";

export function generateStaticParams() {
  return industryCategoriesMock.map((category) => ({
    categoryId: category.categoryId,
  }));
}

export default async function CategoryDetailPage({
  params,
}: {
  params: Promise<{ categoryId: string }>;
}) {
  const { categoryId } = await params;
  const category = getCategoryById(categoryId);

  if (!category) {
    notFound();
  }

  const subcategories = getSubcategoriesByCategoryId(category.categoryId);

  return (
    <MobileLayout subtitle="免费大类详情" title={category.name}>
      <div className="space-y-4">
        <ReportSection
          title={`${category.name} · 五行属性解析`}
          subtitle="免费开放"
          element={category.mainElement}
          paragraphs={category.freeAnalysis}
        />

        <Card className="bg-card/75">
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <CardTitle>该大类下的细分行业</CardTitle>
              <ElementBadge element={category.secondaryElement} label="付费报告" />
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {subcategories.map((subcategory) => (
              <Link
                key={subcategory.subcategoryId}
                href={`/subcategory/${subcategory.subcategoryId}`}
                className="block rounded-md border border-border bg-muted/35 p-3"
              >
                <span className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold">{subcategory.name}</span>
                  <ElementBadge element={subcategory.mainElement} status="locked" />
                </span>
                <span className="mt-2 block text-xs leading-5 text-muted-foreground">
                  {subcategory.paidSummary}
                </span>
              </Link>
            ))}
          </CardContent>
        </Card>
      </div>
    </MobileLayout>
  );
}
