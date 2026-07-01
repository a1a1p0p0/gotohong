# calendar_ganzhi.csv Validation Report

- Date range: 2020-01-01 to 2035-12-31
- Generated rows: 5844
- HKO rows loaded: 2192
- Verified rows: 2192
- Verification rate: 37.51%
- HKO-verified random sample size: 30
- Output source field: HKO verified rows use `HKO_DATA_GOV_HK_GREGORIAN_LUNAR_TABLE;lunar_python_1.4.8`; generated-only rows use `lunar_python_1.4.8;HKO_DATA_GOV_HK_UNAVAILABLE_FOR_YEAR`
- Output confidence field: 100 for HKO-verified rows, 70 for generated-only rows.

| Date | Lunar Year GZ | LiChun Year GZ | Month GZ | Day GZ | HKO Verified |
| --- | --- | --- | --- | --- | --- |
| 2026-05-04 | 丙午 | 丙午 | 壬辰 | 戊寅 | true |
| 2025-07-21 | 乙巳 | 乙巳 | 癸未 | 辛卯 | true |
| 2023-02-28 | 癸卯 | 癸卯 | 甲寅 | 丁巳 | true |
| 2028-05-10 | 戊申 | 戊申 | 丁巳 | 乙未 | true |
| 2023-12-10 | 癸卯 | 癸卯 | 甲子 | 壬寅 | true |
| 2025-09-08 | 乙巳 | 乙巳 | 乙酉 | 庚辰 | true |
| 2027-11-30 | 丁未 | 丁未 | 辛亥 | 癸丑 | true |
| 2025-04-25 | 乙巳 | 乙巳 | 庚辰 | 甲子 | true |
| 2027-04-20 | 丁未 | 丁未 | 甲辰 | 己巳 | true |
| 2027-09-05 | 丁未 | 丁未 | 戊申 | 丁亥 | true |
| 2028-02-20 | 戊申 | 戊申 | 甲寅 | 乙亥 | true |
| 2028-01-05 | 丁未 | 丁未 | 壬子 | 己丑 | true |
| 2028-07-09 | 戊申 | 戊申 | 己未 | 乙未 | true |
| 2028-06-21 | 戊申 | 戊申 | 戊午 | 丁丑 | true |
| 2026-07-10 | 丙午 | 丙午 | 乙未 | 乙酉 | true |
| 2028-02-12 | 戊申 | 戊申 | 甲寅 | 丁卯 | true |
| 2028-08-17 | 戊申 | 戊申 | 庚申 | 甲戌 | true |
| 2026-01-11 | 乙巳 | 乙巳 | 己丑 | 乙酉 | true |
| 2024-04-30 | 甲辰 | 甲辰 | 戊辰 | 甲子 | true |
| 2023-10-23 | 癸卯 | 癸卯 | 壬戌 | 甲寅 | true |
| 2026-02-21 | 丙午 | 丙午 | 庚寅 | 丙寅 | true |
| 2023-06-01 | 癸卯 | 癸卯 | 丁巳 | 庚寅 | true |
| 2027-05-19 | 丁未 | 丁未 | 乙巳 | 戊戌 | true |
| 2026-08-28 | 丙午 | 丙午 | 丙申 | 甲戌 | true |
| 2026-01-14 | 乙巳 | 乙巳 | 己丑 | 戊子 | true |
| 2026-03-17 | 丙午 | 丙午 | 辛卯 | 庚寅 | true |
| 2027-12-25 | 丁未 | 丁未 | 壬子 | 戊寅 | true |
| 2027-12-28 | 丁未 | 丁未 | 壬子 | 辛巳 | true |
| 2024-01-14 | 癸卯 | 癸卯 | 乙丑 | 丁丑 | true |
| 2028-03-21 | 戊申 | 戊申 | 乙卯 | 乙巳 | true |

Notes:
- HKO / DATA.GOV.HK is used to verify Gregorian date, lunar year Gan-Zhi, lunar month and lunar day.
- lunar_python generates solar terms, LiChun year Gan-Zhi, Jie-Qi month Gan-Zhi and daily Gan-Zhi.
- The analysis engine should use `lichun_year_ganzhi` as the default year Gan-Zhi.
- `month_ganzhi` uses Jie-Qi month, not Gregorian month.
