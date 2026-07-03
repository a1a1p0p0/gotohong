export type ApiEnvelope<T> = {
  success: boolean;
  code: string;
  message: string;
  data: T;
  paywall: null | {
    required: boolean;
    message: string;
    next_action: string;
  };
  risk_notice: string;
};

export type WuxingElement = "wood" | "fire" | "earth" | "metal" | "water";

export type ElementIntensity = "main" | "secondary" | "muted";

export type WuxingElementMeta = {
  key: WuxingElement;
  label: string;
  color: string;
  path: string;
};

export type WuxingHeroData = {
  solarDate: string;
  lunarDate: string;
  ganzhiText: string;
  updatedAt: string;
  eyebrow: string;
  title: string;
  subtitle: string;
  mainElements: WuxingElement[];
  secondaryElements: WuxingElement[];
  centerTitle: string;
  centerMainText: string;
  explanation: string;
  primaryAction: {
    label: string;
    href: string;
  };
  secondaryAction: {
    label: string;
    href: string;
  };
  riskText: string;
};

export type IndustrySubcategoryMock = {
  subcategoryId: string;
  categoryId: string;
  name: string;
  mainElement: WuxingElement;
  secondaryElement: WuxingElement;
  paidSummary: string;
  fullReport: string[];
  riskTags: string[];
};

export type IndustryCategoryMock = {
  categoryId: string;
  name: string;
  mainElement: WuxingElement;
  secondaryElement: WuxingElement;
  statusTag: "升温" | "平衡" | "整理";
  freeSummary: string;
  freeAnalysis: string[];
  paidHint: string;
};

export type BoardType = "industry" | "concept";

export type BoardProfile = {
  boardCode: string;
  boardName: string;
  boardType: BoardType;
  categoryId: string;
  mainElement: WuxingElement;
  secondaryElement: WuxingElement;
  reason: string;
  needReview: boolean;
  confidence: number;
  updatedAt: string;
};
