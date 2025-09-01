# 自动标书生成系统配置文件

# ========== API配置 ==========
# 始皇API配置（继承原有配置）
SHIHUANG_API_KEY = "sk-4sYV1WXMcdGcLz9XEKWyntV58pSnhb4GXM6aMBfzWUic3pLfnwob"
SHIHUANG_BASE_URL = "https://api.oaipro.com/v1"
SHIHUANG_MODEL = "gpt-4o-mini"

# ========== 匹配阈值配置 ==========
# 内容匹配阈值
EXACT_MATCH_THRESHOLD = 0.8    # 直接复制阈值
REWRITE_THRESHOLD = 0.5        # 改写阈值
GENERATE_THRESHOLD = 0.3       # 原创生成阈值

# 语义匹配配置
SEMANTIC_SIMILARITY_THRESHOLD = 0.7  # 语义相似度阈值
EMBEDDING_MODEL = "text-embedding-ada-002"  # embedding模型

# ========== 文档识别关键词 ==========
# 需求文档识别关键词
REQUIREMENT_KEYWORDS = [
    "采购需求", "技术规范", "功能要求", "需求说明", "技术要求",
    "系统要求", "技术指标", "性能要求", "功能规格", "技术参数"
]

# 评分标准识别关键词
SCORING_KEYWORDS = [
    "打分表", "评分表", "评标准", "技术评分", "评分标准",
    "评价标准", "技术评价", "评审标准", "评分细则", "评标办法"
]

# 评分权重关键词
WEIGHT_KEYWORDS = ["分", "分值", "权重", "%", "百分比", "占比"]

# ========== 文本处理配置 ==========
# 文本清理配置
MIN_PARAGRAPH_LENGTH = 10  # 最小段落长度
MAX_PARAGRAPH_LENGTH = 2000  # 最大段落长度

# 章节标题识别模式
SECTION_PATTERNS = [
    r'^[一二三四五六七八九十]+[、\.]',  # 中文数字
    r'^\d+[、\.]',  # 阿拉伯数字
    r'^[（\(]\d+[）\)]',  # 括号数字
    r'^\d+\.\d+',  # 多级编号
    r'^第[一二三四五六七八九十]+章',  # 章节
]

# ========== LLM提示词配置 ==========
# 大纲生成提示词
OUTLINE_PROMPT = """
你是一个专业的标书撰写专家。请根据以下评分标准生成技术方案大纲：

评分标准：
{scoring_criteria}

需求内容：
{requirements}

请生成一个结构化的技术方案大纲，要求：
1. 严格按照评分标准的项目和权重安排章节
2. 每个章节要有明确的标题和要点
3. 章节顺序要符合技术方案的逻辑性
4. 输出格式为JSON格式

输出格式示例：
{{
    "outline": [
        {{
            "level": 1,
            "title": "技术架构",
            "weight": "20分",
            "subsections": [
                {{
                    "level": 2,
                    "title": "系统架构设计",
                    "points": ["要点1", "要点2"]
                }}
            ]
        }}
    ]
}}
"""

# 内容生成提示词
CONTENT_GENERATION_PROMPT = """
你是一个专业的技术文档撰写专家。请根据以下信息生成技术方案内容：

需求描述：{requirement}
产品功能：{product_features}
章节标题：{section_title}

请生成800-1200字的专业技术内容，要求：
1. 紧扣需求描述，突出产品优势
2. 使用专业术语，体现技术深度
3. 结构清晰，逻辑严谨
4. 适合标书技术方案的写作风格
"""

# 内容改写提示词
CONTENT_REWRITE_PROMPT = """
你是一个专业的技术文档编辑。请将以下产品文档内容改写为标书技术方案格式：

原始内容：{original_content}
目标需求：{target_requirement}
章节标题：{section_title}

请改写内容，要求：
1. 保持原意但调整表达方式适应标书语境
2. 突出与需求的匹配性
3. 增强说服力和专业性
4. 字数控制在600-800字
"""

# ========== 文件路径配置 ==========
# 输出路径配置
OUTPUT_DIR = "output"
TEMP_DIR = "temp"

# 默认文件名
DEFAULT_OUTLINE_FILE = "技术方案大纲.json"
DEFAULT_PROPOSAL_FILE = "技术方案.docx"
DEFAULT_MATCH_REPORT = "匹配度报告.xlsx"

# ========== 日志配置 ==========
LOG_LEVEL = "INFO"
LOG_FILE = "tender_generator.log"

# ========== 其他配置 ==========
# 最大并发处理数
MAX_CONCURRENT_REQUESTS = 5

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# 文档最大页数限制
MAX_DOCUMENT_PAGES = 500