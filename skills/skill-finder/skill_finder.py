#!/usr/bin/env python3
"""
🔍 AI技能发现助手
根据需求智能推荐可用技能
"""

import subprocess
import json
import sys

class SkillFinder:
    """技能发现器"""
    
    # 常用技能映射表（持续更新）
    SKILL_MAPPING = {
        "语音": ["openai-whisper", "faster-whisper", "speech-to-text", "voice-wake-say"],
        "语音转文字": ["openai-whisper", "faster-whisper", "speech-to-text"],
        "语音识别": ["openai-whisper", "local-whisper"],
        "天气": ["weather", "openweather", "yr-weather"],
        "天气查询": ["weather"],
        "PDF": ["nano-pdf", "pdf-edit", "pdf-tools", "pdf"],
        "pdf": ["nano-pdf"],
        "PDF编辑": ["nano-pdf"],
        "pdf编辑": ["nano-pdf"],
        "钉钉": ["dingtalk-webhook", "dingtalk-bot"],
        "图片": ["openai-image-gen", "nano-banana-pro", "stable-diffusion"],
        "图片生成": ["openai-image-gen", "stable-diffusion"],
        "视频": ["video-frames", "ffmpeg-edit"],
        "视频剪辑": ["video-frames"],
        "搜索": ["tavily", "web-search", "brave-search"],
        "网络搜索": ["tavily", "web-search"],
        "笔记": ["obsidian", "notion", "apple-notes"],
        "笔记管理": ["obsidian", "notion"],
        "股票": ["stock-query", "yahoo-finance"],
        "股票查询": ["stock-query"],
        "邮件": ["himalaya", "gmail", "email-send"],
        "发送邮件": ["himalaya"],
        "数据库": ["sqlite", "mysql-query", "postgres-cli"],
        "GitHub": ["github", "git-ops"],
        "代码管理": ["github", "coding-agent"],
    }
    
    def find_skills(self, keyword):
        """查找技能"""
        keyword = keyword.lower().strip()
        
        # 1. 查本地映射表
        matched = []
        for k, skills in self.SKILL_MAPPING.items():
            if keyword in k or k in keyword:
                matched.extend(skills)
        
        # 去重
        matched = list(set(matched))
        
        if matched:
            return {
                "source": "本地知识库",
                "skills": matched,
                "message": f"找到 {len(matched)} 个推荐技能"
            }
        
        # 2. 调用 clawhub 搜索
        try:
            result = subprocess.run(
                ["npx", "clawhub", "search", keyword, "--limit", "5"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "source": "ClawHub搜索",
                "output": result.stdout,
                "message": "已搜索 ClawHub 技能库"
            }
            
        except Exception as e:
            return {
                "source": "搜索失败",
                "error": str(e),
                "message": "搜索出错，请检查网络"
            }
    
    def recommend(self, task_description):
        """
        根据任务描述推荐技能
        
        示例:
        - "我想语音识别" → 推荐 whisper
        - "需要查天气" → 推荐 weather
        - "要编辑PDF" → 推荐 nano-pdf
        """
        # 提取关键词
        keywords = self._extract_keywords(task_description)
        
        all_recommendations = []
        for kw in keywords:
            result = self.find_skills(kw)
            if result.get("skills"):
                all_recommendations.extend(result["skills"])
        
        # 去重
        all_recommendations = list(set(all_recommendations))
        
        return {
            "task": task_description,
            "keywords": keywords,
            "recommendations": all_recommendations,
            "install_command": f"npx clawhub install {all_recommendations[0]}" if all_recommendations else None
        }
    
    def _extract_keywords(self, text):
        """从描述中提取关键词"""
        # 简单的关键词提取
        text = text.lower()
        keywords = []
        
        # 检查映射表中的关键词
        for k in self.SKILL_MAPPING.keys():
            if k in text:
                keywords.append(k)
        
        # 如果没找到，返回原文本
        if not keywords:
            keywords = [text]
        
        return keywords


def main():
    if len(sys.argv) < 2:
        print("🔍 AI技能发现助手")
        print("=" * 50)
        print("用法:")
        print("  python3 skill_finder.py '语音识别'")
        print("  python3 skill_finder.py '我想做PDF编辑'")
        print("  python3 skill_finder.py '需要查天气'")
        print("")
        print("💡 会自动搜索 ClawHub 技能库并推荐")
        sys.exit(1)
    
    query = sys.argv[1]
    
    finder = SkillFinder()
    result = finder.recommend(query)
    
    print("=" * 50)
    print(f"📝 任务: {result['task']}")
    print(f"🔑 关键词: {', '.join(result['keywords'])}")
    print("")
    
    if result['recommendations']:
        print("✅ 推荐技能:")
        for i, skill in enumerate(result['recommendations'][:5], 1):
            print(f"  {i}. {skill}")
        print("")
        print(f"💾 安装命令:")
        print(f"  npx clawhub install {result['recommendations'][0]}")
    else:
        print("❌ 未找到匹配技能")
        print("💡 建议: 尝试其他关键词或直接搜索 'npx clawhub search'")
    
    print("=" * 50)


if __name__ == '__main__':
    main()
