import type { MetadataRoute } from "next";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "五行行业动能",
    short_name: "五行动能",
    description: "本地五行行业动能分析工具",
    start_url: "/",
    display: "standalone",
    background_color: "#f7f3ea",
    theme_color: "#1f7a6d",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
