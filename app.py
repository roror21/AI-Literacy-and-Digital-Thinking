# app.py
# ==========================================
# 부산 유튜브 해외 트렌드 분석기
# 추가 기능:
# 1. 기간 선택
# 2. 키워드 분석
# 3. 실제 댓글 예시 출력
# ==========================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

from googleapiclient.discovery import build
from transformers import pipeline
from langdetect import detect
from collections import Counter
from datetime import datetime
import re
import random

# ==========================================
# 한글 폰트 설정
# ==========================================

if platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
else:
    plt.rcParams["font.family"] = "NanumGothic"

plt.rcParams["axes.unicode_minus"] = False
# ==========================================
# Streamlit 설정
# ==========================================

st.set_page_config(
    page_title="부산 해외 유튜브 트렌드 분석기",
    layout="wide"
)

st.title("🌏 부산 해외 유튜브 트렌드 분석기")

st.write("""
외국인들이 부산에 대해 어떤 영상을 올리고,
댓글에서는 어떤 반응을 보이는지 분석합니다.
""")

# ==========================================
# API KEY 입력
# ==========================================

api_key = st.text_input(
    "YouTube API Key 입력",
    type="password"
)

# ==========================================
# 검색 설정
# ==========================================

search_keyword = st.text_input(
    "검색 키워드",
    value="Busan travel"
)

max_videos = st.slider(
    "분석할 영상 개수",
    10,
    100,
    30
)

# ==========================================
# 기간 선택
# ==========================================

st.subheader("📅 기간 설정")

start_date = st.date_input(
    "시작 날짜",
    value=datetime(2024, 1, 1)
)

end_date = st.date_input(
    "종료 날짜",
    value=datetime.today()
)


# ==========================================
# YouTube API 연결
# ==========================================

def get_youtube_service(api_key):
    return build(
        "youtube",
        "v3",
        developerKey=api_key
    )


# ==========================================
# 영상 검색
# ==========================================

def search_videos(
        youtube,
        keyword,
        start_date,
        end_date,
        max_results
):

    keywords = [
        "Busan travel",
        "Busan trip",
        "Busan tourism",
        "Busan vacation",
        "Visit Busan",
        "Busan vlog",
        "釜山旅行",
        "釜山 観光",
        "釜山旅游"
    ]

    videos = []
    seen_ids = set()

    for kw in keywords:

        try:

            next_page_token = None

            for _ in range(3):

                request = youtube.search().list(
                    q=kw,
                    part="snippet",
                    type="video",
                    maxResults=50,
                    order="date",
                    pageToken=next_page_token,
                    publishedAfter=start_date.isoformat() + "T00:00:00Z",
                    publishedBefore=end_date.isoformat() + "T23:59:59Z"
                )

                response = request.execute()

                for item in response["items"]:

                    video_id = item["id"]["videoId"]

                    if video_id in seen_ids:
                        continue

                    snippet = item["snippet"]

                    title = snippet["title"]

                    # 한국어 제목 제거
                    if re.search(r"[가-힣]", title):
                        continue

                    title_lower = title.lower()

                    exclude_keywords = [
                        "food",
                        "restaurant",
                        "chicken",
                        "mukbang",
                        "recipe",
                        "asmr",
                        "music",
                        "cover",
                        "dance",
                        "kpop",
                        "shorts"
                    ]

                    if any(word in title_lower for word in exclude_keywords):
                        continue

                    if not any(
                            word.lower() in title_lower
                            for word in travel_keywords
                    ):
                        continue

                    seen_ids.add(video_id)

                    videos.append({
                        "video_id": video_id,
                        "title": title,
                        "channel": snippet["channelTitle"],
                        "published": snippet["publishedAt"]
                    })

                next_page_token = response.get(
                    "nextPageToken"
                )

                if not next_page_token:
                    break

        except Exception as e:
            print("오류:", e)

    return pd.DataFrame(
    videos[:max_results],
    columns=[
        "video_id",
        "title",
        "channel",
        "published"
    ]
)

# ==========================================
# 댓글 수집
# ==========================================

def get_comments(youtube, video_id, max_comments=100):
    comments = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_comments,
            textFormat="plainText"
        )

        response = request.execute()

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

            comments.append(comment)

    except:
        pass

    return comments


# ==========================================
# 외국어 댓글 판별
# ==========================================

