import Link from "next/link";
import { ArrowUpRight, LockKeyhole } from "lucide-react";
import { buttonVariants } from "./ui/button";
import { cn } from "../lib/utils";

export type HeroActionButtonsProps = {
  primary: {
    label: string;
    href: string;
  };
  secondary: {
    label: string;
    href: string;
  };
};

export function HeroActionButtons({ primary, secondary }: HeroActionButtonsProps) {
  return (
    <div className="grid grid-cols-2 gap-2">
      <Link href={primary.href} className={cn(buttonVariants(), "min-h-12 px-3 text-[13px]")}>
        {primary.label}
        <ArrowUpRight className="h-4 w-4 shrink-0" />
      </Link>
      <Link
        href={secondary.href}
        className={cn(buttonVariants({ variant: "outline" }), "min-h-12 border-primary/40 px-3 text-[13px]")}
      >
        <LockKeyhole className="h-4 w-4 shrink-0" />
        {secondary.label}
      </Link>
    </div>
  );
}
