import { cn } from "../lib/utils";

export type RiskNoticeProps = {
  text?: string;
  className?: string;
};

const defaultRiskText =
  "本工具仅作文化分析和行业情绪参考，不构成投资建议，不承诺收益。";

export function RiskNotice({ text = defaultRiskText, className }: RiskNoticeProps) {
  return (
    <p className={cn("px-4 py-3 text-[11px] leading-5 text-muted-foreground", className)}>
      {text}
    </p>
  );
}
