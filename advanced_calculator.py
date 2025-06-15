#!/usr/bin/env python3
"""
Advanced Monte Carlo Investment Calculator

Enhanced calculation engine with multiple modes, inflation, taxes,
withdrawal phase, and advanced portfolio analysis capabilities.
"""

import numpy as np
from scipy.stats import norm, lognorm, beta
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Union
from enum import Enum
import pandas as pd
from joblib import Parallel, delayed
import warnings
warnings.filterwarnings('ignore')


class CalculationMode(Enum):
    """Investment calculation modes."""
    ACCUMULATION = "accumulation"  # Фаза накопления
    WITHDRAWAL = "withdrawal"      # Фаза снятия (Entsparphase)
    MIXED = "mixed"               # Смешанная фаза


class DepositType(Enum):
    """Types of deposits."""
    MONTHLY = "monthly"           # Ежемесячные взносы
    LUMP_SUM = "lump_sum"        # Единоразовый взнос
    IRREGULAR = "irregular"       # Нерегулярные взносы


class TaxSystem(Enum):
    """Tax systems."""
    GERMAN = "german"            # Немецкая система
    SIMPLE = "simple"            # Простая система (фиксированный %)
    NONE = "none"               # Без налогов


@dataclass
class AdvancedParameters:
    """Advanced calculation parameters."""
    
    # Basic parameters
    calculation_mode: CalculationMode = CalculationMode.ACCUMULATION
    deposit_type: DepositType = DepositType.MONTHLY
    
    # Financial parameters
    initial_amount: float = 10000.0
    monthly_deposit: float = 500.0
    lump_sum_deposits: List[Tuple[int, float]] = None  # (month, amount)
    
    # Interest rate (Monte Carlo ranges)
    interest_rate_min: float = 5.0
    interest_rate_max: float = 12.0
    interest_rate_mean: float = 8.0
    volatility_min: float = 10.0
    volatility_max: float = 25.0
    volatility_mean: float = 15.0
    
    # Time parameters
    accumulation_years: int = 20
    withdrawal_years: int = 30
    
    # Inflation and taxes
    inflation_rate: float = 2.5
    inflation_volatility: float = 1.0
    tax_system: TaxSystem = TaxSystem.GERMAN
    tax_rate: float = 26.375  # German Abgeltungssteuer
    
    # Withdrawal phase
    target_withdrawal_rate: float = 4.0  # SWR in %
    withdrawal_strategy: str = "fixed_percentage"  # fixed_amount, fixed_percentage, dynamic
    
    # Advanced options
    rebalancing_frequency: int = 12  # months
    management_fee: float = 0.5  # % per year
    consider_sequence_risk: bool = True
    
    # Simulation parameters
    iterations: int = 10000
    confidence_levels: List[float] = None
    
    def __post_init__(self):
        if self.lump_sum_deposits is None:
            self.lump_sum_deposits = []
        if self.confidence_levels is None:
            self.confidence_levels = [99, 95, 90, 75, 50, 25, 10, 5, 1]


