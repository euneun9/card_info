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

date_range = st.sidebar.date_input("도큐먼트 생성일",
                 [datetime.date(2019, 1, 1), datetime.date(2024, 1, 3)])
clicked2 = st.sidebar.button("생성일 확인")


if(clicked1 == True):
    result = search_index(index_name, field_name, match_name)
    # st.write(result.to_dict())
    # st.write(result.to_dict()["hits"]["hits"])

    # source_data = [entry["_source"] for entry in result.to_dict()["hits"]["hits"]]
    # df = pd.DataFrame(source_data)
    # st.dataframe(df)


###########################################################
    # 수정사항
    for info_frame in result.to_dict()["hits"]["hits"]:
        img_id = info_frame["_source"]["id"] # Document id 저장 (이미지 불러오기용)
        card_name = info_frame["_source"]["card_name"] # 카드 이름
        card_link = info_frame["_source"]["card_link"] # 카드고릴라 링크
        domestic_year_cost = info_frame["_source"]["domestic_year_cost"] # 국내전용 연회비
        abroad_year_cost = info_frame["_source"]["abroad_year_cost"] # 해외겸용 연회비
        previous_month_performance = info_frame["_source"]["previous_month_performance"] # 전월실적
        category = info_frame["_source"]["category"] # 혜택들

        ### 카드 이미지, 이름, 연회비, 실적 정보
        # 카드 이미지 링크 설정
        card_img_num = '{0:03d}'.format(img_id)
        img_url = f'https://woori-fisa-bucket.s3.ap-northeast-2.amazonaws.com/index_img/bcc_{card_img_num}.png'

        # 카드 정보 출력
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1: # 카드 이미지
            st.image(img_url)
        with col3: # 카드 이름, 연회비, 실적 정보
            st.subheader(card_name)
            st.write('')
            st.write('')
            st.write('')
            st.write(f'링크 {card_link}')
            st.write(f'국내전용 {domestic_year_cost}원 / 해외겸용 {abroad_year_cost}원')
            st.write(f'전월실적 {previous_month_performance}만원 이상')

        ### 혜택 정보
        for cate in category:
            with st.expander(f"{cate["class"]} - {cate["benefit"]}"):
                st.markdown(cate["condition"], unsafe_allow_html=True)

        st.divider()
###########################################################


if(clicked2 == True):
    start_p = date_range[0]
    end_p = date_range[1] + datetime.timedelta(days=1)
    result = search_index_with_date_range(index_name, field_name, match_name, start_date=start_p, end_date=end_p)
    st.write(result.to_dict()["hits"]["hits"])
    source_data = [entry["_source"] for entry in result.to_dict()["hits"]["hits"]]
    df = pd.DataFrame(source_data)
    st.dataframe(df)

    csv_data = df.to_csv()
    excel_data = BytesIO()
    df.to_excel(excel_data)
    columns = st.columns(2)
    with columns[0]:
        st.download_button("CSV 파일 다운로드", csv_data, file_name='card_data.csv')
    with columns[1]:
        st.download_button("엑셀 파일 다운로드",
        excel_data, file_name='card_data.xlsx')