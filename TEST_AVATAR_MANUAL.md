# Manual Test — Avatar Upload Functionality

## Prerequisites
- Backend running: `uvicorn app.main:app --reload` (port 8000)
- Frontend running: `npm run dev` (port 5173)
- User logged in with valid JWT token

## Test Steps

### 1. Open Profile Page
```
Navigate to: http://localhost:5173/app/account/profile
```

Expected: Profile header visible with avatar and user identity

### 2. Click Upload Avatar Button
```
Click the camera icon on the avatar
```

Expected: File picker opens

### 3. Select Valid Image
```
Choose a PNG, JPEG, GIF, or WebP image (< 5MB)
```

Expected:
- Loading spinner appears
- File uploads to /api/account/upload-avatar
- New avatar displays immediately
- No errors in console

### 4. Verify API Response
```
Network tab should show:
- POST /api/account/upload-avatar
- Status: 200
- Response: { "avatar_url": "/uploads/avatars/{uuid}.png" }
```

### 5. Refresh Page
```
Press F5 to reload
```

Expected: Avatar persists (saved to database)

### 6. Try Invalid File (Negative Test)
```
Try uploading a PDF or text file
```

Expected:
- Request fails with 400 Bad Request
- Detail: "Tipo de arquivo não permitido"
- Avatar unchanged

### 7. Try Large File (Negative Test)
```
Try uploading a file > 5MB
```

Expected:
- Request fails with 400 Bad Request
- Detail: "Arquivo muito grande (máx 5MB)"

## Success Criteria
- ✅ Avatar uploads successfully
- ✅ Invalid types rejected
- ✅ Size limit enforced
- ✅ Avatar persists on refresh
- ✅ No TypeScript errors
- ✅ No console errors
- ✅ Profile form functions normally

## Edge Cases Tested (Automated)
- ✅ PNG file type validation
- ✅ PDF rejection
- ✅ Missing file handling

---

**Status:** All automated tests pass (4/4)  
**Ready for:** Manual QA / Production
