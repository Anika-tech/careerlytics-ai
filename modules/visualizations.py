import plotly.graph_objects as go
import plotly.express as px


def chart_layout(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2b3448"),
        margin=dict(l=20, r=20, t=45, b=20),
    )
    fig.update_xaxes(gridcolor="rgba(42,54,82,.11)", zerolinecolor="rgba(42,54,82,.14)")
    fig.update_yaxes(gridcolor="rgba(42,54,82,.11)", zerolinecolor="rgba(42,54,82,.14)")
    return fig


def skill_bar_chart(skills):
    names = [str(s) for s in skills]
    fig = go.Figure(go.Bar(
        x=[len(names) - i for i in range(len(names))],
        y=names,
        orientation="h",
        marker=dict(color=["#8b5cf6", "#38bdf8"][0:1] * len(names),
                    line=dict(width=0)),
    ))
    fig.update_layout(title="Detected Technical Skills", showlegend=False)
    return chart_layout(fig)


def recommendation_chart(recommendations):
    if recommendations is None or recommendations.empty:
        return chart_layout(go.Figure())
    fig = px.bar(
        recommendations.sort_values("compatibility", ascending=True),
        x="compatibility", y="job_title", orientation="h",
        color="compatibility", color_continuous_scale=["#1d4ed8", "#8b5cf6", "#38bdf8"],
        labels={"compatibility": "Compatibility (%)", "job_title": "Role"},
    )
    fig.update_layout(title="Top Job Ranking", coloraxis_showscale=False)
    return chart_layout(fig)


def skill_gap_chart(gap):
    fig = go.Figure()
    fig.add_bar(name="Matching", x=["Skills"], y=[len(gap["matching"])], marker_color="#168fa4")
    fig.add_bar(name="Missing", x=["Skills"], y=[len(gap["missing"])], marker_color="#7557e8")
    fig.update_layout(barmode="group", title="Skill Gap Comparison")
    return chart_layout(fig)


def category_chart(series):
    if series is None or series.empty:
        return chart_layout(go.Figure())
    fig = px.bar(x=series.index.astype(str), y=series.values,
                 color=series.values, color_continuous_scale=["#312e81", "#8b5cf6", "#38bdf8"],
                 labels={"x": "Category", "y": "Jobs"})
    fig.update_layout(title="Job Category Distribution", coloraxis_showscale=False)
    return chart_layout(fig, height=420)


def score_gauge(score, label="Resume content quality"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"size": 28, "color": "#263247"}},
        title={"text": label, "font": {"size": 14, "color": "#68738a"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#68738a"},
            "bar": {"color": "#8b70f8", "thickness": 0.28},
            "bgcolor": "#edf0f7",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "#f0e9f4"},
                {"range": [50, 75], "color": "#eeeafc"},
                {"range": [75, 100], "color": "#e4f2ee"},
            ],
        },
    ))
    return chart_layout(fig, height=245)


def skill_mix_chart(technical_skills, soft_skills):
    labels = ["Technical", "Soft"]
    values = [len(technical_skills), len(soft_skills)]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.68,
        sort=False,
        marker={"colors": ["#7557e8", "#168fa4"], "line": {"color": "#ffffff", "width": 3}},
        textinfo="label+value",
        textfont={"color": "#263247"},
    ))
    fig.update_layout(title="Detected skill mix", showlegend=False)
    return chart_layout(fig, height=320)


def skill_radar_chart(candidate_skills, required_skills, title="Skills against target role"):
    all_skills = sorted(
        {str(skill) for skill in candidate_skills} | {str(skill) for skill in required_skills},
        key=str.lower,
    )[:10]
    fig = go.Figure()
    if not all_skills:
        return chart_layout(fig, height=380)

    candidate_set = {str(skill).casefold() for skill in candidate_skills}
    required_set = {str(skill).casefold() for skill in required_skills}
    closed_skills = all_skills + [all_skills[0]]
    candidate_values = [100 if skill.casefold() in candidate_set else 0 for skill in all_skills]
    required_values = [100 if skill.casefold() in required_set else 0 for skill in all_skills]
    fig.add_trace(go.Scatterpolar(
        r=candidate_values + [candidate_values[0]],
        theta=closed_skills,
        fill="toself",
        name="Detected in resume",
        line={"color": "#168fa4"},
        fillcolor="rgba(22,143,164,.17)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=required_values + [required_values[0]],
        theta=closed_skills,
        fill="toself",
        name="Target skills",
        line={"color": "#7557e8"},
        fillcolor="rgba(117,87,232,.14)",
    ))
    fig.update_layout(
        title=title,
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {"visible": True, "range": [0, 100], "gridcolor": "rgba(42,54,82,.13)", "color": "#68738a"},
            "angularaxis": {"gridcolor": "rgba(42,54,82,.12)", "color": "#4c5870"},
        },
        legend={"orientation": "h", "y": -0.15},
    )
    return chart_layout(fig, height=390)


def recommendation_skill_heatmap(recommendations, candidate_skills):
    fig = go.Figure()
    if recommendations is None or recommendations.empty:
        return chart_layout(fig, height=330)

    subset = recommendations.head(5)
    skill_names = set()
    for _, row in subset.iterrows():
        skill_names.update(row["matching_skills"])
        skill_names.update(row["missing_skills"])
    skills = sorted(skill_names, key=str.lower)[:9]
    if not skills:
        return chart_layout(fig, height=330)

    candidate_set = {str(skill).casefold() for skill in candidate_skills}
    z_values = []
    for _, row in subset.iterrows():
        role_skills = {str(skill).casefold() for skill in row["matching_skills"] + row["missing_skills"]}
        z_values.append([
            (1 if skill.casefold() in candidate_set else 0)
            if skill.casefold() in role_skills else None
            for skill in skills
        ])

    fig.add_trace(go.Heatmap(
        z=z_values,
        x=skills,
        y=subset["job_title"].tolist(),
        zmin=0,
        zmax=1,
        colorscale=[[0, "#ef9ba8"], [0.5, "#eef1f7"], [1, "#39b98b"]],
        showscale=False,
        xgap=3,
        ygap=3,
        hovertemplate="%{y}<br>%{x}: %{z}<extra></extra>",
    ))
    fig.update_layout(title="Top-role skill alignment")
    return chart_layout(fig, height=330)
