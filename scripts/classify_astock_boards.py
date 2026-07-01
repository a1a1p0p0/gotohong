"""Classify synced A-share boards into wuxing profiles.

This script reads synced raw board CSV files and local industry mapping JSON.
It does not make investment conclusions and does not classify only by board
name. The score combines board metadata, matched category/subcategory profiles,
industry position, business model, board type, member count, and matched
keywords. Uncertain boards are marked as need_review instead of being forced
into a wuxing conclusion.
"""

from __future__ import annotations

import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wuxing_stock_app import database

DATA_DIR = PROJECT_ROOT / "data"
APP_DATA_DIR = PROJECT_ROOT / "wuxing_stock_app" / "data"

INDUSTRY_RAW_CSV = DATA_DIR / "astock_industry_raw.csv"
CONCEPT_RAW_CSV = DATA_DIR / "astock_concept_raw.csv"
CATEGORIES_JSON = APP_DATA_DIR / "industry_categories.json"
SUBCATEGORIES_JSON = APP_DATA_DIR / "industry_subcategories.json"
OUTPUT_CSV = DATA_DIR / "astock_board_wuxing_profiles.csv"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "classify_astock_boards.log"

SOURCE = "local_industry_mapping_rules"
REVIEW_CONFIDENCE_THRESHOLD = 60
ELEMENTS = ("wood", "fire", "earth", "metal", "water")
OUTPUT_FIELDS = [
    "board_code",
    "board_name",
    "board_type",
    "category",
    "subcategory",
    "main_element",
    "secondary_element",
    "wood_score",
    "fire_score",
    "earth_score",
    "metal_score",
    "water_score",
    "confidence",
    "reason",
    "paid_required",
    "source",
    "updated_at",
    "need_review",
]

TEXT_ELEMENT_KEYWORDS = {'wood': ['研发', '创新', '成长', '扩张', '生物', '医药', '农业', '种业', '教育', '软件', '机器人', '风电', '氢能'],
 'fire': ['传播', '营销', '传媒', '消费', '旅游', '品牌', '应用', '娱乐', '热度', '广告', '游戏', '影视', '短剧', '光伏', 'CPO'],
 'earth': ['平台', '基础设施', '基建', '地产', '供应链', '承载', '整合', '数据中心', '物流', '物业', '建筑', '水利'],
 'metal': ['制造', '硬件', '精密', '设备', '标准', '规则', '半导体', '芯片', '军工', '机械', 'PCB', '器械', '有色', '稀土', '黄金'],
 'water': ['数据', '云', '流动', '资金', '金融', '储能', '能源', '交通', '贸易', '存储', '银行', '保险', '航运', '水处理']}

POSITION_ELEMENT_HINTS = {'上游': {'earth': 4, 'water': 3},
 '中游': {'metal': 4, 'earth': 3},
 '下游': {'fire': 4, 'earth': 2},
 '全产业链': {'earth': 4, 'water': 2, 'metal': 2}}

BUSINESS_MODEL_HINTS = {'研发': {'wood': 4},
 '创新': {'wood': 4},
 '订阅': {'water': 2, 'earth': 2},
 '制造': {'metal': 5},
 '设备': {'metal': 4},
 '平台': {'earth': 5},
 '供应链': {'earth': 4},
 '运营': {'earth': 3},
 '营销': {'fire': 4},
 '品牌': {'fire': 4},
 '数据': {'water': 4},
 '资金': {'water': 4},
 '储备': {'water': 4}}

