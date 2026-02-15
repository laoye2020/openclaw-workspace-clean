# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

### Polymarket 交易

- **启动交易工具**: `cd polymarket-tool && ./start.sh`
- **交易工具地址**: http://localhost:8502
- **API Key**: 019c3d3c-80a9-725f-96bd-2e29348b07f6

### OpenClaw 快捷命令

- **查看状态**: `openclaw status`
- **查看日志**: `openclaw logs --follow`
- **重启网关**: `openclaw gateway restart`
- **查看技能**: `openclaw skill list`
