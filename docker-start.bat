@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo 古玩字画智能对比系统 - Docker 启动脚本
echo ==========================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker 未安装
    echo 请先安装 Docker Desktop
    pause
    exit /b 1
)

echo 请选择启动模式:
echo   1) 生产环境
echo   2) 开发环境
echo   3) 仅启动数据库
echo   4) 停止所有服务
echo.

set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto production
if "%choice%"=="2" goto development
if "%choice%"=="3" goto database
if "%choice%"=="4" goto stop
goto invalid

:production
echo.
echo 🚀 启动生产环境...
docker-compose up -d
goto end

:development
echo.
echo 🔧 启动开发环境...
docker-compose -f docker-compose.dev.yml up -d
goto end

:database
echo.
echo 🗄️  启动数据库...
docker-compose up -d postgres
echo.
echo ✅ 数据库已启动
echo.
echo 连接信息:
echo   主机: localhost
echo   端口: 5432
echo   数据库: antique_comparison
echo   用户名: postgres
echo   密码: postgres
goto end

:stop
echo.
echo 🛑 停止所有服务...
docker-compose down
docker-compose -f docker-compose.dev.yml down
echo ✅ 所有服务已停止
pause
exit /b 0

:invalid
echo.
echo ❌ 无效的选项
pause
exit /b 1

:end
echo.
echo ==========================================
echo ✅ 启动完成!
echo.
echo 访问地址:
echo   前端: http://localhost
echo   后端: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo 查看日志:
echo   docker-compose logs -f
echo.
echo 停止服务:
echo   docker-compose down
echo ==========================================
pause
