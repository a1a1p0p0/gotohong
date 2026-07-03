import { cn } from "../lib/utils";
import { elementLabels, elementTone, type EnergyStatus, type WuxingElement } from "./design-system";

const statusLabels: Record<EnergyStatus, string> = {
  warming: "增强",
  stable: "平衡",
  cooling: "收敛",
  locked: "待解锁",
};

export type ElementBadgeProps = {
  element?: WuxingElement;
  status?: EnergyStatus;
  label?: string;
  className?: string;
};

export function ElementBadge({
  element = "earth",
  status = "stable",
  label,
  className,
}: ElementBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center rounded-full border px-2.5 text-xs font-medium",
        elementTone[element],
        className,
      )}
    >
      {label ?? `${elementLabels[element]} · ${statusLabels[status]}`}
    </span>
  );
}
