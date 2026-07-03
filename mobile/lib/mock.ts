import type { IndustryCategoryMock, IndustrySubcategoryMock, WuxingElementMeta, WuxingHeroData } from "./types";
import { boardProfiles } from "./board-data";

export const wuxingElements: WuxingElementMeta[] = [
  {
    key: "wood",
    label: "木",
    color: "#45d483",
    path: "M 110 22 A 88 88 0 0 1 193.7 82.8",
  },
  {
    key: "fire",
    label: "火",
    color: "#ff7a3d",
    path: "M 193.7 82.8 A 88 88 0 0 1 161.7 181.2",
  },
  {
    key: "earth",
    label: "土",
    color: "#d8b35a",
    path: "M 161.7 181.2 A 88 88 0 0 1 58.3 181.2",
  },
  {
    key: "metal",
    label: "金",
    color: "#f2d98b",
    path: "M 58.3 181.2 A 88 88 0 0 1 26.3 82.8",
  },
  {
    key: "water",
    label: "水",
    color: "#4cc9f0",
    path: "M 26.3 82.8 A 88 88 0 0 1 110 22",
  },
];

function getShanghaiToday() {
  return new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Shanghai" }));
}

function formatSolarDate(date: Date) {
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
}

function getMockLunarDate(date: Date) {
  const base = new Date(2026, 6, 2);
  const dayOffset = Math.round((date.getTime() - base.getTime()) / 86400000);
  const lunarDay = 18 + dayOffset;
  const lunarDayText: Record<number, string> = {
    18: "十八",
    19: "十九",
    20: "二十",
    21: "廿一",
    22: "廿二",
    23: "廿三",
    24: "廿四",
    25: "廿五",
    26: "廿六",
    27: "廿七",
    28: "廿八",
    29: "廿九",
    30: "三十",
  };

  return `农历二零二六年五月${lunarDayText[lunarDay] || "十九"}日`;
}

export function getWuxingHeroData(): WuxingHeroData {
  const today = getShanghaiToday();

  return {
    ...wuxingHeroMock,
    solarDate: formatSolarDate(today),
    lunarDate: getMockLunarDate(today),
    ganzhiText: "年柱丙午 · 月柱甲午 · 日柱戊寅 · 时柱丙辰",
    updatedAt: "每日 08:00 已更新",
  };
}

export const wuxingHeroMock: WuxingHeroData = {
  solarDate: formatSolarDate(getShanghaiToday()),
  lunarDate: getMockLunarDate(getShanghaiToday()),
  ganzhiText: "年柱丙午 · 月柱甲午 · 日柱戊寅 · 时柱丙辰",
  updatedAt: "每日 08:00 已更新",
  eyebrow: "今日势能已更新",
  title: "今天什么行业更顺势？",
  subtitle: "五行代表动能，今日以土为主势，火与木提供放大和启动条件",
  mainElements: ["earth"],
  secondaryElements: ["fire", "wood"],
  centerTitle: "今日势能",
  centerMainText: "主势：土",
  explanation: "土主承载、聚合与转化落地；火带来显化和传播，木带来启动和生长。今天更利于把分散关注沉淀为稳定结构。",
  primaryAction: {
    label: "免费查看行业大类",
    href: "/categories",
  },
  secondaryAction: {
    label: "解锁今日细分行业",
    href: "/subcategory",
  },
  riskText: "本工具仅作文化分析和行业情绪参考，不构成投资建议，不承诺收益。",
};

export const testUnlockCode = "TEST123";

export const industryCategoriesMock: IndustryCategoryMock[] = [
  {
    categoryId: "digital",
    name: "数字科技",
    mainElement: "fire",
    secondaryElement: "metal",
    statusTag: "升温",
    freeSummary: "数字科技主五行偏火，副五行偏金。",
    freeAnalysis: [
      "火代表释放、传播、显化和用户感知。",
      "金代表规则、精密、硬件和标准成型。",
      "所以数字科技大类的核心动能，是把底层技术转化成用户可感知的效率、内容和产品结果。",
    ],
    paidHint: "解锁后查看数字科技下细分行业的完整五行动能报告。",
  },
  {
    categoryId: "advanced-manufacturing",
    name: "先进制造",
    mainElement: "metal",
    secondaryElement: "earth",
    statusTag: "平衡",
    freeSummary: "结构相对稳定，机器人、半导体设备、工业母机呈现分层观察特征。",
    freeAnalysis: [
      "主五行为金，代表秩序、效率和结构收敛。",
      "副五行为土，代表承载、稳定和节奏修复。",
    ],
    paidHint: "解锁后查看先进制造细分行业的结构变化和动能拆解。",
  },
  {
    categoryId: "green-energy",
    name: "绿色能源",
    mainElement: "wood",
    secondaryElement: "water",
    statusTag: "升温",
    freeSummary: "动能有扩散迹象，储能、光伏、液冷适合继续观察节奏变化。",
    freeAnalysis: [
      "主五行为木，代表启动、生长和方向扩散。",
      "副五行为水，代表流动、蓄势和节奏转换。",
    ],
    paidHint: "解锁后查看绿色能源下细分行业的完整报告和风险标签。",
  },
];

