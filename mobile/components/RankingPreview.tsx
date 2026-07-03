import { TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ElementBadge } from "./ElementBadge";
import type { EnergyStatus, WuxingElement } from "./design-system";

export type RankingItem = {
  rank: number;
  name: string;
  element: WuxingElement;
  status: EnergyStatus;
  score: string;
  locked?: boolean;
};

export type RankingPreviewProps = {
  title?: string;
  items?: RankingItem[];
};

const mockItems: RankingItem[] = [
  { rank: 1, name: "TOP 1 细分板块", element: "earth", status: "locked", score: "解锁查看", locked: true },
  { rank: 2, name: "TOP 2 细分板块", element: "fire", status: "locked", score: "解锁查看", locked: true },
  { rank: 3, name: "储能", element: "wood", status: "warming", score: "木势启动增强" },
  { rank: 4, name: "AI 应用", element: "fire", status: "warming", score: "火势显化增强" },
  { rank: 5, name: "工业母机", element: "earth", status: "warming", score: "土势结构增强" },
];

export function RankingPreview({ title = "行业 TOP 榜预览", items = mockItems }: RankingPreviewProps) {
  return (
    <Card className="bg-card/75">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <CardTitle>{title}</CardTitle>
        <TrendingUp className="h-4 w-4 text-primary" />
      </CardHeader>
      <CardContent className="space-y-2">
        {items.map((item) => (
          <div
            key={`${item.rank}-${item.name}`}
            className="flex items-center gap-3 rounded-md border border-border/70 bg-muted/40 p-3"
          >
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-background text-sm font-semibold">
              {item.rank}
            </span>
            <div className="min-w-0 flex-1">
              <p className={item.locked ? "text-sm font-semibold blur-[2px]" : "text-sm font-semibold"}>
                {item.name}
              </p>
              <p className="text-xs text-muted-foreground">{item.score}</p>
            </div>
            <ElementBadge element={item.element} status={item.status} />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
