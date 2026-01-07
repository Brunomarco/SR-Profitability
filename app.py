"""
Marken Healthcare Logistics - Profitability Dashboard
Executive-level financial analytics for SR Technics Engine Services
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
MARKEN_LIGHT_GRAY = "#F3F4F6"
MARKEN_SUCCESS = "#10B981"
MARKEN_WARNING = "#F59E0B"
MARKEN_DANGER = "#EF4444"

# Custom CSS for MBB-style professional appearance
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        background-color: #FAFBFC;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1B365D 0%, #0066B3 100%);
        padding: 2rem 2.5rem;
        border-radius: 0 0 16px 16px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 20px rgba(27, 54, 93, 0.15);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
        border: 1px solid #E5E7EB;
        transition: all 0.2s ease;
    }
    
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .kpi-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6B7280;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1B365D;
        line-height: 1.2;
    }
    
    .kpi-delta {
        font-size: 0.875rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .kpi-delta.positive { color: #10B981; }
    .kpi-delta.negative { color: #EF4444; }
    
    /* Section headers */
    .section-header {
        font-size: 1.125rem;
        font-weight: 700;
        color: #1B365D;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #0066B3;
    }
    
    /* Data table styling */
    .dataframe {
        font-size: 0.875rem !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1B365D;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Metric styling override */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1B365D;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6B7280;
        font-weight: 600;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed #D1D5DB;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #EBF5FF 0%, #F0F9FF 100%);
        border-left: 4px solid #0066B3;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    .info-box p {
        color: #1B365D;
        margin: 0;
        font-size: 0.875rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1B365D;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def format_currency(value, decimals=0):
    """Format number as USD currency"""
    if pd.isna(value) or value == 0:
        return "$0"
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:,.{decimals}f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:,.{decimals}f}K"
    else:
        return f"${value:,.{decimals}f}"


def format_percentage(value, decimals=1):
    """Format number as percentage"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def calculate_margin(profit, revenue):
    """Calculate profit margin safely"""
    if revenue == 0 or pd.isna(revenue):
        return 0
    return (profit / revenue) * 100


def load_and_process_data(uploaded_file):
    """Load and process the uploaded Excel file"""
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)
        
        # Ensure date column exists and is datetime
        if 'ORD DT' in df.columns:
            df['ORD DT'] = pd.to_datetime(df['ORD DT'])
        else:
            st.error("Required column 'ORD DT' not found in the uploaded file.")
            return None
        
        # Define cost columns
        cost_columns = ['PU COST', 'SHIP COST', 'MAN COST', 'DEL COST']
        
        # Fill NaN values with 0 for cost columns
        for col in cost_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0)
            else:
                df[col] = 0
        
        # Fill NaN values for NET (revenue)
        if 'NET' in df.columns:
            df['NET'] = df['NET'].fillna(0)
        else:
            st.error("Required column 'NET' not found in the uploaded file.")
            return None
        
        # Calculate total costs
        df['TOTAL_COSTS'] = df[cost_columns].sum(axis=1)
        
        # Calculate profit
        df['PROFIT'] = df['NET'] - df['TOTAL_COSTS']
        
        # Extract month and year
        df['YEAR'] = df['ORD DT'].dt.year
        df['MONTH'] = df['ORD DT'].dt.month
        df['MONTH_NAME'] = df['ORD DT'].dt.strftime('%b')
        df['YEAR_MONTH'] = df['ORD DT'].dt.to_period('M')
        df['MONTH_YEAR_STR'] = df['ORD DT'].dt.strftime('%b %Y')
        
        return df
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None


def create_monthly_summary(df):
    """Create monthly summary of revenue, costs, and profit"""
    monthly = df.groupby(['YEAR_MONTH', 'MONTH_YEAR_STR']).agg({
        'NET': 'sum',
        'TOTAL_COSTS': 'sum',
        'PROFIT': 'sum',
        'PU COST': 'sum',
        'SHIP COST': 'sum',
        'MAN COST': 'sum',
        'DEL COST': 'sum',
        'ORD DT': 'count'
    }).reset_index()
    
    monthly.columns = ['Period', 'Month', 'Revenue', 'Total Costs', 'Profit', 
                       'Pickup Cost', 'Shipping Cost', 'Management Cost', 'Delivery Cost', 'Orders']
    
    monthly['Margin %'] = monthly.apply(
        lambda row: calculate_margin(row['Profit'], row['Revenue']), axis=1
    )
    
    # Sort by period
    monthly = monthly.sort_values('Period')
    
    return monthly


