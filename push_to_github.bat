@echo off
echo ========================================
echo Pushing StudyMate AI to GitHub
echo ========================================
echo.

echo Step 1: Adding all changes...
git add .

echo.
echo Step 2: Showing status...
git status

echo.
echo Step 3: Committing changes...
git commit -m "feat: Complete StudyMate AI multi-agent system for Microsoft Agents League Hackathon 2026 - Implemented all 8 AI agents with adaptive learning loop - Complete demo data system - Comprehensive README documentation - All dependencies included"

echo.
echo Step 4: Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo Done! Check your GitHub repo.
echo ========================================
pause
