from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.message_components import Video
import astrbot.api.message_components as Comp
from astrbot.core.conversation_mgr import Conversation
from astrbot.core.agent.message import (
    AssistantMessageSegment,
    UserMessageSegment,
    TextPart,
)

print=logger.info
@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)


    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("shit")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)

        chain=[Comp.Image.fromURL(url='https://localhost/shits/mm.jpg')]
        yield event.chain_result(chain)
    @filter.command('c')
    async def chat(self, event: AstrMessageEvent,chat_message:str):
        umo = event.unified_msg_origin
        provider_id = await self.context.get_current_chat_provider_id(umo=umo)

        uid = event.unified_msg_origin
        conv_mgr = self.context.conversation_manager
        curr_cid = await conv_mgr.get_curr_conversation_id(uid)
        conversation = await conv_mgr.get_conversation(uid, curr_cid)  # Conversation
        print(uid,conversation,curr_cid,conversation)
        curr_cid = await conv_mgr.get_curr_conversation_id(event.unified_msg_origin)
        user_msg = UserMessageSegment(content=[TextPart(text="hi")])
        llm_resp = await self.context.llm_generate(
            chat_provider_id=provider_id,  # 聊天模型 ID
            contexts=[user_msg],  # 当未指定 prompt 时，使用 contexts 作为输入；同时指定 prompt 和 contexts 时，prompt 会被添加到 LLM 输入的最后
        )
        await conv_mgr.add_message_pair(
            cid=curr_cid,
            user_message=user_msg,
            assistant_message=AssistantMessageSegment(
                content=[TextPart(text=llm_resp.completion_text)]
            ),
        )

        llm_resp = await self.context.llm_generate(
            chat_provider_id=provider_id,  # 聊天模型 ID
            prompt=chat_message+'/no_think'
        )

        yield event.chain_result([Comp.Plain(llm_resp.completion_text)])

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
