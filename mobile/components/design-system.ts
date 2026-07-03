export type WuxingElement = "metal" | "wood" | "water" | "fire" | "earth";

export type EnergyStatus = "warming" | "stable" | "cooling" | "locked";

export const elementLabels: Record<WuxingElement, string> = {
  metal: "金",
  wood: "木",
  water: "水",
  fire: "火",
  earth: "土",
};

export const elementTone: Record<WuxingElement, string> = {
  metal: "border-amber-300/50 bg-amber-300/10 text-amber-100",
  wood: "border-emerald-300/50 bg-emerald-300/10 text-emerald-100",
  water: "border-cyan-300/50 bg-cyan-300/10 text-cyan-100",
  fire: "border-orange-300/50 bg-orange-300/10 text-orange-100",
  earth: "border-stone-300/50 bg-stone-300/10 text-stone-100",
};
