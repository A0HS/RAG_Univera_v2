import streamlit as st
import os
import sys
from datetime import datetime
import json

# 로컬 모듈 import
from rag_system import RAGSystem
from ui_components import ChatUI, SidebarUI
from config import Config

# 페이지 설정
st.set_page_config(
    page_title="유니베라 RAG 챗봇",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
def load_css():
    st.markdown("""
    <style>
    /* 메인 컨테이너 */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* 채팅 메시지 스타일 */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 20%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: var(--background-color);
        border: 1px solid var(--border-color);
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 20%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 다크모드 스타일 */
    .dark-mode .assistant-message {
        background: #2d3748;
        border-color: #4a5568;
        color: #e2e8f0;
    }
    
    /* 로딩 애니메이션 */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-right: 20%;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    /* 입력창 스타일 */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 12px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* 사이드바 스타일 */
    .sidebar .sidebar-content {
        background: var(--sidebar-background);
    }
    
    /* 헤더 스타일 */
    .header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }
    
    .header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        font-size: 2.5rem;
    }
    
    /* 다크모드 변수 */
    :root {
        --background-color: #ffffff;
        --border-color: #e2e8f0;
        --sidebar-background: #f7fafc;
        --text-color: #262730;
        --secondary-background: #f0f2f6;
    }
    
    /* 다크모드 스타일 */
    .dark-mode {
        --background-color: #1a202c;
        --border-color: #4a5568;
        --sidebar-background: #2d3748;
        --text-color: #e2e8f0;
        --secondary-background: #2d3748;
    }
    
    /* 다크모드 적용 */
    .dark-mode .stApp {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }
    
    .dark-mode .stSidebar {
        background-color: var(--sidebar-background) !important;
    }
    
    .dark-mode .stSelectbox > div > div {
        background-color: var(--secondary-background) !important;
        color: var(--text-color) !important;
    }
    
    .dark-mode .stSlider > div > div {
        background-color: var(--secondary-background) !important;
    }
    
    .dark-mode .stButton > button {
        background-color: var(--secondary-background) !important;
        color: var(--text-color) !important;
        border-color: var(--border-color) !important;
    }
    </style>
    
    <script>
    // 다크모드 적용 스크립트
    function applyDarkMode() {
        const isDarkMode = window.parent.document.querySelector('[data-testid="stSidebar"]')?.getAttribute('data-dark-mode') === 'true' || 
                          localStorage.getItem('darkMode') === 'true';
        
        if (isDarkMode) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }
    
    // 페이지 로드 시 적용
    applyDarkMode();
    
    // 사이드바 변경 감지
    const observer = new MutationObserver(applyDarkMode);
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """세션 상태 초기화"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def load_rag_system():
    """RAG 시스템 로드"""
    if st.session_state.rag_system is None:
        try:
            with st.spinner("🔧 RAG 시스템을 자동으로 초기화하는 중... (시간이 걸릴 수 있습니다)"):
                st.session_state.rag_system = RAGSystem(
                    pinecone_api_key=Config.PINECONE_API_KEY,
                    pinecone_index_name=Config.PINECONE_INDEX_NAME,
                    openai_api_key=Config.OPENAI_API_KEY
                )
            st.success("✅ RAG 시스템이 성공적으로 로드되었습니다!")
            return True
        except Exception as e:
            st.error(f"❌ RAG 시스템 자동 초기화 실패: {str(e)}")
            
            # 오류 상세 정보 표시
            with st.expander("🔍 오류 상세 정보", expanded=True):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
            
            # 설정 정보 표시
            with st.expander("📋 현재 설정", expanded=False):
                st.json({
                    "문서 경로": Config.FOLDER_PATH,
                    "Pinecone API 키": Config.PINECONE_API_KEY[:20] + "...",
                    "OpenAI API 키": Config.OPENAI_API_KEY[:20] + "...",
                    "인덱스 이름": Config.PINECONE_INDEX_NAME
                })
            
            st.warning("💡 해결 방법:")
            st.write("1. API 키가 올바른지 확인하세요")
            st.write("2. 인터넷 연결을 확인하세요")
            st.write("3. 문서 경로가 존재하는지 확인하세요")
            st.write("4. 터미널에서 오류 로그를 확인하세요")
            
            # 수동 재시도 옵션
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 다시 시도", type="primary"):
                    st.rerun()
            with col2:
                if st.button("📋 설정 확인"):
                    st.write("**현재 설정:**")
                    st.json({
                        "문서 경로": Config.FOLDER_PATH,
                        "Pinecone API 키": Config.PINECONE_API_KEY[:20] + "...",
                        "OpenAI API 키": Config.OPENAI_API_KEY[:20] + "...",
                        "인덱스 이름": Config.PINECONE_INDEX_NAME
                    })
            
            return False
    return True  # 이미 초기화됨

def main():
    """메인 애플리케이션"""
    load_css()
    initialize_session_state()
    
    # 헤더
    st.markdown("""
    <div class="header">
        <h1>🌿 유니베라 RAG 챗봇</h1>
        <p>유니베라 회사에 대한 모든 정보를 AI와 함께 알아보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # RAG 시스템 초기화
    rag_initialized = load_rag_system()
    
    if not rag_initialized:
        # RAG 시스템이 초기화되지 않은 경우
        st.markdown("---")
        st.warning("⚠️ RAG 시스템이 초기화되지 않았습니다. 위의 버튼을 클릭하여 초기화하세요.")
        
        # 사이드바만 표시
        sidebar_ui = SidebarUI()
        sidebar_ui.render()
        return
    
    # 사이드바
    sidebar_ui = SidebarUI()
    sidebar_ui.render()
    
    # 메인 채팅 영역
    chat_ui = ChatUI()
    
    # 레이아웃 모드에 따른 컬럼 설정
    layout_mode = st.session_state.get('layout_mode', 'wide')
    
    if layout_mode == 'wide':
        # 넓은 화면 레이아웃
        col1, col2 = st.columns([3, 1])
    else:
        # 일반 화면 레이아웃
        col1, col2 = st.columns([2, 1])
    
    with col1:
        # 채팅 히스토리 표시
        chat_ui.display_chat_history()
        
        # 입력 영역
        chat_ui.render_input_area()
    
    with col2:
        # 정보 패널
        chat_ui.render_info_panel()

if __name__ == "__main__":
    main()
