# sololib

一个 Python 工具包，提供多样化的对话语料生成功能。

## 安装

```bash
pip install sololib
```

## 功能

### 语料生成

生成多样化的对话模板，支持中英文混合：

```python
import sololib

# 生成多轮对话
conversation = sololib.get_random_conversation()
# 返回: [("How do I learn Python?", "programming"), ("Can you tell me more?", "programming")]

# 生成单个随机问题
question = sololib.generate_single_question()
# 返回: "What's the best way to learn Django as a beginner?"

# 批量生成问题
questions = sololib.generate_questions(10)
# 返回: 10 个随机问题列表
```

### 统计信息

```python
# 获取语料库统计
stats = sololib.get_corpus_stats()
# 返回:
# {
#     "question_templates": {"en": 465, "cn": 117, "total": 582},
#     "followup_templates": {"en": 30, "cn": 10, "total": 40},
#     "estimated_combinations": 1850503,
#     ...
# }

# 估计不重复组合数
combos = sololib.estimate_combinations()  # ~185 万
```

## 核心函数

| 函数 | 说明 |
|------|------|
| `get_random_conversation(n=1)` | 生成 n 组多轮对话 |
| `generate_single_question()` | 生成单个随机问题 |
| `generate_questions(n=10)` | 批量生成 n 个问题 |
| `get_corpus_stats()` | 获取语料库统计信息 |
| `estimate_combinations()` | 估算不重复组合数 |

## 数据规模

- **英文问题模板**: 465 条
- **中文问题模板**: 117 条
- **追问模板**: 40 条
- **估计组合数**: 1,850,503+

覆盖领域：烹饪、编程、健身、旅行、书籍、音乐、宠物、科学、职业、情感等。

## 开发

```bash
# 克隆仓库
git clone https://github.com/iding2959/sololib.git
cd sololib

# 安装开发依赖
uv sync --all-extras --dev

# 运行测试
uv run sololib
```

## License

MIT