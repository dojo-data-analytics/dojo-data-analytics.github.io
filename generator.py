import plotly.express as px
import pandas as pd
import numpy as np

np.random.seed(42)
date = pd.date_range("2026-01-01", periods=90, freq="D")
follower = np.cumsum(np.random.randint(-5, 25, size=90)) + 1200
like_medi = np.random.randint(40, 180, size=90)

df = pd.DataFrame({
    "Data": date,
    "Follower": follower,
    "Like Medi": like_medi
})

fig = px.line(
    df,
    x="Data",
    y=["Follower", "Like Medi"],
    title="Dashboard Interattiva - Metriche Social",
    markers=True,
    template="plotly_white"
)

fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=[
            dict(count=7, label="7 Giorni", step="day", stepmode="backward"),
            dict(count=1, label="1 Mese", step="month", stepmode="backward"),
            dict(step="all", label="Tutto lo storico")
        ]
    )
)
fig.update_layout(hovermode="x unified")

fig.write_html(
    "index.html",
    include_plotlyjs="cdn",        
    full_html=True,                
    config={"responsive": True}    
)
print("File index.html generato con successo!")