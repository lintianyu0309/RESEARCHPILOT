import json
import os
from typing import Any, cast

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)
from openai.types.chat.chat_completion import ChatCompletion


load_dotenv()


def get_client():
    """
    创建 DeepSeek API 客户端。
    """

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError(
            "没有找到 DEEPSEEK_API_KEY。请检查 .env 文件。"
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


def get_model_name():
    """
    从 .env 文件读取 DeepSeek 模型名称。
    """

    return os.getenv(
        "DEEPSEEK_MODEL",
        "deepseek-flash"
    )


def send_message(system_prompt, user_prompt):
    """
    向 DeepSeek 发送普通文本请求。
    """

    client = get_client()

    system_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": system_prompt
    }

    user_message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": user_prompt
    }

    messages: list[ChatCompletionMessageParam] = [
        system_message,
        user_message
    ]

    response = cast(
        ChatCompletion,
        client.chat.completions.create(
            model=get_model_name(),
            messages=messages,
            stream=False
        )
    )

    return response.choices[0].message.content or ""


def send_json_message(system_prompt, user_prompt):
    """
    请求 DeepSeek 返回结构化 JSON 数据。
    若第一次返回空内容，会自动重试一次。
    """

    client = get_client()

    system_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": system_prompt
    }

    user_message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": user_prompt
    }

    messages: list[ChatCompletionMessageParam] = [
        system_message,
        user_message
    ]

    for attempt in range(2):

        response = cast(
            ChatCompletion,
            client.chat.completions.create(
                model=get_model_name(),
                messages=messages,
                stream=False,
                max_tokens=4000,
                response_format=cast(
                    Any,
                    {"type": "json_object"}
                ),
                extra_body=cast(
                    Any,
                    {
                        "thinking": {
                            "type": "disabled"
                        }
                    }
                )
            )
        )

        content = response.choices[0].message.content or ""

        if content.strip():

            try:
                return json.loads(content)

            except json.JSONDecodeError:

                if attempt == 1:
                    raise ValueError(
                        "DeepSeek 返回的内容不是有效 JSON。"
                    )

    raise ValueError(
        "DeepSeek 连续两次返回空内容。"
        "请检查 .env 中的 DEEPSEEK_MODEL。"
    )


def generate_ai_keyword_analysis(papers):
    """
    由 DeepSeek 阅读论文，生成关键词、主题簇、关系和对比矩阵。
    """

    paper_text = ""

    for paper in papers:

        text = paper["text"]

        if len(text) > 12000:

            text = (
                text[:6000]
                + "\n\n[中间内容已省略]\n\n"
                + text[-6000:]
            )

        paper_text += (
            f"\n\n========== 论文：{paper['title']} ==========\n"
            f"{text}"
        )

    system_prompt = """
你是 ResearchPilot 的科研文献分析引擎。

请阅读用户提供的多篇论文，识别真正的研究主题、方法、任务和概念关系。
不要输出作者姓名、引用信息、年份、机构名称、单个泛化词，
例如 graph、model、method、paper、learning、zhang、wang、et al。

关键词必须是 2 至 5 个词组成的专业英文术语短语，
例如 "graph neural network"、"molecular property prediction"。

请只输出合法 json，不要输出 Markdown 或解释文字。

JSON 输出必须严格使用以下结构：

{
  "project_summary": "中文项目总结，2到4句话",
  "project_keywords": [
    {
      "keyword": "英文专业短语",
      "chinese_label": "中文术语翻译",
      "theme": "英文主题名称",
      "average_tfidf": 1,
      "document_frequency": 1
    }
  ],
  "paper_keywords": {
    "论文文件名.pdf": [
      {
        "keyword": "英文专业短语"
      }
    ]
  },
  "cooccurrence_edges": [
    {
      "source": "英文专业短语",
      "target": "英文专业短语",
      "cooccurrence": 1
    }
  ],
  "theme_clusters": [
    {
      "theme": "英文主题名称",
      "theme_zh": "中文主题名称",
      "description": "中文说明该主题在本项目中的研究作用",
      "keywords": [
        "属于该主题的英文专业短语"
      ]
    }
  ],
  "paper_comparisons": [
    {
      "title": "论文文件名.pdf",
      "research_question": "中文概括的研究问题",
      "core_method": "中文概括的核心方法",
      "task_or_data": "任务、数据集或应用场景",
      "main_finding": "中文概括的主要发现",
      "limitation": "中文概括的局限性；若论文未说明则写未明确说明"
    }
  ]
}

规则：
1. project_keywords 最多 20 个。
2. average_tfidf 不是真实 TF-IDF，而是 AI 判断的重要性评分，范围 1 到 5。
3. document_frequency 是该关键词相关的论文数量。
4. 每篇论文给出 5 到 8 个关键词。
5. cooccurrence_edges 最多 25 条。
6. cooccurrence 是 AI 判断的关联强度，范围 1 到 5。
7. source 和 target 必须来自 project_keywords。
8. paper_comparisons 必须为每篇论文生成一条记录。
9. title 必须与输入中的论文文件名完全一致。
10. 对比字段必须使用简洁中文，每个字段最多两句话。
11. 每个 project_keywords 都必须包含 chinese_label 和 theme。
12. theme_clusters 输出 2 到 5 个主题簇。
13. theme_clusters 的 keywords 必须来自 project_keywords。
14. theme_zh 和 description 使用中文。
15. 主题名称应体现研究方向，例如 Molecular Property Prediction、
    Representation Learning、Few-shot Learning。
"""

    user_prompt = (
        "请基于以下论文生成 JSON 格式的项目关键词分析："
        f"{paper_text}"
    )

    return send_json_message(
        system_prompt,
        user_prompt
    )


