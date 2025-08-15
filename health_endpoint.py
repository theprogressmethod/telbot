# Health Check Endpoint for Nova Bot
# Add this to your Render deployment to respond to keep-alive pings

from aiohttp import web
import asyncio
import logging

logger = logging.getLogger(__name__)

async def health_check(request):
    """Simple health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "Nova (@ProgressMethodBot)",
        "timestamp": str(request.headers.get('Date', 'unknown'))
    })

async def create_health_server(port=8080):
    """Create a simple health check server"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)  # Root endpoint as backup
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"✅ Health check server running on port {port}")
    return runner

# Add this to your main telbot.py file to run alongside the bot:
# 
# async def main():
#     # Start health server for keep-alive
#     health_runner = await create_health_server()
#     
#     # Start your bot
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())