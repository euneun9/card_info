import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import pandas as pd
from elastic_api import search_index, search_index_with_date_range

# st.title("엘라스틱서치에 저장된 인덱스 조회")
st.title("검색 결과")
st.markdown(
    """     <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{width:250px;}     </style>
    """, unsafe_allow_html=True )

st.sidebar.header("조회하고 싶은 인덱스명을 입력하세요")
index_name = st.sidebar.text_input('인덱스명', value="card_info").lower()

field_name = st.sidebar.text_input('필드명', value="card_name")

match_name = st.sidebar.text_input('조회하려는 내용', value="카드의정석")
clicked1 = st.sidebar.button("해당 정보 확인")

# 한 페이지에 표시할 카드 개수 설정
CARDS_PER_PAGE = 5

# 세션 상태를 사용하여 데이터와 페이지 상태를 관리
if "result" not in st.session_state:
    st.session_state.result = None
if "page_number" not in st.session_state:
    st.session_state.page_number = 1

# 검색 버튼이 눌리면 데이터 검색 및 초기화
if clicked1:
    st.session_state.result = search_index(index_name, field_name, match_name)
    st.session_state.page_number = 1  # 새로운 검색 시 페이지 번호를 1로 초기화

# 결과가 존재할 경우에만 페이지 네비게이션 및 데이터 표시
if st.session_state.result is not None:
    # 전체 카드 데이터
    source_data = st.session_state.result.to_dict()["hits"]["hits"]
    
    # 페이지 수 계산
    total_cards = len(source_data)
    total_pages = (total_cards + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE

    # 페이지 번호가 유효한지 확인하고, 그렇지 않으면 1로 초기화
    if total_pages < 1:
        st.sidebar.write("검색 결과가 없습니다.")
        total_pages = 1
    
    # 페이지 선택 바
    st.session_state.page_number = st.sidebar.number_input('페이지 번호', min_value=1, max_value=total_pages, value=st.session_state.page_number)

    # 선택된 페이지에 해당하는 데이터 인덱스 범위
    start_index = (st.session_state.page_number - 1) * CARDS_PER_PAGE
    end_index = min(start_index + CARDS_PER_PAGE, total_cards)  # 범위를 전체 카드 수로 제한

    # 선택된 페이지에 해당하는 카드 데이터만 표시
    if start_index < total_cards:
        for info_frame in source_data[start_index:end_index]:
            img_id = info_frame["_source"]["id"]  # Document id 저장 (이미지 불러오기용)
            card_name = info_frame["_source"]["card_name"]  # 카드 이름
            card_link = info_frame["_source"]["card_link"]  # 카드고릴라 링크
            domestic_year_cost = info_frame["_source"]["domestic_year_cost"]  # 국내전용 연회비
            abroad_year_cost = info_frame["_source"]["abroad_year_cost"]  # 해외겸용 연회비
            previous_month_performance = info_frame["_source"]["previous_month_performance"]  # 전월실적
            category = info_frame["_source"]["category"]  # 혜택들

            # 카드 이미지 링크 설정
            card_img_num = '{0:03d}'.format(img_id)
            img_url = f'https://woori-fisa-bucket.s3.ap-northeast-2.amazonaws.com/index_img/bcc_{card_img_num}.png'

            # 카드 정보 출력
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:  # 카드 이미지
                st.image(img_url)
            with col3:  # 카드 이름, 연회비, 실적 정보
                st.subheader(card_name)
                st.write('')
                st.write('')
                st.write('')
                st.write(f'링크 {card_link}')
                st.write(f'국내전용 {domestic_year_cost}원 / 해외겸용 {abroad_year_cost}원')
                st.write(f'전월실적 {previous_month_performance}만원 이상')

            # 혜택 정보
            for cate in category:
                with st.expander(f"{cate['class']} - {cate['benefit']}"):
                    st.markdown(cate["condition"], unsafe_allow_html=True)

            st.divider()
    else:
        st.write("선택된 페이지에 표시할 데이터가 없습니다.")

    # 페이지 정보 표시
    st.sidebar.write(f"총 {total_cards}개의 결과 중 {st.session_state.page_number}/{total_pages} 페이지")
