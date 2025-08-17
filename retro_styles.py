#!/usr/bin/env python3
"""
Shared Retro Terminal Styles
Miami Vice + Commodore 64 aesthetic for all dashboards
"""

def get_retro_css():
    """Get the shared retro terminal CSS styles"""
    return """
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
        
        * { 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
        }
        
        body { 
            font-family: 'Courier Prime', 'Courier New', monospace; 
            background: linear-gradient(45deg, #0a0a0a 0%, #1a0a2e 25%, #16213e 50%, #0f3460 75%, #001122 100%);
            color: #00ff88;
            min-height: 100vh;
            font-size: 13px;
            line-height: 1.3;
            overflow-x: auto;
        }
        
        .terminal {
            background: linear-gradient(135deg, #ff006b 0%, #8338ec 25%, #3a86ff 50%, #06ffa5 75%, #ffbe0b 100%);
            background-size: 400% 400%;
            animation: gradient 8s ease infinite;
            padding: 2px;
            margin: 6px;
            border-radius: 4px;
        }
        
        @keyframes gradient {
            0%{background-position:0% 50%}
            50%{background-position:100% 50%}
            100%{background-position:0% 50%}
        }
        
        .screen {
            background: #000011;
            padding: 8px;
            border-radius: 2px;
            border: 1px solid #00ff88;
            box-shadow: 0 0 20px #00ff8844;
        }
        
        .header {
            text-align: center;
            margin-bottom: 6px;
            border-bottom: 1px solid #00ff88;
            padding-bottom: 3px;
        }
        
        .header h1 {
            font-size: 16px;
            font-weight: 700;
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            letter-spacing: 1px;
        }
        
        .header h2 {
            font-size: 14px;
            font-weight: 700;
            color: #ff006b;
            text-shadow: 0 0 8px #ff006b;
            letter-spacing: 1px;
            margin: 4px 0;
        }
        
        .status-bar {
            display: flex;
            justify-content: space-between;
            margin: 6px 0;
            padding: 3px 0;
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            font-size: 11px;
            flex-wrap: wrap;
        }
        
        .status-item {
            color: #ff6b35;
            margin: 1px 4px;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 4px;
            margin: 6px 0;
        }
        
        .metric-card {
            background: #001a33;
            border: 1px solid #00ff88;
            border-radius: 2px;
            padding: 4px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 16px;
            font-weight: 700;
            color: #00ff88;
            text-shadow: 0 0 8px #00ff88;
        }
        
        .metric-label {
            font-size: 10px;
            color: #8338ec;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .critical {
            color: #ff006b !important;
            text-shadow: 0 0 8px #ff006b !important;
            border-color: #ff006b !important;
        }
        
        .warning {
            color: #ffbe0b !important;
            text-shadow: 0 0 8px #ffbe0b !important;
            border-color: #ffbe0b !important;
        }
        
        .good {
            color: #06ffa5 !important;
            text-shadow: 0 0 8px #06ffa5 !important;
            border-color: #06ffa5 !important;
        }
        
        .data-section {
            margin: 6px 0;
            border: 1px solid #333;
            border-radius: 2px;
            background: #000a11;
        }
        
        .data-header {
            background: #001a33;
            padding: 3px 6px;
            border-bottom: 1px solid #333;
            font-size: 12px;
            font-weight: 700;
            color: #3a86ff;
            text-shadow: 0 0 6px #3a86ff;
        }
        
        .data-content {
            padding: 6px;
        }
        
        .data-table {
            width: 100%;
            font-size: 11px;
            border-collapse: collapse;
        }
        
        .data-table th,
        .data-table td {
            padding: 2px 4px;
            text-align: left;
            border-bottom: 1px solid #222;
        }
        
        .data-table th {
            color: #ff6b35;
            font-weight: 700;
            background: #001122;
        }
        
        .data-table td {
            color: #00ff88;
        }
        
        .tab-nav {
            display: flex;
            margin: 6px 0;
            border-bottom: 1px solid #333;
        }
        
        .tab-btn {
            background: #001122;
            border: 1px solid #333;
            color: #8338ec;
            padding: 4px 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            border-radius: 2px 2px 0 0;
            margin-right: 2px;
        }
        
        .tab-btn.active {
            background: #001a33;
            color: #00ff88;
            border-bottom: 1px solid #001a33;
        }
        
        .tab-btn:hover {
            background: #002244;
            color: #ff006b;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .form-group {
            margin: 4px 0;
        }
        
        .form-group label {
            display: block;
            font-size: 11px;
            color: #ff6b35;
            margin-bottom: 2px;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            background: #000a11;
            border: 1px solid #333;
            color: #00ff88;
            padding: 3px;
            font-family: inherit;
            font-size: 11px;
            border-radius: 2px;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #00ff88;
            box-shadow: 0 0 4px #00ff8844;
        }
        
        .btn {
            background: #001a33;
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 4px 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            border-radius: 2px;
            margin: 2px;
        }
        
        .btn:hover {
            background: #002244;
            box-shadow: 0 0 6px #00ff8844;
        }
        
        .btn-primary {
            border-color: #3a86ff;
            color: #3a86ff;
        }
        
        .btn-primary:hover {
            box-shadow: 0 0 6px #3a86ff44;
        }
        
        .btn-danger {
            border-color: #ff006b;
            color: #ff006b;
        }
        
        .btn-danger:hover {
            box-shadow: 0 0 6px #ff006b44;
        }
        
        .footer {
            margin-top: 6px;
            padding-top: 3px;
            border-top: 1px solid #333;
            font-size: 10px;
            color: #666;
            text-align: center;
        }
        
        .blink {
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        .ascii-border {
            color: #8338ec;
            font-size: 10px;
            text-align: center;
            margin: 2px 0;
            text-shadow: 0 0 6px #8338ec44;
        }
        
        .loading {
            color: #ffbe0b;
            text-align: center;
            padding: 20px;
            font-size: 12px;
        }
        
        .error {
            color: #ff006b;
            background: #220011;
            border: 1px solid #ff006b;
            padding: 4px;
            border-radius: 2px;
            font-size: 11px;
        }
        
        .success {
            color: #06ffa5;
            background: #001122;
            border: 1px solid #06ffa5;
            padding: 4px;
            border-radius: 2px;
            font-size: 11px;
        }
        
        @media (max-width: 768px) {
            .metric-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .status-bar {
                font-size: 10px;
            }
            .terminal {
                margin: 3px;
            }
        }
    """

