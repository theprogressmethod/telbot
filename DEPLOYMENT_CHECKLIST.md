# PRODUCTION DEPLOYMENT CHECKLIST
**Use this checklist for every production deployment**

## PRE-DEPLOYMENT (Required)

### Environment Verification
- [ ] **Environment Detection Working**
  ```bash
  python -c "from environment_manager import env_manager; print(env_manager.current_env.value)"
  ```
  
- [ ] **Configuration Valid**
  ```bash
  python -c "from environment_manager import env_manager; print(env_manager.validate_config())"
  ```
  
- [ ] **Claude Context Generated**
  ```bash
  python environment_manager.py
  ```
  - [ ] Verify `CLAUDE_CONTEXT.json` exists
  - [ ] Check for production warnings

### Code Quality Checks
- [ ] **Critical Path Tests Pass**
  ```bash
  python -m pytest test_critical_paths.py -v
  ```
  
- [ ] **No Undefined Variables**
  - [ ] Search codebase for undefined variable references
  - [ ] Verify all variables are defined before use
  
- [ ] **Feature Flags Reviewed**
  - [ ] Production feature flags are conservative
  - [ ] No beta features enabled in production
  - [ ] `first_impression_fsm` is disabled

### Database Safety
- [ ] **Database Backup Created**
  - [ ] Recent backup available
  - [ ] Backup tested and validated
  
- [ ] **Schema Changes Reviewed**
  - [ ] All migrations tested in staging
  - [ ] Rollback scripts prepared

### Monitoring Setup
- [ ] **Error Tracking Configured**
  - [ ] Sentry or similar error monitoring active
  - [ ] Production alerts configured
  
- [ ] **Health Checks Working**
  - [ ] `/health` endpoint responding
  - [ ] Database connectivity verified

## DEPLOYMENT PROCESS

### 1. Pre-Deployment Announcement
- [ ] **Notify team of deployment window**
- [ ] **Check for any ongoing user sessions**
- [ ] **Prepare rollback plan**

### 2. Deploy to Staging First
- [ ] **Deploy to staging environment**
  ```bash
  # Deploy to staging
  git push origin staging
  ```
  
- [ ] **Run staging tests**
  ```bash
  python test_critical_paths.py
  ```
  
- [ ] **Manual staging verification**
  - [ ] `/start` command works
  - [ ] `/commit` command works
  - [ ] `/done` command works  
  - [ ] `/help` command works
  - [ ] No error messages or crashes

### 3. Production Deployment
- [ ] **Deploy to production**
  ```bash
  git push origin main
  ```
  
- [ ] **Monitor deployment logs**
  - [ ] No error messages during startup
  - [ ] Environment detected correctly
  - [ ] Database connection established
  
- [ ] **Immediate health check**
  ```bash
  curl https://your-production-url.com/health
  ```

### 4. Post-Deployment Verification
- [ ] **Critical Commands Test** (within 5 minutes)
  - [ ] Send `/start` to production bot - should respond
  - [ ] Send `/help` to production bot - should respond  
  - [ ] Send `/commit test` to production bot - should work
  - [ ] Send `/done` to production bot - should work
  
- [ ] **Monitor Error Rates** (first 15 minutes)
  - [ ] Check error monitoring dashboard
  - [ ] Review application logs
  - [ ] No increase in error rates

### 5. Extended Monitoring
- [ ] **User Experience Check** (first hour)
  - [ ] Monitor user interactions
  - [ ] Check for user complaints
  - [ ] Verify core functionality working
  
- [ ] **Performance Monitoring** (first 24 hours)
  - [ ] Response times normal
  - [ ] Database performance stable
  - [ ] No memory leaks or issues

## POST-DEPLOYMENT (Required)

### Immediate Actions (0-1 hour)
- [ ] **Update deployment log**
- [ ] **Notify team of successful deployment**
- [ ] **Archive deployment artifacts**

### Follow-up Actions (24 hours)
- [ ] **Review error logs**
- [ ] **Check user engagement metrics**
- [ ] **Document any issues encountered**

## ROLLBACK PROCEDURE

### When to Rollback
- [ ] **Critical errors in logs**
- [ ] **Users cannot use basic commands**
- [ ] **Database connection issues**
- [ ] **Significant increase in error rate**

### Rollback Steps
1. **Immediate Action**
   ```bash
   # Revert to previous deployment
   git revert HEAD
   git push origin main
   ```

2. **Database Rollback** (if needed)
   ```bash
   # Run rollback scripts
   # Restore from backup if necessary
   ```

3. **Verification**
   - [ ] Previous version working
   - [ ] Critical commands functional
   - [ ] Users can interact with bot

4. **Communication**
   - [ ] Notify team of rollback
   - [ ] Document rollback reason
   - [ ] Plan fix for next deployment

## EMERGENCY CONTACTS

**Primary:** Thomas Mulhern  
**Backup:** [Add backup contact]  
**Escalation:** [Add escalation contact]

## LESSONS FROM AUGUST 18, 2025 OUTAGE

### Root Cause
- **Undefined variable `is_first_time`** in `/start` command handler
- **No environment separation** - dev features in production
- **No critical path testing** before deployment

### Prevention Measures Implemented
- ✅ **Environment Manager** - Prevents dev/prod contamination
- ✅ **Feature Flags** - Safe rollout of new features  
- ✅ **Critical Path Tests** - Catches basic errors
- ✅ **Emergency Fix Applied** - Fixed undefined variable
- ✅ **Claude Context System** - Always know which environment you're in

### Never Again Checklist
- [ ] **No undefined variables** - Check with tests
- [ ] **Environment isolation** - Verify with environment manager
- [ ] **Feature flags conservative** - Production gets stable features only
- [ ] **Critical paths tested** - `/start`, `/commit`, `/done`, `/help` must work
- [ ] **Rollback ready** - Can revert within 5 minutes

---

**Remember: The August 18 outage was caused by a simple undefined variable. This checklist prevents similar incidents.**

**Production is sacred. Test everything. When in doubt, don't deploy.**