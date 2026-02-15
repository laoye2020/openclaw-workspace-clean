#!/bin/bash
# 飞书监工系统配置

APP_ID="cli_a9028c2e64f8dcc6"
APP_SECRET="wDf80ug34S2WmUcfTd0FfgYASOMeqZoA"

# 获取 tenant_access_token
get_token() {
    curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}"
}

# 发送文本消息
send_message() {
    local user_id=$1
    local text=$2
    local token=$(get_token | grep -o '"tenant_access_token":"[^"]*' | cut -d'"' -f4)
    
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"receive_id\": \"$user_id\",
            \"msg_type\": \"text\",
            \"content\": \"{\\\"text\\\": \\\"$text\\\"}\"
        }"
}

# 获取用户列表
get_users() {
    local token=$(get_token | grep -o '"tenant_access_token":"[^"]*' | cut -d'"' -f4)
    
    curl -s -X GET "https://open.feishu.cn/open-apis/contact/v3/users" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json"
}

echo "飞书监工系统工具脚本"
echo "===================="
echo ""
echo "使用方法:"
echo "  获取 Token:  ./feishu-tool.sh token"
echo "  获取用户:   ./feishu-tool.sh users"  
echo "  发送消息:   ./feishu-tool.sh send <user_id> '消息内容'"
echo ""

case "$1" in
    token)
        get_token | jq .
        ;;
    users)
        get_users | jq .
        ;;
    send)
        send_message "$2" "$3"
        ;;
    *)
        echo "未知命令: $1"
        echo "使用: token | users | send"
        ;;
esac
