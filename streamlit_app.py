import math
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="도형 탐험대 | 넓이와 대칭",
    page_icon="📐",
    layout="wide",
)

GRID_MIN = -6
GRID_MAX = 6
SHAPES = {
    "삼각형": [(-3, -2), (2, -2), (0, 3)],
    "사각형": [(-3, -2), (2, -2), (2, 2), (-3, 2)],
    "원": [(0, 0), (3, 0)],
}
drag_polygon_component = components.declare_component(
    "drag_polygon",
    path=str(Path(__file__).parent / "components" / "drag_polygon"),
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
    :root { --ink:#172b4d; --muted:#718096; --teal:#087f8c; --coral:#ff8066; }
    html, body, [class*="css"] { font-family: 'DM Sans','Noto Sans KR',sans-serif; }
    .stApp { background: #f5f8fc; color: var(--ink); }
    [data-testid="stSidebar"] { background: #102a43; }
    [data-testid="stSidebar"] * { color: #eef7fb; }
    .hero { padding: 1.7rem 2rem; border-radius: 22px; color: white;
      background: linear-gradient(115deg,#087f8c 0%,#16a6a1 55%,#5bc6b6 100%);
      margin: .25rem 0 1.5rem; box-shadow: 0 12px 30px #087f8c22; }
    .hero h1 { font-size: 2rem; margin: 0 0 .45rem; color:white; }
    .hero p { margin: 0; color:#e4fffa; font-size:1.04rem; }
    .eyebrow { font-size:.78rem; letter-spacing:.12em; font-weight:800; opacity:.85; }
    .card { background:white; border:1px solid #e6edf4; border-radius:18px;
      padding:1.1rem 1.25rem; box-shadow:0 5px 18px #152b4510; }
    .hint { color:#53657c; background:#e9f7f5; padding:.8rem 1rem;
      border-left:4px solid #13a39b; border-radius:8px; margin:.6rem 0 1rem; }
    .stButton > button { border-radius:10px; font-weight:700; }
    h2, h3 { color:#172b4d; }
    </style>
    """,
    unsafe_allow_html=True,
)


def polygon_area(points):
    return abs(
        sum(
            points[i][0] * points[(i + 1) % len(points)][1]
            - points[(i + 1) % len(points)][0] * points[i][1]
            for i in range(len(points))
        )
    ) / 2


def side_lengths(points):
    return [
        math.hypot(
            points[(i + 1) % len(points)][0] - point[0],
            points[(i + 1) % len(points)][1] - point[1],
        )
        for i, point in enumerate(points)
    ]


def interior_angles(points):
    angles = []
    orientation = sum(
        points[i][0] * points[(i + 1) % len(points)][1]
        - points[(i + 1) % len(points)][0] * points[i][1]
        for i in range(len(points))
    )
    for i, current in enumerate(points):
        previous = points[i - 1]
        following = points[(i + 1) % len(points)]
        first = (previous[0] - current[0], previous[1] - current[1])
        second = (following[0] - current[0], following[1] - current[1])
        denominator = math.hypot(*first) * math.hypot(*second)
        if denominator == 0:
            angles.append(0.0)
            continue
        cosine = sum(a * b for a, b in zip(first, second)) / denominator
        smaller_angle = math.degrees(math.acos(max(-1.0, min(1.0, cosine))))
        cross = first[0] * second[1] - first[1] * second[0]
        is_reflex = cross * orientation > 0
        angles.append(360 - smaller_angle if is_reflex else smaller_angle)
    return angles


def draw_grid(points=None, *, dashed=False, axis=None, label=None, height=440):
    points = points or []
    width = 560
    padding = 38
    span = width - 2 * padding
    step = span / (GRID_MAX - GRID_MIN)

    def to_svg(point):
        x, y = point
        return padding + (x - GRID_MIN) * step, padding + (GRID_MAX - y) * step

    lines = []
    for value in range(GRID_MIN, GRID_MAX + 1):
        x, y = to_svg((value, value))
        lines.append(
            f'<line x1="{x:.1f}" y1="{padding}" x2="{x:.1f}" y2="{width-padding}" class="grid"/>'
        )
        lines.append(
            f'<line x1="{padding}" y1="{y:.1f}" x2="{width-padding}" y2="{y:.1f}" class="grid"/>'
        )
    axis_lines = ""
    if axis == "vertical":
        x, _ = to_svg((0, 0))
        axis_lines = (
            f'<line x1="{x:.1f}" y1="{padding}" x2="{x:.1f}" '
            f'y2="{width-padding}" stroke="#ff8066" stroke-width="3"/>'
            f'<text x="{x + 8:.1f}" y="29" class="axis-label">대칭축</text>'
        )
    elif axis == "horizontal":
        _, y = to_svg((0, 0))
        axis_lines = (
            f'<line x1="{padding}" y1="{y:.1f}" x2="{width-padding}" '
            f'y2="{y:.1f}" stroke="#ff8066" stroke-width="3"/>'
            f'<text x="{width-100}" y="{y - 8:.1f}" class="axis-label">대칭축</text>'
        )
    polygon = ""
    dots = ""
    if points:
        mapped = [to_svg(point) for point in points]
        coordinates = " ".join(f"{x:.1f},{y:.1f}" for x, y in mapped)
        fill = "#bfece5" if not dashed else "#fff0eb"
        stroke = "#087f8c" if not dashed else "#f0785d"
        dash = 'stroke-dasharray="7 6"' if dashed else ""
        polygon = (
            f'<polygon points="{coordinates}" fill="{fill}" fill-opacity=".72" '
            f'stroke="{stroke}" stroke-width="3" stroke-linejoin="round" {dash}/>'
        )
        dots = "".join(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#087f8c"/>'
            f'<text x="{x + 8:.1f}" y="{y - 8:.1f}" class="point-label">'
            f'{chr(65 + index)}</text>'
            for index, (x, y) in enumerate(mapped)
        )
    caption = f'<text x="{padding}" y="{width-10}" class="caption">{label or ""}</text>'
    return f"""
    <svg viewBox="0 0 {width} {width}" role="img" aria-label="격자 위 도형"
      style="width:100%;height:auto;max-height:{height}px;background:#fff;border-radius:16px">
      <style>
        .grid {{ stroke:#dbe5ed;stroke-width:1.2 }}
        .point-label {{ font:700 13px sans-serif;fill:#087f8c }}
        .axis-label {{ font:700 13px sans-serif;fill:#e66c52 }}
        .caption {{ font:12px sans-serif;fill:#718096 }}
      </style>
      {''.join(lines)}{axis_lines}{polygon}{dots}{caption}
    </svg>
    """


def draggable_polygon(
    shape_name,
    initial_points,
    *,
    key_prefix=None,
    axis=None,
    reset_label="처음 모양으로 되돌리기",
):
    state_key = (
        f"{key_prefix}_points_{shape_name}"
        if key_prefix
        else f"practice_points_{shape_name}"
    )
    widget_key = (
        f"{key_prefix}_drag_polygon_{shape_name}"
        if key_prefix
        else f"drag_polygon_{shape_name}"
    )
    reset_key = (
        f"reset_{key_prefix}_{shape_name}"
        if key_prefix
        else f"reset_{shape_name}"
    )
    points = st.session_state.get(state_key, initial_points)
    if st.button(reset_label, key=reset_key):
        points = initial_points
        st.session_state[state_key] = points
        st.session_state.pop(widget_key, None)
    updated_points = drag_polygon_component(
        points=points,
        shape_name=shape_name,
        min_coord=GRID_MIN,
        max_coord=GRID_MAX,
        height=540,
        axis=axis,
        key=widget_key,
        default=points,
    )
    if updated_points is not None:
        normalized_points = [
            (int(point[0]), int(point[1])) for point in updated_points
        ]
        if (
            len(normalized_points) == len(initial_points)
            and all(
                GRID_MIN <= x <= GRID_MAX and GRID_MIN <= y <= GRID_MAX
                for x, y in normalized_points
            )
        ):
            points = normalized_points
            st.session_state[state_key] = points
    return points


def show_measurements(points, shape_name):
    if shape_name == "원":
        center, edge = points
        radius = math.hypot(edge[0] - center[0], edge[1] - center[1])
        if radius == 0:
            st.warning("원의 중심과 둘레 위의 점은 서로 다른 위치에 놓아 주세요.")
            return
        st.markdown("#### 📏 도형 측정 도구")
        metric_columns = st.columns(3)
        metric_columns[0].metric("반지름", f"{radius:.1f} cm")
        metric_columns[1].metric("넓이", f"{math.pi * radius ** 2:.1f} ㎠")
        metric_columns[2].metric("둘레", f"{2 * math.pi * radius:.1f} cm")
        st.caption(
            "반지름은 중심과 둘레 위 점을 잇는 선의 길이예요. "
            "넓이는 πr², 둘레는 2πr로 계산해요."
        )
        return
    if len(set(points)) != len(points):
        st.warning("꼭짓점 위치가 겹쳐 있어요. 서로 다른 격자점을 선택해 주세요.")
        return
    area = polygon_area(points)
    lengths = side_lengths(points)
    angles = interior_angles(points)
    st.markdown("#### 📏 도형 측정 도구")
    metric_columns = st.columns(3)
    metric_columns[0].metric("넓이", f"{area:g} ㎠")
    metric_columns[1].metric("변의 수", f"{len(points)}개")
    metric_columns[2].metric("둘레", f"{sum(lengths):.1f} cm")
    st.caption("격자 한 칸의 한 변을 1 cm로 계산해요.")
    detail_columns = st.columns(2)
    detail_columns[0].markdown(
        "**변의 길이**  \n"
        + " · ".join(f"{chr(65+i)}–{chr(65+(i+1)%len(points))}: {length:.1f} cm"
                     for i, length in enumerate(lengths))
    )
    detail_columns[1].markdown(
        "**각의 크기**  \n"
        + " · ".join(f"{chr(65+i)}: {angle:.0f}°" for i, angle in enumerate(angles))
    )


def render_practice():
    st.markdown(
        '<div class="hero"><div class="eyebrow">01 · SHAPE STUDIO</div>'
        '<h1>도형을 직접 만들어요</h1>'
        '<p>도형을 고르고 꼭짓점을 움직여 보세요. 변의 길이와 각, 넓이가 어떻게 달라질까요?</p></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.05, 1])
    with left:
        shape_name = st.selectbox("연습할 도형을 골라요", list(SHAPES))
        if shape_name == "원":
            hint = (
                "💡 원둘레 위의 점을 움직이면 중심과 점 사이 선의 길이가 "
                "반지름이 되어 원의 크기가 바뀌어요. 중심점을 움직여 원을 옮길 수도 있어요."
            )
        else:
            hint = "💡 모눈종이의 꼭짓점을 잡고 원하는 칸으로 끌어 보세요."
        st.markdown(
            f'<div class="hint">{hint} 마우스와 터치 모두 사용할 수 있어요.</div>',
            unsafe_allow_html=True,
        )
    with right:
        points = draggable_polygon(shape_name, SHAPES[shape_name])
    st.divider()
    show_measurements(points, shape_name)


def render_symmetry_quiz():
    st.subheader("🪞 대칭 도형 완성하기")
    st.write("주어진 도형을 대칭축의 반대편에 똑같이 그려 보세요.")
    original = [(-5, -2), (-2, -2), (-2, 2), (-4, 2)]
    reflected = [(-x, y) for x, y in original]
    left, right = st.columns([1, 1.1])
    with left:
        components.html(
            draw_grid(original, axis="vertical", label="주어진 도형"),
            height=480,
            scrolling=False,
        )
        st.caption("왼쪽 도형의 각 꼭짓점과 대칭축까지의 거리를 살펴보세요.")
    with right:
        st.markdown("**오른쪽 격자에서 꼭짓점을 움직여 대칭 도형을 완성해 보세요.**")
        answer = draggable_polygon(
            "내 답안",
            [(1, -2), (4, -2), (4, 2), (2, 2)],
            key_prefix="quiz_symmetry",
            axis="vertical",
            reset_label="답안 초기화",
        )
    if st.button("대칭 확인하기", type="primary", key="check_symmetry"):
        if sorted(answer) == sorted(reflected):
            st.success("정답이에요! 대칭축에서 같은 거리만큼 떨어져 있어요. 🎉")
            st.balloons()
        else:
            st.info("아직 조금 달라요. 각 꼭짓점의 높이와 대칭축까지의 거리를 다시 확인해 보세요.")


def render_copy_quiz():
    st.subheader("✏️ 똑같이 그려보기")
    st.write("왼쪽 도형을 모눈 칸 수와 꼭짓점 위치까지 똑같이 따라 그려 보세요.")
    target = [(-4, -2), (1, -2), (3, 1), (-2, 3)]
    left, right = st.columns(2)
    with left:
        components.html(
            draw_grid(target, label="따라 그릴 도형"),
            height=480,
            scrolling=False,
        )
    with right:
        st.markdown("**격자 위 꼭짓점을 움직여 똑같이 그려 보세요.**")
        answer = draggable_polygon(
            "내 답안",
            [(-3, -2), (2, -2), (2, 2), (-3, 2)],
            key_prefix="quiz_copy",
            reset_label="답안 초기화",
        )
    if st.button("그림 확인하기", type="primary", key="check_copy"):
        if answer == target:
            st.success("정확하게 그렸어요! 꼭짓점의 순서와 위치가 모두 같아요. 🌟")
            st.balloons()
        else:
            st.info("아직 달라요. 각 꼭짓점의 위치와 순서를 다시 비교해 보세요.")


def render_area_quiz():
    st.subheader("🧠 넓이 맞히기")
    st.write("격자의 한 칸은 1㎠예요. 도형의 넓이를 구해 보세요.")
    target = [(-4, -2), (2, -2), (2, 2), (-1, 2)]
    left, right = st.columns([1, 1])
    with left:
        components.html(
            draw_grid(target, label="넓이를 구해 보세요"),
            height=480,
            scrolling=False,
        )
    with right:
        st.markdown(
            '<div class="card"><h3>넓이는 몇 ㎠일까요?</h3>'
            '<p>필요하다면 도형을 직사각형과 삼각형으로 나누어 생각해 보세요.</p></div>',
            unsafe_allow_html=True,
        )
        answer = st.number_input("넓이 (㎠)", min_value=0, max_value=144, step=1,
                                 key="area_answer")
        if st.button("정답 확인하기", type="primary", key="check_area"):
            if answer == polygon_area(target):
                st.success("정답이에요! 도형을 나누어 넓이를 잘 구했어요. 🎉")
                st.balloons()
            else:
                st.info("다시 세어 볼까요? 가로·세로로 잘라 넓이를 더해 보세요.")
    st.caption("힌트: 이 도형을 큰 직사각형에서 작은 삼각형을 빼는 방법으로 생각해 보세요.")


def render_quiz():
    st.markdown(
        '<div class="hero"><div class="eyebrow">02 · QUICK QUIZ</div>'
        '<h1>배운 내용을 퀴즈로 확인해요</h1>'
        '<p>대칭을 완성하거나, 도형을 따라 그리고, 넓이를 구해 보세요.</p></div>',
        unsafe_allow_html=True,
    )
    quiz = st.radio(
        "퀴즈 선택",
        ["대칭 도형 완성", "똑같이 그려보기", "넓이 맞히기"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.divider()
    if quiz == "대칭 도형 완성":
        render_symmetry_quiz()
    elif quiz == "똑같이 그려보기":
        render_copy_quiz()
    else:
        render_area_quiz()


with st.sidebar:
    st.markdown("## 📐 도형 탐험대")
    st.caption("넓이와 대칭을 재미있게!")
    page = st.radio("학습 메뉴", ["도형 연습", "퀴즈 풀기"], label_visibility="collapsed")
    st.divider()
    st.markdown("### 오늘의 미션")
    st.markdown("1. 꼭짓점을 움직여 보기\n2. 도형의 넓이 확인하기\n3. 퀴즈에 도전하기")
    st.caption("격자 한 칸 = 1 cm × 1 cm")

if page == "도형 연습":
    render_practice()
else:
    render_quiz()
