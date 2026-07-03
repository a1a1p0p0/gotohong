import { Activity, Clock3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ElementBadge } from "./ElementBadge";
import type { WuxingElement } from "./design-system";

export type EnergyMetric = {
  label: string;
  value: string;
};

export type EnergyCardProps = {
  title?: string;
  summary?: string;
  mainElement?: WuxingElement;
  updatedAt?: string;
  metrics?: EnergyMetric[];
};

const mockMetrics: EnergyMetric[] = [
  { label: "承载度", value: "偏强" },
  { label: "显化度", value: "稳定" },
  { label: "启动度", value: "观察中" },
];

export function EnergyCard({
  title = "今日五行动能",
  summary = "土主承载、聚合与转化落地；火带来显化和传播，木带来启动和生长。今天更利于把分散关注沉淀为稳定结构。",
  mainElement = "earth",
  updatedAt = "今日 08:00",
  metrics = mockMetrics,
}: EnergyCardProps) {
  return (
    <Card className="overflow-hidden border-amber-200/20 bg-card/80">
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-2">
            <ElementBadge element={mainElement} status="warming" />
            <CardTitle className="text-xl">{title}</CardTitle>
          </div>
          <Activity className="mt-1 h-5 w-5 text-primary" />
        </div>
        <p className="text-sm leading-6 text-muted-foreground">{summary}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-2">
          {metrics.map((metric) => (
            <div key={metric.label} className="rounded-md border border-border/70 bg-muted/50 p-3">
              <p className="text-[11px] text-muted-foreground">{metric.label}</p>
              <p className="mt-1 text-sm font-semibold">{metric.value}</p>
            </div>
          ))}
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock3 className="h-3.5 w-3.5" />
          <span>更新时间：{updatedAt}</span>
        </div>
      </CardContent>
    </Card>
  );
}
