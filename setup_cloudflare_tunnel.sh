#!/bin/bash
# Cloudflare Tunnel setup for Dream Recorder

echo "=== Cloudflare Tunnel Setup for Dream Recorder ==="
echo ""
echo "This will expose your Dream Recorder to the internet via Cloudflare Tunnel"
echo "Prerequisites:"
echo "1. A Cloudflare account"
echo "2. Your domain ([YOUR-DOMAIN]) added to Cloudflare"
echo ""
echo "Steps:"
echo "1. Install cloudflared:"
echo "   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared"
echo "   sudo mv cloudflared /usr/local/bin/"
echo "   sudo chmod +x /usr/local/bin/cloudflared"
echo ""
echo "2. Login to Cloudflare:"
echo "   cloudflared tunnel login"
echo ""
echo "3. Create a tunnel:"
echo "   cloudflared tunnel create dream-recorder"
echo ""
echo "4. Create config file at ~/.cloudflared/config.yml:"
cat << 'CONFIG'
url: http://localhost:5000
tunnel: <TUNNEL_ID>
credentials-file: /home/dreamer/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: dreams.[YOUR-DOMAIN]
    service: http://localhost:5000
  - hostname: [YOUR-DOMAIN]
    service: http://localhost:5000
  - service: http_status:404
CONFIG
echo ""
echo "5. Route traffic to your tunnel:"
echo "   cloudflared tunnel route dns dream-recorder dreams.[YOUR-DOMAIN]"
echo ""
echo "6. Run the tunnel:"
echo "   cloudflared tunnel run dream-recorder"
echo ""
echo "7. Create a systemd service for auto-start:"
echo "   sudo cloudflared service install"
