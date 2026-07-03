"use client";

import { useState } from "react";
import MobileLayout from "../../components/MobileLayout";
import { PaywallCard } from "../../components/PaywallCard";
import { RankingPreview, type RankingItem } from "../../components/RankingPreview";
import { UnlockCodeInput } from "../../components/UnlockCodeInput";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";

const previewItems: RankingItem[] = [
  { rank: 1, name: "TOP 1 细分板块", element: "earth", status: "locked", score: "解锁查看", locked: true },
  { rank: 2, name: "TOP 2 细分板块", element: "fire", status: "locked", score: "解锁查看", locked: true },
  { rank: 3, name: "储能", element: "wood", status: "warming", score: "木势启动增强" },
  { rank: 4, name: "AI 应用", element: "fire", status: "warming", score: "火势显化增强" },
  { rank: 5, name: "工业母机", element: "earth", status: "warming", score: "土势结构增强" },
];

const fullItems: RankingItem[] = [
  { rank: 1, name: "基础化工", element: "earth", status: "warming", score: "土势承载最强" },
  { rank: 2, name: "数据中心", element: "fire", status: "warming", score: "火势显化增强" },
  { rank: 3, name: "储能", element: "wood", status: "warming", score: "木势启动增强" },
  { rank: 4, name: "AI 应用", element: "fire", status: "warming", score: "传播动能增强" },
  { rank: 5, name: "工业母机", element: "earth", status: "warming", score: "结构落地增强" },
];

export default function RankingPage() {
  const [period, setPeriod] = useState("今日");
  const [unlocked, setUnlocked] = useState(false);

  return (
    <MobileLayout subtitle="榜单预览" title="行业 TOP 榜">
      <div className="space-y-4">
        <Card className="bg-card/75">
          <CardHeader>
            <CardTitle>榜单周期</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-3 gap-2">
            {["今日", "本周", "本月"].map((item) => (
              <Button
                key={item}
                variant={period === item ? "default" : "secondary"}
                size="sm"
                onClick={() => setPeriod(item)}
              >
                {item}
              </Button>
            ))}
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-card/75">
          <CardContent className="space-y-2 p-4 text-sm leading-6 text-muted-foreground">
            <p className="font-medium text-foreground">今日主势为土，副势为火、木。</p>
            <p>本页只展示与当日势能最贴近的前五个板块，其中前二需要解锁查看。</p>
          </CardContent>
        </Card>

        <RankingPreview title={`${period}行业 TOP 榜`} items={unlocked ? fullItems : previewItems} />

        {!unlocked && (
          <>
            <PaywallCard
              title="解锁 TOP 1-2"
              description="免费版展示 TOP 3-5，用于快速理解今日行业动能方向。TOP 1-2 需要输入测试解锁码查看。"
            />
            <UnlockCodeInput onUnlocked={() => setUnlocked(true)} />
          </>
        )}
      </div>
    </MobileLayout>
  );
}
