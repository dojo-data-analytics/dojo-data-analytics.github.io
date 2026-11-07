import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================================================
# CONFIGURAZIONE PARTE 1: INPUT QUALITATIVI (RADAR CHART)
# ==============================================================================
FATTORI_INPUT = [
    "Gesticolazione",
    "Postura",
    "Intonazione",
    "Tone of voice",
    "Ritmo parlato",
    "Gesti manipolatori",
    "Fluidità verbale",
    "Capacità di sintesi",
    "Coerenza",
    "Logica del ragionamento",
    "Oggettificazione dei numeri",
    "Uso di parole/verbi oggettificanti",
    "Demographic dress",
    "Tenere l'avversario nel proprio campo",
    "Tempo parlato",
    "Interruzioni ricevute",
    "Interruzioni perpetrate",
    "Lunghezza periodi",
    "Negazioni oppositive usate",
    "Abbassamenti dello sguardo",
]

FILE_INPUT = {
    "Social": "./data/Test1l/Social.txt",
    "Dibattito": "./data/Test1l/Dibattito.txt",
    "Gazebo": "./data/Test1l/Gazebo.txt",
}

# ==============================================================================
# CONFIGURAZIONE PARTE 2: OUTPUT VS STANDARD (BOLLE + BARRE BENCHMARK)
# ==============================================================================
VARIABILI_OUTPUT = {
    "Metriche Social": {
        "file": "./data/ConfronTable/output_social.txt",
        "etichette": [
            "Like",
            "Tempo visualizzazione",
            "Commenti",
            "Visite al profilo",
            "Link cliccati",
            "Follower",
            "Repost",
            "Condivisioni",
            "Salvataggi",
        ],
    },
    "Contatto Pubblico": {
        "file": "./data/ConfronTable/output_contatto.txt",
        "etichette": [
            "Presenti manifestazione",
            "Contatti raccolti",
            "Persone parlate",
            "Gadget dati via",
            "Donazioni effettuate",
            "Soldi da merch",
            "ROI",
            "Merch venduti",
            "Volantini consegnati",
        ],
    },
}


# 1. Caricamento dati Input (Radar)
def carica_input(percorso):
  dati = np.loadtxt(percorso)
  c, p = dati[:, 0], dati[:, 1]
  ov = np.sum(c * p) / np.sum(p)
  return c.tolist(), p.tolist(), round(float(ov), 2)


dati_input = {}
cat_input = list(FILE_INPUT.keys())
ov_input = []

for nome, fpath in FILE_INPUT.items():
  c, p, ov = carica_input(fpath)
  dati_input[nome] = {"conteggi": c, "ponderazioni": p, "overall": ov}
  ov_input.append(ov)


# 2. Caricamento dati Output (Confronto vs Standard)
def carica_output(percorso):
  dati = np.loadtxt(percorso)
  conteggi = dati[:, 0]
  standard = dati[:, 1]
  confronto = (conteggi / standard) * 100.0
  overall = np.mean(confronto)
  return (
      conteggi.tolist(),
      standard.tolist(),
      confronto.tolist(),
      round(float(overall), 2),
  )


dati_output = {}
for nome_gruppo, info in VARIABILI_OUTPUT.items():
  c, s, conf, ov = carica_output(info["file"])
  dati_output[nome_gruppo] = {
      "etichette": info["etichette"],
      "conteggi": c,
      "standard": s,
      "confronto": [round(x, 2) for x in conf],
      "overall": ov,
  }

# ==============================================================================
# COSTRUZIONE GRAFICO 1: RADAR CHART (INPUT)
# ==============================================================================
r_chiuso = ov_input + [ov_input[0]]
theta_chiuso = cat_input + [cat_input[0]]

fig_radar = go.Figure(
    data=go.Scatterpolar(
        r=r_chiuso,
        theta=theta_chiuso,
        fill="toself",
        fillcolor="rgba(37, 99, 235, 0.25)",
        line=dict(color="rgb(37, 99, 235)", width=3),
        marker=dict(size=10, color="rgb(29, 78, 216)"),
        hovertemplate="<b>%{theta}</b><br>Overall: %{r:.2f} / 100<extra></extra>",
    )
)
fig_radar.update_layout(
    title=dict(
        text="Risultante Qualitativa della Comunicazione (Input)",
        x=0.5,
        font=dict(size=18),
    ),
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100]),
        angularaxis=dict(
            tickfont=dict(size=14, weight="bold"),
            direction="clockwise",
            rotation=90,
        ),
    ),
    showlegend=False,
    margin=dict(l=50, r=50, t=70, b=50),
    template="plotly_white",
)
div_radar = fig_radar.to_html(
    full_html=False,
    include_plotlyjs="cdn",
    div_id="radar-chart",
    config={"responsive": True},
)

