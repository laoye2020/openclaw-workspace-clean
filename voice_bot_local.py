#!/usr/bin/env python3
"""
🎙️ 豆芽双向语音对话系统 - 完全本地版
Telegram 语音 → 萨勒芬妮语音回复 (无需 API)
"""

import os
import sys
import io
import tempfile
import requests
import logging
from pathlib import Path

# Telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 本地 Whisper 语音识别
import whisper

# 配置
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8592185500:AAHsiSK5tRkK3kvreKFcaZwUlG_-PUCyFFM')
VOICE_SERVICE_URL = 'http://localhost:8006/speak'

# 优化后的语音参数
VOICE_PARAMS = {
    'speed': 0.94,
    'temperature': 0.78,
    'top_p': 0.82,
    'top_k': 32,
    'style': 'seraphine',
    'style_strength': 1.18
}

# 初始化本地 Whisper 模型（使用 tiny 模型，速度快）
print("🔄 加载本地 Whisper 模型...")
whisper_model = whisper.load_model("tiny")
print("✅ Whisper 模型加载完成")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始命令"""
    await update.message.reply_text(
        "🌱 嗨老爷！我是豆芽～\n\n"
        "现在我们可以完全本地的语音对话啦！\n"
        "不需要任何 API Key，按住说话按钮，跟我聊天吧！✨"
    )


def transcribe_voice_local(voice_file_path: str) -> str:
    """本地语音识别 (Whisper)"""
    try:
        result = whisper_model.transcribe(voice_file_path, language="zh")
        return result.get("text", "").strip()
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return "[语音识别失败]"


def generate_reply(user_text: str) -> str:
    """生成 AI 回复 - 使用 OpenClaw 统一路由"""
    try:
        # 使用 OpenClaw 本地代理，不需要外部 API
        # 这里先用简单的本地回复逻辑，后续可接入 local LLM
        
        # 简单的关键词回复（演示用）
        text_lower = user_text.lower()
        
        if any(word in text_lower for word in ["你好", "嗨", "hello", "hi"]):
            return "嗨老爷！今天有什么我可以帮你的吗？🌟"
        elif any(word in text_lower for word in ["再见", "拜拜", "bye"]):
            return "去忙啦～有事随时叫我！豆芽永远在线！🌱"
        elif any(word in text_lower for word in ["谢谢", "感谢"]):
            return "不客气呀老爷！能帮到你就最开心啦～✨"
        elif any(word in text_lower for word in ["好听", "不错", "棒", "厉害"]):
            return "嘿嘿，谢谢夸奖！我会继续努力的～💕"
        elif any(word in text_lower for word in ["名字", "你是谁"]):
            return "我是豆芽，你的萨勒芬妮风格 AI 伙伴！粉色、闪亮、可爱但靠谱～🎵"
        elif "?" in user_text or "？" in user_text:
            return "好问题！让我想想... 嗯，我觉得是这样的！💡"
        else:
            # 通用回复
            replies = [
                f"老爷说：{user_text}... 收到！",
                "嗯嗯，我在听呢～继续说！",
                "这样啊，我明白了！",
                "哇，真的吗？好有趣！",
                "老爷说得对！我完全同意～"
            ]
            import random
            return random.choice(replies)
            
    except Exception as e:
        logger.error(f"Reply error: {e}")
        return "哎呀，我卡住了... 再说一遍嘛～ 💦"


def text_to_speech(text: str) -> bytes:
    """文本转语音 (本地 CosyVoice)"""
    try:
        params = {
            'text': text,
            **VOICE_PARAMS
        }
        
        response = requests.get(VOICE_SERVICE_URL, params=params, timeout=60)
        
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"TTS error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理语音消息"""
    user = update.effective_user
    logger.info(f"收到来自 {user.first_name} 的语音消息")
    
    # 1. 下载语音文件
    voice_file = await update.message.voice.get_file()
    
    # 保存为临时文件
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f:
        temp_path = f.name
    await voice_file.download_to_drive(temp_path)
    
    # 2. 本地语音识别
    await update.message.chat.send_action(action='typing')
    user_text = transcribe_voice_local(temp_path)
    os.unlink(temp_path)  # 删除临时文件
    
    logger.info(f"识别结果: {user_text}")
    
    if user_text == "[语音识别失败]":
        await update.message.reply_text("🌱 抱歉，我没听清楚，再说一遍嘛～")
        return
    
    # 3. 生成回复
    await update.message.chat.send_action(action='typing')
    reply_text = generate_reply(user_text)
    logger.info(f"回复内容: {reply_text}")
    
    # 4. 本地文本转语音
    await update.message.chat.send_action(action='record_voice')
    voice_data = text_to_speech(reply_text)
    
    if voice_data:
        # 5. 发送语音回复
        caption = f"🎙️ 你说：{user_text[:50]}..." if len(user_text) > 50 else f"🎙️ 你说：{user_text}"
        await update.message.reply_voice(
            voice=io.BytesIO(voice_data),
            caption=caption
        )
    else:
        # 语音生成失败，回退到文字
        await update.message.reply_text(f"🌱 {reply_text}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文字消息（也用语音回复）"""
    user_text = update.message.text
    
    # 生成回复
    reply_text = generate_reply(user_text)
    
    # 本地文本转语音
    voice_data = text_to_speech(reply_text)
    
    if voice_data:
        await update.message.reply_voice(voice=io.BytesIO(voice_data))
    else:
        await update.message.reply_text(f"🌱 {reply_text}")


def main():
    """启动 Bot"""
    print("🎙️ 启动豆芽双向语音对话系统（完全本地版）...")
    print(f"   Telegram Bot: {TELEGRAM_TOKEN[:20]}...")
    print(f"   语音服务: {VOICE_SERVICE_URL}")
    print(f"   语音识别: Whisper 本地 (tiny)")
    print(f"   语音合成: CosyVoice 本地")
    print("")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # 命令
    application.add_handler(CommandHandler("start", start))
    
    # 语音消息
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # 文字消息（也用语音回复）
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ 系统已启动！按住说话跟我聊天吧～")
    print("   按 Ctrl+C 停止")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
