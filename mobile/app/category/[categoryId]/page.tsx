import Link from "next/link";
import { notFound } from "next/navigation";
import MobileLayout from "../../../components/MobileLayout";
import { ElementBadge } from "../../../components/ElementBadge";
import { elementLabels } from "../../../components/design-system";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { buttonVariants } from "../../../components/ui/button";
import { cn } from "../../../lib/utils";
import { boardProfiles } from "../../../lib/board-data";
import { getCategoryById } from "../../../lib/mock";

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

  const boards = boardProfiles.filter((board) => board.categoryId === category.categoryId).slice(0, 12);

  return (
    <MobileLayout subtitle="行业大类免费详情" title={category.name}>
      <div className="space-y-4">
        <Card className="bg-card/75">
          <CardHeader className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <ElementBadge
                element={category.mainElement}
                label={`主五行：${elementLabels[category.mainElement]}`}
              />
              <ElementBadge
                element={category.secondaryElement}
                label={`副五行：${elementLabels[category.secondaryElement]}`}
              />
            </div>
            <CardTitle>{category.freeSummary}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {category.freeAnalysis.map((paragraph) => (
              <p key={paragraph} className="text-sm leading-6 text-muted-foreground">
                {paragraph}
              </p>
            ))}
          </CardContent>
        </Card>

        <Card className="border-primary/30 bg-primary/10">
          <CardHeader>
            <CardTitle>该大类下的细分行业需要解锁</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm leading-6 text-muted-foreground">{category.paidHint}</p>
            <p className="text-xs leading-5 text-muted-foreground">
              当前仅展示前 12 条本地真实板块数据，完整列表请回到行业大类页搜索和筛选。
            </p>
          </CardContent>
        </Card>

        <section className="space-y-3">
          {boards.map((board) => (
            <Card key={board.boardCode} className="bg-card/75">
              <CardHeader className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs text-muted-foreground">
                      {board.boardType === "industry" ? "行业板块" : "概念板块"}
                    </p>
                    <CardTitle className="mt-1">{board.boardName}</CardTitle>
                  </div>
                  <ElementBadge element={board.mainElement} status="locked" />
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  <ElementBadge
                    element={board.mainElement}
                    label={`主五行：${elementLabels[board.mainElement]}`}
                  />
                  <ElementBadge
                    element={board.secondaryElement}
                    label={`副五行：${elementLabels[board.secondaryElement]}`}
                  />
                </div>
                <p className="text-sm leading-6 text-muted-foreground">{board.reason}</p>
                <Link
                  href={`/subcategory/${board.boardCode}`}
                  className={cn(buttonVariants({ variant: "outline" }), "border-primary/40 text-primary")}
                >
                  解锁查看完整报告
                </Link>
              </CardContent>
            </Card>
          ))}
        </section>
      </div>
    </MobileLayout>
  );
}
