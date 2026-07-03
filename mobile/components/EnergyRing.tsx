import { RisingEnergyFlow } from "./RisingEnergyFlow";
import type { WuxingElement, WuxingElementMeta } from "../lib/types";

export type EnergyRingProps = {
  elements: WuxingElementMeta[];
  mainElements: WuxingElement[];
  secondaryElements: WuxingElement[];
  centerTitle: string;
  centerMainText: string;
};

export function EnergyRing({
  elements,
  mainElements,
  secondaryElements,
  centerTitle,
  centerMainText,
}: EnergyRingProps) {
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[19rem]">
      <svg
        className="absolute inset-0 h-full w-full overflow-visible"
        viewBox="0 0 220 220"
        role="img"
        aria-label="今日五行能量环"
      >
        <defs>
          <filter id="wuxing-main-glow" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <linearGradient id="wuxing-flow-gradient" x1="118" y1="84" x2="205" y2="30" gradientUnits="userSpaceOnUse">
            <stop stopColor="#45d483" stopOpacity="0" />
            <stop offset="0.5" stopColor="#ffd77a" stopOpacity="0.92" />
            <stop offset="1" stopColor="#7df7d4" stopOpacity="0.24" />
          </linearGradient>
        </defs>

        <circle cx="110" cy="110" r="72" fill="rgba(4,14,13,0.78)" stroke="rgba(242,217,139,0.14)" />
        <circle cx="110" cy="110" r="43" fill="rgba(8,22,20,0.94)" stroke="rgba(255,255,255,0.08)" />

        <g className="wuxing-ring-breathe">
          {elements.map((element) => {
            const isMain = mainElements.includes(element.key);
            const isSecondary = secondaryElements.includes(element.key);

            return (
              <path
                key={element.key}
                d={element.path}
                fill="none"
                stroke={element.color}
                strokeLinecap="round"
                strokeWidth={isMain ? 15 : isSecondary ? 12 : 9}
                strokeOpacity={isMain ? 1 : isSecondary ? 0.62 : 0.24}
                filter={isMain ? "url(#wuxing-main-glow)" : undefined}
                className={isMain ? "wuxing-main-pulse" : undefined}
              />
            );
          })}
        </g>

        <path
          d="M 48 158 A 92 92 0 0 0 173 63"
          fill="none"
          stroke="rgba(242,217,139,0.18)"
          strokeDasharray="8 14"
          strokeLinecap="round"
        />
        <path
          d="M 62 171 A 108 108 0 0 0 196 48"
          fill="none"
          stroke="rgba(125,247,212,0.13)"
          strokeDasharray="20 18"
          strokeLinecap="round"
        />

        <RisingEnergyFlow />
      </svg>

      <div className="absolute inset-[24%] flex flex-col items-center justify-center rounded-full border border-primary/15 bg-background/75 text-center shadow-[inset_0_0_32px_rgba(214,166,63,0.08)] backdrop-blur">
        <p className="text-xs text-muted-foreground">{centerTitle}</p>
        <p className="mt-1 text-lg font-semibold text-foreground">{centerMainText}</p>
      </div>
    </div>
  );
}