BOARD_PROFILE_ALIASES = {'创新药': 'medicine_innovative_drug',
 '化学制药': 'medicine_innovative_drug',
 '化学制剂': 'medicine_innovative_drug',
 '原料药': 'medicine_innovative_drug',
 '生物制品': 'medicine_vaccine',
 '血液制品': 'medicine_vaccine',
 '医疗研发外包': 'medicine_cro',
 'CRO': 'medicine_cro',
 '医疗服务': 'medicine_device',
 '医疗设备': 'medicine_device',
 '医疗耗材': 'medicine_device',
 '医疗美容': 'consumer_beauty',
 '医美': 'consumer_beauty',
 '宠物': 'consumer_pet',
 '空调': 'consumer_home_appliance',
 '家电': 'consumer_home_appliance',
 '白酒': 'consumer_liquor',
 '食品': 'consumer_food_beverage',
 '饮料': 'consumer_food_beverage',
 '乳品': 'consumer_food_beverage',
 '旅游': 'consumer_tourism',
 '酒店': 'consumer_tourism',
 '免税': 'consumer_duty_free',
 '零售': 'consumer_retail',
 '商贸': 'consumer_retail',
 '半导体': 'tech_semiconductor',
 '芯片': 'tech_semiconductor',
 '集成电路': 'tech_semiconductor',
 '分立器件': 'tech_semiconductor',
 '存储': 'tech_storage_chip',
 '光模块': 'tech_optical_module',
 'CPO': 'tech_cpo',
 '液冷': 'tech_liquid_cooling',
 '数据中心': 'tech_data_center',
 '云计算': 'tech_cloud',
 '软件': 'tech_software',
 '机器人': 'tech_robotics',
 'AI': 'tech_ai_application',
 '人工智能': 'tech_ai_application',
 '煤': 'energy_coal',
 '石油': 'energy_oil',
 '天然气': 'energy_gas',
 '光伏': 'energy_pv',
 '逆变器': 'energy_pv',
 '风电': 'energy_wind',
 '储能': 'energy_storage',
 '氢能': 'energy_hydrogen',
 '银行': 'finance_bank',
 '证券': 'finance_broker',
 '保险': 'finance_insurance',
 '支付': 'finance_fintech',
 '金融科技': 'finance_fintech',
 '地产': 'real_estate_development',
 '物业': 'real_estate_property',
 '工程机械': 'manufacturing_engineering_machinery',
 '工业母机': 'manufacturing_machine_tool',
 '自动化': 'manufacturing_automation',
 '农机': 'agriculture_farm_machine',
 '种业': 'agriculture_seed',
 '养殖': 'agriculture_breeding',
 '游戏': 'media_game',
 '影视': 'media_film_tv',
 '广告': 'media_advertising',
 '短剧': 'media_short_drama',
 '航运': 'transport_shipping',
 '航空': 'transport_airline',
 '快递': 'transport_express',
 '物流': 'transport_express',
 '军工': 'defense_avionics',
 '卫星': 'defense_satellite',
 '无人机': 'defense_drone',
 '有色': 'resources_nonferrous',
 '铜': 'resources_nonferrous',
 '铝': 'resources_nonferrous',
 '稀土': 'resources_rare_earth',
 '黄金': 'resources_gold',
 '建筑': 'infrastructure_construction',
 '轨交': 'infrastructure_rail',
 '水利': 'infrastructure_water',
 '电网': 'infrastructure_power_grid',
 '水处理': 'environment_water_treatment',
 '固废': 'environment_solid_waste',
 '碳中和': 'environment_carbon_neutral',
 '再生资源': 'environment_recycling'}

