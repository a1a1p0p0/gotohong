import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { buttonVariants } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { cn } from "../lib/utils";

export type FreeEntryItem = {
  title: string;
  description: string;
  href: string;
};

export type FreeEntryCardProps = {
  title?: string;
  items?: FreeEntryItem[];
};

const mockItems: FreeEntryItem[] = [
  { title: "行业大类", description: "查看五行归属与当前热度", href: "/categories" },
  { title: "本周分析", description: "阅读本周结构变化摘要", href: "/free-week" },
];

export function FreeEntryCard({ title = "免费查看", items = mockItems }: FreeEntryCardProps) {
  return (
    <Card className="bg-card/75">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(buttonVariants({ variant: "secondary" }), "h-auto justify-between p-3")}
          >
            <span className="text-left">
              <span className="block text-sm font-semibold">{item.title}</span>
              <span className="block text-xs font-normal text-muted-foreground">{item.description}</span>
            </span>
            <ArrowRight className="h-4 w-4 shrink-0" />
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}