def generate_research_analysis(
    question,
    papers,
    project_keywords,
    cooccurrence_edges
):
    """
    根据用户问题、论文、AI 关键词和关系生成中文研究回答。
    """

    keyword_text = ""

    for item in project_keywords[:20]:

        keyword_text += (
            f"- {item['keyword']} "
            f"（中文：{item.get('chinese_label', '')}，"
            f"主题：{item.get('theme', '')}，"
            f"AI 重要性：{item['average_tfidf']}，"
            f"相关论文数：{item['document_frequency']}）\n"
        )

    relation_text = ""

    for edge in cooccurrence_edges[:20]:

        relation_text += (
            f"- {edge['source']} ↔ {edge['target']} "
            f"（AI 关联强度：{edge['cooccurrence']}）\n"
        )

    paper_text = ""

    for paper in papers:

        text = paper["text"]

        if len(text) > 12000:

            text = (
                text[:6000]
                + "\n\n[中间内容已省略]\n\n"
                + text[-6000:]
            )

        paper_text += (
            f"\n\n========== 论文：{paper['title']} ==========\n"
            f"{text}"
        )

    system_prompt = (
        "你是 ResearchPilot，一名严谨的科研文献分析助手。"
        "用户可以使用中文或英文提问，你必须使用中文回答。"
        "你会收到项目关键词、概念关系和论文原文。"
        "关键词和概念关系只能作为辅助线索，论文原文才是事实依据。"
        "请自行判断哪些信息与问题相关。"
        "不要编造论文中没有的信息。"
        "如果证据不足或论文之间存在冲突，必须明确说明。"
        "论文原文中使用【第 N 页】标记了页码。"
        "每个关键结论后都必须标注证据，格式为"
        "[论文：文件名，第 N 页]。"
        "只能引用论文原文中实际出现过的页码，绝对不要猜测页数。"
        "如果结论来自多个页面或多篇论文，应分别列出多个引用。"
        "如果原文不足以支持结论，必须明确说证据不足。"
        "回答应尽量包括：直接结论、依据、论文异同和局限性。"
    )

    user_prompt = (
        f"用户问题：{question}\n\n"
        f"项目关键词：\n{keyword_text}\n"
        f"概念关系：\n{relation_text}\n"
        f"论文原文：\n{paper_text}"
    )

    return send_message(
        system_prompt,
        user_prompt
    )