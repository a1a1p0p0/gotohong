import { LockKeyhole } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export type PaywallCardProps = {
  title?: string;
  description?: string;
  features?: string[];
  actionLabel?: string;
  onUnlock?: () => void;
};

const mockFeatures = ["细分行业完整报告", "行业 TOP 榜完整视图", "本周五行动能拆解"];

export function PaywallCard({
  title = "解锁完整视图",
  description = "免费内容展示大类观察，解锁后可查看更细的行业结构与榜单维度。",
  features = mockFeatures,
  actionLabel = "输入解锁码",
  onUnlock,
}: PaywallCardProps) {
  return (
    <Card className="border-primary/30 bg-primary/10">
      <CardHeader className="space-y-2">
        <div className="flex items-center gap-2 text-primary">
          <LockKeyhole className="h-4 w-4" />
          <CardTitle>{title}</CardTitle>
        </div>
        <p className="text-sm leading-6 text-muted-foreground">{description}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <ul className="grid gap-2 text-sm text-foreground/90">
          {features.map((feature) => (
            <li key={feature} className="rounded-md border border-primary/20 bg-background/30 px-3 py-2">
              {feature}
            </li>
          ))}
        </ul>
        <Button onClick={onUnlock}>{actionLabel}</Button>
      </CardContent>
    </Card>
  );
}