def get_retro_js():
    """Get shared retro terminal JavaScript"""
    return """
        // Terminal startup effect
        document.addEventListener('DOMContentLoaded', function() {
            document.body.style.opacity = '0';
            setTimeout(() => {
                document.body.style.transition = 'opacity 0.3s';
                document.body.style.opacity = '1';
            }, 50);
        });
        
        // Tab management
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            const tabContent = document.getElementById(tabName + '-tab') || document.getElementById('content-' + tabName);
            const tabBtn = document.querySelector(`[onclick*="${tabName}"]`);
            
            if (tabContent) tabContent.classList.add('active');
            if (tabBtn) tabBtn.classList.add('active');
        }
        
        // Auto-refresh timestamps
        function updateTimestamp() {
            const now = new Date();
            const timeStr = now.toTimeString().substring(0, 8);
            
            document.querySelectorAll('#time, #footer-time, .timestamp').forEach(el => {
                if (el) el.textContent = timeStr;
            });
        }
        
        setInterval(updateTimestamp, 1000);
        
        // Loading states
        function showLoading(elementId) {
            const el = document.getElementById(elementId);
            if (el) el.innerHTML = '<div class="loading">LOADING...</div>';
        }
        
        function showError(elementId, message) {
            const el = document.getElementById(elementId);
            if (el) el.innerHTML = `<div class="error">ERROR: ${message}</div>`;
        }
        
        function showSuccess(elementId, message) {
            const el = document.getElementById(elementId);
            if (el) el.innerHTML = `<div class="success">✓ ${message}</div>`;
        }
    """