BOARD_PROFILE_ALIASES.update({
    "\u8bca\u65ad": "medicine_device",
    "\u533b\u9662": "medicine_device",
    "\u836f\u5e97": "medicine_tcm",
    "\u52a8\u7269\u4fdd\u5065": "medicine_tcm",
    "\u9972\u6599": "agriculture_breeding",
    "\u79cd\u690d": "agriculture_seed",
    "\u519c\u6797\u7267\u6e14": "agriculture_breeding",
    "\u6c34\u4ea7": "agriculture_breeding",
    "\u6e14\u4e1a": "agriculture_breeding",
    "\u666f\u533a": "consumer_tourism",
    "\u9910\u996e": "consumer_food_beverage",
    "\u5564\u9152": "consumer_food_beverage",
    "\u8c03\u5473": "consumer_food_beverage",
    "\u96f6\u98df": "consumer_food_beverage",
    "\u4e2a\u62a4": "consumer_beauty",
    "\u6d17\u62a4": "consumer_beauty",
    "\u7f8e\u5bb9\u62a4\u7406": "consumer_beauty",
    "\u73e0\u5b9d": "resources_gold",
    "\u9970\u54c1": "resources_gold",
    "\u8d35\u91d1\u5c5e": "resources_gold",
    "\u767d\u94f6": "resources_gold",
    "\u94bc": "resources_nonferrous",
    "\u954d": "resources_nonferrous",
    "\u9502": "resources_nonferrous",
    "\u94b4": "resources_nonferrous",
    "\u94c5\u950c": "resources_nonferrous",
    "\u5c0f\u91d1\u5c5e": "resources_nonferrous",
    "\u94a2\u94c1": "resources_nonferrous",
    "\u666e\u94a2": "resources_nonferrous",
    "\u957f\u6750": "resources_nonferrous",
    "\u94c1\u77ff\u77f3": "resources_nonferrous",
    "\u6c1f\u5316\u5de5": "resources_nonferrous",
    "\u7eaf\u78b1": "resources_nonferrous",
    "\u6c2f\u78b1": "resources_nonferrous",
    "\u94be\u80a5": "resources_nonferrous",
    "\u590d\u5408\u80a5": "resources_nonferrous",
    "\u6709\u673a\u7845": "resources_nonferrous",
    "\u5408\u6210\u6811\u8102": "resources_nonferrous",
    "\u9020\u7eb8": "manufacturing_engineering_machinery",
    "\u5305\u88c5": "manufacturing_engineering_machinery",
    "\u7eba\u7ec7": "consumer_retail",
    "\u670d\u88c5": "consumer_retail",
    "\u5bb6\u5c45": "consumer_home_appliance",
    "\u53a8\u536b": "consumer_home_appliance",
    "\u536b\u6d74": "consumer_home_appliance",
    "\u5f69\u7535": "consumer_home_appliance",
    "\u51b0\u6d17": "consumer_home_appliance",
    "\u4e58\u7528\u8f66": "manufacturing_engineering_machinery",
    "\u5546\u7528\u8f66": "manufacturing_engineering_machinery",
    "\u6469\u6258\u8f66": "manufacturing_engineering_machinery",
    "\u94c1\u8def": "transport_express",
    "\u516c\u8def": "transport_express",
    "\u6e2f\u53e3": "transport_shipping",
    "\u673a\u573a": "transport_airline",
    "\u71c3\u6c14": "energy_gas",
    "\u53d1\u7535": "energy_pv",
    "\u7535\u529b": "infrastructure_power_grid",
    "\u7535\u4fe1": "tech_cloud",
    "\u51fa\u7248": "media_film_tv",
    "\u5a92\u4f53": "media_film_tv",
    "\u9662\u7ebf": "media_film_tv",
    "\u6587\u5a31": "media_game",
    "\u6587\u5316": "media_game",
    "\u6559\u80b2": "media_advertising",
    "\u4eba\u529b\u8d44\u6e90": "consumer_retail",
    "\u4f1a\u5c55": "media_advertising",
    "\u73af\u5883": "environment_solid_waste",
    "\u73af\u4fdd": "environment_solid_waste",
    "\u6c34\u52a1": "environment_water_treatment",
    "\u5de5\u7a0b\u54a8\u8be2": "infrastructure_construction",
    "\u4e13\u4e1a\u5de5\u7a0b": "infrastructure_construction",
    "\u94a2\u7ed3\u6784": "infrastructure_construction",
    "\u91d1\u5c5e\u5236\u54c1": "manufacturing_machine_tool",
})


