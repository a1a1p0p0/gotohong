const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..");
const src = path.join(root, "data", "astock_board_wuxing_profiles.csv");
const out = path.join(root, "mobile", "lib", "board-data.ts");
const text = fs.readFileSync(src, "utf8").trim();

function parseCsvLine(line) {
  const result = [];
  let current = "";
  let quoted = false;

  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === "\"") {
      if (quoted && line[index + 1] === "\"") {
        current += "\"";
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      result.push(current);
      current = "";
    } else {
      current += char;
    }
  }

  result.push(current);
  return result;
}

const lines = text.split(/\r?\n/);
const headers = parseCsvLine(lines[0]);
const rows = lines.slice(1).map((line) => {
  const cells = parseCsvLine(line);
  return Object.fromEntries(headers.map((header, index) => [header, cells[index] || ""]));
});

function includesAny(textValue, words) {
  return words.some((word) => textValue.includes(word));
}

function inferCategory(row) {
  const haystack = `${row.board_name}${row.category}${row.subcategory}${row.reason}`;

  if (
    includesAny(haystack, [
      "AI",
      "人工智能",
      "算力",
      "数据",
      "云",
      "软件",
      "互联网",
      "通信",
      "半导体",
      "芯片",
      "电子",
      "传媒",
      "信创",
      "数字",
      "信息",
      "网络",
      "游戏",
      "存储",
      "ChatGPT",
      "AIGC",
    ])
  ) {
    return "digital";
  }

  if (
    includesAny(haystack, [
      "机器人",
      "机械",
      "设备",
      "工业",
      "母机",
      "制造",
      "汽车",
      "军工",
      "自动化",
      "机床",
      "航天",
      "船舶",
      "仪器",
      "专用设备",
      "通用设备",
    ])
  ) {
    return "advanced-manufacturing";
  }

  if (
    includesAny(haystack, [
      "储能",
      "光伏",
      "新能源",
      "风电",
      "电力",
      "电池",
      "锂",
      "液冷",
      "能源",
      "环保",
      "充电",
      "氢",
      "碳",
      "绿电",
      "太阳能",
    ])
  ) {
    return "green-energy";
  }

  return "needs-review";
}

const allowedElements = new Set(["wood", "fire", "earth", "metal", "water"]);
const profiles = rows.map((row) => {
  const categoryId = inferCategory(row);
  return {
    boardCode: row.board_code,
    boardName: row.board_name,
    boardType: row.board_type === "concept" ? "concept" : "industry",
    categoryId,
    mainElement: allowedElements.has(row.main_element) ? row.main_element : "earth",
    secondaryElement: allowedElements.has(row.secondary_element) ? row.secondary_element : "metal",
    reason: row.reason,
    needReview: row.need_review === "true" || categoryId === "needs-review",
    confidence: Number(row.confidence || 0),
    updatedAt: row.updated_at,
  };
});

const output = `import type { BoardProfile } from "./types";\n\nexport const boardProfiles: BoardProfile[] = ${JSON.stringify(
  profiles,
  null,
  2,
)};\n`;

fs.writeFileSync(out, output, "utf8");
console.log(`wrote ${out} rows=${profiles.length}`);
console.log(
  profiles.reduce((acc, item) => {
    acc[item.categoryId] = (acc[item.categoryId] || 0) + 1;
    return acc;
  }, {}),
);