export const industrySubcategoriesMock: IndustrySubcategoryMock[] = [
  {
    subcategoryId: "ai-application",
    categoryId: "digital",
    name: "AI 应用",
    mainElement: "fire",
    secondaryElement: "wood",
    paidSummary: "关注度集中，重点观察应用入口、内容触达和场景转化链路。",
    fullReport: [
      "AI 应用体现火属性动能，传播效率高，用户注意力容易形成聚集。",
      "木属性作为副势，代表应用入口、产品迭代和用户连接能力正在形成承接。",
    ],
    riskTags: ["热度波动", "应用落地分化", "仅作情绪参考"],
  },
  {
    subcategoryId: "data-center",
    categoryId: "digital",
    name: "数据中心",
    mainElement: "earth",
    secondaryElement: "fire",
    paidSummary: "偏承载与放大，重点观察算力基础设施对上层应用的支撑。",
    fullReport: [
      "数据中心体现土属性承载，强调基础设施、稳定性和资源调度。",
      "火属性作为副势，代表需求侧关注度升温和计算场景扩散。",
    ],
    riskTags: ["建设节奏", "能耗约束", "需求验证"],
  },
  {
    subcategoryId: "memory-chip",
    categoryId: "digital",
    name: "存储芯片",
    mainElement: "metal",
    secondaryElement: "water",
    paidSummary: "偏结构与蓄势，重点观察供需修复和数据链条承接。",
    fullReport: [
      "存储芯片体现金属性结构，强调工艺、供给节奏和产业链秩序。",
      "水属性作为副势，代表数据流动和需求蓄势。",
    ],
    riskTags: ["周期波动", "价格敏感", "供需变化"],
  },
  {
    subcategoryId: "robotics",
    categoryId: "advanced-manufacturing",
    name: "机器人",
    mainElement: "metal",
    secondaryElement: "fire",
    paidSummary: "偏效率与关注度，重点观察制造场景和服务场景的动能分化。",
    fullReport: [
      "机器人体现（金）属性效率和结构升级，也受火属性关注度推动。",
      "当前观察重点在应用场景扩散、供应链成熟度和订单节奏。",
    ],
    riskTags: ["应用分化", "订单节奏", "估值情绪"],
  },
  {
    subcategoryId: "semiconductor-equipment",
    categoryId: "advanced-manufacturing",
    name: "半导体设备",
    mainElement: "metal",
    secondaryElement: "earth",
    paidSummary: "产业链位置偏上游，重点观察订单节奏、扩散度和五行联动。",
    fullReport: [
      "半导体设备以金属性为主，代表工艺秩序、效率提升和结构收敛。",
      "土属性承接带来稳定观察维度，适合结合先进制造大类节奏继续跟踪。",
    ],
    riskTags: ["订单验证", "国产替代节奏", "周期扰动"],
  },
  {
    subcategoryId: "industrial-machine",
    categoryId: "advanced-manufacturing",
    name: "工业母机",
    mainElement: "metal",
    secondaryElement: "wood",
    paidSummary: "偏结构升级与启动，重点观察制造链条的基础能力修复。",
    fullReport: [
      "工业母机体现制造底座的金属性秩序，强调精度、效率和产业链基础。",
      "木属性作为副势，代表更新启动和需求修复。",
    ],
    riskTags: ["更新节奏", "需求分层", "产业链验证"],
  },
  {
    subcategoryId: "energy-storage",
    categoryId: "green-energy",
    name: "储能",
    mainElement: "wood",
    secondaryElement: "water",
    paidSummary: "动能处在扩散观察区，重点关注细分方向分化。",
    fullReport: [
      "储能以木属性为主，体现启动、生长和系统连接能力。",
      "水属性提供蓄势视角，说明节奏变化需要结合周期和场景观察。",
    ],
    riskTags: ["项目节奏", "价格竞争", "政策变化"],
  },
  {
    subcategoryId: "photovoltaic",
    categoryId: "green-energy",
    name: "光伏",
    mainElement: "wood",
    secondaryElement: "fire",
    paidSummary: "偏启动与放大，重点观察供需改善和产业链传导。",
    fullReport: [
      "光伏体现木属性启动，产业链修复需要观察供需关系和价格节奏。",
      "火属性作为副势，代表阶段性关注度和转化触点增加。",
    ],
    riskTags: ["供需变化", "价格波动", "海外扰动"],
  },
  {
    subcategoryId: "liquid-cooling",
    categoryId: "green-energy",
    name: "液冷",
    mainElement: "water",
    secondaryElement: "metal",
    paidSummary: "偏流动与效率，重点观察算力基础设施中的散热需求。",
    fullReport: [
      "液冷体现水属性流动与调节，适合观察高密度计算场景下的需求扩散。",
      "金属性作为副势，代表设备效率、结构优化和工程化落地。",
    ],
    riskTags: ["需求验证", "技术路线", "交付节奏"],
  },
];

export function getCategoryById(categoryId: string) {
  return industryCategoriesMock.find((category) => category.categoryId === categoryId);
}

export function getSubcategoriesByCategoryId(categoryId: string) {
  return industrySubcategoriesMock.filter((subcategory) => subcategory.categoryId === categoryId);
}

export function getSubcategoryById(subcategoryId: string) {
  const mockSubcategory = industrySubcategoriesMock.find((subcategory) => subcategory.subcategoryId === subcategoryId);
  if (mockSubcategory) return mockSubcategory;

  const board = boardProfiles.find((item) => item.boardCode === subcategoryId);
  if (!board) return undefined;

  const fallbackCategoryId = board.categoryId === "needs-review" ? "digital" : board.categoryId;
  return {
    subcategoryId: board.boardCode,
    categoryId: fallbackCategoryId,
    name: board.boardName,
    mainElement: board.mainElement,
    secondaryElement: board.secondaryElement,
    paidSummary: board.reason || "该板块已接入本地五行标注数据，完整分析需要解锁查看。",
    fullReport: [
      board.reason || "该板块已接入本地五行标注数据，当前用于最小操作验证。",
      `板块类型：${board.boardType === "industry" ? "行业板块" : "概念板块"}。置信度：${board.confidence}。`,
    ],
    riskTags: [board.needReview ? "需要复核" : "已标注", "本地板块数据", "仅作情绪参考"],
  };
}
