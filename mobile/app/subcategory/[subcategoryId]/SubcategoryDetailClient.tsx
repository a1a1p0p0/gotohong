"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import MobileLayout from "../../../components/MobileLayout";
import { ElementBadge } from "../../../components/ElementBadge";
import { ReportSection } from "../../../components/ReportSection";
import { UnlockCodeInput } from "../../../components/UnlockCodeInput";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { elementLabels } from "../../../components/design-system";
import { testUnlockCode } from "../../../lib/mock";
import type { IndustryCategoryMock, IndustrySubcategoryMock } from "../../../lib/types";

export type SubcategoryDetailClientProps = {
  category: IndustryCategoryMock;
  subcategory: IndustrySubcategoryMock;
};

function getStorageKey(subcategoryId: string) {
  return `wuxing_unlocked_subcategory_${subcategoryId}`;
}

export function SubcategoryDetailClient({ category, subcategory }: SubcategoryDetailClientProps) {
  const [unlocked, setUnlocked] = useState(false);

  useEffect(() => {
    setUnlocked(window.localStorage.getItem(getStorageKey(subcategory.subcategoryId)) === "true");
  }, [subcategory.subcategoryId]);

  function handleUnlocked() {
    window.localStorage.setItem(getStorageKey(subcategory.subcategoryId), "true");
    setUnlocked(true);
  }

  return (
    <MobileLayout subtitle="细分行业付费分析" title={subcategory.name}>
      <div className="space-y-4">
        <Card className="bg-card/75">
          <CardHeader className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <ElementBadge
                element={subcategory.mainElement}
                label={`主五行：${elementLabels[subcategory.mainElement]}`}
              />
              <ElementBadge
                element={subcategory.secondaryElement}
                label={`副五行：${elementLabels[subcategory.secondaryElement]}`}
              />
            </div>
            <CardTitle>{subcategory.name} · 免费预览</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm leading-6 text-muted-foreground">{subcategory.paidSummary}</p>
            <p className="text-xs leading-5 text-muted-foreground">
              所属大类：{category.name}。该细分行业属于付费分析。
            </p>
          </CardContent>
        </Card>

        {!unlocked ? (
          <>
            <Card className="border-primary/30 bg-primary/10">
              <CardHeader>
                <CardTitle>解锁后可查看</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="grid gap-2 text-sm text-muted-foreground">
                  {[
                    "主五行和副五行",
                    "行业动能行为",
                    "当日五行关系",
                    "最有利条件",
                    "过亢风险",
                    "观察重点",
                    "完整报告",
                  ].map((item) => (
                    <li key={item} className="rounded-md border border-primary/20 bg-background/30 px-3 py-2">
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <UnlockCodeInput
              mockCode={testUnlockCode}
              submitLabel="输入解锁码查看完整报告"
              onUnlocked={handleUnlocked}
            />
          </>
        ) : (
          <div className="space-y-3">
            <ReportSection
              title={`${subcategory.name} · 完整报告`}
              subtitle="已解锁"
              element={subcategory.mainElement}
              paragraphs={[
                `主五行：${elementLabels[subcategory.mainElement]}，副五行：${elementLabels[subcategory.secondaryElement]}。`,
                ...subcategory.fullReport,
              ]}
            />
            <ReportSection
              title="动能行为与观察重点"
              subtitle="完整报告"
              element={subcategory.secondaryElement}
              paragraphs={[
                "行业动能行为：观察该细分方向是否从分散关注走向明确场景。",
                "当日五行关系：结合主副五行判断动能释放、承接和约束条件。",
                "最有利条件：需求线索清晰、传播效率提升、产业链承接顺畅。",
                "过亢风险：短期关注过热、预期过满、节奏过快。",
                `风险标签：${subcategory.riskTags.join(" / ")}`,
              ]}
            />
          </div>
        )}

        <Link href={`/category/${category.categoryId}`} className="block text-center text-sm font-semibold text-primary">
          返回大类详情
        </Link>
      </div>
    </MobileLayout>
  );
}
