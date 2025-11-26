# 🔑 LICENSE KEY - QUICK REFERENCE

## Your Generated License Key

```
eyJjcmVhdGVkX2F0IjogIjIwMjUtMTEtMjZUMTI6NDg6NDguMDM3ODExIiwgImVuZF9kYXRlIjogIjIwMjYtMDItMjQiLCAibGljZW5zZV9pZCI6ICJUUklBT
CIsICJzdGFydF9kYXRlIjogIjIwMjUtMTEtMjYifQ==.9b7a1a0605e1b5383b8405368590f2418b47fbb05160098c8e730f719c73e9e5
```

### License Details
- **Type:** TRIAL
- **Valid From:** November 26, 2025
- **Valid Until:** February 24, 2026
- **Days Remaining:** 90 days
- **Status:** ✅ ACTIVE

---

## How to Use

### Option 1: Automatic (Recommended)
The key is already saved to `.license` file. Just run:
```powershell
python main.py
```
The application will auto-load the license.

### Option 2: Manual Activation in App
1. Launch the application
2. Click "🔓 Activate" button
3. Paste the key above
4. Click "Activate"

### Option 3: Command Line
```powershell
python generate_key.py --validate "key_here"
```

---

## Key Management Commands

### Generate Different License Types
```powershell
# 30-day Demo
python generate_key.py --days 30 --type DEMO

# 365-day Professional
python generate_key.py --days 365 --type PROFESSIONAL

# 90-day Trial (default)
python generate_key.py --days 90 --type TRIAL
```

### Validate Your Key
```powershell
python generate_key.py --validate "YOUR_KEY_HERE"
```

### Get Key Information
```powershell
python generate_key.py --info "YOUR_KEY_HERE"
```

---

## Troubleshooting

### "License expired"
Generate a new 90-day key:
```powershell
python generate_key.py --days 90 --type TRIAL
```

### "License signature invalid"
The key has been corrupted. Use the one above or generate a new one.

### "Not activated"
Paste this key into the app's activation dialog:
```
eyJjcmVhdGVkX2F0IjogIjIwMjUtMTEtMjZUMTI6NDg6NDguMDM3ODExIiwgImVuZF9kYXRlIjogIjIwMjYtMDItMjQiLCAibGljZW5zZV9pZCI6ICJUUklBT
CIsICJzdGFydF9kYXRlIjogIjIwMjUtMTEtMjYifQ==.9b7a1a0605e1b5383b8405368590f2418b47fbb05160098c8e730f719c73e9e5
```

---

## Start the Application

```powershell
# 1. Install PyQt6 (first time only)
pip install PyQt6

# 2. Launch the application
python main.py
```

---

## Security Notes

- ✅ License key is HMAC-SHA256 signed (tamper-proof)
- ✅ Stored locally in `.license` file
- ✅ Only developer can generate new keys
- ✅ Cannot be modified without invalidating signature

---

**Generated:** November 26, 2025  
**License File:** `.license`  
**Application:** Sports Forecasting Platform v1.0