BOARD_PROFILE_ALIASES.update({
    "\u6a61\u80f6": "resources_nonferrous",
    "\u6a61\u80f6\u52a9\u5242": "resources_nonferrous",
    "\u8f85\u6599": "resources_nonferrous",
    "\u751f\u6d3b\u7528\u7eb8": "consumer_retail",
    "\u7528\u7eb8": "consumer_retail",
    "\u9152\u7c7b": "consumer_liquor",
    "\u6cb9\u7530\u670d\u52a1": "energy_oil",
    "\u6cb9\u670d": "energy_oil",
    "\u6cb9\u6c14": "energy_oil",
    "\u7535\u5b50\u5316\u5b66\u54c1": "resources_nonferrous",
    "\u7535\u6c60\u5316\u5b66\u54c1": "resources_nonferrous",
    "\u5316\u5b66\u54c1": "resources_nonferrous",
    "\u5316\u5b66\u539f\u6599": "resources_nonferrous",
    "\u5316\u5b66\u5236\u54c1": "resources_nonferrous",
    "\u57fa\u7840\u5316\u5de5": "resources_nonferrous",
    "\u70bc\u5316": "energy_oil",
    "\u70ad\u9ed1": "resources_nonferrous",
    "\u519c\u5316": "resources_nonferrous",
    "\u7845\u6599": "energy_pv",
    "\u7845\u7247": "energy_pv",
    "\u767e\u8d27": "consumer_retail",
    "\u8d85\u5e02": "consumer_retail",
    "\u7535\u5546": "consumer_retail",
    "\u4e13\u4e1a\u8fde\u9501": "consumer_retail",
    "\u5316\u5986\u54c1": "consumer_beauty",
    "\u719f\u98df": "consumer_food_beverage",
    "\u7cae\u6cb9": "consumer_food_beverage",
    "\u8089\u5236\u54c1": "consumer_food_beverage",
    "\u4fdd\u5065\u54c1": "medicine_tcm",
    "\u677f\u6750": "resources_nonferrous",
    "\u7ba1\u6750": "resources_nonferrous",
    "\u5de5\u4e1a\u91d1\u5c5e": "resources_nonferrous",
    "\u51b6\u94a2": "resources_nonferrous",
    "\u7279\u94a2": "resources_nonferrous",
    "\u7279\u79cd\u7eb8": "consumer_retail",
    "\u5546\u7528\u8f7d\u8d27\u8f66": "manufacturing_engineering_machinery",
    "\u5546\u7528\u8f7d\u5ba2\u8f66": "manufacturing_engineering_machinery",
    "\u6c7d\u8f66": "manufacturing_engineering_machinery",
    "\u6c7d\u8f66\u96f6\u90e8\u4ef6": "manufacturing_engineering_machinery",
    "\u8f66\u8eab": "manufacturing_engineering_machinery",
    "\u5e95\u76d8": "manufacturing_engineering_machinery",
    "\u53d1\u52a8\u673a": "manufacturing_engineering_machinery",
    "\u8f6e\u80ce": "manufacturing_engineering_machinery",
    "\u53a8\u623f\u7535\u5668": "consumer_home_appliance",
    "\u5bb6\u7528\u7535\u5668": "consumer_home_appliance",
    "\u5bb6\u7eba": "consumer_retail",
    "\u68c9\u7eba": "consumer_retail",
    "\u6da4\u7eb6": "consumer_retail",
    "\u9526\u7eb6": "consumer_retail",
    "\u7c98\u80f6": "consumer_retail",
    "\u6797\u4e1a": "agriculture_seed",
    "\u79cd\u5b50": "agriculture_seed",
    "\u519c\u4ea7\u54c1\u52a0\u5de5": "consumer_food_beverage",
    "\u679c\u852c": "consumer_food_beverage",
    "\u98df\u7528\u83cc": "consumer_food_beverage",
    "\u6d77\u6d0b\u6355\u635e": "agriculture_breeding",
    "\u7126\u70ad": "energy_coal",
    "\u4fe1\u6258": "finance_insurance",
    "\u8d44\u4ea7\u7ba1\u7406": "finance_insurance",
    "\u671f\u8d27": "finance_broker",
    "\u519c\u5546\u884c": "finance_bank",
    "\u57ce\u5546\u884c": "finance_bank",
    "\u4eea\u5668\u4eea\u8868": "manufacturing_machine_tool",
    "\u7535\u5de5\u4eea\u5668\u4eea\u8868": "manufacturing_machine_tool",
    "\u7ebf\u7f06": "infrastructure_power_grid",
    "\u7535\u80fd": "infrastructure_power_grid",
    "\u7535\u6c60": "energy_storage",
    "\u7535\u5b50": "tech_semiconductor",
    "\u8ba1\u7b97\u673a": "tech_software",
    "IT\u670d\u52a1": "tech_software",
    "\u95e8\u6237\u7f51\u7ad9": "media_advertising",
    "\u7535\u89c6\u5e7f\u64ad": "media_film_tv",
    "\u5a31\u4e50\u7528\u54c1": "media_game",
    "\u4f53\u80b2": "media_game",
    "\u5370\u5237": "manufacturing_engineering_machinery",
    "\u5efa\u6750": "infrastructure_construction",
    "\u6c34\u6ce5": "infrastructure_construction",
    "\u88c5\u4fee": "infrastructure_construction",
    "\u74f7\u7816": "infrastructure_construction",
    "\u8010\u706b\u6750\u6599": "resources_nonferrous",
    "\u57fa\u7840\u5efa\u8bbe": "infrastructure_construction",
    "\u623f\u5c4b\u5efa\u8bbe": "infrastructure_construction",
    "\u822a\u6d77\u88c5\u5907": "defense_avionics",
    "\u822a\u5929\u88c5\u5907": "defense_satellite",
    "\u6c11\u7206": "defense_avionics",
    "\u5149\u5b66": "tech_optical_module",
    "\u9762\u677f": "tech_semiconductor",
    "\u516c\u4ea4": "transport_express",
    "\u516c\u7528\u4e8b\u4e1a": "infrastructure_power_grid",
    "\u793e\u4f1a\u670d\u52a1": "consumer_tourism",
    "\u79df\u8d41": "consumer_retail",
    "\u4e13\u4e1a\u670d\u52a1": "consumer_retail",
    "\u6c2e\u80a5": "resources_nonferrous",
    "\u78f7\u80a5": "resources_nonferrous",
    "\u519c\u836f": "resources_nonferrous",
    "\u65e0\u673a\u76d0": "resources_nonferrous",
    "\u77f3\u5316": "energy_oil",
    "\u70bc\u6cb9\u5316\u5de5": "energy_oil",
    "\u8d38\u6613": "consumer_retail",
    "\u5316\u5b66\u7ea4\u7ef4": "consumer_retail",
    "\u5370\u67d3": "consumer_retail",
    "\u80f6\u9ecf\u5242": "resources_nonferrous",
    "\u80f6\u5e26": "resources_nonferrous",
    "\u6d82\u6599": "resources_nonferrous",
    "\u6cb9\u58a8": "resources_nonferrous",
    "\u5851\u6599": "resources_nonferrous",
    "\u805a\u6c28\u916f": "resources_nonferrous",
    "\u819c\u6750\u6599": "resources_nonferrous",
    "\u949b\u767d\u7c89": "resources_nonferrous",
    "\u94a8": "resources_nonferrous",
    "\u78c1\u6027\u6750\u6599": "resources_nonferrous",
    "\u975e\u91d1\u5c5e\u6750\u6599": "resources_nonferrous",
    "\u91d1\u5c5e\u65b0\u6750\u6599": "resources_nonferrous",
    "\u78e8\u5177\u78e8\u6599": "manufacturing_machine_tool",
    "\u673a\u5e8a\u5de5\u5177": "manufacturing_machine_tool",
    "\u7535\u673a": "manufacturing_automation",
    "\u88ab\u52a8\u5143\u4ef6": "tech_semiconductor",
    "\u5143\u4ef6": "tech_semiconductor",
    "\u5370\u5236\u7535\u8def\u677f": "tech_pcb",
    "LED": "tech_semiconductor",
    "\u901a\u4fe1": "tech_cloud",
    "\u901a\u4fe1\u5de5\u7a0b": "tech_cloud",
    "\u901a\u4fe1\u670d\u52a1": "tech_cloud",
    "\u901a\u4fe1\u7ec8\u7aef": "tech_cloud",
    "\u5730\u9762\u5175\u88c5": "defense_avionics",
    "\u70ed\u529b\u670d\u52a1": "energy_gas",
    "\u56ed\u6797\u5de5\u7a0b": "infrastructure_construction",
    "\u5927\u6c14\u6cbb\u7406": "environment_solid_waste",
    "\u68c0\u6d4b\u670d\u52a1": "medicine_device",
    "\u91cd\u7ec4\u86cb\u767d": "medicine_innovative_drug",
    "\u51cf\u80a5\u836f": "medicine_innovative_drug",
    "\u5355\u6297": "medicine_innovative_drug",
    "CAR-T": "medicine_innovative_drug",
    "\u809d\u7d20": "medicine_innovative_drug",
    "\u963f\u5179\u6d77\u9ed8": "medicine_innovative_drug",
    "\u514d\u75ab\u6cbb\u7597": "medicine_innovative_drug",
    "\u72ec\u5bb6\u836f\u54c1": "medicine_tcm",
    "\u809d\u708e": "medicine_innovative_drug",
    "\u7279\u8272\u836f": "medicine_tcm",
    "\u75c5\u6bd2\u9632\u6cbb": "medicine_innovative_drug",
    "\u75c5\u539f\u4f53\u9632\u6cbb": "medicine_innovative_drug",
    "\u5e7d\u95e8\u87ba\u6746\u83cc": "medicine_innovative_drug",
    "\u6d41\u611f": "medicine_vaccine",
    "\u7ef4\u751f\u7d20": "medicine_tcm",
    "\u8f85\u52a9\u751f\u6b96": "medicine_device",
    "\u9752\u84bf\u7d20": "medicine_tcm",
    "\u7cbe\u51c6\u533b\u7597": "medicine_device",
    "\u57fa\u56e0\u6d4b\u5e8f": "medicine_device",
    "\u957f\u5bff\u836f": "medicine_innovative_drug",
    "\u6bdb\u53d1\u533b\u7597": "consumer_beauty",
    "\u5408\u6210\u751f\u7269": "medicine_innovative_drug",
    "\u4e92\u8054\u533b\u7597": "medicine_device",
    "\u51c0\u6c34": "environment_water_treatment",
    "\u5de5\u4e1a\u6c14\u4f53": "resources_nonferrous",
    "\u6c26\u6c14": "resources_nonferrous",
    "\u53ef\u63a7\u6838\u805a\u53d8": "energy_hydrogen",
    "\u4f4e\u78b3\u51b6\u91d1": "resources_nonferrous",
    "\u7a00\u7f3a\u8d44\u6e90": "resources_nonferrous",
    "\u8d44\u6e90\u5f00\u91c7": "resources_nonferrous",
    "\u5149\u523b\u673a": "tech_semiconductor",
    "\u78b3\u5316\u7845": "tech_semiconductor",
    "\u6c2e\u5316\u9553": "tech_semiconductor",
    "IGBT": "tech_semiconductor",
    "\u9ad8\u5e26\u5bbd\u5185\u5b58": "tech_storage_chip",
    "PVDF": "resources_nonferrous",
    "\u4eba\u8111\u5de5\u7a0b": "tech_ai_application",
    "\u5de5\u4e1a\u5927\u9ebb": "agriculture_seed",
    "\u732a\u8089": "agriculture_breeding",
    "\u9e21\u8089": "agriculture_breeding",
    "\u8f6c\u57fa\u56e0": "agriculture_seed",
    "\u917f\u9152": "consumer_liquor",
    "\u7a7a\u6c14\u80fd\u70ed\u6cf5": "consumer_home_appliance",
    "\u793e\u533a\u56e2\u8d2d": "consumer_retail",
    "\u9000\u7a0e\u5546\u5e97": "consumer_retail",
    "\u51b0\u96ea\u7ecf\u6d4e": "consumer_tourism",
    "\u76f2\u76d2": "consumer_blind_box",
    "\u4e73\u4e1a": "consumer_food_beverage",
    "\u5a74\u7ae5": "consumer_food_beverage",
})


