"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type React from "react";
import { BarChart3, Compass, LockKeyhole, Sparkles } from "lucide-react";
import { cn } from "../lib/utils";

export type BottomNavItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
};

export type BottomNavProps = {
  items?: BottomNavItem[];
  className?: string;
};

const defaultItems: BottomNavItem[] = [
  { href: "/", label: "今日", icon: Sparkles },
  { href: "/categories", label: "行业", icon: Compass },
  { href: "/ranking", label: "榜单", icon: BarChart3 },
  { href: "/payment", label: "解锁", icon: LockKeyhole },
];

export function BottomNav({ items = defaultItems, className }: BottomNavProps) {
  const pathname = usePathname();

  return (
    <nav
      className={cn(
        "fixed inset-x-0 bottom-0 z-40 mx-auto grid max-w-md grid-cols-4 border-t border-border/80 bg-background/95 px-2 pb-[calc(env(safe-area-inset-bottom)+0.35rem)] pt-2 backdrop-blur",
        className,
      )}
      aria-label="底部导航"
    >
      {items.map((item) => {
        const active = pathname === item.href;
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex min-h-12 flex-col items-center justify-center gap-1 rounded-md text-xs text-muted-foreground",
              active && "bg-accent text-foreground",
            )}
          >
            <Icon className="h-4 w-4" />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
