#!/usr/bin/env python3
# Keep-Alive Service for Nova Bot on Render
# Prevents cold starts by pinging the service every 10 minutes

import asyncio
import aiohttp
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Render deployment URL for Nova bot
NOVA_WEBHOOK_URL = "https://telbot-oo91.onrender.com"
PING_INTERVAL = 600  # 10 minutes (Render sleeps after 15 minutes)

async def ping_nova():
    """Send keep-alive ping to Nova bot"""
    try:
        async with aiohttp.ClientSession() as session:
            # Send a simple GET request to keep the service awake
            async with session.get(f"{NOVA_WEBHOOK_URL}/health", timeout=30) as response:
                status = response.status
                if status == 200:
                    logger.info(f"✅ Nova bot is awake (status: {status})")
                else:
                    logger.warning(f"⚠️ Nova bot responded with status: {status}")
                return status
    except asyncio.TimeoutError:
        logger.error("⏱️ Ping timeout - Nova bot may be starting up")
        return None
    except Exception as e:
        logger.error(f"❌ Ping failed: {e}")
        return None

async def keep_alive_loop():
    """Main loop to keep Nova bot awake"""
    logger.info("🚀 Starting Nova Bot Keep-Alive Service")
    logger.info(f"   Target: {NOVA_WEBHOOK_URL}")
    logger.info(f"   Interval: {PING_INTERVAL} seconds")
    
    consecutive_failures = 0
    
    while True:
        try:
            status = await ping_nova()
            
            if status == 200:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                
            # Alert if multiple failures
            if consecutive_failures >= 3:
                logger.error(f"🚨 Nova bot unresponsive for {consecutive_failures} pings")
            
            # Wait for next ping
            await asyncio.sleep(PING_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("⏹️ Keep-alive service stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            await asyncio.sleep(PING_INTERVAL)

def run_as_background_service():
    """Run as a background service (for deployment)"""
    try:
        asyncio.run(keep_alive_loop())
    except KeyboardInterrupt:
        logger.info("Keep-alive service terminated")

if __name__ == "__main__":
    print("=" * 50)
    print("NOVA BOT KEEP-ALIVE SERVICE")
    print("=" * 50)
    print("\nThis service will ping Nova bot every 10 minutes")
    print("to prevent Render cold starts.\n")
    print("Press Ctrl+C to stop\n")
    
    run_as_background_service()