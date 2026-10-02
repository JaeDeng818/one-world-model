JAE-TRADE v1.1
│
├── 01 database
│   ├── data_sources
│   ├── indicators
│   ├── observations
│   ├── markets
│   ├── industries
│   ├── exposure
│   ├── scoring_rules
│   ├── events
│   └── daily_scores
│
├── 02 data engine
│   ├── 数据标准化
│   ├── 异常值检测
│   └── 数据质量检查
│
├── 03 freshness engine
│   └── 半衰期 + structural floor
│
├── 04 confidence engine
│   └── 来源可信度 + 多源交叉验证
│
├── 05 scoring engine
│   ├── PMI
│   ├── 商品
│   ├── 汇率
│   ├── 海运
│   └── 出口动能
│
├── 06 event engine
│   ├── 关税
│   ├── 反倾销
│   ├── 制裁
│   ├── 战争
│   ├── 港口
│   └── 能源冲击
│
└── 07 forecast engine
    ├── Market Score
    ├── Industry Score
    ├── Profit Pressure
    └── 7D Forecast