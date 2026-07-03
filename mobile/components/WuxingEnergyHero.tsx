import { ElementBadge } from "./ElementBadge";
import { EnergyRing } from "./EnergyRing";
import { HeroActionButtons } from "./HeroActionButtons";
import { getWuxingHeroData, wuxingElements } from "../lib/mock";
import type { WuxingHeroData } from "../lib/types";

export type WuxingEnergyHeroProps = {
  data?: WuxingHeroData;
};

export function WuxingEnergyHero({ data = getWuxingHeroData() }: WuxingEnergyHeroProps) {
  return (
    <section className="wuxing-hero-enter relative overflow-hidden rounded-lg border border-primary/20 bg-[radial-gradient(circle_at_50%_34%,rgba(69,212,131,0.14),transparent_30%),radial-gradient(circle_at_72%_42%,rgba(255,122,61,0.16),transparent_28%),linear-gradient(180deg,rgba(12,35,32,0.96),rgba(5,14,14,0.99))] px-4 pb-5 pt-5 shadow-[0_18px_60px_rgba(0,0,0,0.38)]">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(135deg,rgba(255,255,255,0.07),transparent_36%,rgba(214,166,63,0.06))]" />
      <div className="pointer-events-none absolute -right-20 top-10 h-40 w-40 rounded-full bg-primary/10 blur-3xl" />

      <div className="relative z-10 space-y-4">
        <header className="space-y-2">
          <div className="flex items-center gap-2">
            <ElementBadge element="wood" label={data.eyebrow} />
            <ElementBadge element="fire" label="动能行为" className="bg-transparent" />
          </div>
          <p className="text-[11px] leading-5 text-muted-foreground">
            {data.solarDate} · {data.lunarDate} · {data.updatedAt}
          </p>
          <p className="text-[11px] leading-5 text-muted-foreground">{data.ganzhiText}</p>
          <h1 className="text-[28px] font-semibold leading-tight tracking-normal text-foreground">
            {data.title}
          </h1>
          <p className="max-w-[19rem] text-sm leading-6 text-muted-foreground">{data.subtitle}</p>
        </header>

        <EnergyRing
          elements={wuxingElements}
          mainElements={data.mainElements}
          secondaryElements={data.secondaryElements}
          centerTitle={data.centerTitle}
          centerMainText={data.centerMainText}
        />

        <p className="mx-auto max-w-[20rem] text-center text-sm leading-6 text-muted-foreground">
          {data.explanation}
        </p>

        <HeroActionButtons primary={data.primaryAction} secondary={data.secondaryAction} />
      </div>
    </section>
  );
}
