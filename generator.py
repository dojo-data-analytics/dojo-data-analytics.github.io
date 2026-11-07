import json
import numpy as np
import plotly.graph_objects as go

# Nomi dei 20 fattori nell'ordine esatto della tabella Excel
FATTORI = [
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

FILE_DATI = {
    "Social": "./data/Test1l/Social.txt",
    "Dibattito": "./data/Test1l/Dibattito.txt",
    "Gazebo": "./data/Test1l/Gazebo.txt",
}


def carica_e_calcola(percorso_file):
  """Legge un file .txt con 2 colonne (Conteggio, Ponderazione) e calcola l'Overall."""
  dati = np.loadtxt(percorso_file)
  conteggi = dati[:, 0]
  ponderazioni = dati[:, 1]
  overall = np.sum(conteggi * ponderazioni) / np.sum(ponderazioni)
  return conteggi.tolist(), ponderazioni.tolist(), float(overall)


# 1. Estrazione dati dai 3 file .txt
struttura_dati = {}
categorie = list(FILE_DATI.keys())
valori_overall = []

for nome_cat, nome_file in FILE_DATI.items():
  c, p, ov = carica_e_calcola(nome_file)
  struttura_dati[nome_cat] = {
      "conteggi": c,
      "ponderazioni": p,
      "overall": round(ov, 2),
  }
  valori_overall.append(round(ov, 2))

# Per chiudere il triangolo nel Radar Chart di Plotly, ripetiamo il primo vertice alla fine
r_chiuso = valori_overall + [valori_overall[0]]
theta_chiuso = categorie + [categorie[0]]

# 2. Creazione del grafico a ragnatela (Radar Chart) con Plotly
fig = go.Figure(
    data=go.Scatterpolar(
        r=r_chiuso,
        theta=theta_chiuso,
        fill="toself",
        fillcolor="rgba(37, 99, 235, 0.25)",
        line=dict(color="rgb(37, 99, 235)", width=3),
        marker=dict(size=10, color="rgb(29, 78, 216)"),
        name="Overall Comunicazione",
        hovertemplate="<b>%{theta}</b><br>Overall: %{r:.2f} / 100<extra></extra>",
    )
)

fig.update_layout(
    title=dict(
        text="Risultante Qualitativa della Comunicazione (Overall)",
        x=0.5,
        font=dict(size=20),
    ),
    polar=dict(
        radialaxis=dict(
            visible=True, range=[0, 100], tickfont=dict(size=12), ticksuffix=""
        ),
        angularaxis=dict(
            tickfont=dict(size=15, weight="bold"),
            direction="clockwise",
            rotation=90,  # Mette il primo vertice ("Social") esattamente in alto
        ),
    ),
    showlegend=False,
    margin=dict(l=60, r=60, t=80, b=60),
    template="plotly_white",
)

# 3. Esportazione del grafico e iniezione dei controlli in tempo reale in index.html
div_plotly = fig.to_html(
    full_html=False,
    include_plotlyjs="cdn",
    div_id="radar-chart",
    config={"responsive": True},
)

dati_json = json.dumps(struttura_dati)
fattori_json = json.dumps(FATTORI)

html_completo = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Comunicazione - Radar Interattivo</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0; padding: 24px;
            background: #f8fafc; color: #1e293b;
        }}
        .layout {{
            display: grid;
            grid-template-columns: 1fr 1.1fr;
            gap: 24px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        @media (max-width: 960px) {{
            .layout {{ grid-template-columns: 1fr; }}
        }}
        .card {{
            background: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07);
        }}
        .kpi-row {{
            display: flex;
            justify-content: space-around;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e2e8f0;
        }}
        .kpi {{ text-align: center; }}
        .kpi span {{ display: block; font-size: 0.85rem; color: #64748b; text-transform: uppercase; }}
        .kpi strong {{ font-size: 1.5rem; color: #2563eb; }}
        .tabs {{ display: flex; gap: 8px; margin-bottom: 16px; }}
        .tab-btn {{
            flex: 1; padding: 10px; cursor: pointer;
            border: 1px solid #cbd5e1; background: #f1f5f9;
            border-radius: 8px; font-weight: 600; color: #334155;
        }}
        .tab-btn.active {{ background: #2563eb; color: white; border-color: #2563eb; }}
        .table-wrap {{ max-height: 520px; overflow-y: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        th, td {{ padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
        th {{ position: sticky; top: 0; background: #f8fafc; font-weight: 600; }}
        input[type="number"] {{
            width: 72px; padding: 5px 8px;
            border: 1px solid #cbd5e1; border-radius: 6px;
            font-size: 0.9rem; text-align: right;
        }}
        .btn-reset {{
            margin-top: 12px; padding: 8px 14px;
            background: #e2e8f0; border: none; border-radius: 6px;
            cursor: pointer; font-weight: 600; color: #475569;
        }}
        .btn-reset:hover {{ background: #cbd5e1; }}
    </style>
</head>
<body>
    <div class="layout">
        <!-- Colonna Sinistra: Grafico a Ragnatela Plotly -->
        <div class="card">
            {div_plotly}
            <div class="kpi-row">
                <div class="kpi"><span>Social</span><strong id="kpi-Social">0</strong></div>
                <div class="kpi"><span>Dibattito</span><strong id="kpi-Dibattito">0</strong></div>
                <div class="kpi"><span>Gazebo</span><strong id="kpi-Gazebo">0</strong></div>
            </div>
        </div>

        <!-- Colonna Destra: Modifica Conteggi in Tempo Reale -->
        <div class="card">
            <h3 style="margin-top:0;">Simulatore Conteggi in Tempo Reale</h3>
            <p style="font-size:0.85rem; color:#64748b; margin-top:-6px;">
                Modifica qualsiasi valore di <b>Conteggio</b> (0-100) per aggiornare istantaneamente la media ponderata e il grafico.
            </p>
            <div class="tabs">
                <button class="tab-btn active" onclick="cambiaScheda('Social')">Social</button>
                <button class="tab-btn" onclick="cambiaScheda('Dibattito')">Dibattito</button>
                <button class="tab-btn" onclick="cambiaScheda('Gazebo')">Gazebo</button>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Fattore da studiare</th>
                            <th>Conteggio</th>
                            <th>Ponderazione</th>
                            <th>Risultato</th>
                        </tr>
                    </thead>
                    <tbody id="tabella-fattori"></tbody>
                </table>
            </div>
            <button class="btn-reset" onclick="ripristinaDati()">Ripristina valori originali (.txt)</button>
        </div>
    </div>

    <script>
        const datiOriginali = {dati_json};
        let datiCorrenti = JSON.parse(JSON.stringify(datiOriginali));
        const fattori = {fattori_json};
        let schedaAttiva = 'Social';

        function calcolaOverall(cat) {{
            const c = datiCorrenti[cat].conteggi;
            const p = datiCorrenti[cat].ponderazioni;
            let sommaRisultati = 0, sommaPesi = 0;
            for (let i = 0; i < c.length; i++) {{
                sommaRisultati += c[i] * p[i];
                sommaPesi += p[i];
            }}
            return sommaRisultati / sommaPesi;
        }}

        function aggiornaGrafico() {{
            const categorie = ['Social', 'Dibattito', 'Gazebo'];
            const nuoviOverall = categorie.map(cat => {{
                const ov = calcolaOverall(cat);
                document.getElementById('kpi-' + cat).textContent = ov.toFixed(2);
                return Number(ov.toFixed(2));
            }});
            // Chiude il poligono ripetendo il primo valore
            const rChiuso = [...nuoviOverall, nuoviOverall[0]];
            Plotly.restyle('radar-chart', {{ r: [rChiuso] }});
        }}

        function renderTabella() {{
            const tbody = document.getElementById('tabella-fattori');
            tbody.innerHTML = '';
            const c = datiCorrenti[schedaAttiva].conteggi;
            const p = datiCorrenti[schedaAttiva].ponderazioni;

            fattori.forEach((nome, idx) => {{
                const risultato = (c[idx] * p[idx]).toFixed(2);
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${{nome}}</td>
                    <td>
                        <input type="number" min="0" max="100" step="1" value="${{c[idx]}}"
                               oninput="modificaConteggio(${{idx}}, this.value)">
                    </td>
                    <td>${{p[idx].toFixed(2)}}</td>
                    <td id="ris-${{idx}}">${{risultato}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function modificaConteggio(indice, nuovoValore) {{
            const val = parseFloat(nuovoValore) || 0;
            datiCorrenti[schedaAttiva].conteggi[indice] = val;
            const peso = datiCorrenti[schedaAttiva].ponderazioni[indice];
            document.getElementById('ris-' + indice).textContent = (val * peso).toFixed(2);
            aggiornaGrafico();
        }}

        function cambiaScheda(nuovaScheda) {{
            schedaAttiva = nuovaScheda;
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.textContent === nuovaScheda);
            }});
            renderTabella();
        }}

        function ripristinaDati() {{
            datiCorrenti = JSON.parse(JSON.stringify(datiOriginali));
            renderTabella();
            aggiornaGrafico();
        }}

        // Inizializzazione all'apertura della pagina
        renderTabella();
        aggiornaGrafico();
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
  f.write(html_completo)

print("File index.html generato correttamente!")
for cat in categorie:
  print(f"- Overall {cat}: {struttura_dati[cat]['overall']:.2f}")