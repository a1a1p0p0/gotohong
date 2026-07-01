import type { Metadata } from "next";
import ServiceWorkerRegister from "../components/ServiceWorkerRegister";
import "./globals.css";

export const metadata: Metadata = {
  title: "五行行业动能",
  description: "本地五行行业动能分析工具",
  manifest: "/manifest.webmanifest",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <ServiceWorkerRegister />
        {children}
      </body>
    </html>
  );
}
