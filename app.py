"""
Marken Healthcare Logistics - Profitability Dashboard
Executive-level financial analytics for SR Technics Engine Services
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION & STYLING
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Marken | Profitability Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Marken brand colors
MARKEN_NAVY = "#1B365D"
MARKEN_BLUE = "#0066B3"
MARKEN_LIGHT_BLUE = "#4A90D9"
MARKEN_GRAY = "#6B7280"
MARKEN_GREEN = "#10B981"
MARKEN_RED = "#EF4444"
MARKEN_ORANGE = "#F59E0B"

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
    
    .stApp {
        background-color: #FAFBFC;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1B365D 0%, #0066B3 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 12px 12px;
        margin: -1rem -1rem 1.5rem -1rem;
    }
    
    .main-header h1 {
        color: white;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1B365D;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #0066B3;
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6B7280;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1B365D;
    }
    
    .metric-value.positive { color: #10B981; }
    .metric-value.negative { color: #EF4444; }
    
    .info-banner {
        background: #EBF5FF;
        border-left: 4px solid #0066B3;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #1B365D;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    section[data-testid="stSidebar"] {
        background-color: #1B365D;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def format_currency(value):
    """Format number as USD currency with appropriate scale"""
    if pd.isna(value) or value == 0:
        return "$0"
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    if abs_val >= 1_000_000_000:
        return f"{sign}${abs_val/1_000_000_000:,.1f}B"
    elif abs_val >= 1_000_000:
        return f"{sign}${abs_val/1_000_000:,.1f}M"
    elif abs_val >= 1_000:
        return f"{sign}${abs_val/1_000:,.1f}K"
    else:
        return f"{sign}${abs_val:,.0f}"


def format_number(value):
    """Format large numbers with commas"""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.2f}"


def load_and_process_data(uploaded_file):
    """Load and process the uploaded Excel file"""
    try:
        df = pd.read_excel(uploaded_file)
        
        if 'ORD DT' not in df.columns:
            st.error("Required column 'ORD DT' not found.")
            return None
        
        df['ORD DT'] = pd.to_datetime(df['ORD DT'])
        
        # Cost columns
        cost_columns = ['PU COST', 'SHIP COST', 'MAN COST', 'DEL COST']
        for col in cost_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
        
        # Revenue column
        if 'NET' in df.columns:
            df['NET'] = pd.to_numeric(df['NET'], errors='coerce').fillna(0)
        else:
            st.error("Required column 'NET' not found.")
            return None
        
        # Calculations
        df['TOTAL_COSTS'] = df[cost_columns].sum(axis=1)
        df['PROFIT'] = df['NET'] - df['TOTAL_COSTS']
        df['MARGIN_PCT'] = df.apply(lambda row: (row['PROFIT'] / row['NET'] * 100) if row['NET'] != 0 else 0, axis=1)
        
        # Date fields
        df['YEAR'] = df['ORD DT'].dt.year
        df['MONTH'] = df['ORD DT'].dt.month
        df['YEAR_MONTH'] = df['ORD DT'].dt.to_period('M')
        df['MONTH_LABEL'] = df['ORD DT'].dt.strftime('%b %Y')
        
        return df
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None


def create_monthly_summary(df):
    """Create monthly aggregated summary"""
    monthly = df.groupby(['YEAR_MONTH']).agg({
        'NET': 'sum',
        'TOTAL_COSTS': 'sum',
        'PROFIT': 'sum',
        'PU COST': 'sum',
        'SHIP COST': 'sum',
        'MAN COST': 'sum',
        'DEL COST': 'sum',
        'ORD DT': 'count'
    }).reset_index()
    
    monthly.columns = ['Period', 'Revenue', 'Total_Costs', 'Profit', 
                       'Pickup_Cost', 'Shipping_Cost', 'Management_Cost', 'Delivery_Cost', 'Orders']
    
    monthly['Margin_Pct'] = monthly.apply(
        lambda row: (row['Profit'] / row['Revenue'] * 100) if row['Revenue'] != 0 else 0, axis=1
    )
    
    monthly = monthly.sort_values('Period')
    monthly['Month_Label'] = monthly['Period'].astype(str)
    
    return monthly


# ══════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_revenue_chart(monthly_df):
    """Simple monthly revenue bar chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly_df['Month_Label'],
        y=monthly_df['Revenue'],
        marker_color=MARKEN_BLUE,
        text=[format_currency(v) for v in monthly_df['Revenue']],
        textposition='outside',
        textfont=dict(size=11, color=MARKEN_NAVY),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='<b>Monthly Revenue</b>', font=dict(size=16, color=MARKEN_NAVY), x=0),
        xaxis=dict(title='', tickfont=dict(size=11), tickangle=-45),
        yaxis=dict(title='Revenue (USD)', tickformat='$,.0f', gridcolor='rgba(0,0,0,0.08)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=80, l=80, r=40),
        height=400,
        showlegend=False
    )
    
    return fig


