import MobileLayout from "../../../components/MobileLayout";
import { ElementBadge } from "../../../components/ElementBadge";
import { PaywallCard } from "../../../components/PaywallCard";
import { ReportSection } from "../../../components/ReportSection";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";

export function generateStaticParams() {
  return Array.from({ length: 20 }, (_, index) => ({
    id: String(index + 1),
  }));
}

export default async function ReportDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <MobileLayout subtitle="报告详情" title="五行动能报告">
      <div className="space-y-4">
        <Card className="border-primary/25 bg-card/80">
          <CardHeader className="space-y-3">
            <div className="flex items-start justify-between gap-3">
              <CardTitle>今日行业结构观察</CardTitle>
              <ElementBadge element="earth" status="warming" />
            </div>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>报告编号：{id}</p>
            <p>更新时间：2026-07-03 08:00</p>
            <p>干支信息：年柱丙午 · 月柱甲午 · 日柱戊寅 · 时柱丙辰</p>
            <p>内容口径：行业大类、五行动能、榜单预览与细分章节摘要。</p>
          </CardContent>
        </Card>

        <ReportSection
          title="观察摘要"
          subtitle="免费章节"
          element="earth"
          paragraphs={[
            "今日行业结构以土属性承载、聚合与转化落地为主，火属性提供显化传播，木属性提供启动生长。",
            "该报告用于整理行业动能观察，不涉及个股判断、买卖方向或收益承诺。",
          ]}
        />

        <ReportSection
          title="行业分布"
          subtitle="免费章节"
          element="fire"
          paragraphs={[
            "基础化工、数据中心、储能等板块更贴近今日土主、火木为辅的观察口径。",
            "免费章节保留大类视角，细分行业和完整榜单需要解锁查看。",
          ]}
        />

        <ReportSection title="细分行业拆解" subtitle="锁定章节" locked />

        <PaywallCard
          title="解锁完整报告"
          description="完整报告包含细分行业拆解、行业 TOP 榜和本周动能章节。"
        />
      </div>
    </MobileLayout>
  );
}