def is_foreign_comment(text):
    try:
        return detect(text) != "ko"

    except:
        return False


def detect_video_language(title):
    title_lower = title.lower()

    if re.search(r"[가-힣]", title):
        return "ko"

    if re.search(r"[ぁ-んァ-ン]", title):
        return "ja"

    if re.search(r"[\u4e00-\u9fff]", title):
        return "zh"

    try:

        lang = detect(title)

        if lang in language_map:
            return lang

        return "unknown"

    except:
        return "unknown"


language_map = {
    "en": "영어",
    "ko": "한국어",
    "ja": "일본어",

    "zh": "중국어",
    "zh-cn": "중국어",
    "zh-tw": "중국어",

    "fr": "프랑스어",
    "de": "독일어",
    "es": "스페인어",
    "ru": "러시아어",
    "th": "태국어",
    "vi": "베트남어",
    "id": "인도네시아어",
    "ar": "아랍어",

    "unknown": "기타"
}

travel_keywords = [

    "travel",
    "trip",
    "tour",
    "tourism",
    "vacation",
    "visit",
    "itinerary",
    "guide",
    "things to do",
    "vlog",

    "旅行",
    "旅游",
    "觀光",
    "観光",

    "busan travel",
    "busan trip",
    "visit busan"
]


# ==========================================
# 감성 분석 모델
# ==========================================

@st.cache_resource
def load_model():
    return pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-roberta-base-sentiment-latest"
    )


# ==========================================
# 감성 분석
# ==========================================

def analyze_sentiment(model, comment_items):
    if len(comment_items) == 0:
        return pd.DataFrame()

    texts = [item["comment"][:512] for item in comment_items]

    results = []
    chunk_size = 16
    total = len(texts)

    # 진행 표시
    progress = st.progress(0)
    status = st.empty()

    for start in range(0, total, chunk_size):

        end = start + chunk_size
        batch_texts = texts[start:end]
        batch_items = comment_items[start:end]

        try:
            outputs = model(batch_texts, truncation=True)
        except Exception:
            continue

        for item, output in zip(batch_items, outputs):
            results.append({
                "comment": item["comment"],
                "language": item["language"],
                "label": output["label"],
                "score": output["score"]
            })

        done = min(end, total)
        progress.progress(done / total)
        status.write(f"감성 분석 중... {done} / {total}개")

    progress.empty()
    status.empty()

    return pd.DataFrame(results)


# ==========================================
# 키워드 분석
# ==========================================

def keyword_analysis(comments):
    text = " ".join(comments).lower()

    words = re.findall(r'\b[a-z]{4,}\b', text)

    stopwords = {
        "this", "that", "with", "have", "from",
        "your", "they", "will", "about", "there",
        "their", "would", "could", "should",
        "video", "korea", "korean"
    }

    filtered = [
        w for w in words
        if w not in stopwords
    ]

    counter = Counter(filtered)

    return counter.most_common(15)


# ==========================================
# 분석 시작 버튼
# ==========================================

