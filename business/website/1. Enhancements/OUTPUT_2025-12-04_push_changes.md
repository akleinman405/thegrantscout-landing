# How to Push Website Changes

## 1. Open PowerShell
Press **Win + R**, type `powershell`, hit Enter.

## 2. Navigate to your project folder
```powershell
cd "C:\TheGrantScout\3. Website\thegrantscout-landing"
```

## 3. Check the current status
```powershell
git status
```

## 4. Add all changed files
```powershell
git add .
```

## 5. Commit the changes
```powershell
git commit -m "added yearly subscription offer"
```

## 6. Push to GitHub
```powershell
git push
```

## 7. Netlify Deploys Automatically
Once pushed to GitHub, Netlify rebuilds and redeploys the website automatically.