def create_cost_breakdown(df):
    """Create cost breakdown summary"""
    cost_data = {
        'Cost Type': ['Pickup Cost', 'Shipping Cost', 'Management Cost', 'Delivery Cost'],
        'Amount': [
            df['PU COST'].sum(),
            df['SHIP COST'].sum(),
            df['MAN COST'].sum(),
            df['DEL COST'].sum()
        ]
    }
    
    cost_df = pd.DataFrame(cost_data)
    total = cost_df['Amount'].sum()
    cost_df['Percentage'] = (cost_df['Amount'] / total * 100).round(2)
    cost_df = cost_df.sort_values('Amount', ascending=False)
    
    return cost_df


# ══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_revenue_cost_chart(monthly_df):
    """Create combined revenue and cost trend chart"""
    fig = go.Figure()
    
    # Revenue bars
    fig.add_trace(go.Bar(
        name='Revenue',
        x=monthly_df['Month'],
        y=monthly_df['Revenue'],
        marker_color=MARKEN_BLUE,
        text=[format_currency(v) for v in monthly_df['Revenue']],
        textposition='outside',
        textfont=dict(size=10)
    ))
    
    # Cost bars
    fig.add_trace(go.Bar(
        name='Total Costs',
        x=monthly_df['Month'],
        y=monthly_df['Total Costs'],
        marker_color=MARKEN_NAVY,
        text=[format_currency(v) for v in monthly_df['Total Costs']],
        textposition='outside',
        textfont=dict(size=10)
    ))
    
    fig.update_layout(
        barmode='group',
        title=dict(
            text='<b>Monthly Revenue vs Total Costs</b>',
            font=dict(size=16, color=MARKEN_NAVY),
            x=0
        ),
        xaxis=dict(
            title='',
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title='Amount (USD)',
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.08)',
            tickformat='$,.0f'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=11)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=80, b=60, l=80, r=40),
        height=420
    )
    
    return fig


