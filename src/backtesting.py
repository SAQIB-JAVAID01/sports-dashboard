"""
Backtesting Framework with Kelly Criterion Bet Sizing

Proves whether predicted edge translates to actual profit

Kelly Criterion:
  Optimal Bet Fraction = (p * b - q) / b
  
  Where:
  - p = win probability (from model)
  - q = 1 - p (loss probability)
  - b = odds payoff (decimal odds - 1)

Example:
  Model predicts 55% win probability on -110 odds (decimal 1.909)
  
  b = 1.909 - 1 = 0.909
  Kelly = (0.55 * 0.909 - 0.45) / 0.909
  Kelly = (0.4999 - 0.45) / 0.909 = 5.5%
  
  Kelly says bet 5.5% of bankroll on this prediction
  
Key Properties:
- Maximizes long-term bankroll growth
- Fractional Kelly (e.g., 25% Kelly = 25% × Kelly fraction) is more conservative
- Conservative Kelly reduces drawdowns at cost of slower growth
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
import logging
from dataclasses import dataclass

logger = logging.getLogger("backtesting")


@dataclass
class Bet:
    """Single bet record"""
    game_id: str
    sport: str
    date: str
    prediction_prob: float
    actual_outcome: int
    odds_decimal: float
    bet_amount: float
    win: bool
    pnl: float


class KellyCriterion:
    """
    Kelly Criterion bet sizing calculator
    """
    
    @staticmethod
    def calculate_kelly_fraction(win_prob: float, odds_decimal: float) -> float:
        """
        Calculate optimal Kelly fraction
        
        Args:
            win_prob: Predicted win probability (0-1)
            odds_decimal: Decimal odds (e.g., 1.909 for -110)
        
        Returns:
            Kelly fraction as percentage of bankroll
        """
        if odds_decimal <= 1:
            raise ValueError("Odds must be > 1")
        
        if not (0 < win_prob < 1):
            raise ValueError("Probability must be between 0 and 1")
        
        b = odds_decimal - 1  # Payoff
        q = 1 - win_prob
        
        kelly = (win_prob * b - q) / b
        
        # Kelly can be negative (bad bet)
        return max(0, kelly)
    
    @staticmethod
    def fractional_kelly(kelly_fraction: float, kelly_multiplier: float = 0.25) -> float:
        """
        Apply fractional Kelly for conservative bet sizing
        
        Args:
            kelly_fraction: Full Kelly fraction
            kelly_multiplier: Fraction to use (0.25 = 1/4 Kelly)
        
        Returns:
            Fractional Kelly amount
        """
        return kelly_fraction * kelly_multiplier
    
    @staticmethod
    def calculate_bet_size(bankroll: float, kelly_fraction: float,
                          fractional: float = 0.25) -> float:
        """
        Calculate bet size based on Kelly Criterion
        
        Args:
            bankroll: Current bankroll
            kelly_fraction: Full Kelly fraction
            fractional: Multiplier for fractional Kelly
        
        Returns:
            Bet amount in dollars
        """
        full_kelly = bankroll * kelly_fraction
        fractional_kelly = full_kelly * fractional
        
        return fractional_kelly


class Backtester:
    """
    Simulate betting strategy and calculate profitability
    """
    
    def __init__(self, initial_bankroll: float = 10000.0, kelly_multiplier: float = 0.25):
        """
        Initialize backtester
        
        Args:
            initial_bankroll: Starting bankroll (default $10k)
            kelly_multiplier: Fraction of Kelly to use (0.25 = conservative)
        """
        self.initial_bankroll = initial_bankroll
        self.kelly_multiplier = kelly_multiplier
        self.bets: List[Bet] = []
        self.logger = logger
    
    # ========================================================================
    # BET PLACEMENT
    # ========================================================================
    
    def place_bet(self, game_id: str, sport: str, date: str,
                 prediction_prob: float, odds_decimal: float,
                 min_probability: float = 0.52) -> bool:
        """
        Decide whether to place a bet based on Kelly Criterion
        
        Args:
            game_id: Game identifier
            sport: Sport (NBA, NFL, etc)
            date: Game date
            prediction_prob: Model's predicted win probability
            odds_decimal: Decimal odds
            min_probability: Minimum probability to bet (default 52%)
        
        Returns:
            True if bet should be placed, False otherwise
        """
        # Don't bet if prediction is below threshold
        if prediction_prob < min_probability:
            return False
        
        # Don't bet on bad odds (negative expected value)
        kelly = KellyCriterion.calculate_kelly_fraction(prediction_prob, odds_decimal)
        if kelly <= 0:
            return False
        
        return True
    
    def backtest_bets(self, games_df: pd.DataFrame, predictions: np.ndarray,
                     odds_column: str = 'odds_decimal') -> Tuple[float, float, float]:
        """
        Backtest betting strategy
        
        Args:
            games_df: DataFrame with games (must have odds_decimal and actual_outcome columns)
            predictions: Array of predicted probabilities
            odds_column: Column name for odds
        
        Returns:
            (final_bankroll, roi, win_rate)
        """
        # Reset index to ensure alignment with predictions array
        games_df = games_df.reset_index(drop=True)
        
        # Ensure predictions length matches games_df length
        if len(predictions) != len(games_df):
            self.logger.warning(f"Predictions length ({len(predictions)}) doesn't match games ({len(games_df)})")
            # Truncate to shorter length
            min_len = min(len(predictions), len(games_df))
            games_df = games_df.iloc[:min_len]
            predictions = predictions[:min_len]
        
        bankroll = self.initial_bankroll
        bets_placed = 0
        bets_won = 0
        total_wagered = 0
        
        self.logger.info(f"Starting backtest with ${bankroll:,.2f}")
        
        for idx, row in games_df.iterrows():
            prediction_prob = predictions[idx]
            odds_decimal = row[odds_column]
            actual_outcome = row['actual_outcome']
            
            # Calculate Kelly
            kelly = KellyCriterion.calculate_kelly_fraction(prediction_prob, odds_decimal)
            
            # Skip if Kelly is too small
            if kelly < 0.001:
                continue
            
            # Calculate bet size (fractional Kelly)
            bet_size = bankroll * kelly * self.kelly_multiplier
            
            # Simulate bet outcome
            if prediction_prob > 0.5:
                win = actual_outcome == 1
            else:
                win = actual_outcome == 0
            
            if win:
                pnl = bet_size * (odds_decimal - 1)
                bets_won += 1
            else:
                pnl = -bet_size
            
            bankroll += pnl
            total_wagered += bet_size
            bets_placed += 1
            
            # Record bet
            bet_record = Bet(
                game_id=row.get('game_id', f'game_{idx}'),
                sport=row.get('sport', 'unknown'),
                date=row.get('date', 'unknown'),
                prediction_prob=prediction_prob,
                actual_outcome=actual_outcome,
                odds_decimal=odds_decimal,
                bet_amount=bet_size,
                win=win,
                pnl=pnl
            )
            self.bets.append(bet_record)
        
        roi = (bankroll - self.initial_bankroll) / self.initial_bankroll
        win_rate = bets_won / bets_placed if bets_placed > 0 else 0
        
        self.logger.info(f"\nBacktest Results:")
        self.logger.info(f"  Bets Placed: {bets_placed}")
        self.logger.info(f"  Bets Won: {bets_won}")
        self.logger.info(f"  Win Rate: {win_rate:.2%}")
        self.logger.info(f"  Total Wagered: ${total_wagered:,.2f}")
        self.logger.info(f"  Final Bankroll: ${bankroll:,.2f}")
        self.logger.info(f"  Profit: ${bankroll - self.initial_bankroll:,.2f}")
        self.logger.info(f"  ROI: {roi:.2%}")
        
        return bankroll, roi, win_rate
    
    # ========================================================================
    # ANALYSIS
    # ========================================================================
    
    def calculate_metrics(self) -> Dict:
        """Calculate comprehensive backtesting metrics"""
        if not self.bets:
            return {}
        
        bets_df = pd.DataFrame([
            {
                'date': bet.date,
                'sport': bet.sport,
                'prediction': bet.prediction_prob,
                'odds': bet.odds_decimal,
                'bet_amount': bet.bet_amount,
                'win': bet.win,
                'pnl': bet.pnl
            }
            for bet in self.bets
        ])
        
        # Basic metrics
        total_bets = len(self.bets)
        total_wins = sum(1 for b in self.bets if b.win)
        total_losses = total_bets - total_wins
        win_rate = total_wins / total_bets if total_bets > 0 else 0
        
        total_wagered = sum(b.bet_amount for b in self.bets)
        total_pnl = sum(b.pnl for b in self.bets)
        roi = total_pnl / self.initial_bankroll
        
        # Advanced metrics
        avg_bet_size = np.mean([b.bet_amount for b in self.bets])
        max_bet_size = max([b.bet_amount for b in self.bets])
        
        # Winning vs losing bets
        winning_pnl = sum(b.pnl for b in self.bets if b.win)
        losing_pnl = sum(b.pnl for b in self.bets if not b.win)
        
        avg_win = winning_pnl / total_wins if total_wins > 0 else 0
        avg_loss = losing_pnl / total_losses if total_losses > 0 else 0
        
        # Profit factor
        profit_factor = winning_pnl / abs(losing_pnl) if losing_pnl != 0 else float('inf')
        
        # Drawdown
        cumulative_pnl = np.cumsum([b.pnl for b in self.bets])
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdowns = cumulative_pnl - running_max
        max_drawdown = np.min(drawdowns)
        
        # Expected value
        avg_prediction = np.mean([b.prediction_prob for b in self.bets])
        
        return {
            'total_bets': total_bets,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'win_rate': win_rate,
            'total_wagered': total_wagered,
            'total_pnl': total_pnl,
            'roi': roi,
            'avg_bet_size': avg_bet_size,
            'max_bet_size': max_bet_size,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'avg_prediction': avg_prediction
        }
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_report(self) -> str:
        """Generate comprehensive backtest report"""
        metrics = self.calculate_metrics()
        
        if not metrics:
            return "No bets to report"
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     KELLY CRITERION BACKTEST REPORT                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

BETTING SUMMARY
═════════════════════════════════════════════════════════════════════════════════

Total Bets Placed:              {metrics['total_bets']:,}
Total Wins:                     {metrics['total_wins']:,}
Total Losses:                   {metrics['total_losses']:,}
Win Rate:                       {metrics['win_rate']:.2%}

FINANCIAL PERFORMANCE
═════════════════════════════════════════════════════════════════════════════════

Initial Bankroll:               ${self.initial_bankroll:,.2f}
Total Amount Wagered:           ${metrics['total_wagered']:,.2f}
Total Profit/Loss:              ${metrics['total_pnl']:,.2f}
Return on Investment (ROI):     {metrics['roi']:.2%}

BETTING STATISTICS
═════════════════════════════════════════════════════════════════════════════════

Average Bet Size:               ${metrics['avg_bet_size']:,.2f}
Maximum Bet Size:               ${metrics['max_bet_size']:,.2f}
Average Winning Bet:            ${metrics['avg_win']:,.2f}
Average Losing Bet:             ${metrics['avg_loss']:,.2f}

Profit Factor:                  {metrics['profit_factor']:.2f}
└─ Ratio of wins to losses
└─ Target: > 1.5 (50% more wins than losses)

Maximum Drawdown:               ${metrics['max_drawdown']:,.2f}
└─ Worst losing streak
└─ Impact: {(metrics['max_drawdown'] / self.initial_bankroll):.2%} of bankroll

MODEL QUALITY
═════════════════════════════════════════════════════════════════════════════════

Average Predicted Probability:  {metrics['avg_prediction']:.2%}
└─ Should be ~55% (5% edge over 50% random)


VERDICT
═════════════════════════════════════════════════════════════════════════════════
"""
        
        if metrics['roi'] > 0.05:
            report += "\n✓✓✓ STRONG PROFITABLE EDGE ✓✓✓\n"
            report += f"Model shows consistent profitability with {metrics['roi']:.1%} ROI\n"
        elif metrics['roi'] > 0:
            report += "\n✓ SLIGHT PROFITABLE EDGE ✓\n"
            report += f"Model is profitable but edge is small ({metrics['roi']:.1%} ROI)\n"
        else:
            report += "\n✗ UNPROFITABLE ✗\n"
            report += "Model does not show consistent profitability\n"
        
        report += f"""
═════════════════════════════════════════════════════════════════════════════════
Report Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
═════════════════════════════════════════════════════════════════════════════════
"""
        
        return report
    
    def plot_bankroll_curve(self) -> 'matplotlib.figure.Figure':
        """Plot bankroll growth over time"""
        import matplotlib.pyplot as plt
        
        cumulative_pnl = np.cumsum([b.pnl for b in self.bets])
        bankroll_curve = self.initial_bankroll + cumulative_pnl
        
        plt.figure(figsize=(14, 7))
        
        plt.plot(bankroll_curve, linewidth=2, color='blue')
        plt.axhline(y=self.initial_bankroll, color='red', linestyle='--', 
                   linewidth=1, alpha=0.7, label='Starting Bankroll')
        
        plt.xlabel('Bet Number', fontsize=12)
        plt.ylabel('Bankroll ($)', fontsize=12)
        plt.title('Bankroll Growth - Kelly Criterion Betting', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=11)
        
        # Format y-axis as currency
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        return plt


