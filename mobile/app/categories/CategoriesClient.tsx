"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ElementBadge } from "../../components/ElementBadge";
import { ReportSection } from "../../components/ReportSection";
import { elementLabels } from "../../components/design-system";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { cn } from "../../lib/utils";
import type { BoardProfile, IndustryCategoryMock } from "../../lib/types";

type BoardFilter = "all" | "industry" | "concept" | "review";

const pageSize = 12;

const filterOptions: Array<{ value: BoardFilter; label: string }> = [
  { value: "all", label: "全部" },
  { value: "industry", label: "行业板块" },
  { value: "concept", label: "概念板块" },
  { value: "review", label: "需要复核" },
];

function getCategoryName(categories: IndustryCategoryMock[], categoryId: string) {
  return categories.find((category) => category.categoryId === categoryId)?.name || "需要复核";
}

export type CategoriesClientProps = {
  categories: IndustryCategoryMock[];
  boards: BoardProfile[];
};

export function CategoriesClient({ categories, boards }: CategoriesClientProps) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<BoardFilter>("all");
  const [page, setPage] = useState(1);

  const filteredBoards = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return boards.filter((board) => {
      const matchesQuery =
        !normalizedQuery ||
        board.boardName.toLowerCase().includes(normalizedQuery) ||
        board.boardCode.toLowerCase().includes(normalizedQuery);
      const matchesFilter =
        filter === "all" ||
        (filter === "industry" && board.boardType === "industry") ||
        (filter === "concept" && board.boardType === "concept") ||
        (filter === "review" && board.needReview);

      return matchesQuery && matchesFilter;
    });
  }, [boards, filter, query]);

  const totalPages = Math.max(1, Math.ceil(filteredBoards.length / pageSize));
  const safePage = Math.min(page, totalPages);
  const visibleBoards = filteredBoards.slice((safePage - 1) * pageSize, safePage * pageSize);

  function updateQuery(value: string) {
    setQuery(value);
    setPage(1);
  }

  function updateFilter(value: BoardFilter) {
    setFilter(value);
    setPage(1);
  }

  return (
    <div className="space-y-4">
      <ReportSection
        title="行业大类五行解析"
        subtitle="本页免费开放"
        element="earth"
        paragraphs={[
          "行业大类免费展示五行属性解析；行业板块和概念板块来自本地真实板块数据。",
          "点击具体板块后进入细分行业付费页，使用 TEST123 做最小解锁验证。",
        ]}
      />

      <section className="space-y-3">
        {categories.map((item) => (
          <Card key={item.categoryId} className="bg-card/75">
            <CardHeader className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <CardTitle>{item.name}</CardTitle>
                <ElementBadge element={item.mainElement} label={item.statusTag} />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm leading-6 text-muted-foreground">{item.freeSummary}</p>
              <p className="text-xs leading-5 text-muted-foreground">
                主五行：{elementLabels[item.mainElement]} · 副五行：{elementLabels[item.secondaryElement]}
              </p>
              <Link href={`/category/${item.categoryId}`} className="text-sm font-semibold text-primary">
                查看大类详情
              </Link>
            </CardContent>
          </Card>
        ))}
      </section>

      <Card className="bg-card/75">
        <CardHeader>
          <CardTitle>板块搜索</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input
            aria-label="搜索板块名称"
            placeholder="搜索行业板块或概念板块"
            value={query}
            onChange={(event) => updateQuery(event.target.value)}
          />
          <div className="grid grid-cols-4 gap-2">
            {filterOptions.map((option) => (
              <Button
                key={option.value}
                size="sm"
                variant={filter === option.value ? "default" : "secondary"}
                onClick={() => updateFilter(option.value)}
                className="px-2 text-xs"
              >
                {option.label}
              </Button>
            ))}
          </div>
          <p className="text-xs leading-5 text-muted-foreground">
            当前匹配 {filteredBoards.length} 条，每页显示 {pageSize} 条。
          </p>
        </CardContent>
      </Card>

      <section className="space-y-3">
        {visibleBoards.map((board) => (
          <Card key={board.boardCode} className={cn("bg-card/75", board.needReview && "border-primary/30")}>
            <CardHeader className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs text-muted-foreground">
                    {getCategoryName(categories, board.categoryId)} ·{" "}
                    {board.boardType === "industry" ? "行业板块" : "概念板块"}
                  </p>
                  <CardTitle className="mt-1">{board.boardName}</CardTitle>
                </div>
                {board.needReview && <ElementBadge element="earth" label="需要复核" />}
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <ElementBadge element={board.mainElement} label={`主五行：${elementLabels[board.mainElement]}`} />
                <ElementBadge
                  element={board.secondaryElement}
                  label={`副五行：${elementLabels[board.secondaryElement]}`}
                />
              </div>
              <p className="text-sm leading-6 text-muted-foreground">{board.reason}</p>
              <Link href={`/subcategory/${board.boardCode}`} className="text-sm font-semibold text-primary">
                解锁查看完整报告
              </Link>
            </CardContent>
          </Card>
        ))}
      </section>

      <div className="grid grid-cols-3 items-center gap-2">
        <Button variant="secondary" disabled={safePage <= 1} onClick={() => setPage((current) => current - 1)}>
          上一页
        </Button>
        <p className="text-center text-xs text-muted-foreground">
          {safePage} / {totalPages}
        </p>
        <Button
          variant="secondary"
          disabled={safePage >= totalPages}
          onClick={() => setPage((current) => current + 1)}
        >
          下一页
        </Button>
      </div>
    </div>
  );
}
