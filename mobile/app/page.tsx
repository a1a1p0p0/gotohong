import MobileLayout from "../components/MobileLayout";
import { WuxingEnergyHero } from "../components/WuxingEnergyHero";

export const dynamic = "force-dynamic";

export default function HomePage() {
  return (
    <MobileLayout showPageHeader={false}>
      <section className="min-h-[calc(100dvh-8rem)]">
        <WuxingEnergyHero />
      </section>
    </MobileLayout>
  );
}