class SensitivityAnalysis:
    """
    Analyze how betting results change with different parameters
    """
    
    @staticmethod
    def kelly_multiplier_sensitivity(bets: List[Bet], initial_bankroll: float,
                                    multipliers: np.ndarray = None) -> pd.DataFrame:
        """
        Test backtest results with different Kelly multipliers
        
        Args:
            bets: List of Bet records
            initial_bankroll: Starting bankroll
            multipliers: Array of Kelly multipliers to test
        
        Returns:
            DataFrame with results for each multiplier
        """
        if multipliers is None:
            multipliers = np.array([0.1, 0.2, 0.25, 0.5, 0.75, 1.0])
        
        results = []
        
        for mult in multipliers:
            bankroll = initial_bankroll
            
            for bet in bets:
                kelly = KellyCriterion.calculate_kelly_fraction(
                    bet.prediction_prob, bet.odds_decimal
                )
                bet_size = bankroll * kelly * mult
                
                if bet.win:
                    pnl = bet_size * (bet.odds_decimal - 1)
                else:
                    pnl = -bet_size
                
                bankroll += pnl
            
            roi = (bankroll - initial_bankroll) / initial_bankroll
            
            results.append({
                'kelly_multiplier': mult,
                'final_bankroll': bankroll,
                'profit': bankroll - initial_bankroll,
                'roi': roi
            })
        
        return pd.DataFrame(results)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create sample games data
    n_games = 500
    games = pd.DataFrame({
        'game_id': [f'game_{i}' for i in range(n_games)],
        'sport': np.random.choice(['NBA', 'NFL', 'MLB', 'NHL'], n_games),
        'date': pd.date_range('2023-01-01', periods=n_games),
        'odds_decimal': np.random.uniform(1.8, 2.2, n_games),  # -120 to -110 odds
        'actual_outcome': np.random.randint(0, 2, n_games)
    })
    
    # Predictions slightly better than random (55%)
    predictions = np.random.binomial(1, 0.55, n_games) * 0.1 + np.random.uniform(0.4, 0.6, n_games)
    predictions = np.clip(predictions, 0, 1)
    
    # Backtest
    backtester = Backtester(initial_bankroll=10000.0, kelly_multiplier=0.25)
    final_bankroll, roi, win_rate = backtester.backtest_bets(games, predictions)
    
    # Report
    print(backtester.generate_report())
    
    # Sensitivity analysis
    sensitivity = SensitivityAnalysis.kelly_multiplier_sensitivity(
        backtester.bets, backtester.initial_bankroll
    )
    print("\nKelly Multiplier Sensitivity:")
    print(sensitivity.to_string(index=False))
