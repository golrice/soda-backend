import json
from openai import OpenAI
import os
# from project.settings import OPENAI_API_KEY

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.deepseek.com",
)

system_prompt = """
你是标签工程师，User会给你一篇文章，请你根据文章，以JSON格式返回文章的标签，主标签为1个，辅助标签数量为5个。
主标签的输出只能为以下几种的其中一个：
科技、体育、娱乐圈、游戏、教育、财经、军事、户外、人文、生活、动物、二次元、其他
假设输入为一篇苹果手机的评测文章，则输出为：（JSON格式）
{
    "main": "科技",
    "label1": "手机",
    "label2": "苹果",
    "label3": "iPhone 14",
    "label4": "评测",
    "label5": "电子产品"
}
"""

def get_tags(user_prompt):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    answer = json.loads(response.choices[0].message.content)
    return answer

if __name__ == '__main__':
    url = 'D:/projects/soda/soda-backend/media/posts/article1'
    answer = get_tags(url)
    print(answer['main'])
    for i in range(5):
        print(f"label{i+1}: {answer[f'label{i+1}']} ")
    