def main() -> None:
    setup_logging()
    rows = classify_astock_boards()
    print(f"Classified {len(rows)} boards: {OUTPUT_CSV}")


def classify_astock_boards(
    *,
    industry_csv: Path | str = INDUSTRY_RAW_CSV,
    concept_csv: Path | str = CONCEPT_RAW_CSV,
    categories_json: Path | str = CATEGORIES_JSON,
    subcategories_json: Path | str = SUBCATEGORIES_JSON,
    output_csv: Path | str = OUTPUT_CSV,
    updated_at: str | None = None,
    db_path: Path | str = database.DB_PATH,
) -> list[dict[str, Any]]:
    setup_logging()
    updated_at = updated_at or datetime.now().replace(microsecond=0).isoformat()
    logging.info("step=classification_start")
    categories = load_json_list(categories_json)
    subcategories = load_json_list(subcategories_json)
    logging.info("step=mapping_profiles_loaded categories=%s subcategories=%s", len(categories), len(subcategories))
    profiles = build_mapping_profiles(categories, subcategories)
    boards = load_board_rows(industry_csv) + load_board_rows(concept_csv)
    logging.info("step=raw_boards_loaded count=%s", len(boards))
    classified = [classify_board(board, profiles, updated_at=updated_at) for board in boards]
    database.initialize_database(db_path)
    ensure_wuxing_profile_schema(db_path)
    save_profiles_to_sqlite(classified, db_path=db_path)
    logging.info("step=classification_sqlite_written count=%s", len(classified))
    write_csv(Path(output_csv), classified)
    logging.info(
        "step=classification_csv_written path=%s count=%s need_review=%s",
        output_csv,
        len(classified),
        sum(1 for row in classified if row["need_review"] == "true"),
    )
    return classified


