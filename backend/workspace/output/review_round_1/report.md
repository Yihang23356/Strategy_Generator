# JSON 差异分析报告

## 元数据
- **分析时间**: 2026-04-26T18:52:53.266960
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

## 验证结果
- **验证通过**: ✅
- **抽样检查**: 8 个样本
- **备注**: 随机抽样 8 个差异进行验证，全部通过

---
*报告生成完成*