def create_profit_margin_chart(monthly_df):
    """Create profit and margin trend chart"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Profit bars with conditional coloring
    colors = [MARKEN_SUCCESS if p >= 0 else MARKEN_DANGER for p in monthly_df['Profit']]
    
    fig.add_trace(
        go.Bar(
            name='Profit',
            x=monthly_df['Month'],
            y=monthly_df['Profit'],
            marker_color=colors,
            text=[format_currency(v) for v in monthly_df['Profit']],
            textposition='outside',
            textfont=dict(size=10)
        ),
        secondary_y=False
    )
    
    # Margin line
    fig.add_trace(
        go.Scatter(
            name='Margin %',
            x=monthly_df['Month'],
            y=monthly_df['Margin %'],
            mode='lines+markers+text',
            line=dict(color=MARKEN_WARNING, width=3),
            marker=dict(size=8, color=MARKEN_WARNING),
            text=[f"{v:.1f}%" for v in monthly_df['Margin %']],
            textposition='top center',
            textfont=dict(size=10, color=MARKEN_WARNING)
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title=dict(
            text='<b>Monthly Profit & Margin Analysis</b>',
            font=dict(size=16, color=MARKEN_NAVY),
            x=0
        ),
        xaxis=dict(
            title='',
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=11)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=80, b=60, l=80, r=80),
        height=420
    )
    
    fig.update_yaxes(
        title_text='Profit (USD)',
        tickformat='$,.0f',
        gridcolor='rgba(0,0,0,0.08)',
        secondary_y=False
    )
    
    fig.update_yaxes(
        title_text='Margin (%)',
        tickformat='.1f',
        gridcolor='rgba(0,0,0,0)',
        secondary_y=True
    )
    
    return fig


def create_cost_breakdown_chart(cost_df):
    """Create cost breakdown donut chart"""
    fig = go.Figure(data=[go.Pie(
        labels=cost_df['Cost Type'],
        values=cost_df['Amount'],
        hole=0.55,
        marker=dict(
            colors=[MARKEN_NAVY, MARKEN_BLUE, MARKEN_LIGHT_BLUE, MARKEN_GRAY]
        ),
        textinfo='label+percent',
        textfont=dict(size=12),
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Share: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text='<b>Cost Breakdown by Category</b>',
            font=dict(size=16, color=MARKEN_NAVY),
            x=0
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            font=dict(size=11)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=80, l=40, r=40),
        height=400,
        annotations=[
            dict(
                text=f'<b>Total</b><br>{format_currency(cost_df["Amount"].sum())}',
                x=0.5, y=0.5,
                font=dict(size=14, color=MARKEN_NAVY),
                showarrow=False
            )
        ]
    )
    
    return fig


def create_cost_trend_chart(monthly_df):
    """Create stacked area chart for cost components over time"""
    fig = go.Figure()
    
    cost_cols = ['Pickup Cost', 'Shipping Cost', 'Management Cost', 'Delivery Cost']
    colors = [MARKEN_NAVY, MARKEN_BLUE, MARKEN_LIGHT_BLUE, MARKEN_GRAY]
    
    for col, color in zip(cost_cols, colors):
        fig.add_trace(go.Scatter(
            name=col,
            x=monthly_df['Month'],
            y=monthly_df[col],
            mode='lines',
            stackgroup='one',
            fillcolor=color,
            line=dict(width=0.5, color=color),
            hovertemplate=f'<b>{col}</b><br>Amount: $%{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text='<b>Cost Components Over Time</b>',
            font=dict(size=16, color=MARKEN_NAVY),
            x=0
        ),
        xaxis=dict(
            title='',
            tickfont=dict(size=11),
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title='Amount (USD)',
            tickformat='$,.0f',
            gridcolor='rgba(0,0,0,0.08)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=11)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=80, b=60, l=80, r=40),
        height=400
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
        st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="color: white; font-size: 1.25rem; margin-bottom: 1rem;">⚙️ Dashboard Controls</h2>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Upload the SR Technics profitability data file"
        )
        
        st.markdown("---")
        
        st.markdown("""
        <div style="color: rgba(255,255,255,0.8); font-size: 0.875rem;">
            <p><strong>Required Columns:</strong></p>
            <ul style="margin-left: 1rem; line-height: 1.8;">
                <li>ORD DT (Date)</li>
                <li>PU COST</li>
                <li>SHIP COST</li>
                <li>MAN COST</li>
                <li>DEL COST</li>
                <li>NET (Revenue)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div style="color: rgba(255,255,255,0.6); font-size: 0.75rem; margin-top: 2rem;">
            <p>© 2025 Marken Healthcare Logistics</p>
            <p>Executive Dashboard v1.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if uploaded_file is not None:
        # Load and process data
        df = load_and_process_data(uploaded_file)
        
        if df is not None:
            # Calculate summaries
            monthly_df = create_monthly_summary(df)
            cost_df = create_cost_breakdown(df)
            
            # Calculate annual totals
            total_revenue = df['NET'].sum()
            total_costs = df['TOTAL_COSTS'].sum()
            total_profit = df['PROFIT'].sum()
            overall_margin = calculate_margin(total_profit, total_revenue)
            total_orders = len(df)
            
            # Get date range
            date_min = df['ORD DT'].min().strftime('%b %Y')
            date_max = df['ORD DT'].max().strftime('%b %Y')
            
            # Account info
            account_name = df['ACCT NM'].iloc[0] if 'ACCT NM' in df.columns else "N/A"
            
            # Info box
            st.markdown(f"""
            <div class="info-box">
                <p><strong>Analysis Period:</strong> {date_min} — {date_max} | 
                <strong>Customer:</strong> {account_name} | 
                <strong>Total Orders:</strong> {total_orders:,}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # ══════════════════════════════════════════════════════════════════
            # KEY METRICS ROW
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-header">Key Financial Metrics (Annual Summary)</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="TOTAL REVENUE",
                    value=format_currency(total_revenue, 1),
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="TOTAL COSTS",
                    value=format_currency(total_costs, 1),
                    delta=None
                )
            
            with col3:
                profit_color = "normal" if total_profit >= 0 else "inverse"
                st.metric(
                    label="TOTAL PROFIT",
                    value=format_currency(total_profit, 1),
                    delta=f"{format_percentage(overall_margin)} margin",
                    delta_color=profit_color
                )
            
            with col4:
                avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
                st.metric(
                    label="AVG ORDER VALUE",
                    value=format_currency(avg_order_value, 1),
                    delta=f"{total_orders:,} orders"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ══════════════════════════════════════════════════════════════════
            # CHARTS ROW 1: Revenue/Costs and Profit/Margin
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-header">Monthly Performance Analysis</div>', unsafe_allow_html=True)
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                revenue_cost_chart = create_revenue_cost_chart(monthly_df)
                st.plotly_chart(revenue_cost_chart, use_container_width=True)
            
            with chart_col2:
                profit_margin_chart = create_profit_margin_chart(monthly_df)
                st.plotly_chart(profit_margin_chart, use_container_width=True)
            
            # ══════════════════════════════════════════════════════════════════
            # CHARTS ROW 2: Cost Breakdown
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-header">Cost Structure Analysis</div>', unsafe_allow_html=True)
            
            cost_col1, cost_col2 = st.columns(2)
            
            with cost_col1:
                cost_breakdown_chart = create_cost_breakdown_chart(cost_df)
                st.plotly_chart(cost_breakdown_chart, use_container_width=True)
            
            with cost_col2:
                cost_trend_chart = create_cost_trend_chart(monthly_df)
                st.plotly_chart(cost_trend_chart, use_container_width=True)
            
            # ══════════════════════════════════════════════════════════════════
            # DETAILED TABLES
            # ══════════════════════════════════════════════════════════════════
            
            st.markdown('<div class="section-header">Detailed Data Tables</div>', unsafe_allow_html=True)
            
            tab1, tab2, tab3 = st.tabs(["📅 Monthly Summary", "💰 Cost Breakdown", "📋 Raw Data"])
            
            with tab1:
                # Format monthly summary for display
                display_monthly = monthly_df.copy()
                display_monthly['Revenue'] = display_monthly['Revenue'].apply(lambda x: f"${x:,.2f}")
                display_monthly['Total Costs'] = display_monthly['Total Costs'].apply(lambda x: f"${x:,.2f}")
                display_monthly['Profit'] = display_monthly['Profit'].apply(lambda x: f"${x:,.2f}")
                display_monthly['Margin %'] = display_monthly['Margin %'].apply(lambda x: f"{x:.2f}%")
                
                # Select columns to display
                display_cols = ['Month', 'Revenue', 'Total Costs', 'Profit', 'Margin %', 'Orders']
                
                st.dataframe(
                    display_monthly[display_cols],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button
                csv_monthly = monthly_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Monthly Summary (CSV)",
                    data=csv_monthly,
                    file_name="monthly_summary.csv",
                    mime="text/csv"
                )
            
            with tab2:
                # Format cost breakdown for display
                display_cost = cost_df.copy()
                display_cost['Amount'] = display_cost['Amount'].apply(lambda x: f"${x:,.2f}")
                display_cost['Percentage'] = display_cost['Percentage'].apply(lambda x: f"{x:.2f}%")
                
                st.dataframe(
                    display_cost,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Cost insights
                st.markdown("#### 💡 Key Insights")
                top_cost = cost_df.iloc[0]
                st.markdown(f"""
                - **Largest Cost Driver:** {top_cost['Cost Type']} accounts for **{top_cost['Percentage']:.1f}%** of total costs
                - **Total Operating Costs:** {format_currency(cost_df['Amount'].sum())}
                """)
            
            with tab3:
                # Show raw data with selected columns
                raw_cols = ['ORD DT', 'ACCT NM', 'ORD#', 'PU COST', 'SHIP COST', 'MAN COST', 
                           'DEL COST', 'TOTAL_COSTS', 'NET', 'PROFIT', 'STATUS', 'PU CTRY']
                available_cols = [c for c in raw_cols if c in df.columns]
                
                st.dataframe(
                    df[available_cols].sort_values('ORD DT', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download raw data
                csv_raw = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Full Data (CSV)",
                    data=csv_raw,
                    file_name="profitability_data.csv",
                    mime="text/csv"
                )
            
            # ══════════════════════════════════════════════════════════════════
            # EXECUTIVE SUMMARY
            # ══════════════════════════════════════════════════════════════════
            
            with st.expander("📊 Executive Summary", expanded=False):
                st.markdown(f"""
                ### Financial Performance Overview
                
                **Period Analyzed:** {date_min} to {date_max}
                
                **Revenue Performance:**
                - Total Revenue: **{format_currency(total_revenue)}**
                - Average Monthly Revenue: **{format_currency(total_revenue / len(monthly_df))}**
                - Number of Orders: **{total_orders:,}**
                
                **Cost Analysis:**
                - Total Operating Costs: **{format_currency(total_costs)}**
                - Primary Cost Driver: **{cost_df.iloc[0]['Cost Type']}** ({cost_df.iloc[0]['Percentage']:.1f}% of total)
                - Average Cost per Order: **{format_currency(total_costs / total_orders if total_orders > 0 else 0)}**
                
                **Profitability:**
                - Net Profit/(Loss): **{format_currency(total_profit)}**
                - Profit Margin: **{format_percentage(overall_margin)}**
                
                ---
                *Dashboard generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}*
                """)
    
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📂</div>
            <h2 style="color: #1B365D; margin-bottom: 1rem;">Welcome to the Profitability Dashboard</h2>
            <p style="color: #6B7280; font-size: 1.1rem; max-width: 600px; margin: 0 auto 2rem auto;">
                Upload your SR Technics Excel file using the sidebar to begin analyzing 
                revenue, costs, and profitability metrics.
            </p>
            <div style="background: #F3F4F6; border-radius: 12px; padding: 2rem; max-width: 500px; margin: 0 auto;">
                <h4 style="color: #1B365D; margin-bottom: 1rem;">📋 Required Data Format</h4>
                <ul style="text-align: left; color: #4B5563; line-height: 1.8;">
                    <li><strong>ORD DT</strong> - Order date</li>
                    <li><strong>PU COST</strong> - Pickup cost</li>
                    <li><strong>SHIP COST</strong> - Shipping cost</li>
                    <li><strong>MAN COST</strong> - Management cost</li>
                    <li><strong>DEL COST</strong> - Delivery cost</li>
                    <li><strong>NET</strong> - Revenue amount</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