def load_board_rows(path: Path | str) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_json_list(path: Path | str) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"expected list json: {path}")
    return data


def build_mapping_profiles(
    categories: list[dict[str, Any]],
    subcategories: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    category_by_id = {item["category_id"]: item for item in categories}
    profiles: list[dict[str, Any]] = []
    for category in categories:
        profiles.append(
            {
                "level": "category",
                "category_id": category.get("category_id", ""),
                "subcategory_id": "",
                "category": category.get("category_name", ""),
                "subcategory": "",
                "paid_required": False,
                "element_scores": category.get("element_scores", {}),
                "industry_position": "",
                "business_model": "",
                "text": profile_text(category),
}

        )
    for subcategory in subcategories:
        category = category_by_id.get(subcategory.get("category_id", ""), {})
        profiles.append(
            {
                "level": "subcategory",
                "category_id": subcategory.get("category_id", ""),
                "subcategory_id": subcategory.get("subcategory_id", ""),
                "category": category.get("category_name", subcategory.get("category_id", "")),
                "subcategory": subcategory.get("subcategory_name", ""),
                "paid_required": True,
                "element_scores": subcategory.get("element_scores", {}),
                "industry_position": subcategory.get("industry_position", ""),
                "business_model": subcategory.get("business_model", ""),
                "text": profile_text(category) + " " + profile_text(subcategory),
            }
        )
    return profiles


def classify_board(board: dict[str, str], profiles: list[dict[str, Any]], *, updated_at: str) -> dict[str, Any]:
    board_name = board.get("board_name", "").strip()
    board_type = board.get("board_type", "").strip()
    member_count = parse_int(board.get("member_count", "0"))
    best_profile, matched_keywords = find_best_profile(board_name, profiles)
    scores = base_scores(best_profile)

    apply_board_type_modifier(scores, board_type)
    apply_member_count_modifier(scores, member_count)
    apply_keyword_modifiers(scores, matched_keywords)
    apply_position_modifier(scores, best_profile.get("industry_position", ""))
    apply_business_model_modifier(scores, best_profile.get("business_model", ""))

    normalized_scores = normalize_scores(scores)
    main_element, secondary_element = top_two_elements(normalized_scores)
    confidence = calculate_confidence(
        normalized_scores,
        matched_keywords=matched_keywords,
        matched_level=best_profile.get("level", ""),
        member_count=member_count,
    )
    need_review = should_need_review(confidence, matched_keywords, best_profile)

    if need_review:
        category = "need_review"
        subcategory = ""
        main_element = "need_review"
        secondary_element = "need_review"
    else:
        category = best_profile.get("category", "")
        subcategory = best_profile.get("subcategory", "")

    return {
        "board_code": board.get("board_code", "").strip(),
        "board_name": board_name,
        "board_type": board_type,
        "category": category,
        "subcategory": subcategory,
        "main_element": main_element,
        "secondary_element": secondary_element,
        "wood_score": normalized_scores["wood"],
        "fire_score": normalized_scores["fire"],
        "earth_score": normalized_scores["earth"],
        "metal_score": normalized_scores["metal"],
        "water_score": normalized_scores["water"],
        "confidence": confidence,
        "reason": build_reason(board, best_profile, matched_keywords, need_review=need_review),
        "paid_required": str(bool(best_profile.get("paid_required"))).lower(),
        "source": SOURCE,
        "updated_at": updated_at,
        "need_review": str(need_review).lower(),
    }


def find_best_profile(board_name: str, profiles: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    profile_by_subcategory_id = {
        profile.get("subcategory_id"): profile
        for profile in profiles
        if profile.get("subcategory_id")
    }
    for keyword, subcategory_id in BOARD_PROFILE_ALIASES.items():
        if keyword in board_name and subcategory_id in profile_by_subcategory_id:
            return profile_by_subcategory_id[subcategory_id], [keyword]

    best_profile = profiles[0] if profiles else default_profile()
    best_keywords: list[str] = []
    best_score = -1
    for profile in profiles:
        keywords = match_keywords(board_name, profile["text"])
        score = len(keywords) * (3 if profile["level"] == "subcategory" else 2)
        if profile.get("subcategory") and profile["subcategory"] in board_name:
            score += 6
            keywords.append(profile["subcategory"])
        if profile.get("category") and profile["category"] in board_name:
            score += 4
            keywords.append(profile["category"])
        if score > best_score:
            best_profile = profile
            best_keywords = sorted(set(keywords))
            best_score = score
    return best_profile, best_keywords


def match_keywords(board_name: str, profile_text_value: str) -> list[str]:
    keywords = []
    for element_keywords in TEXT_ELEMENT_KEYWORDS.values():
        for keyword in element_keywords:
            if keyword in board_name and keyword in profile_text_value:
                keywords.append(keyword)
    return keywords


def base_scores(profile: dict[str, Any]) -> dict[str, float]:
    raw_scores = profile.get("element_scores") or {}
    return {element: float(raw_scores.get(element, 20)) for element in ELEMENTS}


def apply_board_type_modifier(scores: dict[str, float], board_type: str) -> None:
    if board_type == "concept":
        scores["fire"] += 4
        scores["wood"] += 2
    elif board_type == "industry":
        scores["earth"] += 3
        scores["metal"] += 2


def apply_member_count_modifier(scores: dict[str, float], member_count: int) -> None:
    if member_count >= 80:
        scores["earth"] += 5
    elif 30 <= member_count < 80:
        scores["earth"] += 3
        scores["water"] += 2
    elif 0 < member_count < 30:
        scores["wood"] += 3
        scores["fire"] += 2


def apply_keyword_modifiers(scores: dict[str, float], matched_keywords: list[str]) -> None:
    for keyword in matched_keywords:
        for element, keywords in TEXT_ELEMENT_KEYWORDS.items():
            if keyword in keywords:
                scores[element] += 3


def apply_position_modifier(scores: dict[str, float], industry_position: str) -> None:
    for keyword, modifiers in POSITION_ELEMENT_HINTS.items():
        if keyword in industry_position:
            for element, value in modifiers.items():
                scores[element] += value


def apply_business_model_modifier(scores: dict[str, float], business_model: str) -> None:
    for keyword, modifiers in BUSINESS_MODEL_HINTS.items():
        if keyword in business_model:
            for element, value in modifiers.items():
                scores[element] += value


def normalize_scores(scores: dict[str, float]) -> dict[str, int]:
    total = sum(max(value, 0) for value in scores.values())
    if total <= 0:
        return {element: 20 for element in ELEMENTS}
    normalized = {element: round(max(scores[element], 0) / total * 100) for element in ELEMENTS}
    diff = 100 - sum(normalized.values())
    normalized[max(normalized, key=normalized.get)] += diff
    return normalized


def top_two_elements(scores: dict[str, int]) -> tuple[str, str]:
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return ranked[0][0], ranked[1][0]


def calculate_confidence(
    scores: dict[str, int],
    *,
    matched_keywords: list[str],
    matched_level: str,
    member_count: int,
) -> int:
    ranked = sorted(scores.values(), reverse=True)
    separation = ranked[0] - ranked[1]
    confidence = 35 + min(25, separation) + min(20, len(matched_keywords) * 5)
    if matched_level == "subcategory":
        confidence += 10
    if matched_level == "subcategory" and matched_keywords:
        confidence += 15
    if member_count > 0:
        confidence += 5
    return max(0, min(100, confidence))


def should_need_review(
    confidence: int,
    matched_keywords: list[str],
    profile: dict[str, Any],
) -> bool:
    if confidence < REVIEW_CONFIDENCE_THRESHOLD:
        return True
    if not matched_keywords and profile.get("level") != "subcategory":
        return True
    return False


def build_reason(
    board: dict[str, str],
    profile: dict[str, Any],
    matched_keywords: list[str],
    *,
    need_review: bool,
) -> str:
    keyword_text = "、".join(matched_keywords) if matched_keywords else "无明显关键词"
    parts = [
        f"board_type={board.get('board_type', '')}",
        f"member_count={board.get('member_count', '0')}",
        f"matched_keywords={keyword_text}",
        f"category={profile.get('category', '')}",
    ]
    if profile.get("subcategory"):
        parts.append(f"subcategory={profile.get('subcategory')}")
    if profile.get("industry_position"):
        parts.append(f"industry_position={profile.get('industry_position')}")
    if profile.get("business_model"):
        parts.append(f"business_model={profile.get('business_model')}")
    if need_review:
        parts.append("need_review=true")
    return "；".join(parts)


def profile_text(profile: dict[str, Any]) -> str:
    values = []
    for key in (
        "category_name",
        "subcategory_name",
        "description",
        "keywords",
        "industry_position",
        "business_model",
        "upstream_midstream_downstream",
        "behavior_description",
        "free_description",
        "paid_description",
    ):
        value = profile.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        elif value:
            values.append(str(value))
    return " ".join(values)


def parse_int(value: Any) -> int:
    try:
        return int(float(str(value).strip() or 0))
    except ValueError:
        return 0


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in OUTPUT_FIELDS} for row in rows])


