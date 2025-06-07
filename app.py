from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime
import os

app = Flask(__name__)

# Soubor pro ukládání dat
DATA_FILE = 'meteo_data.json'

def load_data():
    """Načte uložená data ze souboru"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    """Uloží data do souboru"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Chyba při ukládání dat: {e}")

@app.route('/data/upload.php', methods=['GET'])
def receive_weather_data():
    """Endpoint pro příjem dat z meteostanice"""
    
    print(f"Přijaty parametry: {dict(request.args)}")
    
    # Získání všech parametrů
    weather_data = {}
    
    # Základní informace
    weather_data['wsid'] = request.args.get('wsid', 'unknown')
    weather_data['datetime'] = request.args.get('datetime', datetime.now().isoformat())
    weather_data['received_at'] = datetime.now().isoformat()
    
    # Tlak
    weather_data['relative_pressure'] = request.args.get('rbar', type=float)
    weather_data['absolute_pressure'] = request.args.get('abar', type=float)
    
    # Vnitřní senzory
    weather_data['indoor_temp'] = request.args.get('intem', type=float)
    weather_data['indoor_humidity'] = request.args.get('inhum', type=int)
    weather_data['console_battery'] = request.args.get('inbat', type=int)
    
    # Venkovní senzory (Type1)
    weather_data['outdoor_temp'] = request.args.get('t1tem', type=float)
    weather_data['outdoor_humidity'] = request.args.get('t1hum', type=int)
    weather_data['feels_like'] = request.args.get('t1feels', type=float)
    weather_data['wind_chill'] = request.args.get('t1chill', type=float)
    weather_data['heat_index'] = request.args.get('t1heat', type=float)
    weather_data['dew_point'] = request.args.get('t1dew', type=float)
    
    # Vítr
    weather_data['wind_direction'] = request.args.get('t1wdir', type=int)
    weather_data['wind_speed'] = request.args.get('t1ws', type=float)
    weather_data['wind_speed_10min_avg'] = request.args.get('t1ws10mav', type=float)
    weather_data['wind_gust'] = request.args.get('t1wgust', type=float)
    
    # Déšť
    weather_data['rain_rate'] = request.args.get('t1rainra', type=float)
    weather_data['rain_hourly'] = request.args.get('t1rainhr', type=float)
    weather_data['rain_daily'] = request.args.get('t1raindy', type=float)
    weather_data['rain_weekly'] = request.args.get('t1rainwy', type=float)
    weather_data['rain_monthly'] = request.args.get('t1rainmth', type=float)
    weather_data['rain_yearly'] = request.args.get('t1rainyr', type=float)
    
    # Ostatní
    weather_data['uv_index'] = request.args.get('t1uvi', type=float)
    weather_data['solar_radiation'] = request.args.get('t1solrad', type=float)
    weather_data['wbgt_temp'] = request.args.get('t1wbgt', type=float)
    weather_data['outdoor_battery'] = request.args.get('t1bat', type=int)
    weather_data['outdoor_connection'] = request.args.get('t1cn', type=int)
    
    # Lightning Sensor (Type5)
    weather_data['lightning_last_strike_time'] = request.args.get('t5lst', type=int)
    weather_data['lightning_distance_km'] = request.args.get('t5lskm', type=int)
    weather_data['lightning_strikes_1hour'] = request.args.get('t5lsf', type=int)
    weather_data['lightning_count_5min'] = request.args.get('t5ls5mtc', type=int)
    weather_data['lightning_count_30min'] = request.args.get('t5ls30mtc', type=int)
    weather_data['lightning_count_1hour'] = request.args.get('t5ls1htc', type=int)
    weather_data['lightning_count_1day'] = request.args.get('t5ls1dtc', type=int)
    weather_data['lightning_battery'] = request.args.get('t5lsbat', type=int)
    weather_data['lightning_connection'] = request.args.get('t5lscn', type=int)
    
    # Dodatečné senzory (Type2,3,4) - prvních 7 kanálů
    # Kanál 2 je obvykle půdní teplota a vlhkost
    for i in range(1, 8):
        temp_key = f't234c{i}tem'
        hum_key = f't234c{i}hum'
        bat_key = f't234c{i}bat'
        cn_key = f't234c{i}cn'
        tp_key = f't234c{i}tp'
        
        if request.args.get(temp_key):
            weather_data[f'ch{i}_temp'] = request.args.get(temp_key, type=float)
            weather_data[f'ch{i}_humidity'] = request.args.get(hum_key, type=int)
            weather_data[f'ch{i}_battery'] = request.args.get(bat_key, type=int)
            weather_data[f'ch{i}_connection'] = request.args.get(cn_key, type=int)
            weather_data[f'ch{i}_type'] = request.args.get(tp_key, type=int)
            
            # Specifické označení pro kanál 2 (půdní senzory)
            if i == 2:
                weather_data['soil_temp'] = request.args.get(temp_key, type=float)
                weather_data['soil_humidity'] = request.args.get(hum_key, type=int)
                weather_data['soil_battery'] = request.args.get(bat_key, type=int)
                weather_data['soil_connection'] = request.args.get(cn_key, type=int)
    
    # Uložení dat
    all_data = load_data()
    all_data.append(weather_data)
    
    # Ponechej pouze posledních 1000 záznamů
    if len(all_data) > 1000:
        all_data = all_data[-1000:]
    
    save_data(all_data)
    
    print(f"Přijata data v {datetime.now()}: Lightning: {weather_data.get('lightning_connection', 'N/A')}, Soil: {weather_data.get('soil_temp', 'N/A')}°C")
    
    return "OK", 200

