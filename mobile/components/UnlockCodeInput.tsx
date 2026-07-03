"use client";

import { useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";

export type UnlockCodeInputProps = {
  title?: string;
  placeholder?: string;
  mockCode?: string;
  submitLabel?: string;
  onUnlocked?: () => void;
};

export function UnlockCodeInput({
  title = "输入解锁码",
  placeholder = "请输入 6 位解锁码",
  mockCode = "TEST123",
  submitLabel = "确认解锁",
  onUnlocked,
}: UnlockCodeInputProps) {
  const [code, setCode] = useState("");
  const [message, setMessage] = useState(`用于测试：请输入解锁码 ${mockCode}`);
  const [unlocked, setUnlocked] = useState(false);

  function handleSubmit() {
    const normalized = code.trim().toUpperCase();
    if (!normalized) {
      setMessage("请先输入解锁码。");
      return;
    }
    if (normalized !== mockCode) {
      setMessage("解锁码无效");
      return;
    }
    setUnlocked(true);
    setMessage("已解锁完整报告。");
    onUnlocked?.();
  }

  return (
    <Card className="bg-card/75">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          aria-label="解锁码"
          autoCapitalize="characters"
          inputMode="text"
          maxLength={12}
          placeholder={placeholder}
          value={code}
          onChange={(event) => setCode(event.target.value)}
        />
        <Button disabled={unlocked} onClick={handleSubmit}>
          {unlocked ? "已解锁" : submitLabel}
        </Button>
        <p className="text-xs leading-5 text-muted-foreground">{message}</p>
      </CardContent>
    </Card>
  );
}