class AdvancedMonteCarloCalculator:
    """Advanced Monte Carlo calculator with multiple modes and features."""
    
    def __init__(self):
        self.currency = "€"
        self.results_cache = {}
    
    def calculate_comprehensive(self, params: AdvancedParameters) -> Dict:
        """Run comprehensive Monte Carlo analysis."""
        
        results = {
            'parameters': self._serialize_parameters(params),
            'accumulation_phase': None,
            'withdrawal_phase': None,
            'combined_analysis': None,
            'risk_metrics': None,
            'charts_data': None
        }
        
        if params.calculation_mode in [CalculationMode.ACCUMULATION, CalculationMode.MIXED]:
            results['accumulation_phase'] = self._calculate_accumulation_phase(params)
        
        if params.calculation_mode in [CalculationMode.WITHDRAWAL, CalculationMode.MIXED]:
            # For withdrawal phase, use accumulated amount or initial amount
            if results['accumulation_phase']:
                withdrawal_start_amount = results['accumulation_phase']['final_amount_mean']
            else:
                withdrawal_start_amount = params.initial_amount
            
            results['withdrawal_phase'] = self._calculate_withdrawal_phase(
                params, withdrawal_start_amount
            )
        
        # Combined analysis
        results['combined_analysis'] = self._calculate_combined_analysis(results, params)
        
        # Risk metrics
        results['risk_metrics'] = self._calculate_risk_metrics(results, params)
        
        # Prepare chart data
        results['charts_data'] = self._prepare_charts_data(results, params)
        
        return results
    
    def _calculate_accumulation_phase(self, params: AdvancedParameters) -> Dict:
        """Calculate accumulation phase with Monte Carlo simulation."""
        
        # Run parallel simulations
        simulation_results = Parallel(n_jobs=-1)(
            delayed(self._simulate_accumulation_scenario)(params, i) 
            for i in range(params.iterations)
        )
        
        # Extract results
        final_amounts = [result['final_amount'] for result in simulation_results]
        monthly_data = [result['monthly_data'] for result in simulation_results]
        
        # Calculate statistics
        stats = self._calculate_statistics(final_amounts, params.confidence_levels)
        
        # Real vs nominal analysis
        real_amounts = self._apply_inflation_adjustment(final_amounts, params)
        real_stats = self._calculate_statistics(real_amounts, params.confidence_levels)
        
        # Tax impact analysis
        after_tax_amounts = self._apply_tax_calculation(final_amounts, params)
        tax_stats = self._calculate_statistics(after_tax_amounts, params.confidence_levels)
        
        return {
            'final_amounts': final_amounts[:1000],  # Limit for web transfer
            'monthly_progression': self._aggregate_monthly_data(monthly_data),
            'nominal_stats': stats,
            'real_stats': real_stats,
            'after_tax_stats': tax_stats,
            'total_invested': self._calculate_total_invested(params),
            'inflation_impact': self._calculate_inflation_impact(stats, real_stats),
            'tax_impact': self._calculate_tax_impact(stats, tax_stats),
            'final_amount_mean': stats['mean']
        }
    
    def _calculate_withdrawal_phase(self, params: AdvancedParameters, start_amount: float) -> Dict:
        """Calculate withdrawal phase (Entsparphase) with Monte Carlo simulation."""
        
        # Run parallel simulations for withdrawal phase
        simulation_results = Parallel(n_jobs=-1)(
            delayed(self._simulate_withdrawal_scenario)(params, start_amount, i) 
            for i in range(params.iterations)
        )
        
        # Extract results
        success_rates = []
        final_amounts = []
        withdrawal_amounts = []
        monthly_balances = []
        
        for result in simulation_results:
            success_rates.append(result['success'])
            final_amounts.append(result['final_amount'])
            withdrawal_amounts.append(result['total_withdrawn'])
            monthly_balances.append(result['monthly_balances'])
        
        # Calculate success probability
        success_probability = np.mean(success_rates) * 100
        
        # Calculate safe withdrawal rates
        swr_analysis = self._calculate_swr_analysis(start_amount, simulation_results, params)
        
        # Sequence of returns risk analysis
        sequence_risk = self._analyze_sequence_risk(monthly_balances, params)
        
        return {
            'start_amount': start_amount,
            'success_probability': success_probability,
            'final_amounts': final_amounts[:1000],
            'withdrawal_amounts': withdrawal_amounts[:1000],
            'monthly_progression': self._aggregate_withdrawal_data(monthly_balances),
            'swr_analysis': swr_analysis,
            'sequence_risk': sequence_risk,
            'recommended_swr': self._calculate_recommended_swr(success_probability, params),
            'monthly_income_stats': self._calculate_income_statistics(simulation_results, params)
        }
    
    def _simulate_accumulation_scenario(self, params: AdvancedParameters, seed: int) -> Dict:
        """Simulate single accumulation scenario."""
        np.random.seed(seed)
        
        total_months = params.accumulation_years * 12
        balance = params.initial_amount
        monthly_data = []
        
        # Generate market conditions for entire period
        market_conditions = self._generate_market_conditions(total_months, params)
        
        for month in range(total_months):
            # Monthly return
            monthly_return = market_conditions['returns'][month]
            
            # Apply management fees
            monthly_fee = params.management_fee / 12 / 100
            monthly_return -= monthly_fee
            
            # Growth
            balance *= (1 + monthly_return)
            
            # Add deposits
            if params.deposit_type == DepositType.MONTHLY:
                # Monthly deposits with inflation adjustment
                inflation_factor = (1 + params.inflation_rate/100) ** (month/12)
                adjusted_deposit = params.monthly_deposit * inflation_factor
                balance += adjusted_deposit
            
            # Add lump sum deposits
            for lump_month, lump_amount in params.lump_sum_deposits:
                if month == lump_month:
                    balance += lump_amount
            
            # Store monthly data
            monthly_data.append({
                'month': month,
                'balance': balance,
                'return': monthly_return,
                'inflation': market_conditions['inflation'][month]
            })
        
        return {
            'final_amount': balance,
            'monthly_data': monthly_data
        }
    
    def _simulate_withdrawal_scenario(self, params: AdvancedParameters, start_amount: float, seed: int) -> Dict:
        """Simulate single withdrawal scenario."""
        np.random.seed(seed + 100000)  # Different seed space
        
        total_months = params.withdrawal_years * 12
        balance = start_amount
        total_withdrawn = 0
        monthly_balances = []
        
        # Generate market conditions
        market_conditions = self._generate_market_conditions(total_months, params)
        
        # Calculate monthly withdrawal amount
        if params.withdrawal_strategy == "fixed_percentage":
            base_monthly_withdrawal = start_amount * (params.target_withdrawal_rate / 100) / 12
        elif params.withdrawal_strategy == "fixed_amount":
            base_monthly_withdrawal = start_amount * (params.target_withdrawal_rate / 100) / 12
        else:  # dynamic
            base_monthly_withdrawal = start_amount * (params.target_withdrawal_rate / 100) / 12
        
        for month in range(total_months):
            # Calculate withdrawal amount for this month
            if params.withdrawal_strategy == "fixed_percentage":
                monthly_withdrawal = balance * (params.target_withdrawal_rate / 100) / 12
            elif params.withdrawal_strategy == "dynamic":
                # Adjust based on portfolio performance
                if month > 0:
                    performance_factor = balance / start_amount
                    monthly_withdrawal = base_monthly_withdrawal * max(0.5, min(1.5, performance_factor))
                else:
                    monthly_withdrawal = base_monthly_withdrawal
            else:  # fixed_amount
                # Adjust for inflation
                inflation_factor = (1 + params.inflation_rate/100) ** (month/12)
                monthly_withdrawal = base_monthly_withdrawal * inflation_factor
            
            # Withdraw money
            balance -= monthly_withdrawal
            total_withdrawn += monthly_withdrawal
            
            # Check if portfolio is depleted
            if balance <= 0:
                balance = 0
                success = False
            else:
                success = True
            
            # Monthly return
            if balance > 0:
                monthly_return = market_conditions['returns'][month]
                monthly_fee = params.management_fee / 12 / 100
                monthly_return -= monthly_fee
                balance *= (1 + monthly_return)
            
            monthly_balances.append({
                'month': month,
                'balance': balance,
                'withdrawal': monthly_withdrawal,
                'return': market_conditions['returns'][month] if balance > 0 else 0
            })
        
        # Success if portfolio lasted the entire period
        success = balance > 0
        
        return {
            'success': success,
            'final_amount': balance,
            'total_withdrawn': total_withdrawn,
            'monthly_balances': monthly_balances
        }
    
    def _generate_market_conditions(self, months: int, params: AdvancedParameters) -> Dict:
        """Generate realistic market conditions with correlations."""
        
        # Generate interest rates (annual)
        if params.interest_rate_min == params.interest_rate_max:
            annual_rates = np.full(months//12 + 1, params.interest_rate_mean)
        else:
            # Use beta distribution for realistic rate distribution
            a, b = self._beta_params_from_mean_range(
                params.interest_rate_mean, 
                params.interest_rate_min, 
                params.interest_rate_max
            )
            annual_rates = beta.rvs(a, b, size=months//12 + 1)
            annual_rates = (annual_rates * (params.interest_rate_max - params.interest_rate_min) + 
                           params.interest_rate_min)
        
        # Generate volatility
        if params.volatility_min == params.volatility_max:
            annual_volatilities = np.full(months//12 + 1, params.volatility_mean)
        else:
            a, b = self._beta_params_from_mean_range(
                params.volatility_mean,
                params.volatility_min,
                params.volatility_max
            )
            annual_volatilities = beta.rvs(a, b, size=months//12 + 1)
            annual_volatilities = (annual_volatilities * (params.volatility_max - params.volatility_min) + 
                                  params.volatility_min)
        
        # Convert to monthly and generate returns
        monthly_returns = []
        monthly_inflation = []
        
        for month in range(months):
            year_idx = month // 12
            
            # Monthly return from annual rate and volatility
            annual_rate = annual_rates[min(year_idx, len(annual_rates)-1)] / 100
            annual_vol = annual_volatilities[min(year_idx, len(annual_volatilities)-1)] / 100
            
            # Convert to monthly
            monthly_rate = (1 + annual_rate) ** (1/12) - 1
            monthly_vol = annual_vol / np.sqrt(12)
            
            # Generate return with some autocorrelation for realism
            if month == 0:
                monthly_return = norm.rvs(monthly_rate, monthly_vol)
            else:
                # Add autocorrelation (markets trend)
                autocorr = 0.1
                monthly_return = (autocorr * monthly_returns[-1] + 
                                (1 - autocorr) * norm.rvs(monthly_rate, monthly_vol))
            
            monthly_returns.append(monthly_return)
            
            # Generate inflation
            base_inflation = params.inflation_rate / 100 / 12
            inflation_vol = params.inflation_volatility / 100 / 12
            monthly_inflation.append(norm.rvs(base_inflation, inflation_vol))
        
        return {
            'returns': monthly_returns,
            'inflation': monthly_inflation
        }
    
    def _beta_params_from_mean_range(self, mean: float, min_val: float, max_val: float) -> Tuple[float, float]:
        """Calculate beta distribution parameters from mean and range."""
        if max_val <= min_val:
            return 2.0, 2.0
        
        # Normalize mean to [0,1] range
        normalized_mean = (mean - min_val) / (max_val - min_val)
        normalized_mean = max(0.01, min(0.99, normalized_mean))  # Avoid edge cases
        
        # Use method of moments with assumed variance
        variance = 0.04  # Reasonable assumption for financial data
        
        # Calculate alpha and beta
        alpha = normalized_mean * (normalized_mean * (1 - normalized_mean) / variance - 1)
        beta_param = (1 - normalized_mean) * (normalized_mean * (1 - normalized_mean) / variance - 1)
        
        # Ensure positive values
        alpha = max(0.5, alpha)
        beta_param = max(0.5, beta_param)
        
        return alpha, beta_param
    
    def _calculate_statistics(self, values: List[float], confidence_levels: List[float]) -> Dict:
        """Calculate comprehensive statistics."""
        values_array = np.array(values)
        
        return {
            'mean': float(np.mean(values_array)),
            'median': float(np.median(values_array)),
            'std': float(np.std(values_array)),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'percentiles': {
                str(p): float(np.percentile(values_array, p)) 
                for p in confidence_levels
            },
            'skewness': float(self._calculate_skewness(values_array)),
            'kurtosis': float(self._calculate_kurtosis(values_array))
        }
    
    def _calculate_skewness(self, values: np.ndarray) -> float:
        """Calculate skewness of distribution."""
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return 0
        return np.mean(((values - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, values: np.ndarray) -> float:
        """Calculate kurtosis of distribution."""
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return 0
        return np.mean(((values - mean) / std) ** 4) - 3
    
    def _apply_inflation_adjustment(self, nominal_amounts: List[float], params: AdvancedParameters) -> List[float]:
        """Apply inflation adjustment to get real purchasing power."""
        inflation_factor = (1 + params.inflation_rate/100) ** params.accumulation_years
        return [amount / inflation_factor for amount in nominal_amounts]
    
    def _apply_tax_calculation(self, amounts: List[float], params: AdvancedParameters) -> List[float]:
        """Calculate after-tax amounts based on tax system."""
        if params.tax_system == TaxSystem.NONE:
            return amounts
        
        total_invested = self._calculate_total_invested(params)
        after_tax_amounts = []
        
        for amount in amounts:
            if amount <= total_invested:
                # No gains, no tax
                after_tax_amounts.append(amount)
            else:
                gains = amount - total_invested
                if params.tax_system == TaxSystem.GERMAN:
                    # German system with Freibetrag
                    freibetrag = 1000  # €1000 tax-free gains per year (simplified)
                    taxable_gains = max(0, gains - freibetrag)
                    tax = taxable_gains * (params.tax_rate / 100)
                elif params.tax_system == TaxSystem.SIMPLE:
                    tax = gains * (params.tax_rate / 100)
                else:
                    tax = 0
                
                after_tax_amounts.append(amount - tax)
        
        return after_tax_amounts
    
    def _calculate_total_invested(self, params: AdvancedParameters) -> float:
        """Calculate total amount invested."""
        total = params.initial_amount
        
        if params.deposit_type == DepositType.MONTHLY:
            # Include inflation adjustment for monthly deposits
            total_monthly = 0
            for year in range(params.accumulation_years):
                inflation_factor = (1 + params.inflation_rate/100) ** year
                yearly_deposits = params.monthly_deposit * 12 * inflation_factor
                total_monthly += yearly_deposits
            total += total_monthly
        
        # Add lump sum deposits
        for _, amount in params.lump_sum_deposits:
            total += amount
        
        return total
    
    def _calculate_swr_analysis(self, start_amount: float, simulation_results: List[Dict], params: AdvancedParameters) -> Dict:
        """Calculate safe withdrawal rate analysis."""
        swr_rates = np.arange(2.0, 8.1, 0.5)  # Test SWR from 2% to 8%
        success_rates = {}
        
        for swr in swr_rates:
            successes = 0
            for result in simulation_results:
                # Recalculate with this SWR
                annual_withdrawal = start_amount * (swr / 100)
                if result['total_withdrawn'] <= annual_withdrawal * params.withdrawal_years:
                    successes += 1
            
            success_rate = (successes / len(simulation_results)) * 100
            success_rates[str(swr)] = success_rate
        
        # Find SWR with 95% success rate
        swr_95 = 2.0
        for swr, success_rate in success_rates.items():
            if success_rate >= 95:
                swr_95 = float(swr)
                break
        
        return {
            'success_rates_by_swr': success_rates,
            'swr_95_percent': swr_95,
            'swr_90_percent': self._find_swr_for_success_rate(success_rates, 90),
            'swr_80_percent': self._find_swr_for_success_rate(success_rates, 80)
        }
    
    def _find_swr_for_success_rate(self, success_rates: Dict, target_rate: float) -> float:
        """Find SWR for given success rate."""
        for swr, success_rate in success_rates.items():
            if success_rate >= target_rate:
                return float(swr)
        return 2.0  # Conservative fallback
    
    def _analyze_sequence_risk(self, monthly_balances: List[List[Dict]], params: AdvancedParameters) -> Dict:
        """Analyze sequence of returns risk."""
        if not params.consider_sequence_risk:
            return {}
        
        # Calculate first 5 years performance impact
        early_returns = []
        late_returns = []
        
        for simulation in monthly_balances:
            if len(simulation) >= 60:  # At least 5 years
                early_months = simulation[:60]
                late_months = simulation[-60:] if len(simulation) >= 120 else simulation[60:]
                
                early_avg_return = np.mean([month['return'] for month in early_months])
                late_avg_return = np.mean([month['return'] for month in late_months])
                
                early_returns.append(early_avg_return)
                late_returns.append(late_avg_return)
        
        return {
            'early_years_return_impact': np.corrcoef(early_returns, [sim[-1]['balance'] for sim in monthly_balances])[0,1] if len(early_returns) > 1 else 0,
            'sequence_risk_score': self._calculate_sequence_risk_score(monthly_balances)
        }
    
    def _calculate_sequence_risk_score(self, monthly_balances: List[List[Dict]]) -> float:
        """Calculate sequence risk score (0-100, higher = more risk)."""
        if not monthly_balances:
            return 0
        
        # Calculate coefficient of variation of final balances
        final_balances = [simulation[-1]['balance'] if simulation else 0 for simulation in monthly_balances]
        mean_balance = np.mean(final_balances)
        std_balance = np.std(final_balances)
        
        if mean_balance == 0:
            return 100
        
        cv = (std_balance / mean_balance) * 100
        return min(100, cv)  # Cap at 100
    
    def _calculate_combined_analysis(self, results: Dict, params: AdvancedParameters) -> Dict:
        """Calculate combined lifecycle analysis."""
        if not results['accumulation_phase'] or not results['withdrawal_phase']:
            return {}
        
        acc_phase = results['accumulation_phase']
        with_phase = results['withdrawal_phase']
        
        # Total lifecycle analysis
        total_invested = acc_phase['total_invested']
        total_withdrawn = np.mean([amount for amount in with_phase['withdrawal_amounts']])
        
        # Lifetime return calculation
        lifetime_return = (total_withdrawn / total_invested - 1) * 100 if total_invested > 0 else 0
        
        # Risk-adjusted return (Sharpe-like ratio)
        returns_volatility = np.std(with_phase['withdrawal_amounts']) / np.mean(with_phase['withdrawal_amounts']) if with_phase['withdrawal_amounts'] else 0
        
        return {
            'total_invested': total_invested,
            'total_withdrawn_mean': total_withdrawn,
            'lifetime_return_percent': lifetime_return,
            'risk_adjusted_score': lifetime_return / (1 + returns_volatility) if returns_volatility > 0 else lifetime_return,
            'success_probability': with_phase['success_probability'],
            'recommended_strategy': self._recommend_strategy(results, params)
        }
    
    def _recommend_strategy(self, results: Dict, params: AdvancedParameters) -> Dict:
        """Recommend optimal strategy based on results."""
        recommendations = []
        
        if results['withdrawal_phase']:
            swr = results['withdrawal_phase']['recommended_swr']
            success_rate = results['withdrawal_phase']['success_probability']
            
            if success_rate < 85:
                recommendations.append({
                    'type': 'warning',
                    'message': f'Низкая вероятность успеха ({success_rate:.1f}%). Рекомендуется снизить SWR до {swr:.1f}%'
                })
            
            if swr < 3.5:
                recommendations.append({
                    'type': 'info',
                    'message': 'Консервативная стратегия. Рассмотрите увеличение доли акций для роста'
                })
        
        if results['accumulation_phase']:
            real_return = results['accumulation_phase']['inflation_impact']['real_return_percent']
            if real_return < 3:
                recommendations.append({
                    'type': 'warning',
                    'message': 'Низкая реальная доходность. Рассмотрите более агрессивную стратегию'
                })
        
        return {
            'recommendations': recommendations,
            'optimal_swr': results['withdrawal_phase']['recommended_swr'] if results['withdrawal_phase'] else 4.0,
            'confidence_level': 'high' if len(recommendations) == 0 else 'medium'
        }
    
    def _calculate_risk_metrics(self, results: Dict, params: AdvancedParameters) -> Dict:
        """Calculate comprehensive risk metrics."""
        risk_metrics = {}
        
        if results['accumulation_phase']:
            acc = results['accumulation_phase']
            risk_metrics['accumulation'] = {
                'volatility': acc['nominal_stats']['std'] / acc['nominal_stats']['mean'] * 100,
                'downside_risk': self._calculate_downside_risk(acc['final_amounts']),
                'max_drawdown': self._estimate_max_drawdown(acc['monthly_progression']),
                'var_95': float(np.percentile(acc['final_amounts'], 5)),
                'cvar_95': float(np.mean([x for x in acc['final_amounts'] if x <= np.percentile(acc['final_amounts'], 5)]))
            }
        
        if results['withdrawal_phase']:
            with_phase = results['withdrawal_phase']
            risk_metrics['withdrawal'] = {
                'failure_probability': 100 - with_phase['success_probability'],
                'sequence_risk': with_phase['sequence_risk'].get('sequence_risk_score', 0),
                'income_volatility': np.std(with_phase['withdrawal_amounts']) / np.mean(with_phase['withdrawal_amounts']) * 100 if with_phase['withdrawal_amounts'] else 0
            }
        
        return risk_metrics
    
    def _calculate_downside_risk(self, values: List[float]) -> float:
        """Calculate downside deviation (semi-standard deviation)."""
        values_array = np.array(values)
        mean_return = np.mean(values_array)
        downside_returns = values_array[values_array < mean_return]
        
        if len(downside_returns) == 0:
            return 0.0
        
        return float(np.sqrt(np.mean((downside_returns - mean_return) ** 2)))
    
    def _estimate_max_drawdown(self, monthly_progression: Dict) -> float:
        """Estimate maximum drawdown from monthly progression."""
        if not monthly_progression or 'mean_balance' not in monthly_progression:
            return 0.0
        
        balances = monthly_progression['mean_balance']
        peak = balances[0]
        max_dd = 0
        
        for balance in balances:
            if balance > peak:
                peak = balance
            dd = (peak - balance) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _aggregate_monthly_data(self, monthly_data: List[List[Dict]]) -> Dict:
        """Aggregate monthly data across all simulations."""
        if not monthly_data:
            return {}
        
        max_months = max(len(simulation) for simulation in monthly_data)
        
        aggregated = {
            'months': list(range(max_months)),
            'mean_balance': [],
            'percentile_5': [],
            'percentile_25': [],
            'percentile_75': [],
            'percentile_95': []
        }
        
        for month in range(max_months):
            month_balances = []
            for simulation in monthly_data:
                if month < len(simulation):
                    month_balances.append(simulation[month]['balance'])
            
            if month_balances:
                aggregated['mean_balance'].append(np.mean(month_balances))
                aggregated['percentile_5'].append(np.percentile(month_balances, 5))
                aggregated['percentile_25'].append(np.percentile(month_balances, 25))
                aggregated['percentile_75'].append(np.percentile(month_balances, 75))
                aggregated['percentile_95'].append(np.percentile(month_balances, 95))
        
        return aggregated
    
    def _aggregate_withdrawal_data(self, monthly_balances: List[List[Dict]]) -> Dict:
        """Aggregate withdrawal phase monthly data."""
        return self._aggregate_monthly_data([[month for month in sim] for sim in monthly_balances])
    
    def _calculate_recommended_swr(self, success_probability: float, params: AdvancedParameters) -> float:
        """Calculate recommended safe withdrawal rate."""
        if success_probability >= 95:
            return params.target_withdrawal_rate
        elif success_probability >= 90:
            return params.target_withdrawal_rate * 0.9
        elif success_probability >= 80:
            return params.target_withdrawal_rate * 0.8
        else:
            return params.target_withdrawal_rate * 0.7
    
    def _calculate_income_statistics(self, simulation_results: List[Dict], params: AdvancedParameters) -> Dict:
        """Calculate income statistics for withdrawal phase."""
        if not simulation_results:
            return {}
        
        # Monthly income analysis
        monthly_incomes = []
        for result in simulation_results:
            if result['monthly_balances']:
                avg_monthly_withdrawal = np.mean([month['withdrawal'] for month in result['monthly_balances']])
                monthly_incomes.append(avg_monthly_withdrawal)
        
        if not monthly_incomes:
            return {}
        
        return {
            'mean_monthly_income': float(np.mean(monthly_incomes)),
            'median_monthly_income': float(np.median(monthly_incomes)),
            'min_monthly_income': float(np.min(monthly_incomes)),
            'max_monthly_income': float(np.max(monthly_incomes)),
            'income_percentiles': {
                '5': float(np.percentile(monthly_incomes, 5)),
                '25': float(np.percentile(monthly_incomes, 25)),
                '75': float(np.percentile(monthly_incomes, 75)),
                '95': float(np.percentile(monthly_incomes, 95))
            }
        }
    
    def _calculate_inflation_impact(self, nominal_stats: Dict, real_stats: Dict) -> Dict:
        """Calculate inflation impact analysis."""
        nominal_mean = nominal_stats['mean']
        real_mean = real_stats['mean']
        
        return {
            'nominal_value': nominal_mean,
            'real_value': real_mean,
            'purchasing_power_loss': (1 - real_mean / nominal_mean) * 100 if nominal_mean > 0 else 0,
            'real_return_percent': (real_mean / nominal_stats.get('invested', nominal_mean) - 1) * 100 if nominal_stats.get('invested', nominal_mean) > 0 else 0
        }
    
    def _calculate_tax_impact(self, pre_tax_stats: Dict, after_tax_stats: Dict) -> Dict:
        """Calculate tax impact analysis."""
        pre_tax_mean = pre_tax_stats['mean']
        after_tax_mean = after_tax_stats['mean']
        
        return {
            'pre_tax_value': pre_tax_mean,
            'after_tax_value': after_tax_mean,
            'tax_cost': pre_tax_mean - after_tax_mean,
            'tax_cost_percent': (1 - after_tax_mean / pre_tax_mean) * 100 if pre_tax_mean > 0 else 0
        }
    
    def _prepare_charts_data(self, results: Dict, params: AdvancedParameters) -> Dict:
        """Prepare data for various chart types."""
        charts_data = {}
        
        if results['accumulation_phase']:
            acc = results['accumulation_phase']
            charts_data['accumulation_distribution'] = {
                'values': acc['final_amounts'],
                'title': 'Распределение конечной стоимости (фаза накопления)'
            }
            
            charts_data['accumulation_timeline'] = {
                'data': acc['monthly_progression'],
                'title': 'Рост портфеля во времени'
            }
        
        if results['withdrawal_phase']:
            with_phase = results['withdrawal_phase']
            charts_data['withdrawal_success'] = {
                'success_rate': with_phase['success_probability'],
                'swr_analysis': with_phase['swr_analysis'],
                'title': 'Анализ безопасного уровня снятия'
            }
            
            charts_data['income_distribution'] = {
                'values': with_phase['withdrawal_amounts'],
                'title': 'Распределение доходов (фаза снятия)'
            }
        
        if results['combined_analysis']:
            charts_data['lifecycle_analysis'] = {
                'data': results['combined_analysis'],
                'title': 'Полный жизненный цикл портфеля'
            }
        
        return charts_data
    
    def _serialize_parameters(self, params: AdvancedParameters) -> Dict:
        """Serialize parameters for JSON response."""
        return {
            'calculation_mode': params.calculation_mode.value,
            'deposit_type': params.deposit_type.value,
            'initial_amount': params.initial_amount,
            'monthly_deposit': params.monthly_deposit,
            'interest_rate_range': [params.interest_rate_min, params.interest_rate_max],
            'volatility_range': [params.volatility_min, params.volatility_max],
            'accumulation_years': params.accumulation_years,
            'withdrawal_years': params.withdrawal_years,
            'inflation_rate': params.inflation_rate,
            'tax_system': params.tax_system.value,
            'tax_rate': params.tax_rate,
            'target_withdrawal_rate': params.target_withdrawal_rate,
            'iterations': params.iterations
        }