# ==============================================================================
# COSTRUZIONE GRAFICO 2A: BOLLE DI GRANDEZZA PROPORZIONALE (BLU 100% VS ROSSO)
# ==============================================================================
gruppi_out = list(dati_output.keys())
ov_out_vals = [dati_output[g]["overall"] for g in gruppi_out]

# Dimensione base bolla Standard (100%) = 65px; la bolla Candidato scala con la radice quadrata (area proporzionale) o linearmente
base_size = 65
size_candidato = [
    max(18, base_size * (val / 100.0)) for val in ov_out_vals
]  # Scala lineare sul diametro come richiesto dai capi

fig_bolle = go.Figure()

# Bolla Blu a Sinistra (Standard = 100%)
fig_bolle.add_trace(
    go.Scatter(
        x=[0, 0],
        y=gruppi_out,
        mode="markers+text",
        name="Standard (100%)",
        marker=dict(
            size=[base_size, base_size],
            color="rgba(37, 99, 235, 0.85)",
            line=dict(width=2, color="#1d4ed8"),
        ),
        text=["100%", "100%"],
        textfont=dict(color="white", size=13, weight="bold"),
        textposition="middle center",
        hovertemplate="<b>%{y} - Standard</b><br>Riferimento: 100%<extra></extra>",
    )
)

# Bolla Rossa a Destra (Candidato = Overall %)
fig_bolle.add_trace(
    go.Scatter(
        x=[1, 1],
        y=gruppi_out,
        mode="markers+text",
        name="Candidato (Overall %)",
        marker=dict(
            size=size_candidato,
            color="rgba(220, 38, 38, 0.85)",
            line=dict(width=2, color="#b91c1c"),
        ),
        text=[f"{v:.1f}%" for v in ov_out_vals],
        textfont=dict(color="white", size=13, weight="bold"),
        textposition="middle center",
        hovertemplate="<b>%{y} - Candidato</b><br>Efficacia Overall: %{text}<extra></extra>",
    )
)

fig_bolle.update_layout(
    title=dict(
        text="Confronto Grandezza Overall: Standard (Blu, sx) vs Candidato (Rosso, dx)",
        x=0.5,
        font=dict(size=16),
    ),
    xaxis=dict(
        tickvals=[0, 1],
        ticktext=["<b>STANDARD (100%)</b>", "<b>CANDIDATO (OVERALL %)</b>"],
        range=[-0.6, 1.6],
        showgrid=False,
        zeroline=False,
    ),
    yaxis=dict(range=[-0.6, 1.6], tickfont=dict(size=14, weight="bold")),
    height=340,
    margin=dict(l=140, r=40, t=60, b=40),
    template="plotly_white",
    showlegend=True,
)
div_bolle = fig_bolle.to_html(
    full_html=False,
    include_plotlyjs=False,
    div_id="bubble-chart",
    config={"responsive": True},
)

# ==============================================================================
# COSTRUZIONE GRAFICO 2B: BARRE DI DETTAGLIO CON LINEA BENCHMARK 100%
# ==============================================================================
primo_gruppo = "Metriche Social"
etichette_init = dati_output[primo_gruppo]["etichette"]
conf_init = dati_output[primo_gruppo]["confronto"]
colori_init = ["#dc2626" if v >= 100 else "#64748b" for v in conf_init]

fig_barre = go.Figure(
    go.Bar(
        x=conf_init,
        y=etichette_init,
        orientation="h",
        marker_color=colori_init,
        text=[f"{v:.1f}%" for v in conf_init],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Confronto vs Standard: %{x:.2f}%<extra></extra>",
    )
)
fig_barre.add_vline(
    x=100,
    line_width=2,
    line_dash="dash",
    line_color="#2563eb",
    annotation_text="Standard (100%)",
    annotation_position="top right",
)
fig_barre.update_layout(
    title=dict(
        text="Dettaglio Variabili (% rispetto allo Standard = 100%)",
        x=0.5,
        font=dict(size=16),
    ),
    xaxis=dict(
        title="Efficacia Percentuale (%)", range=[0, max(250, max(conf_init) * 1.2)]
    ),
    yaxis=dict(autorange="reversed"),
    height=380,
    margin=dict(l=160, r=60, t=50, b=40),
    template="plotly_white",
)
div_barre = fig_barre.to_html(
    full_html=False,
    include_plotlyjs=False,
    div_id="bar-chart",
    config={"responsive": True},
)

