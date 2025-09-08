#!/usr/bin/env python3
"""
유니베라 RAG 챗봇 실행 스크립트
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """필수 요구사항 확인"""
    try:
        import streamlit
        import sentence_transformers
        import pinecone
        import openai
        import rank_bm25
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필수 패키지가 누락되었습니다: {e}")
        print("다음 명령어로 설치하세요: pip install -r requirements.txt")
        return False

def check_config():
    """설정 파일 확인"""
    config_file = Path("config.py")
    if not config_file.exists():
        print("❌ config.py 파일이 없습니다.")
        return False
    
    try:
        from config import Config
        if Config.validate_config():
            print("✅ 설정이 올바르게 구성되었습니다.")
            return True
        else:
            print("❌ 설정에 오류가 있습니다.")
            return False
    except Exception as e:
        print(f"❌ 설정 파일 로드 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🌿 유니베라 RAG 챗봇 시작 중...")
    print("=" * 50)
    
    # 요구사항 확인
    if not check_requirements():
        sys.exit(1)
    
    # 설정 확인
    if not check_config():
        print("⚠️  설정에 문제가 있지만 계속 진행합니다...")
    
    print("=" * 50)
    print("🚀 Streamlit 애플리케이션을 시작합니다...")
    print("브라우저에서 http://localhost:8501 로 접속하세요.")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    try:
        # Streamlit 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 애플리케이션이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 애플리케이션 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