def save_profiles_to_sqlite(rows: list[dict[str, Any]], *, db_path: Path | str = database.DB_PATH) -> None:
    database.execute_many(
        """
        INSERT OR REPLACE INTO astock_board_wuxing_profiles (
          board_code, board_name, board_type, category, subcategory,
          main_element, secondary_element, wood_score, fire_score, earth_score,
          metal_score, water_score, confidence, reason, paid_required,
          source, updated_at, need_review
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            tuple(row[field] for field in OUTPUT_FIELDS)
            for row in rows
        ],
        db_path,
    )


def ensure_wuxing_profile_schema(db_path: Path | str = database.DB_PATH) -> None:
    existing = {
        row["name"]
        for row in database.fetch_all("PRAGMA table_info(astock_board_wuxing_profiles)", db_path=db_path)
    }
    for column, ddl in {
        "source": f"TEXT NOT NULL DEFAULT '{SOURCE}'",
        "need_review": "TEXT NOT NULL DEFAULT 'false'",
    }.items():
        if column not in existing:
            database.execute(f"ALTER TABLE astock_board_wuxing_profiles ADD COLUMN {column} {ddl}", db_path=db_path)


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def default_profile() -> dict[str, Any]:
    return {
        "level": "category",
        "category": "",
        "subcategory": "",
        "paid_required": False,
        "element_scores": {element: 20 for element in ELEMENTS},
        "industry_position": "",
        "business_model": "",
        "text": "",
    }


if __name__ == "__main__":
    main()
