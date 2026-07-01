-- SQLite schema.
-- All persistent data should be read/written through database.py.

CREATE TABLE IF NOT EXISTS app_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- Stores daily year/month/day wuxing calendar data.
CREATE TABLE IF NOT EXISTS calendar_ganzhi (
  date TEXT PRIMARY KEY,
  weekday TEXT NOT NULL,
  solar_term TEXT,
  lunar_year INTEGER NOT NULL,
  lunar_month INTEGER NOT NULL,
  lunar_day INTEGER NOT NULL,
  lunar_year_ganzhi TEXT NOT NULL,
  lichun_year_ganzhi TEXT NOT NULL,
  month_ganzhi TEXT NOT NULL,
  day_ganzhi TEXT NOT NULL,
  year_gan TEXT NOT NULL,
  year_zhi TEXT NOT NULL,
  month_gan TEXT NOT NULL,
  month_zhi TEXT NOT NULL,
  day_gan TEXT NOT NULL,
  day_zhi TEXT NOT NULL,
  year_element TEXT NOT NULL,
  month_element TEXT NOT NULL,
  day_element TEXT NOT NULL,
  main_element TEXT NOT NULL,
  secondary_element TEXT NOT NULL,
  source TEXT NOT NULL,
  verified TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  confidence INTEGER NOT NULL
);

-- Stores free top-level industry category wuxing profiles.
CREATE TABLE IF NOT EXISTS industry_categories (
  category_id TEXT PRIMARY KEY,
  category_name TEXT NOT NULL,
  main_element TEXT NOT NULL,
  secondary_element TEXT NOT NULL,
  wood_score INTEGER NOT NULL,
  fire_score INTEGER NOT NULL,
  earth_score INTEGER NOT NULL,
  metal_score INTEGER NOT NULL,
  water_score INTEGER NOT NULL,
  behavior_description TEXT NOT NULL,
  free_description TEXT,
  paid_hint TEXT,
  updated_at TEXT
);

-- Stores paid detailed industry/subcategory wuxing profiles.
CREATE TABLE IF NOT EXISTS industry_subcategories (
  subcategory_id TEXT PRIMARY KEY,
  category_id TEXT NOT NULL,
  subcategory_name TEXT NOT NULL,
  main_element TEXT NOT NULL,
  secondary_element TEXT NOT NULL,
  wood_score INTEGER NOT NULL,
  fire_score INTEGER NOT NULL,
  earth_score INTEGER NOT NULL,
  metal_score INTEGER NOT NULL,
  water_score INTEGER NOT NULL,
  industry_position TEXT,
  business_model TEXT,
  upstream_midstream_downstream TEXT,
  emotion_heat INTEGER,
  behavior_description TEXT NOT NULL,
  paid_description TEXT,
  risk_tags_json TEXT,
  updated_at TEXT,
  FOREIGN KEY(category_id) REFERENCES industry_categories(category_id)
);

-- Stores raw A-share industry and concept boards.
CREATE TABLE IF NOT EXISTS astock_boards (
  board_type TEXT NOT NULL,
  board_code TEXT NOT NULL,
  board_name TEXT NOT NULL,
  source TEXT NOT NULL,
  member_count INTEGER NOT NULL,
  updated_at TEXT NOT NULL,
  confidence INTEGER NOT NULL DEFAULT 100,
  PRIMARY KEY (board_type, board_code)
);

-- Stores raw component stocks of A-share boards.
CREATE TABLE IF NOT EXISTS astock_board_members (
  board_code TEXT NOT NULL,
  board_name TEXT NOT NULL,
  stock_code TEXT NOT NULL,
  stock_name TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'eastmoney_push2_clist',
  updated_at TEXT NOT NULL,
  confidence INTEGER NOT NULL DEFAULT 100,
  PRIMARY KEY (board_code, stock_code)
);

-- Stores wuxing classification results for each A-share industry/concept board.
CREATE TABLE IF NOT EXISTS astock_board_wuxing_profiles (
  board_code TEXT PRIMARY KEY,
  board_name TEXT NOT NULL,
  board_type TEXT NOT NULL,
  category TEXT,
  subcategory TEXT,
  main_element TEXT NOT NULL,
  secondary_element TEXT NOT NULL,
  wood_score INTEGER NOT NULL,
  fire_score INTEGER NOT NULL,
  earth_score INTEGER NOT NULL,
  metal_score INTEGER NOT NULL,
  water_score INTEGER NOT NULL,
  confidence INTEGER NOT NULL,
  reason TEXT NOT NULL,
  paid_required TEXT NOT NULL,
  source TEXT NOT NULL,
  updated_at TEXT,
  need_review TEXT NOT NULL DEFAULT 'false'
);

-- Stores monthly/weekly/daily favorable and balanced industry rankings.
CREATE TABLE IF NOT EXISTS period_industry_rankings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  period_type TEXT NOT NULL,
  period_key TEXT NOT NULL,
  ranking_type TEXT NOT NULL,
  rank_no INTEGER NOT NULL,
  board_code TEXT,
  board_name TEXT NOT NULL,
  board_type TEXT,
  category TEXT,
  subcategory TEXT,
  main_element TEXT NOT NULL,
  secondary_element TEXT NOT NULL,
  score INTEGER NOT NULL,
  reason TEXT NOT NULL,
  paid_required TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(period_type, period_key, ranking_type, rank_no)
);

CREATE TABLE IF NOT EXISTS payment_orders (
  order_no TEXT PRIMARY KEY,
  access_type TEXT NOT NULL,
  target_key TEXT NOT NULL,
  amount INTEGER NOT NULL,
  payment_channel TEXT NOT NULL,
  status TEXT NOT NULL,
  external_trade_no TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  paid_at TEXT
);

CREATE TABLE IF NOT EXISTS unlock_codes (
  code TEXT PRIMARY KEY,
  access_type TEXT NOT NULL,
  target_key TEXT NOT NULL,
  max_use_count INTEGER NOT NULL,
  used_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  order_no TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TEXT,
  FOREIGN KEY(order_no) REFERENCES payment_orders(order_no)
);

CREATE TABLE IF NOT EXISTS access_usage_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  access_type TEXT NOT NULL,
  target_key TEXT NOT NULL,
  unlock_code TEXT,
  action TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  note TEXT,
  FOREIGN KEY(unlock_code) REFERENCES unlock_codes(code)
);

CREATE TABLE IF NOT EXISTS reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  report_type TEXT NOT NULL,
  target_key TEXT NOT NULL,
  title TEXT,
  report_date TEXT,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usage_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  endpoint TEXT NOT NULL,
  access_type TEXT,
  target_key TEXT,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_calendar_ganzhi_month ON calendar_ganzhi(substr(date, 1, 7));
CREATE INDEX IF NOT EXISTS idx_astock_boards_type ON astock_boards(board_type);
CREATE INDEX IF NOT EXISTS idx_astock_board_members_board ON astock_board_members(board_code);
CREATE INDEX IF NOT EXISTS idx_period_rankings_lookup
  ON period_industry_rankings(period_type, period_key, ranking_type);
CREATE INDEX IF NOT EXISTS idx_reports_user ON reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_user_created ON reports(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_usage_logs_endpoint ON usage_logs(endpoint);
