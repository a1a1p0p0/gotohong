import { LockKeyhole } from "lucide-react";
import { cn } from "../lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ElementBadge } from "./ElementBadge";
import type { WuxingElement } from "./design-system";

export type ReportSectionProps = {
  title?: string;
  subtitle?: string;
  element?: WuxingElement;
  paragraphs?: string[];
  locked?: boolean;
  className?: string;
};

const mockParagraphs = [
  "本周行业大类呈现承载与转化落地优先，土属性方向更突出，火、木方向分别作为显化与启动条件。",
  "该内容仅用于结构观察，重点展示行业动能变化、热度分布和报告摘要。",
];

export function ReportSection({
  title = "本周五行动能摘要",
  subtitle = "免费报告",
  element = "earth",
  paragraphs = mockParagraphs,
  locked = false,
  className,
}: ReportSectionProps) {
  return (
    <Card className={cn("bg-card/75", locked && "border-primary/30", className)}>
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">{subtitle}</p>
            <CardTitle>{title}</CardTitle>
          </div>
          {locked ? (
            <span className="inline-flex h-7 items-center gap-1 rounded-full border border-primary/40 px-2.5 text-xs text-primary">
              <LockKeyhole className="h-3 w-3" />
              锁定
            </span>
          ) : (
            <ElementBadge element={element} status="stable" />
          )}
        </div>
      </CardHeader>
      <CardContent className={cn("space-y-3", locked && "select-none")}>
        {paragraphs.map((paragraph) => (
          <p key={paragraph} className={cn("text-sm leading-6 text-muted-foreground", locked && "blur-[2px]")}>
            {paragraph}
          </p>
        ))}
      </CardContent>
    </Card>
  );
}
