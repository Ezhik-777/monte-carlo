#!/usr/bin/env python3
"""
Monte Carlo Investment Calculator - Web Application

A Flask-based web application for sophisticated Monte Carlo investment analysis
with interactive visualizations and comprehensive risk assessment.
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import io
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np
from scipy.stats import norm
from joblib import Parallel, delayed
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import pandas as pd
from advanced_calculator import (
    AdvancedMonteCarloCalculator, 
    AdvancedParameters, 
    CalculationMode, 
    DepositType, 
    TaxSystem
)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'monte-carlo-investment-calculator-2024'

# Enhanced Investment presets with advanced parameters
PRESETS = {
    'conservative': {
        'name': 'Консервативный портфель',
        'description': 'Низкий риск, стабильная доходность (облигации + немного акций)',
        'initial_amount': 10000,
        'monthly_deposit': 500,
        'interest_rate_min': -2.0,
        'interest_rate_max': 8.0,
        'interest_rate_mean': 4.5,
        'volatility_min': 5.0,
        'volatility_max': 12.0,
        'volatility_mean': 7.0,
        'accumulation_years': 20,
        'withdrawal_years': 30,
        'target_withdrawal_rate': 3.5,
        'inflation_rate': 2.5,
        'color': '#4CAF50',
        'icon': 'shield-alt'
    },
    'moderate': {
        'name': 'Сбалансированный портфель',
        'description': 'Умеренный риск, сбалансированная доходность (60/40 акции/облигации)',
        'initial_amount': 10000,
        'monthly_deposit': 500,
        'interest_rate_min': -8.0,
        'interest_rate_max': 20.0,
        'interest_rate_mean': 7.5,
        'volatility_min': 10.0,
        'volatility_max': 20.0,
        'volatility_mean': 15.0,
        'accumulation_years': 20,
        'withdrawal_years': 30,
        'target_withdrawal_rate': 4.0,
        'inflation_rate': 2.5,
        'color': '#FF9800',
        'icon': 'balance-scale'
    },
    'aggressive': {
        'name': 'Агрессивный портфель',
        'description': 'Высокий риск, высокий потенциал доходности (80%+ акции)',
        'initial_amount': 10000,
        'monthly_deposit': 500,
        'interest_rate_min': -25.0,
        'interest_rate_max': 35.0,
        'interest_rate_mean': 9.5,
        'volatility_min': 18.0,
        'volatility_max': 35.0,
        'volatility_mean': 25.0,
        'accumulation_years': 20,
        'withdrawal_years': 30,
        'target_withdrawal_rate': 4.5,
        'inflation_rate': 2.5,
        'color': '#F44336',
        'icon': 'rocket'
    },
    'retirement_focused': {
        'name': 'Пенсионная стратегия',
        'description': 'Долгосрочное планирование пенсии с учетом инфляции',
        'initial_amount': 25000,
        'monthly_deposit': 800,
        'interest_rate_min': 6.0,
        'interest_rate_max': 9.0,
        'interest_rate_mean': 7.0,
        'volatility_min': 12.0,
        'volatility_max': 18.0,
        'volatility_mean': 15.0,
        'accumulation_years': 30,
        'withdrawal_years': 25,
        'target_withdrawal_rate': 3.8,
        'inflation_rate': 2.8,
        'color': '#9C27B0',
        'icon': 'piggy-bank'
    },
    'fire_movement': {
        'name': 'FIRE стратегия',
        'description': 'Финансовая независимость и ранний выход на пенсию',
        'initial_amount': 50000,
        'monthly_deposit': 2000,
        'interest_rate_min': 8.0,
        'interest_rate_max': 12.0,
        'interest_rate_mean': 9.5,
        'volatility_min': 15.0,
        'volatility_max': 25.0,
        'volatility_mean': 20.0,
        'accumulation_years': 15,
        'withdrawal_years': 40,
        'target_withdrawal_rate': 3.25,
        'inflation_rate': 2.5,
        'color': '#FF5722',
        'icon': 'fire'
    }
}


class MonteCarloCalculator:
    """Monte Carlo investment calculator engine."""
    
    def __init__(self):
        self.currency = '€'
    
    def calc_ending_value(
        self,
        monthly_deposit: float,
        interest_rate: float,
        volatility: float,
        dynamic: float,
        ending_value: float
    ) -> float:
        """Calculate ending value for one year."""
        norm_obr = interest_rate
        
        if volatility > 0:
            norm_obr = norm.ppf(np.random.random(), interest_rate, volatility)
        
        return ending_value * (1 + norm_obr) + (12.0 * monthly_deposit * (1 + dynamic))
    
    def calc_single_scenario(
        self,
        first_deposit: float,
        monthly_deposit: float,
        interest_rate: float,
        volatility: float,
        dynamic: float,
        years_number: int
    ) -> float:
        """Calculate single Monte Carlo scenario."""
        ending_value = first_deposit
        for _ in range(years_number):
            ending_value = self.calc_ending_value(
                monthly_deposit, interest_rate, volatility, dynamic, ending_value
            )
        return ending_value
    
    def calculate(
        self,
        first_deposit: float,
        monthly_deposit: float,
        interest_rate: float,
        volatility: float,
        dynamic: float,
        years_number: int,
        iter_number: int
    ) -> Dict[str, Any]:
        """Run complete Monte Carlo simulation."""
        
        # Convert percentages to decimals
        interest_rate_decimal = interest_rate / 100
        volatility_decimal = volatility / 100
        dynamic_decimal = dynamic / 100
        
        # Calculate no volatility scenario
        no_volatility_value = self.calc_single_scenario(
            first_deposit, monthly_deposit, interest_rate_decimal, 0, dynamic_decimal, years_number
        )
        
        # Run Monte Carlo simulation
        results = Parallel(n_jobs=-1)(
            delayed(self.calc_single_scenario)(
                first_deposit, monthly_deposit, interest_rate_decimal, 
                volatility_decimal, dynamic_decimal, years_number
            ) for _ in range(iter_number)
        )
        
        # Calculate statistics
        mean = np.mean(results)
        median = np.median(results)
        std_dev = np.std(results)
        
        # Calculate percentiles
        percentiles = [99, 95, 90, 75, 50, 25, 10, 5, 1]
        percentile_values = np.percentile(results, percentiles)
        
        # Calculate additional metrics
        total_invested = first_deposit + (monthly_deposit * 12 * years_number)
        mean_return_percent = ((mean / total_invested) - 1) * 100
        
        # Risk metrics
        downside_risk = ((percentile_values[7] - mean) / mean) * 100  # 5th percentile
        upside_potential = ((percentile_values[0] - mean) / mean) * 100  # 99th percentile
        
        return {
            'parameters': {
                'first_deposit': first_deposit,
                'monthly_deposit': monthly_deposit,
                'interest_rate': interest_rate,
                'volatility': volatility,
                'dynamic': dynamic,
                'years_number': years_number,
                'iter_number': iter_number
            },
            'results': {
                'no_volatility_value': no_volatility_value,
                'mean': mean,
                'median': median,
                'std_dev': std_dev,
                'total_invested': total_invested,
                'mean_return_percent': mean_return_percent,
                'downside_risk': downside_risk,
                'upside_potential': upside_potential
            },
            'percentiles': {
                str(p): v for p, v in zip(percentiles, percentile_values)
            },
            'raw_data': results[:1000]  # Limit for web transfer
        }


calculator = MonteCarloCalculator()
advanced_calculator = AdvancedMonteCarloCalculator()


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html', presets=PRESETS)


@app.route('/advanced')
def advanced():
    """Advanced calculator page."""
    return render_template('index.html', presets=PRESETS)


@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """API endpoint for calculations."""
    try:
        data = request.json
        calculation_type = data.get('calculation_type', 'simple')
        
        if calculation_type == 'advanced':
            return api_calculate_advanced()
        else:
            return api_calculate_simple()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def api_calculate_simple():
    """Simple calculation API (backwards compatibility)."""
    data = request.json
    
    # Validate input
    required_fields = [
        'first_deposit', 'monthly_deposit', 'interest_rate',
        'volatility', 'dynamic', 'years_number', 'iter_number'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    # Run calculation
    results = calculator.calculate(
        float(data['first_deposit']),
        float(data['monthly_deposit']),
        float(data['interest_rate']),
        float(data['volatility']),
        float(data['dynamic']),
        int(data['years_number']),
        int(data['iter_number'])
    )
    
    return jsonify({
        'success': True,
        'data': results,
        'timestamp': datetime.now().isoformat()
    })


def api_calculate_advanced():
    """Advanced calculation API with multiple modes."""
    data = request.json
    
    # Parse advanced parameters
    try:
        params = AdvancedParameters(
            calculation_mode=CalculationMode(data.get('calculation_mode', 'accumulation')),
            deposit_type=DepositType(data.get('deposit_type', 'monthly')),
            initial_amount=float(data.get('initial_amount', 10000)),
            monthly_deposit=float(data.get('monthly_deposit', 500)),
            
            # Interest rate range
            interest_rate_min=float(data.get('interest_rate_min', 5.0)),
            interest_rate_max=float(data.get('interest_rate_max', 10.0)),
            interest_rate_mean=float(data.get('interest_rate_mean', 7.5)),
            
            # Volatility range
            volatility_min=float(data.get('volatility_min', 10.0)),
            volatility_max=float(data.get('volatility_max', 20.0)),
            volatility_mean=float(data.get('volatility_mean', 15.0)),
            
            # Time parameters
            accumulation_years=int(data.get('accumulation_years', 20)),
            withdrawal_years=int(data.get('withdrawal_years', 30)),
            
            # Economic parameters
            inflation_rate=float(data.get('inflation_rate', 2.5)),
            inflation_volatility=float(data.get('inflation_volatility', 1.0)),
            
            # Tax parameters
            tax_system=TaxSystem(data.get('tax_system', 'german')),
            tax_rate=float(data.get('tax_rate', 26.375)),
            
            # Withdrawal parameters
            target_withdrawal_rate=float(data.get('target_withdrawal_rate', 4.0)),
            withdrawal_strategy=data.get('withdrawal_strategy', 'fixed_percentage'),
            
            # Advanced options
            management_fee=float(data.get('management_fee', 0.5)),
            consider_sequence_risk=data.get('consider_sequence_risk', True),
            
            # Simulation parameters
            iterations=int(data.get('iterations', 10000))
        )
        
        # Add lump sum deposits if provided
        if 'lump_sum_deposits' in data:
            params.lump_sum_deposits = [(int(item['month']), float(item['amount'])) 
                                       for item in data['lump_sum_deposits']]
        
        # Run advanced calculation
        results = advanced_calculator.calculate_comprehensive(params)
        
        return jsonify({
            'success': True,
            'data': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {str(e)}'
        }), 400


@app.route('/api/charts/advanced/<chart_type>')
def api_advanced_chart(chart_type):
    """Generate advanced charts for comprehensive analysis."""
    try:
        # Get data from request
        raw_data = request.args.get('data')
        if not raw_data:
            return jsonify({'error': 'No data provided'}), 400
        
        data = json.loads(raw_data)
        
        # Set style for better-looking charts
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        if chart_type == 'lifecycle':
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Accumulation phase
            if data.get('accumulation_phase'):
                acc_data = data['accumulation_phase']['monthly_progression']
                months = acc_data['months']
                years = [m/12 for m in months]
                
                ax1.plot(years, acc_data['mean_balance'], 'b-', linewidth=2, label='Среднее')
                ax1.fill_between(years, acc_data['percentile_25'], acc_data['percentile_75'], 
                               alpha=0.3, color='blue', label='25-75%')
                ax1.fill_between(years, acc_data['percentile_5'], acc_data['percentile_95'], 
                               alpha=0.2, color='blue', label='5-95%')
                ax1.set_title('Фаза накопления', fontsize=14, fontweight='bold')
                ax1.set_xlabel('Годы')
                ax1.set_ylabel('Стоимость портфеля (€)')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
            
            # Withdrawal phase
            if data.get('withdrawal_phase') and data['withdrawal_phase'].get('swr_analysis'):
                swr_data = data['withdrawal_phase']['swr_analysis']['success_rates_by_swr']
                swr_rates = [float(k) for k in swr_data.keys()]
                success_rates = list(swr_data.values())
                
                ax2.plot(swr_rates, success_rates, 'o-', linewidth=2, markersize=6, color='orange')
                ax2.axhline(y=95, color='green', linestyle='--', alpha=0.7, label='95% успеха')
                ax2.axhline(y=90, color='yellow', linestyle='--', alpha=0.7, label='90% успеха')
                ax2.set_title('Анализ SWR', fontsize=14, fontweight='bold')
                ax2.set_xlabel('Ставка снятия (%)')
                ax2.set_ylabel('Вероятность успеха (%)')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            
            # Risk analysis
            if data.get('risk_metrics'):
                risk_categories = ['Волатильность', 'Риск снижения', 'Макс. просадка']
                risk_values = []
                
                if data['risk_metrics'].get('accumulation'):
                    acc_risk = data['risk_metrics']['accumulation']
                    risk_values = [
                        min(acc_risk.get('volatility', 0), 100),
                        min(acc_risk.get('downside_risk', 0) / 1000, 100),
                        min(acc_risk.get('max_drawdown', 0), 100)
                    ]
                
                colors = ['#ff4444', '#ff8844', '#ffcc44']
                bars = ax3.bar(risk_categories, risk_values, color=colors, alpha=0.7)
                ax3.set_title('Профиль рисков', fontsize=14, fontweight='bold')
                ax3.set_ylabel('Уровень риска (%)')
                ax3.set_ylim(0, 100)
                
                # Add value labels on bars
                for bar, value in zip(bars, risk_values):
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{value:.1f}%', ha='center', va='bottom')
            
            # Economic impact
            if data.get('accumulation_phase'):
                acc = data['accumulation_phase']
                categories = ['Номинальная\nстоимость', 'Реальная\nстоимость', 'После\nналогов']
                values = [
                    acc['nominal_stats']['mean'],
                    acc['real_stats']['mean'],
                    acc['after_tax_stats']['mean']
                ]
                
                colors = ['#4CAF50', '#FF9800', '#F44336']
                bars = ax4.bar(categories, values, color=colors, alpha=0.7)
                ax4.set_title('Экономическое воздействие', fontsize=14, fontweight='bold')
                ax4.set_ylabel('Стоимость (€)')
                
                # Add value labels
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height + value*0.01,
                            f'{value:,.0f}€', ha='center', va='bottom')
            
            plt.suptitle('Комплексный анализ жизненного цикла портфеля', fontsize=16, fontweight='bold')
            plt.tight_layout()
        
        elif chart_type == 'monte_carlo_distribution':
            # Enhanced Monte Carlo distribution analysis
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            if data.get('accumulation_phase'):
                values = data['accumulation_phase']['final_amounts']
                
                # Histogram
                n, bins, patches = ax1.hist(values, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
                ax1.axvline(np.mean(values), color='red', linestyle='--', linewidth=2, label=f'Среднее: {np.mean(values):,.0f}€')
                ax1.axvline(np.median(values), color='green', linestyle='--', linewidth=2, label=f'Медиана: {np.median(values):,.0f}€')
                ax1.set_title('Распределение конечной стоимости', fontsize=14, fontweight='bold')
                ax1.set_xlabel('Стоимость (€)')
                ax1.set_ylabel('Частота')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                
                # Q-Q plot for normality check
                from scipy import stats
                stats.probplot(values, dist="norm", plot=ax2)
                ax2.set_title('Q-Q Plot (проверка нормальности)', fontsize=14, fontweight='bold')
                ax2.grid(True, alpha=0.3)
                
                # Percentile analysis
                percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
                perc_values = np.percentile(values, percentiles)
                ax3.plot(percentiles, perc_values, 'o-', linewidth=2, markersize=6)
                ax3.set_title('Анализ процентилей', fontsize=14, fontweight='bold')
                ax3.set_xlabel('Процентиль')
                ax3.set_ylabel('Стоимость (€)')
                ax3.grid(True, alpha=0.3)
                
                # Risk metrics visualization
                mean_val = np.mean(values)
                std_val = np.std(values)
                var_95 = np.percentile(values, 5)
                
                risk_metrics = ['Среднее', 'Ст. отклонение', 'VaR (95%)']
                risk_values = [mean_val, std_val, var_95]
                colors = ['green', 'orange', 'red']
                
                bars = ax4.bar(risk_metrics, risk_values, color=colors, alpha=0.7)
                ax4.set_title('Ключевые метрики риска', fontsize=14, fontweight='bold')
                ax4.set_ylabel('Значение (€)')
                
                for bar, value in zip(bars, risk_values):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height + value*0.01,
                            f'{value:,.0f}€', ha='center', va='bottom')
            
            plt.suptitle('Анализ распределения Monte Carlo', fontsize=16, fontweight='bold')
            plt.tight_layout()
        
        else:
            return jsonify({'error': 'Unknown chart type'}), 400
        
        # Save to bytes
        img = BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight', facecolor='white')
        img.seek(0)
        
        # Encode to base64
        img_b64 = base64.b64encode(img.getvalue()).decode()
        
        plt.close()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_b64}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chart/<chart_type>')
def api_chart(chart_type):
    """Generate charts."""
    try:
        # Get data from request
        raw_data = request.args.get('data')
        if not raw_data:
            return jsonify({'error': 'No data provided'}), 400
        
        data = json.loads(raw_data)
        values = data['raw_data']
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        if chart_type == 'histogram':
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create histogram
            n, bins, patches = ax.hist(values, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
            
            # Add statistics lines
            mean_val = np.mean(values)
            median_val = np.median(values)
            
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Среднее: {mean_val:,.0f}€')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Медиана: {median_val:,.0f}€')
            
            # Add percentiles
            percentiles = [95, 75, 25, 5]
            colors = ['orange', 'yellow', 'purple', 'brown']
            for p, color in zip(percentiles, colors):
                val = np.percentile(values, p)
                ax.axvline(val, color=color, linestyle=':', alpha=0.7, label=f'{p}%: {val:,.0f}€')
            
            ax.set_xlabel('Стоимость инвестиций (€)', fontsize=12)
            ax.set_ylabel('Частота', fontsize=12)
            ax.set_title('Распределение результатов Monte Carlo симуляции', fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        elif chart_type == 'boxplot':
            fig, ax = plt.subplots(figsize=(10, 8))
            
            box_plot = ax.boxplot(values, vert=True, patch_artist=True)
            box_plot['boxes'][0].set_facecolor('lightblue')
            box_plot['boxes'][0].set_alpha(0.7)
            
            ax.set_ylabel('Стоимость инвестиций (€)', fontsize=12)
            ax.set_title('Box Plot распределения результатов', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
        elif chart_type == 'percentiles':
            fig, ax = plt.subplots(figsize=(12, 8))
            
            percentiles = list(range(1, 100))
            percentile_values = np.percentile(values, percentiles)
            
            ax.plot(percentiles, percentile_values, linewidth=2, color='blue')
            ax.fill_between(percentiles, percentile_values, alpha=0.3, color='lightblue')
            
            # Highlight key percentiles
            key_percentiles = [5, 25, 50, 75, 95]
            for p in key_percentiles:
                val = np.percentile(values, p)
                ax.plot(p, val, 'ro', markersize=8)
                ax.annotate(f'{p}%\n{val:,.0f}€', (p, val), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=10)
            
            ax.set_xlabel('Процентиль', fontsize=12)
            ax.set_ylabel('Стоимость инвестиций (€)', fontsize=12)
            ax.set_title('Кривая процентилей', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        else:
            return jsonify({'error': 'Unknown chart type'}), 400
        
        # Save to bytes
        img = BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        
        # Encode to base64
        img_b64 = base64.b64encode(img.getvalue()).decode()
        
        plt.close()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_b64}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/<format_type>')
def api_export(format_type):
    """Export results in various formats."""
    try:
        # Get data from request
        raw_data = request.args.get('data')
        if not raw_data:
            return jsonify({'error': 'No data provided'}), 400
        
        data = json.loads(raw_data)
        
        if format_type == 'json':
            # Return JSON data
            output = BytesIO()
            output.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=f'monte_carlo_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                mimetype='application/json'
            )
        
        elif format_type == 'csv':
            # Create CSV
            df_data = []
            
            # Parameters
            for key, value in data['parameters'].items():
                df_data.append(['Parameter', key, value, ''])
            
            # Results
            for key, value in data['results'].items():
                unit = '€' if 'value' in key or key == 'total_invested' else ('%' if 'percent' in key or 'risk' in key else '')
                df_data.append(['Result', key, value, unit])
            
            # Percentiles
            for perc, value in data['percentiles'].items():
                df_data.append(['Percentile', f'{perc}%', value, '€'])
            
            df = pd.DataFrame(df_data, columns=['Category', 'Metric', 'Value', 'Unit'])
            
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=f'monte_carlo_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mimetype='text/csv'
            )
        
        else:
            return jsonify({'error': 'Unknown export format'}), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/presets')
def api_presets():
    """Get available presets."""
    return jsonify({
        'success': True,
        'presets': PRESETS
    })


@app.route('/api/compare', methods=['POST'])
def api_compare_strategies():
    """Compare multiple investment strategies."""
    try:
        data = request.json
        strategies = data.get('strategies', [])
        
        if len(strategies) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 strategies required for comparison'
            }), 400
        
        comparison_results = []
        
        for i, strategy in enumerate(strategies):
            # Create parameters for this strategy
            params = AdvancedParameters(
                calculation_mode=CalculationMode(strategy.get('calculation_mode', 'mixed')),
                deposit_type=DepositType(strategy.get('deposit_type', 'monthly')),
                initial_amount=float(strategy.get('initial_amount', 10000)),
                monthly_deposit=float(strategy.get('monthly_deposit', 500)),
                
                interest_rate_min=float(strategy.get('interest_rate_min', 5.0)),
                interest_rate_max=float(strategy.get('interest_rate_max', 10.0)),
                interest_rate_mean=float(strategy.get('interest_rate_mean', 7.5)),
                
                volatility_min=float(strategy.get('volatility_min', 10.0)),
                volatility_max=float(strategy.get('volatility_max', 20.0)),
                volatility_mean=float(strategy.get('volatility_mean', 15.0)),
                
                accumulation_years=int(strategy.get('accumulation_years', 20)),
                withdrawal_years=int(strategy.get('withdrawal_years', 30)),
                
                inflation_rate=float(strategy.get('inflation_rate', 2.5)),
                tax_system=TaxSystem(strategy.get('tax_system', 'german')),
                tax_rate=float(strategy.get('tax_rate', 26.375)),
                
                target_withdrawal_rate=float(strategy.get('target_withdrawal_rate', 4.0)),
                
                management_fee=float(strategy.get('management_fee', 0.5)),
                iterations=int(strategy.get('iterations', 5000))  # Reduced for comparison
            )
            
            # Run calculation
            results = advanced_calculator.calculate_comprehensive(params)
            
            # Add strategy metadata
            results['strategy_name'] = strategy.get('name', f'Strategy {i+1}')
            results['strategy_color'] = strategy.get('color', f'hsl({i*60}, 70%, 50%)')
            
            comparison_results.append(results)
        
        # Generate comparison summary
        comparison_summary = generate_comparison_summary(comparison_results)
        
        return jsonify({
            'success': True,
            'data': {
                'strategies': comparison_results,
                'summary': comparison_summary,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_comparison_summary(results_list):
    """Generate comparison summary statistics."""
    summary = {
        'best_accumulation': None,
        'best_withdrawal': None,
        'lowest_risk': None,
        'highest_return': None,
        'most_efficient': None
    }
    
    best_acc_value = 0
    best_withdrawal_success = 0
    lowest_risk_score = float('inf')
    highest_return = 0
    best_efficiency = 0
    
    for result in results_list:
        strategy_name = result['strategy_name']
        
        # Best accumulation
        if result.get('accumulation_phase'):
            acc_value = result['accumulation_phase']['nominal_stats']['mean']
            if acc_value > best_acc_value:
                best_acc_value = acc_value
                summary['best_accumulation'] = {
                    'strategy': strategy_name,
                    'value': acc_value
                }
        
        # Best withdrawal success
        if result.get('withdrawal_phase'):
            success_rate = result['withdrawal_phase']['success_probability']
            if success_rate > best_withdrawal_success:
                best_withdrawal_success = success_rate
                summary['best_withdrawal'] = {
                    'strategy': strategy_name,
                    'success_rate': success_rate
                }
        
        # Lowest risk (simplified risk score)
        if result.get('risk_metrics'):
            risk_score = 0
            if result['risk_metrics'].get('accumulation'):
                risk_score += result['risk_metrics']['accumulation'].get('volatility', 0)
            if result['risk_metrics'].get('withdrawal'):
                risk_score += result['risk_metrics']['withdrawal'].get('failure_probability', 0)
            
            if risk_score < lowest_risk_score:
                lowest_risk_score = risk_score
                summary['lowest_risk'] = {
                    'strategy': strategy_name,
                    'risk_score': risk_score
                }
        
        # Highest return
        if result.get('combined_analysis'):
            return_pct = result['combined_analysis'].get('lifetime_return_percent', 0)
            if return_pct > highest_return:
                highest_return = return_pct
                summary['highest_return'] = {
                    'strategy': strategy_name,
                    'return_percent': return_pct
                }
        
        # Most efficient (risk-adjusted)
        if result.get('combined_analysis'):
            efficiency = result['combined_analysis'].get('risk_adjusted_score', 0)
            if efficiency > best_efficiency:
                best_efficiency = efficiency
                summary['most_efficient'] = {
                    'strategy': strategy_name,
                    'efficiency_score': efficiency
                }
    
    return summary


@app.route('/api/goal-planning', methods=['POST'])
def api_goal_planning():
    """Goal-based investment planning."""
    try:
        data = request.json
        
        goal_amount = float(data.get('goal_amount', 1000000))  # Target amount
        goal_years = int(data.get('goal_years', 20))  # Time to achieve goal
        current_age = int(data.get('current_age', 30))
        retirement_age = int(data.get('retirement_age', 65))
        
        # Base parameters
        initial_amount = float(data.get('initial_amount', 10000))
        risk_tolerance = data.get('risk_tolerance', 'moderate')  # conservative, moderate, aggressive
        
        # Calculate required monthly contribution
        required_scenarios = calculate_required_contributions(
            goal_amount, goal_years, initial_amount, risk_tolerance
        )
        
        # Plan lifecycle strategy
        lifecycle_plan = plan_lifecycle_strategy(
            current_age, retirement_age, goal_amount, risk_tolerance
        )
        
        return jsonify({
            'success': True,
            'data': {
                'goal_analysis': {
                    'target_amount': goal_amount,
                    'time_horizon': goal_years,
                    'required_scenarios': required_scenarios
                },
                'lifecycle_plan': lifecycle_plan,
                'recommendations': generate_goal_recommendations(
                    required_scenarios, lifecycle_plan, risk_tolerance
                )
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def calculate_required_contributions(goal_amount, years, initial_amount, risk_tolerance):
    """Calculate required monthly contributions for different scenarios."""
    
    # Risk-based return assumptions
    return_scenarios = {
        'conservative': {'mean': 5.0, 'std': 8.0},
        'moderate': {'mean': 7.5, 'std': 15.0},
        'aggressive': {'mean': 10.0, 'std': 25.0}
    }
    
    scenarios = {}
    
    for scenario_name, returns in return_scenarios.items():
        annual_return = returns['mean'] / 100
        monthly_return = (1 + annual_return) ** (1/12) - 1
        total_months = years * 12
        
        # Future value of initial amount
        fv_initial = initial_amount * (1 + annual_return) ** years
        
        # Required future value from monthly contributions
        required_from_monthly = goal_amount - fv_initial
        
        if required_from_monthly <= 0:
            required_monthly = 0
        else:
            # PMT calculation
            if monthly_return == 0:
                required_monthly = required_from_monthly / total_months
            else:
                required_monthly = required_from_monthly * monthly_return / (
                    (1 + monthly_return) ** total_months - 1
                )
        
        scenarios[scenario_name] = {
            'required_monthly': max(0, required_monthly),
            'total_invested': initial_amount + (required_monthly * total_months),
            'expected_return': returns['mean'],
            'risk_level': returns['std'],
            'probability_success': calculate_success_probability(
                required_monthly, years, goal_amount, returns
            )
        }
    
    return scenarios


def calculate_success_probability(monthly_payment, years, goal_amount, return_params):
    """Calculate probability of reaching the goal."""
    # Simplified Monte Carlo for goal probability
    import numpy as np
    
    simulations = 1000
    successes = 0
    
    for _ in range(simulations):
        # Generate random annual returns
        annual_returns = np.random.normal(
            return_params['mean']/100, 
            return_params['std']/100, 
            years
        )
        
        # Simulate portfolio growth
        portfolio_value = 0
        for year in range(years):
            portfolio_value *= (1 + annual_returns[year])
            portfolio_value += monthly_payment * 12
        
        if portfolio_value >= goal_amount:
            successes += 1
    
    return (successes / simulations) * 100


def plan_lifecycle_strategy(current_age, retirement_age, goal_amount, base_risk_tolerance):
    """Plan age-based investment strategy."""
    
    phases = []
    years_to_retirement = retirement_age - current_age
    
    # Young phase (aggressive)
    if current_age < 40:
        phases.append({
            'phase': 'young_aggressive',
            'age_range': [current_age, min(40, retirement_age)],
            'duration_years': min(40, retirement_age) - current_age,
            'recommended_allocation': {
                'stocks': 90,
                'bonds': 10
            },
            'expected_return': 9.5,
            'volatility': 22,
            'description': 'Агрессивный рост с высокой долей акций'
        })
    
    # Middle phase (moderate)
    if current_age < 55 and retirement_age > 40:
        start_age = max(current_age, 40)
        end_age = min(55, retirement_age)
        if end_age > start_age:
            phases.append({
                'phase': 'middle_moderate',
                'age_range': [start_age, end_age],
                'duration_years': end_age - start_age,
                'recommended_allocation': {
                    'stocks': 70,
                    'bonds': 30
                },
                'expected_return': 7.5,
                'volatility': 16,
                'description': 'Сбалансированный рост с умеренным риском'
            })
    
    # Pre-retirement phase (conservative)
    if retirement_age > 55:
        start_age = max(current_age, 55)
        if retirement_age > start_age:
            phases.append({
                'phase': 'pre_retirement',
                'age_range': [start_age, retirement_age],
                'duration_years': retirement_age - start_age,
                'recommended_allocation': {
                    'stocks': 50,
                    'bonds': 50
                },
                'expected_return': 6.0,
                'volatility': 12,
                'description': 'Консервативная стратегия перед пенсией'
            })
    
    return {
        'phases': phases,
        'total_duration': years_to_retirement,
        'rebalancing_schedule': 'Ежегодная ребалансировка',
        'risk_adjustment': 'Снижение риска с возрастом (rule of thumb: 100 - возраст = % в акциях)'
    }


def generate_goal_recommendations(required_scenarios, lifecycle_plan, risk_tolerance):
    """Generate personalized recommendations."""
    
    recommendations = []
    
    # Contribution recommendations
    moderate_scenario = required_scenarios.get('moderate', {})
    required_monthly = moderate_scenario.get('required_monthly', 0)
    
    if required_monthly > 0:
        recommendations.append({
            'type': 'contribution',
            'priority': 'high',
            'message': f'Для достижения цели рекомендуется инвестировать {required_monthly:.0f}€ в месяц при умеренной стратегии'
        })
    
    # Risk tolerance recommendations
    if risk_tolerance == 'conservative':
        conservative_monthly = required_scenarios.get('conservative', {}).get('required_monthly', 0)
        if conservative_monthly > required_monthly * 1.5:
            recommendations.append({
                'type': 'risk',
                'priority': 'medium',
                'message': 'Консервативная стратегия требует значительно больших взносов. Рассмотрите умеренный риск для оптимизации.'
            })
    
    # Time horizon recommendations
    if lifecycle_plan['total_duration'] < 10:
        recommendations.append({
            'type': 'time',
            'priority': 'high',
            'message': 'Короткий инвестиционный горизонт увеличивает риск. Рассмотрите более консервативную стратегию или увеличение взносов.'
        })
    
    # Diversification recommendations
    recommendations.append({
        'type': 'diversification',
        'priority': 'medium',
        'message': 'Рекомендуется диверсификация по географическим регионам и классам активов для снижения риска.'
    })
    
    return recommendations


# Additional utility routes
@app.route('/api/portfolio-rebalancing', methods=['POST'])
def api_portfolio_rebalancing():
    """Simulate portfolio rebalancing strategies."""
    try:
        data = request.json
        
        # Rebalancing parameters
        initial_allocation = data.get('initial_allocation', {'stocks': 60, 'bonds': 40})
        rebalancing_frequency = data.get('rebalancing_frequency', 12)  # months
        threshold_rebalancing = data.get('threshold_rebalancing', False)
        threshold_percent = data.get('threshold_percent', 5)  # %
        
        # Simulate different rebalancing strategies
        strategies = {
            'no_rebalancing': simulate_rebalancing(initial_allocation, 0, False, 0),
            'annual_rebalancing': simulate_rebalancing(initial_allocation, 12, False, 0),
            'quarterly_rebalancing': simulate_rebalancing(initial_allocation, 3, False, 0),
            'threshold_rebalancing': simulate_rebalancing(initial_allocation, 0, True, threshold_percent)
        }
        
        return jsonify({
            'success': True,
            'data': strategies
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def simulate_rebalancing(allocation, frequency_months, use_threshold, threshold_pct):
    """Simulate portfolio rebalancing strategy."""
    import numpy as np
    
    # Simplified simulation
    years = 20
    months = years * 12
    
    # Asset return assumptions
    stock_return_annual = 0.09
    bond_return_annual = 0.04
    stock_volatility = 0.18
    bond_volatility = 0.06
    
    # Convert to monthly
    stock_return_monthly = (1 + stock_return_annual) ** (1/12) - 1
    bond_return_monthly = (1 + bond_return_annual) ** (1/12) - 1
    stock_vol_monthly = stock_volatility / np.sqrt(12)
    bond_vol_monthly = bond_volatility / np.sqrt(12)
    
    # Simulation
    simulations = 100
    final_values = []
    
    for sim in range(simulations):
        # Starting values
        stock_value = allocation['stocks'] / 100 * 10000
        bond_value = allocation['bonds'] / 100 * 10000
        total_value = stock_value + bond_value
        
        rebalancing_costs = 0
        last_rebalance = 0
        
        for month in range(months):
            # Generate returns
            stock_return = np.random.normal(stock_return_monthly, stock_vol_monthly)
            bond_return = np.random.normal(bond_return_monthly, bond_vol_monthly)
            
            # Apply returns
            stock_value *= (1 + stock_return)
            bond_value *= (1 + bond_return)
            total_value = stock_value + bond_value
            
            # Check rebalancing
            should_rebalance = False
            
            if frequency_months > 0 and (month - last_rebalance) >= frequency_months:
                should_rebalance = True
            elif use_threshold:
                current_stock_pct = (stock_value / total_value) * 100
                target_stock_pct = allocation['stocks']
                if abs(current_stock_pct - target_stock_pct) >= threshold_pct:
                    should_rebalance = True
            
            if should_rebalance:
                # Rebalance to target allocation
                target_stock_value = total_value * allocation['stocks'] / 100
                target_bond_value = total_value * allocation['bonds'] / 100
                
                # Calculate rebalancing cost (0.1% of traded amount)
                traded_amount = abs(stock_value - target_stock_value)
                rebalancing_costs += traded_amount * 0.001
                
                stock_value = target_stock_value
                bond_value = target_bond_value
                last_rebalance = month
        
        final_values.append(total_value - rebalancing_costs)
    
    return {
        'mean_final_value': np.mean(final_values),
        'median_final_value': np.median(final_values),
        'std_final_value': np.std(final_values),
        'total_rebalancing_costs': np.mean([sim for sim in final_values]),  # Simplified
        'sharpe_ratio': (np.mean(final_values) - 10000) / np.std(final_values) if np.std(final_values) > 0 else 0
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)