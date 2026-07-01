import Link from "next/link";
import "./mobile-layout.css";

export default function MobileLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="mobile-shell">
      <section className="mobile-content">{children}</section>
      <nav className="bottom-nav">
        <Link href="/">首页</Link>
        <Link href="/categories">行业</Link>
        <Link href="/astock">A股</Link>
        <Link href="/ranking">方案</Link>
      </nav>
    </main>
  );
}
