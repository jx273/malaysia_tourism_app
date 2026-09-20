import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="LestariLens Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Safe Global CSS for Premium UI ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #F7F5F0 !important; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #EBE8DE !important; border-right: 1px solid #DEDAD0; }
    [data-testid="stHeader"] { background-color: transparent !important; }
    
    .block-container { padding-top: 2.5rem !important; max-width: 1400px !important; }
    h1, h2, h3 { color: #2D3142 !important; font-weight: 600 !important; margin-top:0; padding-top:0;}
    .sub-header { color: #E27D60; font-size: 0.85rem; text-transform: uppercase; font-weight: 700; margin-bottom: -15px; letter-spacing: 1px;}

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
        border: 1px solid #EAE6DB !important;
    }

    /* Fixed Metric wrapping for long state names */
    [data-testid="stMetricValue"] { color: #2D3142 !important; font-weight: 700 !important; white-space: normal !important; line-height: 1.1 !important; font-size: 1.6rem !important;}
    [data-testid="stMetricValue"] > div { white-space: normal !important; }
    [data-testid="stMetricLabel"] { color: #888C95 !important; font-weight: 600 !important; white-space: normal !important; }

    .stButton>button { border-radius: 8px !important; font-weight: bold !important; transition: 0.2s; border: none !important; }
    button[kind="primary"] { background-color: #E27D60 !important; color: white !important; }
    button[kind="secondary"] { background-color: #85A88F !important; color: white !important; border-radius: 20px !important; }
    button[kind="primary"]:hover { background-color: #D36C4F !important; }
    button[kind="secondary"]:hover { background-color: #72967C !important; }
    
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 15px; border-radius: 8px; margin-bottom: 5px; background-color: transparent; transition: 0.2s all; cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #FFFFFF; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
        color: #E27D60 !important; font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Data Loading (Dynamic Relative Paths) ---
@st.cache_data
def load_data():
    try:
        # Dynamically resolve project root regardless of where the script is run from
        project_root = Path(__file__).resolve().parents[1]
        
        features_path = project_root / "ml" / "handoff" / "for_hongyik" / "state_features.csv"
        ml_path = project_root / "ml" / "handoff" / "for_hongyik" / "sample_predictions.csv"
        
        df = pd.read_csv(features_path)
        df['visitors_M'] = df['visitors_000'] / 1000
        
        df_ml = pd.read_csv(ml_path)
        return df, df_ml
    except Exception as e:
        st.error(f"Critical Error: Could not load data files. Ensure 'state_features.csv' and 'sample_predictions.csv' exist in 'ml/handoff/for_hongyik/'.\n\nError details: {e}")
        st.stop()

df, df_ml = load_data()


# --- 4. Sidebar Navigation & Global Filters ---
with st.sidebar:
    st.markdown("<h2 style='color:#E27D60; margin-bottom:0; font-size: 1.8rem;'>🎯 LestariLens</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.75rem; color: #737373; font-weight:bold; letter-spacing: 1px; margin-top: -5px; margin-bottom: 25px;'>MALAYSIA TOURISM<br>INTELLIGENCE</p>", unsafe_allow_html=True)
    
    selected_page = st.radio("Navigation", ["Overview", "Visitor flows", "Sustainability", "Scenario lab", "Evidence"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #2D3142; font-weight:bold; margin-bottom: -5px;'>📅 Global Year Filter</p>", unsafe_allow_html=True)
    
    available_years = sorted(df['year'].unique().tolist(), reverse=True)
    selected_year = st.selectbox("Year", available_years, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #DDE2DA; padding: 15px; border-radius: 8px; font-size: 0.8rem; color: #555;">
        <b>DOSM official data first</b><br><br>Every insight shows its source, year and analytical limitation.
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# PAGE 1: OVERVIEW DASHBOARD
# ==========================================
def render_overview():
    col_head1, col_head2 = st.columns([2.5, 1.5])
    states_list = ["Malaysia"] + sorted(df['state'].unique().tolist())

    with col_head1:
        st.markdown(f'<p class="sub-header">NATIONAL PULSE · {selected_year} OVERVIEW</p>', unsafe_allow_html=True)
        st.markdown('<h1>Grow tourism value.<br>Protect what makes Malaysia special.</h1>', unsafe_allow_html=True)

    with col_head2:
        st.markdown("<br>", unsafe_allow_html=True)
        selected_region = st.selectbox("Region", states_list, label_visibility="collapsed")
            
        if st.button("✨ Generate brief", type="primary", use_container_width=True):
            st.toast(f"✅ Generating official brief for {selected_region} ({selected_year})...")

    # Time calculations
    all_years_sorted = sorted(df['year'].unique().tolist())
    curr_idx = all_years_sorted.index(selected_year)
    prev_year = all_years_sorted[curr_idx - 1] if curr_idx > 0 else None

    # Sync ML Data with Selected Year
    ml_selected_year = df_ml[df_ml['year'] == selected_year].copy()

    # Filtering Logic
    if selected_region == "Malaysia":
        df_current = df[df['year'] == selected_year]
        df_prev = df[df['year'] == prev_year] if prev_year else pd.DataFrame()
        
        # Sort ONLY the selected year's ML data
        chart_data = ml_selected_year.sort_values(by='opportunity_gap_pct', ascending=False).head(5).copy()
        chart_title = f"Top Untapped Potential (ML Opportunity Gap %, {selected_year})"
        y_axis = 'state'
        x_axis = 'opportunity_gap_pct'
        
        # Safe extraction
        if not chart_data.empty:
            top_ml_state = chart_data.iloc[0]['state']
            top_ml_gap = chart_data.iloc[0]['opportunity_gap_pct']
            top2_ml_state = chart_data.iloc[1]['state'] if len(chart_data) > 1 else ""
        else:
            top_ml_state, top_ml_gap, top2_ml_state = "N/A", 0, ""
            
    else:
        df_current = df[(df['year'] == selected_year) & (df['state'] == selected_region)]
        df_prev = df[(df['year'] == prev_year) & (df['state'] == selected_region)] if prev_year else pd.DataFrame()
        
        chart_data = df[(df['state'] == selected_region) & (df['year'] <= selected_year)].sort_values(by='year', ascending=True).tail(5).copy()
        chart_data['year'] = chart_data['year'].astype(str)
        chart_title = f"Historical Visitor Trend ({selected_region})"
        y_axis = 'year'
        x_axis = 'visitors_M'
        
        top_ml_state = selected_region
        ml_filter = ml_selected_year[ml_selected_year['state'] == selected_region]
        top_ml_gap = ml_filter['opportunity_gap_pct'].values[0] if not ml_filter.empty else 0

    v_current = df_current['visitors_M'].sum() if not df_current.empty else 0
    v_prev = df_prev['visitors_M'].sum() if not df_prev.empty else 0
    v_growth = ((v_current - v_prev) / v_prev) * 100 if v_prev > 0 else 0

    if prev_year:
        delta_label = f"↑ {v_growth:.1f}% vs {prev_year}" if v_growth >= 0 else f"↓ {abs(v_growth):.1f}% vs {prev_year}"
    else:
        delta_label = "N/A (Baseline year)"

    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    with k1.container(border=True): st.metric(f"Domestic visitors ({selected_year})", f"{v_current:.1f}M", delta_label)
    with k2.container(border=True): st.metric("Tourism expenditure (2025 Est.)", "RM121.3B", "↑ 13.6% vs baseline")
    with k3.container(border=True): st.metric("Domestic trips (2025 Est.)", "332.2M", "1.15 trips per visitor", delta_color="off")
    with k4.container(border=True): 
        if top_ml_gap > 0:
            st.metric(f"ML Opportunity ({top_ml_state})", f"+{top_ml_gap:.1f}%", f"Untapped ({selected_year})", delta_color="normal")
        else:
            st.metric(f"ML Opportunity ({top_ml_state})", f"{top_ml_gap:.1f}%", f"Over-indexed ({selected_year})", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)
    mid_col1, mid_col2 = st.columns([2.3, 1])

    with mid_col1:
        with st.container(border=True):
            st.subheader("Market Analysis")
            st.caption(chart_title)
            
            if selected_region == "Malaysia":
                colors = ['#E5E2D9', '#E8B87B', '#85A88F', '#E27D60', '#D36C4F']
                chart_data['Color'] = colors[-len(chart_data):] if not chart_data.empty else []
                fig_bar = px.bar(chart_data.iloc[::-1], x=x_axis, y=y_axis, orientation='h', text=x_axis)
                fig_bar.update_traces(marker_color=chart_data.iloc[::-1]['Color'] if not chart_data.empty else [], marker_line_width=0, texttemplate='+%{text:.1f}%', textposition='outside', textfont=dict(color='#2D3142', size=11))
            else:
                fig_bar = px.bar(chart_data, x=y_axis, y=x_axis, orientation='v', text=x_axis)
                fig_bar.update_traces(marker_color='#E8B87B', marker_line_width=0, texttemplate='%{text:.1f}M', textposition='outside', textfont=dict(color='#2D3142', size=11))
                fig_bar.update_xaxes(type='category')

            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=40, t=10, b=0), height=280, xaxis=dict(showgrid=False, showticklabels=False, title=""), yaxis=dict(showgrid=False, title=""))
            st.plotly_chart(fig_bar, use_container_width=True)

    with mid_col2:
        if selected_region == "Malaysia":
            copilot_title = "ML Policy Copilot"
            # Dynamically state the top 2 states
            copilot_body = f"Our Gradient Boosting model identifies <span style='font-weight: bold;'>{top_ml_state}</span> and <span style='font-weight: bold;'>{top2_ml_state}</span> as having the highest untapped tourism potential relative to their structural benchmarks."
            copilot_evi = f"Evidence: Model predicts {top_ml_state} has a {top_ml_gap:.1f}% opportunity gap between expected and actual visitor share in {selected_year}."
        else:
            actual_share = ml_filter['actual_share_pct'].values[0] if not ml_filter.empty else "N/A"
            expected_share = ml_filter['expected_share_pct'].values[0] if not ml_filter.empty else "N/A"
            
            copilot_title = f"{selected_region} ML Insights"
            if top_ml_gap > 0:
                copilot_body = f"Our model identifies <span style='font-weight: bold;'>{selected_region}</span> as a high-potential growth target. Its actual share of national visitors is lower than its structural fundamentals predict."
            else:
                copilot_body = f"<span style='font-weight: bold;'>{selected_region}</span> is currently over-performing its structural baseline. Focus policies on sustainability and infrastructure rather than mass promotion."
            
            copilot_evi = f"Evidence: Actual Share ({actual_share}%) vs Expected Share ({expected_share}%). Gap: {top_ml_gap}%."

        st.markdown(f"""
        <div style="background-color: #3B3C54; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 10px; height: 320px;">
            <div style="color: white; font-family: sans-serif; font-size: 1.4rem; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center;">
                <span style="margin-right: 8px; font-size: 1.6rem;">🤖</span> {copilot_title}
            </div>
            <div style="color: #F3F4F6; font-family: sans-serif; font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px;">
                {copilot_body}
            </div>
            <div style="background-color: rgba(255,255,255,0.08); padding: 15px; border-radius: 8px; font-family: sans-serif; font-size: 0.85rem; color: #D1D5DB;">
                {copilot_evi}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("💬 Ask why · show sources"):
            st.write(f"**Source:** DOSM Domestic Tourism Survey. Predictions generated by LestariLens Gradient Boosting model.")
            st.write("*Note: Opportunity Gap is a structural benchmark, not a definitive future forecast.*")

    st.markdown("<br>", unsafe_allow_html=True)
    bot_col1, bot_col2 = st.columns([1.5, 1.5])

    with bot_col1:
        with st.container(border=True):
            st.subheader("What visitors spend on")
            st.caption(f"Simulated 2025 Benchmark Share (Fixed Scale)")
            
            pie_data = pd.DataFrame({
                'Category': ['Shopping', 'Food & beverages', 'Automotive fuel', 'Other categories'],
                'Value': [36.9, 16.1, 13.5, 33.5],
                'Color': ['#E27D60', '#85A88F', '#E8B87B', '#E4E4E4']
            })
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=pie_data['Category'], values=pie_data['Value'], hole=0.6,
                marker=dict(colors=pie_data['Color']), textinfo='none', sort=False, direction='clockwise'
            )])
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=10, b=0), 
                height=250, showlegend=True, 
                annotations=[dict(text="2025 est.", x=0.5, y=0.5, font_size=18, font_color="#2D3142", showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with bot_col2:
        with st.container(border=True):
            st.subheader("Scenario lab")
            st.caption("Explore redistribution based on selected region")
            
            shift_pct = st.slider("Shift projected demand", min_value=0, max_value=20, value=5, format="%d%%")
            
            if selected_region == "Malaysia":
                target_state = "Pahang"
                base_vol = df[(df['year'] == selected_year) & (df['state'] == 'Pahang')]['visitors_M'].sum()
                scenario_calc = base_vol + (v_current * (shift_pct / 100))
            else:
                target_state = selected_region
                scenario_calc = v_current * (1 + (shift_pct / 100))
                
            c1, c2 = st.columns(2)
            c1.metric("Projected Shift Scenario", f"{scenario_calc:.1f}M")
            c2.metric("Target State", target_state)


# ==========================================
# PAGE 2: VISITOR FLOWS
# ==========================================
def render_visitor_flows():
    st.markdown(f'<p class="sub-header">ANALYTICS · HISTORICAL TRENDS ({selected_year})</p>', unsafe_allow_html=True)
    st.header("Visitor Flows & Growth Trajectories")
    st.markdown("Track the movement and long-term growth of domestic visitors across all states up to the selected year.")
    
    df_trend = df[df['year'] <= selected_year].groupby(['year', 'state'])['visitors_M'].sum().reset_index()
    
    top_3 = df[df['year'] == selected_year].sort_values('visitors_M', ascending=False).head(3)['state'].tolist()
    df_trend['Highlight'] = df_trend['state'].apply(lambda x: x if x in top_3 else 'Other States')
    
    fig_line = px.line(df_trend, x="year", y="visitors_M", color="Highlight", line_group="state", hover_name="state",
                       color_discrete_map={'Selangor': '#E27D60', 'W.P. Kuala Lumpur': '#85A88F', 'Perak': '#E8B87B', 'Other States': '#DEDAD0'})
    
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500,
                           xaxis=dict(showgrid=False, title="Year"), yaxis=dict(showgrid=True, gridcolor='#E5E2D9', title="Visitors (Millions)"))
    st.plotly_chart(fig_line, use_container_width=True)


# ==========================================
# PAGE 3: SUSTAINABILITY
# ==========================================
def render_sustainability():
    st.markdown(f'<p class="sub-header">INFRASTRUCTURE · CAPACITY ({selected_year})</p>', unsafe_allow_html=True)
    st.header("Sustainability & Tourism Strain")
    st.markdown(f"Analyze local infrastructure capacity versus economic output based on the **{selected_year}** global filter.")
    
    df_yr = df[df['year'] == selected_year].copy()
    
    fig_scatter = px.scatter(df_yr, x="log_gdp_per_capita", y="rooms_per_1k_residents", 
                             size="visitors_M", color="visitors_M", hover_name="state",
                             color_continuous_scale=["#85A88F", "#E8B87B", "#E27D60"],
                             labels={"log_gdp_per_capita": "Economic Strength (Log GDP per Capita)", 
                                     "rooms_per_1k_residents": "Infrastructure Capacity (Rooms per 1k Residents)"})
    
    if not df_yr.empty:
        fig_scatter.add_vline(x=df_yr['log_gdp_per_capita'].median(), line_width=1, line_dash="dash", line_color="gray")
        fig_scatter.add_hline(y=df_yr['rooms_per_1k_residents'].median(), line_width=1, line_dash="dash", line_color="gray")
    
    fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)


# ==========================================
# PAGE 4: SCENARIO LAB
# ==========================================
def render_scenario_lab():
    st.markdown(f'<p class="sub-header">POLICY · SIMULATION ({selected_year})</p>', unsafe_allow_html=True)
    st.header("Scenario Lab: Demand Redistribution")
    st.markdown(f"Simulate the impact of shifting tourism volume from high-density states to developing targets using the **{selected_year}** baseline.")
    
    col1, col2, col3 = st.columns([1, 1, 1.5])
    df_yr = df[df['year'] == selected_year]
    
    with col1:
        source_state = st.selectbox("Source State (Reduce Demand)", df_yr.sort_values('visitors_M', ascending=False)['state'])
    with col2:
        target_state = st.selectbox("Target State (Increase Demand)", df_yr.sort_values('visitors_M')['state'], index=1)
    with col3:
        shift_pct = st.slider("Percentage of Source Visitors to Shift", min_value=0, max_value=30, value=5, format="%d%%")
        
    source_vol = df_yr[df_yr['state'] == source_state]['visitors_M'].values[0] if not df_yr.empty else 0
    target_vol = df_yr[df_yr['state'] == target_state]['visitors_M'].values[0] if not df_yr.empty else 0
    
    shift_amount = source_vol * (shift_pct / 100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1.container(border=True):
        st.subheader(f"📉 {source_state} (Source)")
        st.metric("New Projected Visitors", f"{source_vol - shift_amount:.1f}M", f"-{shift_amount:.1f}M shifted", delta_color="inverse")
        
    with c2.container(border=True):
        st.subheader(f"📈 {target_state} (Target)")
        st.metric("New Projected Visitors", f"{target_vol + shift_amount:.1f}M", f"+{shift_amount:.1f}M gained")


# ==========================================
# PAGE 5: EVIDENCE & LIMITATIONS
# ==========================================
def render_evidence():
    st.markdown('<p class="sub-header">DATA · TRANSPARENCY</p>', unsafe_allow_html=True)
    st.header("Evidence & Methodology")
    st.markdown("Direct access to the underlying DOSM dataset, ML Predictions, and project limitations.")
    
    # Critical Model Limitations section requested in Code Review
    with st.expander("⚠️ ML Methodology & Limitations", expanded=True):
        st.markdown("""
        - **Training vs Holdout:** Data from **2017-2023** was utilized for model training. **2024-2025** serves as an untouched holdout dataset to evaluate structural baselines.
        - **Opportunity Gap Interpretation:** The gap represents a structural benchmark comparing actual visitor share against economic and infrastructure fundamentals. It is **not** a direct future forecast. A positive gap indicates untapped potential but does not definitively prove a lack of marketing exposure alone.
        - **Data Constraints:** Metrics for **Perlis** and **W.P. Putrajaya** possess lower predictive reliability due to naturally smaller sample sizes and outlier density within DOSM records.
        """)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("Total States", df['state'].nunique())
    col3.metric("Year Range", f"{df['year'].min()} - {df['year'].max()}")
    
    st.subheader("Historical Data (DOSM)")
    st.dataframe(df, use_container_width=True, height=300)
    
    st.subheader("Machine Learning Output (Opportunity Gap)")
    st.dataframe(df_ml, use_container_width=True)


# --- 9. Execution Engine ---
if selected_page == "Overview":
    render_overview()
elif selected_page == "Visitor flows":
    render_visitor_flows()
elif selected_page == "Sustainability":
    render_sustainability()
elif selected_page == "Scenario lab":
    render_scenario_lab()
elif selected_page == "Evidence":
    render_evidence()