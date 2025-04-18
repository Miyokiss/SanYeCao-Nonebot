from nonebot.rule import to_me
from nonebot.plugin import on_command
from nonebot.adapters.qq import MessageEvent
from nonebot.exception import FinishedException
from src.providers.llm.AliBL.base import on_bl_new_session_id,on_bl_new_memory_id
from src.clover_sqlite.models.chat import GroupChatRole
from src.clover_sqlite.models.chat import MODE_ELYSIA, MODE_OFF
from nonebot import logger

Elysia_super = on_command("爱莉希雅",aliases={"妖精爱莉"},rule=to_me(),priority=10,block=True)
@Elysia_super.handle()
async def handle_function(message: MessageEvent):

    if not hasattr(message, 'group_openid'):
        await Elysia_super.finish("暂未在当前场景下开放此功能。")

    user_id, group_openid, content = message.get_user_id(), message.group_openid, message.get_plaintext().split()
    # 判断是否为管理员
    if not await GroupChatRole.get_admin_list(group_openid, user_id):
        await Elysia_super.finish("您没有权限使用此功能。")
    else:
        current_mode = await GroupChatRole.is_on(group_openid)
        logger.debug(f"\n{content}")
        if content[0] == "/爱莉希雅":
            values = message.get_plaintext().replace("/爱莉希雅", "").split()
            try:
                if len(values) == 0 or not all(values[1:len(values)]):
                    if current_mode != MODE_ELYSIA:
                        await GroupChatRole.ai_mode(group_openid, MODE_ELYSIA)
                        await Elysia_super.finish("成功开启爱莉希雅对话~")
                    else:
                        await Elysia_super.finish("当前群已是爱莉希雅对话~")
                elif len(values) == 1:
                    if values[0] == "新的对话":
                        msg = await on_bl_new_session_id(user_id)
                        if msg["code"] is True:
                            await Elysia_super.send(msg["msg"])
                            await Elysia_super.finish("开始新的对话啦！~")
                        else:
                            await Elysia_super.finish(msg["msg"])
                    if values[0] == "新的记忆":
                        msg =await on_bl_new_memory_id(user_id)
                        if msg is True:
                            await Elysia_super.finish("开始新的记忆啦！~")
                        else:
                            await Elysia_super.finish(msg)
                    else:
                        await Elysia_super.finish("请输入正确的指令！\n指令格式：\n/爱莉希雅\n/爱莉希雅 <新的对话/新的记忆>")
            except Exception as e:
                if isinstance(e, FinishedException):
                    return
                logger.error(f"处理请求时发生错误: {e}")
                await Elysia_super.finish("处理请求时发生错误，请稍后重试")
        elif content[0] == "/妖精爱莉":
            if current_mode == MODE_ELYSIA:
                await GroupChatRole.ai_mode(group_openid, MODE_OFF)
                await Elysia_super.finish("成功关闭爱莉希雅对话~")
            else:
                await Elysia_super.finish("当前群已开启妖精爱莉聊天~")

            
