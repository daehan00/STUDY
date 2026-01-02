#!/bin/bash

# 가상환경 활성화
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

pyinstaller --noconfirm --onedir --windowed \
    --icon "assets/pulse.icns" \
    --name "Watchdog" \
    --clean \
    --add-data "assets:assets" \
    --hidden-import=pymysql \
    --hidden-import=aiomysql \
    --hidden-import=sqlalchemy.dialects.mysql.aiomysql \
    --hidden-import=sqlalchemy.dialects.mysql.pymysql \
    --hidden-import=psycopg \
    main.py