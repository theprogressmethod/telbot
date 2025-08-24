# Week 1 MVP Manual Testing Checklist
*Test everything we just deployed to production*

## 🎯 **RENDER DEPLOYMENT URLS**
Once your Render deployment is complete, you'll have:
- **Bot API Service**: `https://tpm-bot-api.onrender.com` 
- **Dashboard Service**: `https://tpm-dashboards.onrender.com`

## ✅ **MANUAL TESTING CHECKLIST**

### **1. Health Check (CRITICAL)**
- [ ] Visit: `https://tpm-bot-api.onrender.com/health`
- [ ] Should return: `{"status": "healthy"}` or similar
- [ ] Response time: Under 3 seconds

### **2. User Dashboard (CORE FEATURE)**
- [ ] Visit: `https://tpm-dashboards.onrender.com/dashboard?user_id=865415132`
- [ ] **Night Sky Theme**: Should see starfield background
- [ ] **SCOREBOARD Title**: Should show "{Your Name}'S SCOREBOARD"
- [ ] **Mobile Responsive**: Test on phone - should look good
- [ ] **Data Loading**: Should show your commitments/progress

### **3. Admin Dashboard (CRITICAL)**
- [ ] Visit: `https://tpm-dashboards.onrender.com/admin/week1`
- [ ] **Without API Key**: Should be blocked/unauthorized
- [ ] **With API Key**: Add header `X-Admin-Key: admin_week1_dashboard_access_2025`
  - Use browser dev tools or Postman
  - Should load full admin interface
- [ ] **Users Section**: Should show user list
- [ ] **Pods Section**: Should show pods 
- [ ] **Commitments Section**: Should show commitments

### **4. Pod Settings (MAJOR FIX)**
- [ ] In admin dashboard, go to Pods section
- [ ] Click on a pod to edit settings
- [ ] Change pod name or status
- [ ] Click "Save Settings"
- [ ] **CRITICAL**: Should save WITHOUT "max_members" error
- [ ] Changes should persist after refresh

### **5. Admin Commitment Creation (NEW FEATURE)**
- [ ] In admin dashboard, find "Add Commitment" section
- [ ] Select a user from dropdown
- [ ] Enter a test commitment: "Test admin-created commitment"
- [ ] Submit commitment
- [ ] **Should**: Appear immediately in commitments list
- [ ] **Should**: Show "Created by: admin" attribution

### **6. Database Connectivity**
- [ ] All data should load from production Supabase
- [ ] User count should match your actual users
- [ ] Pod data should be current
- [ ] No "connection refused" or database errors

### **7. API Endpoints**
Test these URLs with admin headers:
- [ ] `GET /api/crud/users` - Returns user list
- [ ] `GET /api/crud/pods` - Returns pods list  
- [ ] `GET /api/crud/commitments` - Returns commitments
- [ ] `PUT /api/crud/pods/{id}` - Updates pod settings
- [ ] `POST /api/crud/commitments` - Creates new commitment

### **8. Cross-Browser Testing**
- [ ] **Chrome**: All features work
- [ ] **Safari**: Dashboard displays correctly
- [ ] **Firefox**: Admin functions work
- [ ] **Mobile Safari**: Responsive design works
- [ ] **Mobile Chrome**: Touch interactions work

## 🚨 **FAILURE SYMPTOMS TO WATCH FOR**

### **Database Issues**:
- "Connection refused" errors
- Empty user/pod lists when you know data exists
- Supabase authentication errors

### **Environment Issues**:
- 500 errors on API calls
- "ADMIN_API_KEY not set" warnings in logs
- Missing environment variable errors

### **UI/CSS Issues**:
- No starfield background (CSS not loading)
- Mobile layout broken
- Missing gradients or night sky theme

### **API Issues**:
- Pod settings still showing max_members error
- Admin commitments not saving
- Unauthorized errors even with correct API key

## ⚡ **QUICK SMOKE TEST (2 MINUTES)**

1. **Health**: Hit `/health` endpoint ✅
2. **User Dashboard**: Load with your user_id ✅  
3. **Admin Login**: Access admin with API key ✅
4. **Pod Save**: Try saving pod settings ✅
5. **Admin Commit**: Create one test commitment ✅

If all 5 pass → **Week 1 MVP is LIVE!** 🎉

## 📋 **AUTOMATED TESTING**

Run the comprehensive test suite:
```bash
python3 week1_comprehensive_test.py
```

Enter your Render URLs when prompted.

---

## 📞 **WHEN TO CALL FOR HELP**

- Health endpoint returns errors
- Admin dashboard won't load with correct API key  
- Pod settings still show max_members error
- User dashboard shows no data
- Mobile layout is completely broken

**Share your Render URLs and I'll help debug immediately!**