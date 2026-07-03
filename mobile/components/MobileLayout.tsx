import type React from "react";
import { cn } from "../lib/utils";
import { BottomNav } from "./BottomNav";
import { RiskNotice } from "./RiskNotice";

export type MobileLayoutProps = {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  showPageHeader?: boolean;
  showBottomNav?: boolean;
  showRiskNotice?: boolean;
  className?: string;
};

export default function MobileLayout({
  children,
  title,
  subtitle,
  showPageHeader = true,
  showBottomNav = true,
  showRiskNotice = true,
  className,
}: MobileLayoutProps) {
  return (
    <main className="min-h-dvh bg-background text-foreground">
      <div className="mx-auto min-h-dvh max-w-md bg-[radial-gradient(circle_at_top,_rgba(245,188,77,0.16),_transparent_36%),linear-gradient(180deg,_rgba(12,36,34,0.96),_rgba(8,20,19,1))]">
        <section className={cn("px-4 pb-24 pt-4", className)}>
          {showPageHeader && (title || subtitle) && (
            <header className="mb-4 space-y-1">
              {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
              {title && <h1 className="text-2xl font-semibold tracking-normal">{title}</h1>}
            </header>
          )}
          {children}
          {showRiskNotice && <RiskNotice className="mt-4 px-0" />}
        </section>
        {showBottomNav && <BottomNav />}
      </div>
    </main>
  );
}
