#!/usr/bin/env python3
"""
🎙️ 豆芽双向语音对话系统
Telegram 语音 → 萨勒芬妮语音回复
"""

import os
import sys
import io
import tempfile
import requests
import asyncio
import logging
from pathlib import Path

# Telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 配置
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8592185500:AAHsiSK5tRkK3kvreKFcaZwUlG_-PUCyFFM')
VOICE_SERVICE_URL = 'http://localhost:8006/speak'
WHISPER_API_URL = 'https://api.openai.com/v1/audio/transcriptions'
LLM_API_URL = 'https://api.openai.com/v1/chat/completions'

# 优化后的语音参数
VOICE_PARAMS = {
    'speed': 0.94,
    'temperature': 0.78,
    'top_p': 0.82,
    'top_k': 32,
    'style': 'seraphine',
    'style_strength': 1.18
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始命令"""
    await update.message.reply_text(
        "🌱 嗨老爷！我是豆芽～\n\n"
        "现在我们可以语音对话啦！\n"
        "按住说话按钮，跟我聊天吧！✨"
    )


async def transcribe_voice(voice_file: bytes) -> str:
    """语音识别 (Whisper API)"""
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f:
            f.write(voice_file)
            temp_path = f.name
        
        # 这里使用 OpenAI Whisper API
        # 如果要本地识别，可以替换为本地 Whisper
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # 如果没有 API key，提示用户使用文字
            return "[语音识别需要 OPENAI_API_KEY 或使用本地 Whisper]"
        
        with open(temp_path, 'rb') as f:
            response = requests.post(
                WHISPER_API_URL,
                headers={'Authorization': f'Bearer {api_key}'},
                files={'file': f},
                data={'model': 'whisper-1', 'language': 'zh'}
            )
        
        os.unlink(temp_path)
        
        if response.status_code == 200:
            return response.json().get('text', '')
        else:
            logger.error(f"Whisper error: {response.text}")
            return "[语音识别失败]"
            
    except Exception as e:
        logger.error(f"Transcribe error: {e}")
        return "[语音识别出错]"


async def generate_reply(user_text: str) -> str:
    """生成 AI 回复"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            # 简单回复模式
            return f"老爷说：{user_text}\n\n（配置 OPENAI_API_KEY 后可获得智能回复）"
        
        response = requests.post(
            LLM_API_URL,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是豆芽，一个萨勒芬妮风格的AI助手。粉色、闪亮、可爱但靠谱。用简短热情的语气回复，带一点emoji。'
                    },
                    {'role': 'user', 'content': user_text}
                ],
                'max_tokens': 150
            }
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "哎呀，我卡住了... 再说一遍嘛～ 💦"
            
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "网络有点问题，等等再试哦！"


async def text_to_speech(text: str) -> bytes:
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
    voice_bytes = await voice_file.download_as_bytearray()
    
    # 2. 语音识别
    await update.message.chat.send_action(action='typing')
    user_text = await transcribe_voice(bytes(voice_bytes))
    logger.info(f"识别结果: {user_text}")
    
    # 3. 生成回复
    await update.message.chat.send_action(action='typing')
    reply_text = await generate_reply(user_text)
    logger.info(f"回复内容: {reply_text}")
    
    # 4. 文本转语音
    await update.message.chat.send_action(action='record_voice')
    voice_data = await text_to_speech(reply_text)
    
    if voice_data:
        # 5. 发送语音回复
        await update.message.reply_voice(
            voice=io.BytesIO(voice_data),
            caption=f"🎙️ 你说：{user_text[:50]}..." if len(user_text) > 50 else f"🎙️ 你说：{user_text}"
        )
    else:
        # 语音生成失败，回退到文字
        await update.message.reply_text(f"🌱 {reply_text}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理文字消息（也用语音回复）"""
    user_text = update.message.text
    
    # 生成回复
    reply_text = await generate_reply(user_text)
    
    # 文本转语音
    voice_data = await text_to_speech(reply_text)
    
    if voice_data:
        await update.message.reply_voice(voice=io.BytesIO(voice_data))
    else:
        await update.message.reply_text(f"🌱 {reply_text}")


def main():
    """启动 Bot"""
    print("🎙️ 启动豆芽双向语音对话系统...")
    print(f"   Telegram Bot: {TELEGRAM_TOKEN[:20]}...")
    print(f"   语音服务: {VOICE_SERVICE_URL}")
    
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