@app.route('/')
def dashboard():
    """Hlavní stránka s přehledem dat"""
    
    html_template = """
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meteostanice Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 20px;
            }
            .nav-tabs {
                display: flex;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                overflow: hidden;
            }
            .nav-tab {
                flex: 1;
                padding: 15px 20px;
                background: white;
                border: none;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.3s;
                border-bottom: 3px solid transparent;
            }
            .nav-tab:hover {
                background: #f8f9ff;
            }
            .nav-tab.active {
                background: #667eea;
                color: white;
                border-bottom: 3px solid #4c51bf;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .card h3 {
                margin-top: 0;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .value {
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }
            .unit {
                font-size: 14px;
                color: #666;
                font-weight: normal;
            }
            .status {
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
            .status.ok {
                background-color: #d4edda;
                color: #155724;
            }
            .status.warning {
                background-color: #fff3cd;
                color: #856404;
            }
            .status.error {
                background-color: #f8d7da;
                color: #721c24;
            }
            .last-update {
                text-align: center;
                color: #666;
                margin-top: 20px;
            }
            .refresh-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin: 10px;
            }
            .refresh-btn:hover {
                background: #5a67d8;
            }
            .lightning-warning {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
            }
            .history-table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .history-table th,
            .history-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            .history-table th {
                background: #667eea;
                color: white;
                font-weight: bold;
            }
            .history-table tr:nth-child(even) {
                background-color: #f8f9ff;
            }
            .history-table tr:hover {
                background-color: #e8ebff;
            }
            .filter-controls {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
            }
            .filter-controls select,
            .filter-controls input {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            .filter-controls button {
                background: #667eea;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-value {
                font-size: 20px;
                font-weight: bold;
                color: #667eea;
            }
            .stat-label {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .export-btn {
                background: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }
            .export-btn:hover {
                background: #218838;
            }
        </style>
        <script>
            let allData = [];
            
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.nav-tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
                
                if (tabName === 'history') {
                    loadHistoryData();
                } else if (tabName === 'stats') {
                    loadStatsData();
                }
            }
            
            function refreshData() {
                if (document.getElementById('current').classList.contains('active')) {
                    loadCurrentData();
                } else if (document.getElementById('history').classList.contains('active')) {
                    loadHistoryData();
                } else if (document.getElementById('stats').classList.contains('active')) {
                    loadStatsData();
                }
            }
            
            async function loadCurrentData() {
                try {
                    const response = await fetch('/api/data');
                    const data = await response.json();
                    allData = data;
                    
                    if (data.length === 0) {
                        document.getElementById('current-content').innerHTML = `
                            <div class="card">
                                <h3>Žádná data</h3>
                                <p>Zatím nebyla přijata žádná data z meteostanice.</p>
                                <p>Zkontroluj nastavení v aplikaci WSLink:</p>
                                <ul>
                                    <li>URL: https://[IP_ADRESA_TOHOTO_SERVERU]:8000/data/upload.php</li>
                                    <li>ID meteostanice: libovolné</li>
                                    <li>Heslo: libovolné</li>
                                </ul>
                            </div>
                        `;
                        return;
                    }
                    
                    const latest = data[data.length - 1];
                    
                    let html = '<div class="grid">';
                    
                    // Základní informace
                    html += `
                        <div class="card">
                            <h3>📊 Základní informace</h3>
                            <div><strong>ID stanice:</strong> ${latest.wsid || 'N/A'}</div>
                            <div><strong>Posledních záznamů:</strong> ${data.length}</div>
                            <div><strong>Připojení:</strong> 
                                <span class="status ${latest.outdoor_connection ? 'ok' : 'error'}">
                                    ${latest.outdoor_connection ? 'Připojeno' : 'Odpojeno'}
                                </span>
                            </div>
                        </div>
                    `;
                    
                    // Teploty
                    html += `
                        <div class="card">
                            <h3>🌡️ Teploty</h3>
                            ${latest.outdoor_temp !== null ? `<div class="value">${latest.outdoor_temp}°C <span class="unit">venkovní</span></div>` : ''}
                            ${latest.indoor_temp !== null ? `<div class="value">${latest.indoor_temp}°C <span class="unit">vnitřní</span></div>` : ''}
                            ${latest.soil_temp !== null ? `<div class="value">${latest.soil_temp}°C <span class="unit">půdní</span></div>` : ''}
                            ${latest.feels_like !== null ? `<div>Pocitová: ${latest.feels_like}°C</div>` : ''}
                            ${latest.dew_point !== null ? `<div>Rosný bod: ${latest.dew_point}°C</div>` : ''}
                        </div>
                    `;
                    
                    // Vlhkost
                    html += `
                        <div class="card">
                            <h3>💧 Vlhkost</h3>
                            ${latest.outdoor_humidity !== null ? `<div class="value">${latest.outdoor_humidity}% <span class="unit">venkovní</span></div>` : ''}
                            ${latest.indoor_humidity !== null ? `<div class="value">${latest.indoor_humidity}% <span class="unit">vnitřní</span></div>` : ''}
                            ${latest.soil_humidity !== null ? `<div class="value">${latest.soil_humidity}% <span class="unit">půdní</span></div>` : ''}
                        </div>
                    `;
                    
                    // Tlak
                    html += `
                        <div class="card">
                            <h3>🌪️ Atmosférický tlak</h3>
                            ${latest.relative_pressure !== null ? `<div class="value">${latest.relative_pressure} <span class="unit">hPa relativní</span></div>` : ''}
                            ${latest.absolute_pressure !== null ? `<div class="value">${latest.absolute_pressure} <span class="unit">hPa absolutní</span></div>` : ''}
                        </div>
                    `;
                    
                    // Vítr
                    html += `
                        <div class="card">
                            <h3>🌪️ Vítr</h3>
                            ${latest.wind_speed !== null ? `<div class="value">${latest.wind_speed} <span class="unit">m/s rychlost</span></div>` : ''}
                            ${latest.wind_gust !== null ? `<div>Náraz: ${latest.wind_gust} m/s</div>` : ''}
                            ${latest.wind_direction !== null ? `<div>Směr: ${latest.wind_direction}°</div>` : ''}
                            ${latest.wind_speed_10min_avg !== null ? `<div>Průměr 10min: ${latest.wind_speed_10min_avg} m/s</div>` : ''}
                        </div>
                    `;
                    
                    // Déšť
                    html += `
                        <div class="card">
                            <h3>🌧️ Srážky</h3>
                            ${latest.rain_rate !== null ? `<div class="value">${latest.rain_rate} <span class="unit">mm/h intenzita</span></div>` : ''}
                            ${latest.rain_daily !== null ? `<div>Dnes: ${latest.rain_daily} mm</div>` : ''}
                            ${latest.rain_hourly !== null ? `<div>Hodinové: ${latest.rain_hourly} mm</div>` : ''}
                            ${latest.rain_monthly !== null ? `<div>Měsíční: ${latest.rain_monthly} mm</div>` : ''}
                        </div>
                    `;
                    
                    // Blesky
                    if (latest.lightning_connection) {
                        html += `
                            <div class="card">
                                <h3>⚡ Detekce blesků</h3>
                                <div><strong>Připojení:</strong> 
                                    <span class="status ${latest.lightning_connection ? 'ok' : 'error'}">
                                        ${latest.lightning_connection ? 'Aktivní' : 'Neaktivní'}
                                    </span>
                                </div>
                                ${latest.lightning_distance_km !== null ? `<div class="value">${latest.lightning_distance_km} <span class="unit">km vzdálenost</span></div>` : ''}
                                ${latest.lightning_strikes_1hour !== null ? `<div>Úderů za hodinu: ${latest.lightning_strikes_1hour}</div>` : ''}
                                ${latest.lightning_count_5min !== null ? `<div>Za 5 min: ${latest.lightning_count_5min}</div>` : ''}
                                ${latest.lightning_count_30min !== null ? `<div>Za 30 min: ${latest.lightning_count_30min}</div>` : ''}
                                ${latest.lightning_battery !== null ? `<div>Baterie: ${latest.lightning_battery}%</div>` : ''}
                            </div>
                        `;
                    }
                    
                    // UV a sluneční záření
                    if (latest.uv_index !== null || latest.solar_radiation !== null) {
                        html += `
                            <div class="card">
                                <h3>☀️ UV & Sluneční záření</h3>
                                ${latest.uv_index !== null ? `<div class="value">${latest.uv_index} <span class="unit">UV index</span></div>` : ''}
                                ${latest.solar_radiation !== null ? `<div class="value">${latest.solar_radiation} <span class="unit">W/m² sluneční záření</span></div>` : ''}
                            </div>
                        `;
                    }
                    
                    html += '</div>';
                    
                    // Poslední aktualizace
                    html += `
                        <div class="last-update">
                            Poslední aktualizace: ${new Date(latest.received_at).toLocaleString('cs-CZ')}
                        </div>
                    `;
                    
                    document.getElementById('current-content').innerHTML = html;
                    
                } catch (error) {
                    console.error('Chyba při načítání dat:', error);
                    document.getElementById('current-content').innerHTML = `
                        <div class="card">
                            <h3>Chyba</h3>
                            <p>Nepodařilo se načíst data. Zkus obnovit stránku.</p>
                        </div>
                    `;
                }
            }
            
            async function loadHistoryData() {
                try {
                    document.getElementById('history-content').innerHTML = '<div class="loading">Načítám historická data...</div>';
                    
                    const response = await fetch('/api/data');
                    const data = await response.json();
                    allData = data;
                    
                    if (data.length === 0) {
                        document.getElementById('history-content').innerHTML = `
                            <div class="card">
                                <h3>Žádná data</h3>
                                <p>Zatím nebyla přijata žádná data z meteostanice.</p>
                            </div>
                        `;
                        return;
                    }
                    
                    const recordCount = document.getElementById('recordCount').value;
                    let displayData = data;
                    
                    if (recordCount !== 'all') {
                        displayData = data.slice(-parseInt(recordCount));
                    }
                    
                    let html = `
                        <div style="overflow-x: auto;">
                            <table class="history-table">
                                <thead>
                                    <tr>
                                        <th>Čas</th>
                                        <th>Teplota (°C)</th>
                                        <th>Vlhkost (%)</th>
                                        <th>Tlak (hPa)</th>
                                        <th>Vítr (m/s)</th>
                                        <th>Déšť (mm)</th>
                                        <th>UV index</th>
                                        <th>Blesky</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    displayData.reverse().forEach(record => {
                        const time = new Date(record.received_at).toLocaleString('cs-CZ');
                        html += `
                            <tr>
                                <td>${time}</td>
                                <td>${record.outdoor_temp !== null ? record.outdoor_temp : '-'}</td>
                                <td>${record.outdoor_humidity !== null ? record.outdoor_humidity : '-'}</td>
                                <td>${record.relative_pressure !== null ? record.relative_pressure : '-'}</td>
                                <td>${record.wind_speed !== null ? record.wind_speed : '-'}</td>
                                <td>${record.rain_rate !== null ? record.rain_rate : '-'}</td>
                                <td>${record.uv_index !== null ? record.uv_index : '-'}</td>
                                <td>${record.lightning_distance_km !== null ? record.lightning_distance_km + ' km' : '-'}</td>
                            </tr>
                        `;
                    });
                    
                    html += `
                                </tbody>
                            </table>
                        </div>
                    `;
                    
                    document.getElementById('history-content').innerHTML = html;
                    
                } catch (error) {
                    console.error('Chyba při načítání historie:', error);
                    document.getElementById('history-content').innerHTML = `
                        <div class="card">
                            <h3>Chyba</h3>
                            <p>Nepodařilo se načíst historická data.</p>
                        </div>
                    `;
                }
            }
            
            async function loadStatsData() {
                try {
                    document.getElementById('stats-content').innerHTML = '<div class="loading">Počítám statistiky...</div>';
                    
                    const response = await fetch('/api/data');
                    const data = await response.json();
                    
                    if (data.length === 0) {
                        document.getElementById('stats-content').innerHTML = `
                            <div class="card">
                                <h3>Žádná data</h3>
                                <p>Zatím nebyla přijata žádná data pro statistiky.</p>
                            </div>
                        `;
                        return;
                    }
                    
                    // Výpočet statistik
                    const stats = calculateStats(data);
                    
                    let html = `
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-value">${stats.temp.min}°C</div>
                                <div class="stat-label">Min. teplota</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.temp.max}°C</div>
                                <div class="stat-label">Max. teplota</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.temp.avg}°C</div>
                                <div class="stat-label">Průměr teplota</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.humidity.min}%</div>
                                <div class="stat-label">Min. vlhkost</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.humidity.max}%</div>
                                <div class="stat-label">Max. vlhkost</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.humidity.avg}%</div>
                                <div class="stat-label">Průměr vlhkost</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.pressure.min}</div>
                                <div class="stat-label">Min. tlak (hPa)</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.pressure.max}</div>
                                <div class="stat-label">Max. tlak (hPa)</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.pressure.avg}</div>
                                <div class="stat-label">Průměr tlak (hPa)</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.wind.max}</div>
                                <div class="stat-label">Max. vítr (m/s)</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.wind.avg}</div>
                                <div class="stat-label">Průměr vítr (m/s)</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${stats.rain.total}</div>
                                <div class="stat-label">Celkem déšť (mm)</div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h3>📊 Přehled za posledních 24 hodin</h3>
                            <div class="grid">
                                <div>
                                    <strong>Celkem záznamů:</strong> ${data.length}<br>
                                    <strong>První záznam:</strong> ${new Date(data[0].received_at).toLocaleString('cs-CZ')}<br>
                                    <strong>Poslední záznam:</strong> ${new Date(data[data.length-1].received_at).toLocaleString('cs-CZ')}
                                </div>
                                <div>
                                    <strong>Aktivní senzory:</strong><br>
                                    ${stats.sensors.outdoor ? '✅ Venkovní senzor' : '❌ Venkovní senzor'}<br>
                                    ${stats.sensors.indoor ? '✅ Vnitřní senzor' : '❌ Vnitřní senzor'}<br>
                                    ${stats.sensors.soil ? '✅ Půdní senzor' : '❌ Půdní senzor'}<br>
                                    ${stats.sensors.lightning ? '✅ Detektor blesků' : '❌ Detektor blesků'}
                                </div>
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('stats-content').innerHTML = html;
                    
                } catch (error) {
                    console.error('Chyba při načítání statistik:', error);
                    document.getElementById('stats-content').innerHTML = `
                        <div class="card">
                            <h3>Chyba</h3>
                            <p>Nepodařilo se načíst statistiky.</p>
                        </div>
                    `;
                }
            }
            
            function calculateStats(data) {
                const stats = {
                    temp: { min: null, max: null, avg: null, values: [] },
                    humidity: { min: null, max: null, avg: null, values: [] },
                    pressure: { min: null, max: null, avg: null, values: [] },
                    wind: { min: null, max: null, avg: null, values: [] },
                    rain: { total: 0, values: [] },
                    sensors: {
                        outdoor: false,
                        indoor: false,
                        soil: false,
                        lightning: false
                    }
                };
                
                data.forEach(record => {
                    // Teplota
                    if (record.outdoor_temp !== null) {
                        stats.temp.values.push(record.outdoor_temp);
                        stats.sensors.outdoor = true;
                    }
                    
                    // Vlhkost
                    if (record.outdoor_humidity !== null) {
                        stats.humidity.values.push(record.outdoor_humidity);
                    }
                    
                    // Tlak
                    if (record.relative_pressure !== null) {
                        stats.pressure.values.push(record.relative_pressure);
                    }
                    
                    // Vítr
                    if (record.wind_speed !== null) {
                        stats.wind.values.push(record.wind_speed);
                    }
                    
                    // Déšť
                    if (record.rain_daily !== null) {
                        stats.rain.values.push(record.rain_daily);
                    }
                    
                    // Senzory
                    if (record.indoor_temp !== null) stats.sensors.indoor = true;
                    if (record.soil_temp !== null) stats.sensors.soil = true;
                    if (record.lightning_connection) stats.sensors.lightning = true;
                });
                
                // Výpočet min/max/avg pro teplotu
                if (stats.temp.values.length > 0) {
                    stats.temp.min = Math.min(...stats.temp.values).toFixed(1);
                    stats.temp.max = Math.max(...stats.temp.values).toFixed(1);
                    stats.temp.avg = (stats.temp.values.reduce((a, b) => a + b, 0) / stats.temp.values.length).toFixed(1);
                } else {
                    stats.temp.min = stats.temp.max = stats.temp.avg = '-';
                }
                
                // Výpočet pro vlhkost
                if (stats.humidity.values.length > 0) {
                    stats.humidity.min = Math.min(...stats.humidity.values);
                    stats.humidity.max = Math.max(...stats.humidity.values);
                    stats.humidity.avg = Math.round(stats.humidity.values.reduce((a, b) => a + b, 0) / stats.humidity.values.length);
                } else {
                    stats.humidity.min = stats.humidity.max = stats.humidity.avg = '-';
                }
                
                // Výpočet pro tlak
                if (stats.pressure.values.length > 0) {
                    stats.pressure.min = Math.min(...stats.pressure.values).toFixed(1);
                    stats.pressure.max = Math.max(...stats.pressure.values).toFixed(1);
                    stats.pressure.avg = (stats.pressure.values.reduce((a, b) => a + b, 0) / stats.pressure.values.length).toFixed(1);
                } else {
                    stats.pressure.min = stats.pressure.max = stats.pressure.avg = '-';
                }
                
                // Výpočet pro vítr
                if (stats.wind.values.length > 0) {
                    stats.wind.min = Math.min(...stats.wind.values).toFixed(1);
                    stats.wind.max = Math.max(...stats.wind.values).toFixed(1);
                    stats.wind.avg = (stats.wind.values.reduce((a, b) => a + b, 0) / stats.wind.values.length).toFixed(1);
                } else {
                    stats.wind.min = stats.wind.max = stats.wind.avg = '-';
                }
                
                // Výpočet pro déšť
                if (stats.rain.values.length > 0) {
                    stats.rain.total = Math.max(...stats.rain.values).toFixed(1);
                } else {
                    stats.rain.total = '-';
                }
                
                return stats;
            }
            
            function exportData() {
                if (allData.length === 0) {
                    alert('Žádná data k exportu');
                    return;
                }
                
                // Vytvoření CSV
                let csv = 'Cas,Venkovni_teplota,Venkovni_vlhkost,Vnitrni_teplota,Vnitrni_vlhkost,Relativni_tlak,Absolutni_tlak,Rychlost_vetru,Smer_vetru,Intenzita_deste,Denny_dest,UV_index,Slunecni_zareni,Vzdalenost_blesku\\n';
                
                allData.forEach(record => {
                    csv += [
                        new Date(record.received_at).toLocaleString('cs-CZ'),
                        record.outdoor_temp || '',
                        record.outdoor_humidity || '',
                        record.indoor_temp || '',
                        record.indoor_humidity || '',
                        record.relative_pressure || '',
                        record.absolute_pressure || '',
                        record.wind_speed || '',
                        record.wind_direction || '',
                        record.rain_rate || '',
                        record.rain_daily || '',
                        record.uv_index || '',
                        record.solar_radiation || '',
                        record.lightning_distance_km || ''
                    ].join(',') + '\\n';
                });
                
                // Stažení souboru
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement('a');
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', `meteodata_${new Date().toISOString().split('T')[0]}.csv`);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
            
            // Auto-refresh každých 30 sekund pouze pro aktuální data
            setInterval(() => {
                if (document.getElementById('current').classList.contains('active')) {
                    loadCurrentData();
                }
            }, 30000);
            
            // Načíst data při načtení stránky
            window.addEventListener('DOMContentLoaded', () => {
                loadCurrentData();
            });
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌤️ Meteostanice Dashboard</h1>
                <button class="refresh-btn" onclick="refreshData()">🔄 Obnovit data</button>
            </div>
            
            <!-- Navigation tabs -->
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('current')">📊 Aktuální data</button>
                <button class="nav-tab" onclick="showTab('history')">📋 Historie</button>
                <button class="nav-tab" onclick="showTab('stats')">📈 Statistiky</button>
            </div>
            
            <!-- Current data tab -->
            <div id="current" class="tab-content active">
                <div id="current-content">
                    <div class="loading">Načítám aktuální data...</div>
                </div>
            </div>
            
            <!-- History tab -->
            <div id="history" class="tab-content">
                <div class="filter-controls">
                    <label>Zobrazit posledních:</label>
                    <select id="recordCount" onchange="loadHistoryData()">
                        <option value="10">10 záznamů</option>
                        <option value="50" selected>50 záznamů</option>
                        <option value="100">100 záznamů</option>
                        <option value="all">Všechny záznamy</option>
                    </select>
                    <button class="export-btn" onclick="exportData()">📥 Export CSV</button>
                </div>
                <div id="history-content">
                    <div class="loading">Klikni na záložku Historie pro načtení dat...</div>
                </div>
            </div>
            
            <!-- Statistics tab -->
            <div id="stats" class="tab-content">
                <div id="stats-content">
                    <div class="loading">Klikni na záložku Statistiky pro načtení dat...</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template)

@app.route('/api/data')
def get_data():
    """API endpoint pro získání dat"""
    data = load_data()
    return jsonify(data)

@app.route('/api/latest')
def get_latest():
    """API endpoint pro nejnovější data"""
    data = load_data()
    if data:
        return jsonify(data[-1])
    return jsonify({})

if __name__ == '__main__':
    print("🌤️ Spouštím meteostanice server...")
    print("Dashboard bude dostupný na: https://localhost:8000")
    print("Endpoint pro WSLink: https://localhost:8000/data/upload.php")
    print()
    print("Pro přístup z jiných zařízení v síti nahraď 'localhost' IP adresou tohoto počítače.")
    print("Stiskni Ctrl+C pro ukončení serveru.")
    
    # Spuštění serveru na všech rozhraních
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))