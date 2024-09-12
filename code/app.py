#app.py
from flask import Flask, render_template, jsonify
import asyncio
import plotly.graph_objects as go
from client import main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph-data')
def graph_data():
    data = asyncio.run(main())
    distance = data.get('distance', 0)
    scanAngle = data.get('scanAngle')

    fig = go.Figure(data=go.Scatterpolar(
        r=[distance],
        theta=[scanAngle],
        mode='markers',
    ))

    fig.update_layout(showlegend=False, polar=dict(radialaxis=dict(range=[0, 200])))

    graphJSON = fig.to_json()
    return jsonify(graphJSON)

if __name__ == "__main__":
    app.run(debug=True)
