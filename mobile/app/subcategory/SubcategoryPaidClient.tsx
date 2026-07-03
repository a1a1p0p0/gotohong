"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import MobileLayout from "../../components/MobileLayout";
import { ElementBadge } from "../../components/ElementBadge";
import { PaywallCard } from "../../components/PaywallCard";
import { ReportSection } from "../../components/ReportSection";
import { UnlockCodeInput } from "../../components/UnlockCodeInput";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import {
  getCategoryById,
  getSubcategoriesByCategoryId,
  getSubcategoryById,
  industryCategoriesMock,
  industrySubcategoriesMock,
  testUnlockCode,
} from "../../lib/mock";

export type SubcategoryPaidClientProps = {
  initialCategoryId?: string;
  initialSubcategoryId?: string;
  backHref?: string;
};

export function SubcategoryPaidClient({
  initialCategoryId,
  initialSubcategoryId,
  backHref,
}: SubcategoryPaidClientProps) {
  const initialSubcategory =
    (initialSubcategoryId && getSubcategoryById(initialSubcategoryId)) || industrySubcategoriesMock[0];
  const initialCategory = getCategoryById(initialCategoryId || initialSubcategory.categoryId) || industryCategoriesMock[0];

  const [selectedCategoryId, setSelectedCategoryId] = useState(initialCategory.categoryId);
  const [selectedSubcategoryId, setSelectedSubcategoryId] = useState(initialSubcategory.subcategoryId);
  const [unlocked, setUnlocked] = useState(false);

  const category = getCategoryById(selectedCategoryId) || initialCategory;
  const subcategories = useMemo(
    () => getSubcategoriesByCategoryId(category.categoryId),
    [category.categoryId],
  );
  const selected =
    getSubcategoryById(selectedSubcategoryId) || subcategories[0] || initialSubcategory;

  function selectCategory(categoryId: string) {
    const nextSubcategory = getSubcategoriesByCategoryId(categoryId)[0];
    setSelectedCategoryId(categoryId);
    setSelectedSubcategoryId(nextSubcategory?.subcategoryId || selectedSubcategoryId);
    setUnlocked(false);
  }

  function selectSubcategory(subcategoryId: string) {
    setSelectedSubcategoryId(subcategoryId);
    setUnlocked(false);
  }

  return (
    <MobileLayout subtitle="细分行业付费页" title={selected.name}>
      <div className="space-y-4">
        <Card className="bg-card/75">
          <CardHeader>
            <CardTitle>当前大类</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              {industryCategoriesMock.map((item) => (
                <button
                  key={item.categoryId}
                  type="button"
                  onClick={() => selectCategory(item.categoryId)}
                  className={`m-0 rounded-md border p-3 text-left text-sm ${
                    category.categoryId === item.categoryId
                      ? "border-primary bg-primary/10 text-foreground"
                      : "border-border bg-muted/35 text-muted-foreground"
                  }`}
                >
                  {item.name}
                </button>
              ))}
            </div>
            <p className="text-xs leading-5 text-muted-foreground">
              大类五行解析免费开放，细分行业完整报告需要测试解锁码。
            </p>
          </CardContent>
        </Card>

        <ReportSection
          title={`${category.name} · 免费五行解析`}
          subtitle="免费开放"
          element={category.mainElement}
          paragraphs={category.freeAnalysis}
        />

        <Card className="bg-card/75">
          <CardHeader>
            <CardTitle>选择细分行业</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {subcategories.map((item) => (
              <button
                key={item.subcategoryId}
                type="button"
                onClick={() => selectSubcategory(item.subcategoryId)}
                className={`m-0 rounded-md border p-3 text-left ${
                  selected.subcategoryId === item.subcategoryId
                    ? "border-primary bg-primary/10 text-foreground"
                    : "border-border bg-muted/35 text-muted-foreground"
                }`}
              >
                <span className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold">{item.name}</span>
                  <ElementBadge
                    element={item.mainElement}
                    status={unlocked && selected.subcategoryId === item.subcategoryId ? "stable" : "locked"}
                  />
                </span>
                <span className="mt-2 block text-xs leading-5">{item.paidSummary}</span>
              </button>
            ))}
          </CardContent>
        </Card>

        {!unlocked ? (
          <>
            <PaywallCard
              title={`解锁 ${selected.name}`}
              description="当前为测试付费墙，不连接真实支付。输入测试解锁码后展示完整报告。"
              features={["细分行业完整报告", "五行动能拆解", "结构变化摘要"]}
              actionLabel={`测试解锁码：${testUnlockCode}`}
            />
            <UnlockCodeInput mockCode={testUnlockCode} onUnlocked={() => setUnlocked(true)} />
          </>
        ) : (
          <div className="space-y-3">
            <ReportSection
              title={`${selected.name} · 完整报告`}
              subtitle="已解锁测试报告"
              element={selected.mainElement}
              paragraphs={selected.fullReport}
            />
            <ReportSection
              title="风险与边界"
              subtitle="说明"
              element={selected.secondaryElement}
              paragraphs={[
                `风险标签：${selected.riskTags.join(" / ")}`,
                "本报告仅用于文化分析和行业情绪参考，不构成投资建议，不承诺收益。",
                "当前数据为前端 mock，用于验证免费大类到付费细分行业的用户路径。",
              ]}
            />
          </div>
        )}

        <Link
          href={backHref || `/category/${category.categoryId}`}
          className="block text-center text-sm font-semibold text-primary"
        >
          返回大类详情
        </Link>
      </div>
    </MobileLayout>
  );
}
