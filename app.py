"""
World Happiness Report 2023 - Interactive Dashboard
A Shiny for Python web application that visualizes and analyzes global happiness data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from shiny import App, reactive, render, ui, Session
from shiny.types import FileInfo
import plotly.graph_objects as go
import plotly.express as px
from shinywidgets import output_widget, render_widget
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.stats import describe
import warnings
warnings.filterwarnings('ignore')

# ==================== DATA LOADING AND PREPARATION ====================

def load_data():
    """Load and prepare the World Happiness Report dataset"""
    csv_path = Path(__file__).parent / "WHR2023.csv"
    df = pd.read_csv(csv_path)
    
    # Clean up column names
    df.columns = df.columns.str.strip()
    
    # Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    return df

# Load data
data = load_data()

# ==================== MACHINE LEARNING MODELS ====================

def perform_clustering(df, n_clusters=4, features=None):
    """Perform K-means clustering on happiness data"""
    if features is None:
        features = ['Ladder score', 'Logged GDP per capita', 'Social support', 
                   'Healthy life expectancy', 'Freedom to make life choices']
    
    # Select and prepare features
    X = df[features].fillna(df[features].mean())
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    return clusters, scaler, X_scaled

def get_cluster_names(cluster_id):
    """Generate descriptive names for clusters based on happiness levels"""
    names = {
        0: "Very Happy",
        1: "Happy", 
        2: "Moderate",
        3: "Struggling"
    }
    return names.get(cluster_id, f"Cluster {cluster_id}")

# ==================== SUMMARY STATISTICS ====================

def get_summary_stats(df):
    """Calculate summary statistics for the dataset"""
    ladder_score = df['Ladder score']
    return {
        'count': len(df),
        'mean': ladder_score.mean(),
        'median': ladder_score.median(),
        'std': ladder_score.std(),
        'min': ladder_score.min(),
        'max': ladder_score.max(),
        'q25': ladder_score.quantile(0.25),
        'q75': ladder_score.quantile(0.75)
    }

# ==================== SHINY APP ====================

app_ui = ui.page_fluid(
    # Custom styling
    ui.tags.style("""
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
        }
        .header-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        .plot-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .filter-panel {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    """),
    
    # Header
    ui.div(
        ui.h1("🌍 World Happiness Report 2023"),
        ui.p("Interactive Dashboard - Exploring Global Well-being and Clustering Analysis"),
        class_="header-section"
    ),
    
    # Main layout
    ui.navset_tab(
        # ==================== TAB 1: OVERVIEW ====================
        ui.nav_panel(
            "Overview",
            ui.row(
                ui.column(
                    12,
                    ui.h3("Summary Statistics"),
                    ui.div(
                        ui.row(
                            ui.column(
                                3,
                                ui.div(
                                    ui.div("Total Countries", class_="stat-label"),
                                    ui.div(ui.output_text("stat_count"), class_="stat-value"),
                                    class_="stat-card"
                                )
                            ),
                            ui.column(
                                3,
                                ui.div(
                                    ui.div("Mean Score", class_="stat-label"),
                                    ui.div(ui.output_text("stat_mean"), class_="stat-value"),
                                    class_="stat-card"
                                )
                            ),
                            ui.column(
                                3,
                                ui.div(
                                    ui.div("Median Score", class_="stat-label"),
                                    ui.div(ui.output_text("stat_median"), class_="stat-value"),
                                    class_="stat-card"
                                )
                            ),
                            ui.column(
                                3,
                                ui.div(
                                    ui.div("Std Deviation", class_="stat-label"),
                                    ui.div(ui.output_text("stat_std"), class_="stat-value"),
                                    class_="stat-card"
                                )
                            ),
                        )
                    )
                )
            ),
            ui.row(
                ui.column(
                    6,
                    ui.div(
                        ui.h4("Top 10 Happiest Countries"),
                        output_widget("top_countries_plot"),
                        class_="plot-container"
                    )
                ),
                ui.column(
                    6,
                    ui.div(
                        ui.h4("Distribution of Happiness Scores"),
                        output_widget("distribution_plot"),
                        class_="plot-container"
                    )
                )
            ),
        ),
        
        # ==================== TAB 2: INTERACTIVE ANALYSIS ====================
        ui.nav_panel(
            "Interactive Analysis",
            ui.row(
                ui.column(
                    3,
                    ui.div(
                        ui.h4("Filters & Controls"),
                        ui.input_slider(
                            "happiness_range",
                            "Happiness Score Range",
                            min=0, max=10, value=[3, 8], step=0.1
                        ),
                        ui.input_slider(
                            "gdp_range",
                            "GDP per Capita Range",
                            min=5, max=12, value=[7, 11.5], step=0.1
                        ),
                        ui.input_checkbox_group(
                            "factor_select",
                            "Select Factors to Display",
                            {
                                "gdp": "GDP per Capita",
                                "social": "Social Support",
                                "health": "Life Expectancy",
                                "freedom": "Freedom to Make Choices",
                                "generosity": "Generosity",
                                "corruption": "Corruption Perception"
                            },
                            selected=["gdp", "social", "health"]
                        ),
                        class_="filter-panel"
                    )
                ),
                ui.column(
                    9,
                    ui.div(
                        ui.h4("Filtered Data Analysis"),
                        output_widget("scatter_plot"),
                        class_="plot-container"
                    )
                )
            ),
            ui.row(
                ui.column(
                    12,
                    ui.div(
                        ui.h4("Correlation Heatmap"),
                        output_widget("correlation_plot"),
                        class_="plot-container"
                    )
                )
            )
        ),
        
        # ==================== TAB 3: ML CLUSTERING ====================
        ui.nav_panel(
            "Clustering Analysis",
            ui.row(
                ui.column(
                    3,
                    ui.div(
                        ui.h4("Clustering Settings"),
                        ui.input_slider(
                            "n_clusters",
                            "Number of Clusters",
                            min=2, max=6, value=4, step=1
                        ),
                        ui.input_checkbox_group(
                            "cluster_features",
                            "Features for Clustering",
                            {
                                "ladder": "Ladder Score",
                                "gdp": "GDP per Capita",
                                "social": "Social Support",
                                "health": "Life Expectancy",
                                "freedom": "Freedom"
                            },
                            selected=["ladder", "gdp", "social", "health"]
                        ),
                        class_="filter-panel"
                    )
                ),
                ui.column(
                    9,
                    ui.div(
                        ui.h4("Cluster Distribution"),
                        output_widget("cluster_3d_plot"),
                        class_="plot-container"
                    )
                )
            ),
            ui.row(
                ui.column(
                    12,
                    ui.div(
                        ui.h4("Countries by Cluster"),
                        ui.output_table("cluster_table"),
                        class_="plot-container"
                    )
                )
            )
        ),
        
        # ==================== TAB 4: DETAILED DATA ====================
        ui.nav_panel(
            "Data Explorer",
            ui.row(
                ui.column(
                    12,
                    ui.input_text("country_search", "Search Countries", placeholder="Type country name..."),
                    ui.output_table("data_table"),
                    class_="filter-panel"
                )
            )
        )
    )
)

# ==================== SERVER LOGIC ====================

def server(input, output, session: Session):
    
    # ==================== COMPUTED REACTIVE VALUES ====================
    
    @reactive.Calc
    def filtered_data():
        """Filter data based on user inputs"""
        df = data.copy()
        
        # Apply happiness range filter
        df = df[(df['Ladder score'] >= input.happiness_range()[0]) & 
                (df['Ladder score'] <= input.happiness_range()[1])]
        
        # Apply GDP range filter
        df = df[(df['Logged GDP per capita'] >= input.gdp_range()[0]) & 
                (df['Logged GDP per capita'] <= input.gdp_range()[1])]
        
        return df
    
    @reactive.Calc
    def clustered_data():
        """Perform clustering on filtered data"""
        df = filtered_data().copy()
        
        # Map selected features
        feature_map = {
            "ladder": "Ladder score",
            "gdp": "Logged GDP per capita",
            "social": "Social support",
            "health": "Healthy life expectancy",
            "freedom": "Freedom to make life choices"
        }
        
        selected_features = [feature_map[f] for f in input.cluster_features() 
                            if f in feature_map]
        
        if not selected_features:
            selected_features = ["Ladder score"]
        
        clusters, scaler, X_scaled = perform_clustering(
            df, 
            n_clusters=input.n_clusters(),
            features=selected_features
        )
        
        df['Cluster'] = clusters
        df['Cluster_Name'] = df['Cluster'].apply(get_cluster_names)
        
        return df, X_scaled, selected_features
    
    @reactive.Calc
    def searched_data():
        """Filter data based on country search"""
        df = data.copy()
        
        if input.country_search():
            search_term = input.country_search().lower()
            df = df[df['Country name'].str.lower().str.contains(search_term, na=False)]
        
        return df.head(20)
    
    # ==================== SUMMARY STATISTICS ====================
    
    @output
    @render.text
    def stat_count():
        stats = get_summary_stats(data)
        return str(stats['count'])
    
    @output
    @render.text
    def stat_mean():
        stats = get_summary_stats(data)
        return f"{stats['mean']:.2f}"
    
    @output
    @render.text
    def stat_median():
        stats = get_summary_stats(data)
        return f"{stats['median']:.2f}"
    
    @output
    @render.text
    def stat_std():
        stats = get_summary_stats(data)
        return f"{stats['std']:.2f}"
    
    # ==================== OVERVIEW TAB PLOTS ====================
    
    @output
    @render_widget
    def top_countries_plot():
        """Top 10 happiest countries"""
        df = data.nlargest(10, 'Ladder score')[['Country name', 'Ladder score']].sort_values('Ladder score')
        
        fig = go.Figure(data=[
            go.Bar(x=df['Ladder score'], y=df['Country name'], orientation='h',
                   marker=dict(color=df['Ladder score'], colorscale='Viridis',
                             showscale=False))
        ])
        
        fig.update_layout(
            title="Top 10 Happiest Countries",
            xaxis_title="Happiness Score",
            yaxis_title="Country",
            height=400,
            showlegend=False,
            hovermode='closest'
        )
        return fig
    
    @output
    @render_widget
    def distribution_plot():
        """Distribution of happiness scores"""
        fig = go.Figure(data=[
            go.Histogram(x=data['Ladder score'], nbinsx=30,
                        marker=dict(color='rgba(102, 126, 234, 0.7)'))
        ])
        
        fig.update_layout(
            title="Distribution of Happiness Scores",
            xaxis_title="Ladder Score",
            yaxis_title="Frequency",
            height=400,
            showlegend=False
        )
        return fig
    
    # ==================== INTERACTIVE ANALYSIS TAB ====================
    
    @output
    @render_widget
    def scatter_plot():
        """Scatter plot with filtered data"""
        df = filtered_data()
        
        # Build trace for each selected factor
        fig = go.Figure()
        
        if "gdp" in input.factor_select():
            fig.add_trace(go.Scatter(
                x=df['Ladder score'], y=df['Logged GDP per capita'],
                mode='markers', name='GDP vs Happiness',
                marker=dict(size=8, color='blue', opacity=0.6)
            ))
        
        if "social" in input.factor_select():
            fig.add_trace(go.Scatter(
                x=df['Ladder score'], y=df['Social support']*10,
                mode='markers', name='Social Support vs Happiness',
                marker=dict(size=8, color='green', opacity=0.6)
            ))
        
        if "health" in input.factor_select():
            fig.add_trace(go.Scatter(
                x=df['Ladder score'], y=df['Healthy life expectancy']/10,
                mode='markers', name='Life Expectancy vs Happiness',
                marker=dict(size=8, color='red', opacity=0.6)
            ))
        
        fig.update_layout(
            title="Filtered Analysis - Factors vs Happiness Score",
            xaxis_title="Happiness Score",
            yaxis_title="Factor Value",
            height=500,
            hovermode='closest'
        )
        return fig
    
    @output
    @render_widget
    def correlation_plot():
        """Correlation heatmap of key features"""
        cols = ['Ladder score', 'Logged GDP per capita', 'Social support',
                'Healthy life expectancy', 'Freedom to make life choices',
                'Generosity', 'Perceptions of corruption']
        
        corr_matrix = data[cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=cols,
            y=cols,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text:.2f}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Correlation Heatmap of Happiness Factors",
            height=600,
            width=900
        )
        return fig
    
    # ==================== CLUSTERING TAB ====================
    
    @output
    @render_widget
    def cluster_3d_plot():
        """3D scatter plot of clusters"""
        df, X_scaled, features = clustered_data()
        
        # Create 3D plot
        fig = go.Figure(data=[
            go.Scatter3d(
                x=X_scaled[:, 0],
                y=X_scaled[:, 1],
                z=X_scaled[:, 2] if X_scaled.shape[1] > 2 else X_scaled[:, 0],
                mode='markers',
                marker=dict(
                    size=6,
                    color=df['Cluster'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Cluster")
                ),
                text=df['Country name'],
                hovertemplate='<b>%{text}</b><br>Cluster: %{marker.color}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f"K-Means Clustering (k={input.n_clusters()})",
            scene=dict(
                xaxis_title="Feature 1 (scaled)",
                yaxis_title="Feature 2 (scaled)",
                zaxis_title="Feature 3 (scaled)"
            ),
            height=600,
            hovermode='closest'
        )
        return fig
    
    @output
    @render.table
    def cluster_table():
        """Table showing countries by cluster"""
        df, _, _ = clustered_data()
        
        # Create summary by cluster
        cluster_summary = []
        for cluster in sorted(df['Cluster'].unique()):
            cluster_df = df[df['Cluster'] == cluster]
            cluster_summary.append({
                'Cluster': get_cluster_names(cluster),
                'Count': len(cluster_df),
                'Avg Happiness': f"{cluster_df['Ladder score'].mean():.2f}",
                'Countries': ', '.join(cluster_df.nlargest(3, 'Ladder score')['Country name'].values)
            })
        
        return pd.DataFrame(cluster_summary)
    
    # ==================== DATA EXPLORER TAB ====================
    
    @output
    @render.table
    def data_table():
        """Full data table with search"""
        cols = ['Country name', 'Ladder score', 'Logged GDP per capita', 
                'Social support', 'Healthy life expectancy', 'Freedom to make life choices']
        return searched_data()[cols]

# Create and run the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
