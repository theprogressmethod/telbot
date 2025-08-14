# Add this to your main.py for form submissions

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime

class PodApplication(BaseModel):
    name: str
    email: EmailStr
    telegram: str = None
    goal: str
    why: str
    timezone: str
    commitment: str
    terms: bool
    timestamp: str

@app.post("/apply")
async def submit_application(application: PodApplication):
    """Handle accountability pod applications from web form"""
    try:
        # Save to Supabase
        application_data = {
            "name": application.name,
            "email": application.email,
            "telegram_username": application.telegram,
            "goal": application.goal,
            "why_accountability": application.why,
            "timezone": application.timezone,
            "weekly_commitment": application.commitment,
            "agreed_to_terms": application.terms,
            "applied_at": application.timestamp,
            "status": "pending"
        }
        
        # Insert into applications table
        result = supabase.table("pod_applications").insert(application_data).execute()
        
        # Send notification to admin via Telegram
        admin_message = f"""
🆕 New Pod Application!

👤 Name: {application.name}
📧 Email: {application.email}
💬 Telegram: {application.telegram or 'Not provided'}
🎯 Goal: {application.goal}
⏰ Timezone: {application.timezone}
📅 Commitment: {application.commitment} hours/week

Review in Supabase dashboard.
"""
        
        # Send to admin (replace with your admin chat ID)
        if bot:
            await bot.send_message(
                chat_id=YOUR_ADMIN_CHAT_ID,  # Add your Telegram user ID here
                text=admin_message
            )
        
        # If they provided Telegram username, send them a welcome message
        if application.telegram:
            # Store for later outreach
            pass
        
        return {
            "status": "success",
            "message": "Application received! Check your email for next steps."
        }
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit application")

@app.get("/applications/stats")
async def get_application_stats():
    """Get statistics on pod applications"""
    try:
        # Get application counts
        total = supabase.table("pod_applications").select("count", count="exact").execute()
        pending = supabase.table("pod_applications").select("count", count="exact").eq("status", "pending").execute()
        approved = supabase.table("pod_applications").select("count", count="exact").eq("status", "approved").execute()
        
        return {
            "total_applications": total.count,
            "pending_review": pending.count,
            "approved": approved.count
        }
    except Exception as e:
        return {"error": str(e)}