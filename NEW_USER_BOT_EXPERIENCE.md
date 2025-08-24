# New User Bot Experience - Progressive Command System

## Overview
The Telegram bot now implements a progressive command discovery system to avoid overwhelming new users while providing advanced functionality for experienced users.

## Command Visibility Progression

### Stage 1: First-Time Users
**Visible Commands:** `/start` only

**Behavior:**
- New users see only the `/start` command in their bot interface
- All other commands are hidden until the user completes onboarding
- The `/start` command initiates the user onboarding process

### Stage 2: Post-Onboarding Users  
**Visible Commands:** `/start`, `/commit`, `/done`, `/help`

**Behavior:**
- After successful completion of `/start` onboarding, users gain access to core functionality
- `/commit` - Create new commitments
- `/done` - Mark commitments as complete  
- `/help` - Show all available commands and explanations
- Advanced commands remain hidden until accessed via `/help`

### Stage 3: Full Access (via /help)
**All Commands Available:**
- `/start` - User onboarding and account setup
- `/commit` - Create new commitments
- `/done` - Mark commitments as complete
- `/list` - View all active commitments
- `/progress` - View progress statistics and streaks
- `/help` - Show this command list with explanations
- `/feedback` - Submit feedback about the system
- `/upgrade` - Access premium features and payment process

## Implementation Status

### ✅ Completed Features
- Progressive command visibility system implemented
- Command hiding/showing based on user onboarding status
- Help system with full command explanations

### 🔄 Pending Implementation
- `/upgrade` command for payment processing
- Integration with payment gateway
- Premium feature gating

## Technical Implementation

### Command Visibility Control
Commands are controlled via the Telegram Bot API's `setMyCommands` endpoint with scope-specific command lists:

```python
# First-time users - only /start
basic_commands = [
    BotCommand(command="start", description="Begin your progress journey")
]

# Post-onboarding users - core commands
core_commands = [
    BotCommand(command="start", description="Account and onboarding"),
    BotCommand(command="commit", description="Create a new commitment"), 
    BotCommand(command="done", description="Mark commitment complete"),
    BotCommand(command="help", description="Show all commands")
]

# Full command set (revealed via /help)
all_commands = core_commands + [
    BotCommand(command="list", description="View active commitments"),
    BotCommand(command="progress", description="View progress stats"),
    BotCommand(command="feedback", description="Send feedback"),
    BotCommand(command="upgrade", description="Access premium features")
]
```

### User State Tracking
User progression is tracked in the database:
- `first_bot_interaction_at` - Timestamp of first `/start`
- `onboarded_at` - Completion of onboarding process
- `status` - User status (new, onboarded, paid, etc.)

## User Flow

### New User Journey
1. **Discovery**: User finds bot and sees only `/start` command
2. **Onboarding**: `/start` guides through account setup and goal setting
3. **Core Usage**: User gains access to `/commit`, `/done`, `/help`
4. **Feature Discovery**: `/help` reveals full command set
5. **Premium Upgrade**: `/upgrade` provides access to paid features

### Command Explanations (via /help)

**Essential Commands:**
- `/start` - Set up your account, define goals, and join the community
- `/commit` - Create a specific, actionable commitment with deadline
- `/done` - Mark commitments complete and build your streak

**Progress Tracking:**
- `/list` - See all your active commitments and their status
- `/progress` - View completion rates, streaks, and achievement stats

**Community & Support:**
- `/feedback` - Send suggestions, bug reports, or success stories
- `/upgrade` - Unlock premium features: advanced analytics, priority support, extended commitment history

## Benefits of Progressive Design

### User Experience Benefits
- **Reduced Cognitive Load**: New users aren't overwhelmed by complex command lists
- **Guided Discovery**: Natural progression from basic to advanced features
- **Improved Onboarding**: Focus on essential actions first

### Business Benefits  
- **Higher Completion Rates**: Users more likely to complete onboarding
- **Better Engagement**: Progressive disclosure encourages exploration
- **Premium Conversion**: `/upgrade` command creates clear premium pathway

## Future Enhancements

### Planned Features
- **Smart Command Suggestions**: Contextual command recommendations
- **Usage-Based Progression**: Unlock commands based on activity level
- **Personalized Help**: Tailored command explanations based on user goals
- **Command Analytics**: Track which commands drive engagement

### Premium Command Extensions
- `/analytics` - Detailed performance insights
- `/coach` - AI-powered progress coaching
- `/export` - Data export and backup
- `/integrations` - Connect with other productivity tools

## Testing Scenarios

### New User Test
1. Create new Telegram account
2. Start conversation with bot
3. Verify only `/start` appears in command menu
4. Complete `/start` onboarding
5. Verify `/commit`, `/done`, `/help` appear
6. Use `/help` to discover full command set

### Returning User Test
1. Use existing user account
2. Verify appropriate commands visible based on user status
3. Test command functionality for each user stage
4. Verify `/upgrade` command for premium flow

---

**Last Updated:** 2025-08-23
**Version:** 1.0
**Status:** Implemented (except /upgrade payment integration)