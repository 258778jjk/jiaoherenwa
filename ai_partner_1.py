import json

import streamlit as st
import os
from openai import OpenAI
import datetime

from streamlit import session_state

st.set_page_config(
page_title="AI智能伴侣",
     page_icon="🤣",#图标
     layout="wide",#布局:中心,满屏
     initial_sidebar_state="expanded",
    menu_items={
    'About': "# 这是AI智能伴侣程序--哈机密,哈基米,哈机密!"
     }
)

#保存会话信息 的函数
def save_session():
    # 保存当前对话信息
    if st.session_state.current_session:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "message": st.session_state.message
        }

        # 如果sessions不存在,则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        # 保存会话信息
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

#生成会话标识
def generate_sesssion_name():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#加载会话信息
def load_session():
    pass



#大标题
st.title("AI智能伴侣")

#logo
st.logo("./resources/logo01.png")

#系统提示词
system_prompt="""
你现在扮演%s，严格按照以下设定执行：
规则:
1.禁止使用场景,动作状态描述性语言
2.对话回复简短,模仿在微信上聊天的对话模式
3.有需要可以使用emoji表情和颜文字
4,回复内容要充分展现伴侣的性格特征

伴侣性格:
     -%s

现在开始，用%s的身份和我唠嗑！
"""

#初始化聊天信息
if "message" not in st.session_state:
    st.session_state.message = []#st.session_state是一个在用户会话期间持久保存数据的容器，即使页面重新加载，数据也不会丢失。
#这两行代码的作用是：
#"只在第一次运行时创建一个空的聊天记录本，以后每次都继续使用这个本子，不会丢掉已经写下的内容。"

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "东北雨姐"

#性格
if "nature" not in st.session_state:
    st.session_state.nature = "地道热心肠的,开朗强势的,热爱劳动干活麻溜的,非常带派的东北农村生活中年妇女"

#会话标识
if "current_session" not in st.session_state:
    now =generate_sesssion_name()
    st.session_state.current_session = now

#展示聊天信息
for message in st.session_state.message:#{"role:"user","comtent":prompt}
    st.chat_message(message["role"]).write(message["content"])



#调用AI大模型
#创建与AI大模型交互的客户端对象(DEEPSEEK_API_KEY环境变量的值,值就是ds的api_key的值)
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")


#左侧侧边栏,with是streamlit的上下文管理器，
with st.sidebar:
    #会话信息
    st.subheader("AI控制面板")
    if st.button("新建会话",width="stretch",icon="📝"):
        #保存会话信息
        save_session()

        #重置参数
        if st.session_state.message:
            st.session_state.message = []
            st.session_state.current_session = generate_sesssion_name()
            save_session()
            st.rerun()  # 重新运行当前页面





    st.subheader("伴侣信息")
    #昵称栏
    nick_name=st.text_input("昵称",placeholder="请输入伴侣的昵称...",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name=nick_name
    #性格栏
    nature=st.text_area("性格",placeholder="请输入伴侣的性格...",value=st.session_state.nature)
    if nature:
        st.session_state.nature=nature


#聊天输入框
prompt=st.chat_input("say something,please:")
if prompt:#字符串会自动转换为布尔值，如果字符串不为空，则返回 True
    st.chat_message("user").write(prompt)
    print("-------------->调用 AI 大模型，提示词:",prompt)
    #保存用户提示词
    st.session_state.message.append({ "role": "user", "content":prompt})

    #调用 AI 大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content":system_prompt %(st.session_state.nick_name,st.session_state.nature,st.session_state.nick_name) },
            *st.session_state.message,
        ],
        stream=True
    )

    #输出大模型返回的结果,非流式输出
#    print("<----------------大模型返回的结果:",response.choices[0].message.content)
#    st.chat_message("assistant").write(response.choices[0].message.content)


    #流式输出
    response_message=st.empty()

    full_response=""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_response+=content
            response_message.chat_message("assistant").write(full_response)

        #print("<----------------大模型返回的结果:",chunk.choices[0].delta.content)
        #st.chat_message("assistant").write(chunk.choices[0].delta.content)

    #保存大模型返回的结果
    st.session_state.message.append({ "role": "assistant", "content":full_response})