# ==============================================================================
# GENERAZIONE PAGINA UNIFICATA (index.html)
# ==============================================================================
html_finale = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Analisi Comunicazione - Input & Output</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; background: #f8fafc; color: #1e293b; }}
        header {{ background: #0f172a; color: white; padding: 14px 28px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
        header h1 {{ margin: 0; font-size: 1.25rem; }}
        .nav-pills {{ display: flex; gap: 10px; }}
        .nav-btn {{ padding: 9px 18px; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #cbd5e1; cursor: pointer; font-weight: 600; font-size: 0.9rem; }}
        .nav-btn.active {{ background: #2563eb; color: white; border-color: #3b82f6; }}
        .page {{ display: none; padding: 24px; max-width: 1440px; margin: 0 auto; }}
        .page.active {{ display: block; }}
        .layout {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 24px; }}
        @media (max-width: 980px) {{ .layout {{ grid-template-columns: 1fr; }} }}
        .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07); margin-bottom: 20px; }}
        .kpi-row {{ display: flex; justify-content: space-around; margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0; }}
        .kpi {{ text-align: center; }}
        .kpi span {{ display: block; font-size: 0.8rem; color: #64748b; text-transform: uppercase; }}
        .kpi strong {{ font-size: 1.4rem; color: #2563eb; }}
        .kpi strong.red {{ color: #dc2626; }}
        .tabs {{ display: flex; gap: 8px; margin-bottom: 14px; }}
        .tab-btn {{ flex: 1; padding: 9px; cursor: pointer; border: 1px solid #cbd5e1; background: #f1f5f9; border-radius: 8px; font-weight: 600; color: #334155; }}
        .tab-btn.active {{ background: #2563eb; color: white; border-color: #2563eb; }}
        .table-wrap {{ max-height: 520px; overflow-y: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
        th, td {{ padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
        th {{ position: sticky; top: 0; background: #f8fafc; font-weight: 600; }}
        input[type="number"] {{ width: 78px; padding: 5px 8px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem; text-align: right; }}
        .btn-reset {{ margin-top: 12px; padding: 8px 14px; background: #e2e8f0; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; color: #475569; }}
    </style>
</head>
<body>

<header>
    <h1>Dojo Data Analytics — Dashboard Comunicazione</h1>
    <div class="nav-pills">
        <button class="nav-btn active" onclick="cambiaPagina('page-input', this)">1. Analisi Qualitativa (Radar Input)</button>
        <button class="nav-btn" onclick="cambiaPagina('page-output', this)">2. Efficacia Azioni vs Standard (Output)</button>
    </div>
</header>

<!-- ==================== PAGINA 1: RADAR INPUT ==================== -->
<div id="page-input" class="page active">
    <div class="layout">
        <div class="card">
            {div_radar}
            <div class="kpi-row">
                <div class="kpi"><span>Social</span><strong id="kpi-in-Social">0</strong></div>
                <div class="kpi"><span>Dibattito</span><strong id="kpi-in-Dibattito">0</strong></div>
                <div class="kpi"><span>Gazebo</span><strong id="kpi-in-Gazebo">0</strong></div>
            </div>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">Simulatore Conteggi Qualitativi (Input)</h3>
            <div class="tabs">
                <button class="tab-btn active" onclick="cambiaSchedaInput('Social', this)">Social</button>
                <button class="tab-btn" onclick="cambiaSchedaInput('Dibattito', this)">Dibattito</button>
                <button class="tab-btn" onclick="cambiaSchedaInput('Gazebo', this)">Gazebo</button>
            </div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>Fattore</th><th>Conteggio</th><th>Ponderazione</th><th>Risultato</th></tr></thead>
                    <tbody id="tbody-input"></tbody>
                </table>
            </div>
            <button class="btn-reset" onclick="resetInput()">Ripristina valori originali</button>
        </div>
    </div>
</div>

<!-- ==================== PAGINA 2: OUTPUT VS STANDARD ==================== -->
<div id="page-output" class="page">
    <div class="layout">
        <div>
            <div class="card">
                {div_bolle}
                <div class="kpi-row">
                    <div class="kpi"><span>Standard Riferimento</span><strong>100.00%</strong></div>
                    <div class="kpi"><span>Overall Metriche Social</span><strong class="red" id="kpi-out-Metriche Social">0%</strong></div>
                    <div class="kpi"><span>Overall Contatto Pubblico</span><strong class="red" id="kpi-out-Contatto Pubblico">0%</strong></div>
                </div>
            </div>
            <div class="card">
                {div_barre}
            </div>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">Simulatore Output Candidato vs Standard</h3>
            <p style="font-size:0.85rem; color:#64748b; margin-top:-6px;">
                Modifica il <b>Conteggio</b> o lo <b>Standard</b>: il diametro della bolla rossa e il grafico a barre si aggiornano in tempo reale.
            </p>
            <div class="tabs">
                <button class="tab-btn active" onclick="cambiaSchedaOutput('Metriche Social', this)">Metriche Social</button>
                <button class="tab-btn" onclick="cambiaSchedaOutput('Contatto Pubblico', this)">Contatto Pubblico</button>
            </div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>Variabile</th><th>Conteggio</th><th>Standard</th><th>Confronto (%)</th></tr></thead>
                    <tbody id="tbody-output"></tbody>
                </table>
            </div>
            <button class="btn-reset" onclick="resetOutput()">Ripristina valori originali</button>
        </div>
    </div>
</div>

<script>
    // --- STATO PAGINA 1 (INPUT) ---
    const origInput = {json.dumps(dati_input)};
    let currInput = JSON.parse(JSON.stringify(origInput));
    const fattoriInput = {json.dumps(FATTORI_INPUT)};
    let schedaInput = 'Social';

    // --- STATO PAGINA 2 (OUTPUT) ---
    const origOutput = {json.dumps(dati_output)};
    let currOutput = JSON.parse(JSON.stringify(origOutput));
    let schedaOutput = 'Metriche Social';

    function cambiaPagina(idPagina, btn) {{
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(idPagina).classList.add('active');
        btn.classList.add('active');
        window.dispatchEvent(new Event('resize'));
    }}

    // ================= LOGICA PAGINA 1 (RADAR) =================
    function calcolaOverallInput(cat) {{
        const c = currInput[cat].conteggi, p = currInput[cat].ponderazioni;
        let sr = 0, sp = 0;
        for (let i = 0; i < c.length; i++) {{ sr += c[i] * p[i]; sp += p[i]; }}
        return sr / sp;
    }}

    function aggiornaRadar() {{
        const cats = ['Social', 'Dibattito', 'Gazebo'];
        const ovs = cats.map(c => {{
            const v = calcolaOverallInput(c);
            document.getElementById('kpi-in-' + c).textContent = v.toFixed(2);
            return Number(v.toFixed(2));
        }});
        Plotly.restyle('radar-chart', {{ r: [[...ovs, ovs[0]]] }});
    }}

    function renderTabellaInput() {{
        const tbody = document.getElementById('tbody-input');
        tbody.innerHTML = '';
        const c = currInput[schedaInput].conteggi, p = currInput[schedaInput].ponderazioni;
        fattoriInput.forEach((f, i) => {{
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${{f}}</td>
                <td><input type="number" value="${{c[i]}}" oninput="modInput(${{i}}, this.value)"></td>
                <td>${{p[i].toFixed(2)}}</td>
                <td id="ris-in-${{i}}">${{(c[i]*p[i]).toFixed(2)}}</td>`;
            tbody.appendChild(tr);
        }});
    }}

    function modInput(i, val) {{
        const v = parseFloat(val) || 0;
        currInput[schedaInput].conteggi[i] = v;
        document.getElementById('ris-in-' + i).textContent = (v * currInput[schedaInput].ponderazioni[i]).toFixed(2);
        aggiornaRadar();
    }}

    function cambiaSchedaInput(s, btn) {{
        schedaInput = s;
        btn.parentElement.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderTabellaInput();
    }}

    function resetInput() {{
        currInput = JSON.parse(JSON.stringify(origInput));
        renderTabellaInput();
        aggiornaRadar();
    }}

    // ================= LOGICA PAGINA 2 (OUTPUT) =================
    function calcolaOverallOutput(gruppo) {{
        const c = currOutput[gruppo].conteggi, s = currOutput[gruppo].standard;
        let sommaPerc = 0;
        for (let i = 0; i < c.length; i++) {{
            const perc = s[i] > 0 ? (c[i] / s[i]) * 100 : 0;
            currOutput[gruppo].confronto[i] = perc;
            sommaPerc += perc;
        }}
        return sommaPerc / c.length;
    }}

    function aggiornaGraficiOutput() {{
        const gruppi = ['Metriche Social', 'Contatto Pubblico'];
        const ovs = gruppi.map(g => {{
            const v = calcolaOverallOutput(g);
            document.getElementById('kpi-out-' + g).textContent = v.toFixed(2) + '%';
            return v;
        }});

        // Aggiorna dimensione e testo della bolla rossa (trace 1)
        const baseSize = 65;
        const nuoveSize = ovs.map(v => Math.max(18, Math.min(160, baseSize * (v / 100.0))));
        const nuoviTesti = ovs.map(v => v.toFixed(1) + '%');
        Plotly.restyle('bubble-chart', {{ 'marker.size': [nuoveSize], text: [nuoviTesti] }}, [1]);

        // Aggiorna grafico a barre per la scheda selezionata
        const conf = currOutput[schedaOutput].confronto;
        const etichette = currOutput[schedaOutput].etichette;
        const colori = conf.map(v => v >= 100 ? '#dc2626' : '#64748b');
        const testiBarre = conf.map(v => v.toFixed(1) + '%');
        const maxRange = Math.max(250, Math.max(...conf) * 1.2);

        Plotly.react('bar-chart', [{{
            type: 'bar', orientation: 'h',
            x: conf, y: etichette,
            marker: {{ color: colori }},
            text: testiBarre, textposition: 'outside'
        }}], {{
            title: {{ text: 'Dettaglio ' + schedaOutput + ' (% rispetto allo Standard = 100%)', x: 0.5, font: {{ size: 16 }} }},
            xaxis: {{ title: 'Efficacia Percentuale (%)', range: [0, maxRange] }},
            yaxis: {{ autorange: 'reversed' }},
            height: 380, margin: {{ l: 160, r: 60, t: 50, b: 40 }},
            template: 'plotly_white',
            shapes: [{{ type: 'line', x0: 100, x1: 100, y0: -0.5, y1: etichette.length - 0.5, line: {{ color: '#2563eb', width: 2, dash: 'dash' }} }}]
        }});
    }}

    function renderTabellaOutput() {{
        const tbody = document.getElementById('tbody-output');
        tbody.innerHTML = '';
        const g = currOutput[schedaOutput];
        g.etichette.forEach((nome, i) => {{
            const perc = g.standard[i] > 0 ? (g.conteggi[i] / g.standard[i]) * 100 : 0;
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${{nome}}</td>
                <td><input type="number" value="${{g.conteggi[i]}}" oninput="modOutput(${{i}}, 'c', this.value)"></td>
                <td><input type="number" value="${{g.standard[i]}}" oninput="modOutput(${{i}}, 's', this.value)"></td>
                <td id="conf-out-${{i}}"><b>${{perc.toFixed(2)}}%</b></td>`;
            tbody.appendChild(tr);
        }});
    }}

    function modOutput(i, tipo, val) {{
        const v = parseFloat(val) || 0;
        if (tipo === 'c') currOutput[schedaOutput].conteggi[i] = v;
        else currOutput[schedaOutput].standard[i] = v;

        const c = currOutput[schedaOutput].conteggi[i];
        const s = currOutput[schedaOutput].standard[i];
        const perc = s > 0 ? (c / s) * 100 : 0;
        document.getElementById('conf-out-' + i).innerHTML = '<b>' + perc.toFixed(2) + '%</b>';
        aggiornaGraficiOutput();
    }}

    function cambiaSchedaOutput(s, btn) {{
        schedaOutput = s;
        btn.parentElement.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderTabellaOutput();
        aggiornaGraficiOutput();
    }}

    function resetOutput() {{
        currOutput = JSON.parse(JSON.stringify(origOutput));
        renderTabellaOutput();
        aggiornaGraficiOutput();
    }}

    // Avvio iniziale
    renderTabellaInput();
    aggiornaRadar();
    renderTabellaOutput();
    aggiornaGraficiOutput();
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
  f.write(html_finale)

print("Dashboard completa generata in index.html!")