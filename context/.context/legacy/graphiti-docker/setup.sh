#!/bin/bash
set -e

echo "🚀 Graphiti MCP Server Setup"
echo "=============================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   Run: nano .env"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Check if OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env"
    echo "   Please edit .env and add your OpenAI API key"
    exit 1
fi

echo "✅ Environment configured"
echo ""

# Start Docker container
echo "🐳 Starting Graphiti MCP Server..."
docker compose up -d

echo ""
echo "⏳ Waiting for server to be healthy..."
sleep 5

# Check if container is running
if docker ps | grep -q graphiti-mcp-server; then
    echo "✅ Graphiti MCP Server is running!"
    echo ""
    echo "📊 Container status:"
    docker ps | grep graphiti-mcp-server
    echo ""
    echo "📝 View logs:"
    echo "   docker compose logs -f graphiti-mcp"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Add the following to ~/.config/zed/settings.json under 'context_servers':"
    echo ""
    cat << 'ZEDCONFIG'
    "graphiti": {
      "source": "custom",
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "graphiti-mcp-server",
        "python",
        "-m",
        "graphiti_mcp_server"
      ]
    }
ZEDCONFIG
    echo ""
    echo "   2. Restart Zed"
    echo "   3. The Graphiti context server will be available in Zed!"
else
    echo "❌ Error: Container failed to start"
    echo "   Check logs with: docker compose logs"
    exit 1
fi