if st.button("분석 시작"):

    if not api_key:
        st.error("YouTube API Key를 입력하세요.")
        st.stop()

    youtube = get_youtube_service(api_key)

    # ==========================================
    # 영상 검색
    # ==========================================

    with st.spinner("영상 검색 중..."):

        video_df = search_videos(
            youtube,
            search_keyword,
            start_date,
            end_date,
            max_videos
        )

    st.success(f"{len(video_df)}개 영상 수집 완료")
    video_df["language_code"] = (
        video_df["title"]
        .apply(detect_video_language)
    )

    video_df = video_df[
        video_df["language_code"] != "ko"
        ]

    video_df["language"] = (
        video_df["language_code"]
        .map(language_map)
        .fillna("기타")
    )
    # ==========================================
    # 영상 목록 출력
    # ==========================================

    st.subheader("🎬 수집된 영상")

    st.dataframe(
        video_df[
            ["title", "channel", "published"]
        ]
    )

    # ==========================================
    # 영상 언어 분포
    # ==========================================
    st.subheader("🌍 영상 언어 분포")

    lang_count = (
        video_df["language"]
        .value_counts()
        .reset_index()
    )

    lang_count.columns = ["language", "count"]

    st.dataframe(lang_count)

    fig_lang, ax_lang = plt.subplots(
        figsize=(8, 8)
    )

    ax_lang.pie(
        lang_count["count"],
        labels=lang_count["language"],
        autopct="%1.1f%%",
        textprops={"fontsize":8},
        labeldistance=1.15
    )

    ax_lang.set_title("영상 언어 분포")

    st.pyplot(fig_lang)

    # ==========================================
    # 댓글 수집
    # ==========================================

    st.subheader("💬 댓글 수집")
    
    all_comments = []
    
    progress = st.progress(0)
    total = len(video_df)
    
    for i, (idx, row) in enumerate(video_df.iterrows()):
    
        comments = get_comments(
            youtube,
            row["video_id"]
        )
    
        foreign_comments = [
            c for c in comments
            if is_foreign_comment(c)
        ]
    
        for c in foreign_comments:
            all_comments.append({
                "comment": c,
                "language": row["language"]
            })
    
        progress.progress(
            (i + 1) / total
        )
    
    st.write(f"외국어 댓글 {len(all_comments)}개 수집 완료")

    # 분석할 댓글 선별 (언어 골고루 뽑히도록 무작위로 섞은 뒤 자름)
    if len(all_comments) > 500:
        st.info(f"수집된 댓글 {len(all_comments)}개 중 500개를 무작위로 골라 분석합니다.")
        random.shuffle(all_comments)
        all_comments = all_comments[:500]

    # ==========================================
    # 감성 분석
    # ==========================================

    if len(all_comments) > 0:

    st.subheader("😊 댓글 감성 분석")

    model = load_model()

    sentiment_df = analyze_sentiment(
        model,
        all_comments
    )

    st.dataframe(sentiment_df)

    # 감성 비율
    label_counts = sentiment_df["label"].value_counts()

    fig2, ax2 = plt.subplots()

    ax2.pie(
        label_counts,
        labels=label_counts.index,
        autopct="%1.1f%%"
    )

    ax2.set_title("댓글 감성 비율")

    st.pyplot(fig2)

    # ==========================================
    # 언어별 감성 분석
    # ==========================================

    st.subheader("🌐 언어별 감성 분석")

    lang_counts = sentiment_df["language"].value_counts()
    valid_langs = lang_counts[lang_counts >= 5].index

    cross_df = sentiment_df[
        sentiment_df["language"].isin(valid_langs)
    ]

    if len(cross_df) > 0:

        cross = pd.crosstab(
            cross_df["language"],
            cross_df["label"]
        )

        st.dataframe(cross)

        cross_pct = cross.div(
            cross.sum(axis=1),
            axis=0
        ) * 100

        fig_cross, ax_cross = plt.subplots(
            figsize=(10, 5)
        )

        cross_pct.plot(
            kind="bar",
            stacked=True,
            ax=ax_cross
        )

        ax_cross.set_xlabel("")
        ax_cross.set_ylabel("비율 (%)")
        ax_cross.set_title("언어별 댓글 감성 비율")
        ax_cross.legend(title="감성")

        plt.xticks(rotation=0)

        st.pyplot(fig_cross)

    else:

        st.info("언어별로 비교할 만큼 댓글이 충분하지 않습니다.")

    # ==========================================
    # 키워드 분석
    # ==========================================

    st.subheader("🔍 자주 등장한 키워드")

    keywords = keyword_analysis(
        [item["comment"] for item in all_comments]
    )

    keyword_df = pd.DataFrame(
        keywords,
        columns=["keyword", "count"]
    )

    st.dataframe(keyword_df)

    # ==========================================
    # 실제 댓글 예시
    # ==========================================

    st.subheader("📝 실제 외국인 댓글 예시")

    positive_comments = sentiment_df[
        sentiment_df["label"] == "positive"
    ]["comment"].head(5)

    neutral_comments = sentiment_df[
        sentiment_df["label"] == "neutral"
    ]["comment"].head(5)

    negative_comments = sentiment_df[
        sentiment_df["label"] == "negative"
    ]["comment"].head(5)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 😊 긍정 댓글")
        for c in positive_comments:
            st.success(c)

    with col2:
        st.markdown("### 😐 중립 댓글")
        for c in neutral_comments:
            st.info(c)

    with col3:
        st.markdown("### 😡 부정 댓글")
        for c in negative_comments:
            st.error(c)

else:

    st.warning("외국어 댓글이 없습니다.")