def create_costs_chart(monthly_df):
    """Simple monthly total costs bar chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly_df['Month_Label'],
        y=monthly_df['Total_Costs'],
        marker_color=MARKEN_NAVY,
        text=[format_currency(v) for v in monthly_df['Total_Costs']],
        textposition='outside',
        textfont=dict(size=11, color=MARKEN_NAVY),
        hovertemplate='<b>%{x}</b><br>Total Costs: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='<b>Monthly Total Costs</b>', font=dict(size=16, color=MARKEN_NAVY), x=0),
        xaxis=dict(title='', tickfont=dict(size=11), tickangle=-45),
        yaxis=dict(title='Costs (USD)', tickformat='$,.0f', gridcolor='rgba(0,0,0,0.08)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=80, l=80, r=40),
        height=400,
        showlegend=False
    )
    
    return fig


def create_profit_chart(monthly_df):
    """Monthly profit bar chart with color coding"""
    colors = [MARKEN_GREEN if p >= 0 else MARKEN_RED for p in monthly_df['Profit']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly_df['Month_Label'],
        y=monthly_df['Profit'],
        marker_color=colors,
        text=[format_currency(v) for v in monthly_df['Profit']],
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=MARKEN_GRAY, line_width=1)
    
    fig.update_layout(
        title=dict(text='<b>Monthly Profit (Revenue - Costs)</b>', font=dict(size=16, color=MARKEN_NAVY), x=0),
        xaxis=dict(title='', tickfont=dict(size=11), tickangle=-45),
        yaxis=dict(title='Profit (USD)', tickformat='$,.0f', gridcolor='rgba(0,0,0,0.08)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=80, l=80, r=40),
        height=400,
        showlegend=False
    )
    
    return fig


def create_waterfall_chart(total_revenue, total_costs, total_profit):
    """Waterfall chart showing Revenue - Costs = Profit"""
    
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=["absolute", "relative", "total"],
        x=["Revenue", "Total Costs", "Profit"],
        y=[total_revenue, -total_costs, total_profit],
        text=[format_currency(total_revenue), format_currency(-total_costs), format_currency(total_profit)],
        textposition="outside",
        textfont=dict(size=14, color=MARKEN_NAVY),
        connector={"line": {"color": MARKEN_GRAY, "width": 1, "dash": "dot"}},
        increasing={"marker": {"color": MARKEN_GREEN}},
        decreasing={"marker": {"color": MARKEN_RED}},
        totals={"marker": {"color": MARKEN_BLUE if total_profit >= 0 else MARKEN_RED}},
        hovertemplate='<b>%{x}</b><br>Amount: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='<b>Annual Profitability Waterfall: Revenue → Costs → Profit</b>', font=dict(size=16, color=MARKEN_NAVY), x=0),
        xaxis=dict(title='', tickfont=dict(size=13)),
        yaxis=dict(title='Amount (USD)', tickformat='$,.0f', gridcolor='rgba(0,0,0,0.08)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=60, l=100, r=40),
        height=450,
        showlegend=False
    )
    
    return fig


def create_cost_breakdown_chart(cost_data):
    """Horizontal bar chart for cost breakdown"""
    
    fig = go.Figure()
    
    colors = [MARKEN_NAVY, MARKEN_BLUE, MARKEN_LIGHT_BLUE, MARKEN_GRAY]
    
    fig.add_trace(go.Bar(
        y=cost_data['Cost_Type'],
        x=cost_data['Amount'],
        orientation='h',
        marker_color=colors[:len(cost_data)],
        text=[f"{format_currency(a)} ({p:.1f}%)" for a, p in zip(cost_data['Amount'], cost_data['Percentage'])],
        textposition='auto',
        textfont=dict(size=11, color='white'),
        hovertemplate='<b>%{y}</b><br>Amount: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='<b>Cost Breakdown by Category</b>', font=dict(size=16, color=MARKEN_NAVY), x=0),
        xaxis=dict(title='Amount (USD)', tickformat='$,.0f', gridcolor='rgba(0,0,0,0.08)'),
        yaxis=dict(title='', tickfont=dict(size=11)),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=60, l=140, r=40),
        height=320,
        showlegend=False
    )
    
    return fig


def create_margin_chart(monthly_df):
    """Line chart for profit margin %"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_df['Month_Label'],
        y=monthly_df['Margin_Pct'],
        mode='lines+markers+text',
        line=dict(color=MARKEN_ORANGE, width=3),
        marker=dict(size=10, color=MARKEN_ORANGE),
        text=[f"{v:.1f}%" for v in monthly_df['Margin_Pct']],
        textposition='top center',
        textfont=dict(size=10, color=MARKEN_ORANGE),
        hovertemplate='<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=MARKEN_GRAY, line_width=1)
    
    fig.update_layout(
        title=dict(text='<b>Monthly Profit Margin %</b>', font=dict(size=16, color=MARKEN_NAVY), x=0),
        xaxis=dict(title='', tickfont=dict(size=11), tickangle=-45),
        yaxis=dict(title='Margin (%)', tickformat='.0f', gridcolor='rgba(0,0,0,0.08)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=80, l=80, r=40),
        height=350,
        showlegend=False
    )
    
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Marken Healthcare Logistics</h1>
        <p>Profitability Dashboard | SR Technics Engine Services</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h3 style='color: white;'>📁 Upload Data</h3>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Upload the SR Technics profitability data"
        )
        
        st.markdown("---")
        
        st.markdown("""
        <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem;">
            <p><b>Required Columns:</b></p>
            <ul style="line-height: 1.6;">
                <li>ORD DT (Date)</li>
                <li>PU COST, SHIP COST, MAN COST, DEL COST</li>
                <li>NET (Revenue)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("<p style='color: rgba(255,255,255,0.5); font-size: 0.75rem;'>© 2025 Marken Healthcare Logistics</p>", unsafe_allow_html=True)
    
    # Main content
    if uploaded_file is not None:
        df = load_and_process_data(uploaded_file)
        
        if df is not None:
            monthly_df = create_monthly_summary(df)
            
            # Annual totals
            total_revenue = df['NET'].sum()
            total_costs = df['TOTAL_COSTS'].sum()
            total_profit = df['PROFIT'].sum()
            overall_margin = (total_profit / total_revenue * 100) if total_revenue != 0 else 0
            total_orders = len(df)
            
            # Date range
            date_min = df['ORD DT'].min().strftime('%b %Y')
            date_max = df['ORD DT'].max().strftime('%b %Y')
            
            # Info banner
            st.markdown(f"""
            <div class="info-banner">
                <b>Period:</b> {date_min} — {date_max} &nbsp;|&nbsp; 
                <b>Customer:</b> SR Technics Engine Services &nbsp;|&nbsp; 
                <b>Orders:</b> {total_orders:,}
            </div>
            """, unsafe_allow_html=True)
            
            # ══════════════════════════════════════════════════════════════════
            # KEY METRICS
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-title">📈 Annual Summary</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("TOTAL REVENUE", format_currency(total_revenue))
            
            with col2:
                st.metric("TOTAL COSTS", format_currency(total_costs))
            
            with col3:
                delta_color = "normal" if total_profit >= 0 else "inverse"
                st.metric("PROFIT", format_currency(total_profit), delta=f"{overall_margin:.1f}% margin", delta_color=delta_color)
            
            with col4:
                st.metric("ORDERS", f"{total_orders:,}")
            
            # ══════════════════════════════════════════════════════════════════
            # WATERFALL CHART
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-title">💧 Revenue to Profit Waterfall</div>', unsafe_allow_html=True)
            
            waterfall_fig = create_waterfall_chart(total_revenue, total_costs, total_profit)
            st.plotly_chart(waterfall_fig, use_container_width=True)
            
            # ══════════════════════════════════════════════════════════════════
            # MONTHLY CHARTS - REVENUE, COSTS, PROFIT
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-title">📅 Monthly Performance</div>', unsafe_allow_html=True)
            
            # Revenue chart
            revenue_fig = create_revenue_chart(monthly_df)
            st.plotly_chart(revenue_fig, use_container_width=True)
            
            # Costs chart
            costs_fig = create_costs_chart(monthly_df)
            st.plotly_chart(costs_fig, use_container_width=True)
            
            # Profit chart
            profit_fig = create_profit_chart(monthly_df)
            st.plotly_chart(profit_fig, use_container_width=True)
            
            # Margin chart
            margin_fig = create_margin_chart(monthly_df)
            st.plotly_chart(margin_fig, use_container_width=True)
            
            # ══════════════════════════════════════════════════════════════════
            # COST BREAKDOWN
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-title">🔍 Cost Breakdown</div>', unsafe_allow_html=True)
            
            # Prepare cost breakdown data
            cost_breakdown = pd.DataFrame({
                'Cost_Type': ['Management Cost', 'Pickup Cost', 'Shipping Cost', 'Delivery Cost'],
                'Amount': [
                    df['MAN COST'].sum(),
                    df['PU COST'].sum(),
                    df['SHIP COST'].sum(),
                    df['DEL COST'].sum()
                ]
            })
            total_cost = cost_breakdown['Amount'].sum()
            cost_breakdown['Percentage'] = (cost_breakdown['Amount'] / total_cost * 100) if total_cost > 0 else 0
            cost_breakdown = cost_breakdown.sort_values('Amount', ascending=True)
            
            cost_fig = create_cost_breakdown_chart(cost_breakdown)
            st.plotly_chart(cost_fig, use_container_width=True)
            
            # Cost table
            st.markdown("**Cost Summary Table:**")
            cost_display = cost_breakdown.sort_values('Amount', ascending=False).copy()
            cost_display['Amount'] = cost_display['Amount'].apply(lambda x: f"${x:,.2f}")
            cost_display['Percentage'] = cost_display['Percentage'].apply(lambda x: f"{x:.2f}%")
            cost_display.columns = ['Cost Category', 'Amount', '% of Total']
            st.dataframe(cost_display, use_container_width=True, hide_index=True)
            
            # ══════════════════════════════════════════════════════════════════
            # DETAILED DATA TABLES
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-title">📋 Detailed Data</div>', unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Monthly Summary", "Raw Data"])
            
            with tab1:
                display_df = monthly_df[['Month_Label', 'Revenue', 'Total_Costs', 'Profit', 'Margin_Pct', 'Orders']].copy()
                display_df.columns = ['Month', 'Revenue', 'Total Costs', 'Profit', 'Margin %', 'Orders']
                display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"${x:,.2f}")
                display_df['Total Costs'] = display_df['Total Costs'].apply(lambda x: f"${x:,.2f}")
                display_df['Profit'] = display_df['Profit'].apply(lambda x: f"${x:,.2f}")
                display_df['Margin %'] = display_df['Margin %'].apply(lambda x: f"{x:.2f}%")
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                csv = monthly_df.to_csv(index=False)
                st.download_button("📥 Download Monthly Summary", csv, "monthly_summary.csv", "text/csv")
            
            with tab2:
                raw_cols = ['ORD DT', 'ORD#', 'PU COST', 'SHIP COST', 'MAN COST', 'DEL COST', 'TOTAL_COSTS', 'NET', 'PROFIT', 'STATUS', 'PU CTRY']
                available_cols = [c for c in raw_cols if c in df.columns]
                
                st.dataframe(
                    df[available_cols].sort_values('ORD DT', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
                
                csv_raw = df.to_csv(index=False)
                st.download_button("📥 Download Full Data", csv_raw, "full_data.csv", "text/csv")
    
    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📂</div>
            <h2 style="color: #1B365D;">Upload Your Data to Begin</h2>
            <p style="color: #6B7280; max-width: 500px; margin: 1rem auto;">
                Use the sidebar to upload your SR Technics Excel file and view profitability analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
