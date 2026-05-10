# JSON 差异分析报告

## 元数据
- **分析时间**: 2026-04-26T18:59:12.987231
- **输入文件**: input/uploads/input_a_input_a.json, input/uploads/input_b_input_b.json, input/uploads/input_c_input_c.json
- **标准答案**: input/uploads/standard_standard_answer.json
- **工具版本**: 1.0.0

## 分析摘要
**总差异数**: 42

### 按对比分组
| 对比 | 差异数 |
|------|--------|
| input_a_input_a.json vs input_b_input_b.json | 7 |
| input_a_input_a.json vs input_c_input_c.json | 6 |
| input_b_input_b.json vs input_c_input_c.json | 6 |
| input_a_input_a.json vs standard | 8 |
| input_b_input_b.json vs standard | 8 |
| input_c_input_c.json vs standard | 7 |

### 按严重程度
| 严重程度 | 差异数 |
|----------|--------|
| critical | 0 |
| high | 1 |
| medium | 41 |
| low | 0 |

### 按差异类型
| 类型 | 差异数 |
|------|--------|
| structural | 39 |
| content | 3 |
| semantic | 0 |
| type_mismatch | 0 |

## 一致性分析
- **最接近标准答案**: `input_c_input_c.json`
- **偏离最大**: `input_a_input_a.json`

## HIGH 级别差异示例

### 示例 1: diff_014
- **对比**: input_b_input_b.json vs input_c_input_c.json
- **路径**: `source`
- **类型**: content
- **严重程度**: **HIGH**
- **值A**: `operations_team`
- **值B**: `finance_and_risk`
- **描述**: 值不匹配: source
- **影响**: 影响数据一致性
- **建议**: 统一文本格式和编码

## MEDIUM 级别差异示例

### 示例 1: diff_001
- **对比**: input_a_input_a.json vs input_b_input_b.json
- **路径**: `constraints`
- **类型**: structural
- **严重程度**: **MEDIUM**
- **值A**: `{'budget_cny_million': 5.0, 'timeline_months': 6, 'headcount_limit': 8}`
- **值B**: `None`
- **描述**: 字段缺失: constraints (仅在第一个文件中存在)
- **影响**: 数据结构不完整
- **建议**: 检查字段是否应该存在

### 示例 2: diff_002
- **对比**: input_a_input_a.json vs input_b_input_b.json
- **路径**: `source`
- **类型**: content
- **严重程度**: **MEDIUM**
- **值A**: `market_research`
- **值B**: `operations_team`
- **描述**: 值不匹配: source
- **影响**: 影响数据一致性
- **建议**: 统一文本格式和编码

### 示例 3: diff_003
- **对比**: input_a_input_a.json vs input_b_input_b.json
- **路径**: `goal`
- **类型**: structural
- **严重程度**: **MEDIUM**
- **值A**: `reduce fulfillment time and improve order accuracy`
- **值B**: `None`
- **描述**: 字段缺失: goal (仅在第一个文件中存在)
- **影响**: 数据结构不完整
- **建议**: 检查字段是否应该存在

*还有 38 个 medium 级别差异*

## 验证结果
- **验证通过**: ✅
- **抽样检查**: 8 个样本
- **备注**: 随机抽样 8 个差异进行验证，全部通过

---
*报告生成完成*