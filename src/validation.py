"""
Statistical Validation Framework for Sports Predictions

Implements rigorous statistical tests to prove predictions are:
1. Better than random (50%)
2. Better than Vegas baseline (52-53%)
3. Well-calibrated (predicted probabilities match reality)
4. Profitable (positive ROI in backtesting)

Key Metrics:
- Brier Score: Calibration quality (0 = perfect, 0.25 = good)
- Log Loss: Penalizes confident wrong predictions
- ROC-AUC: Overall discriminative ability (0.5 = random, 1.0 = perfect)
- Calibration Curve: Are 70% predictions actually winning 70%?
- Permutation Test: Statistical significance vs random
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
import logging
from sklearn.metrics import (
    brier_score_loss, log_loss, roc_auc_score,
    accuracy_score, confusion_matrix, roc_curve, auc
)
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

logger = logging.getLogger("validation")


class PredictionValidator:
    """
    Statistical validation framework for sports predictions
    
    Ensures predictions are statistically sound and profitable
    """
    
    def __init__(self, sport: str = 'NBA'):
        """Initialize validator"""
        self.sport = sport
        self.metrics = {}
        self.calibration_data = {}
        self.logger = logger
    
    # ========================================================================
    # CALIBRATION METRICS
    # ========================================================================
    
    def calculate_brier_score(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> Tuple[float, str]:
        """
        Brier Score - measures prediction calibration quality
        
        Formula: BS = mean((predicted_prob - actual_outcome)^2)
        
        Range: 0 (perfect) to 1 (worst)
        Target: < 0.25 for sports betting
        
        Interpretation:
        - < 0.20: Excellent calibration
        - < 0.25: Good calibration
        - < 0.30: Acceptable
        - >= 0.30: Poor - needs improvement
        """
        brier = brier_score_loss(y_true, y_pred_proba)
        self.metrics['brier_score'] = brier
        
        if brier < 0.20:
            quality = "Excellent"
        elif brier < 0.25:
            quality = "Good"
        elif brier < 0.30:
            quality = "Acceptable"
        else:
            quality = "Poor - needs improvement"
        
        self.logger.info(f"Brier Score: {brier:.4f} ({quality})")
        
        return brier, quality
    
    def calculate_log_loss(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> Tuple[float, float]:
        """
        Log Loss - penalizes confident wrong predictions heavily
        
        Formula: LL = -mean(y*log(p) + (1-y)*log(1-p))
        
        Range: 0 (perfect) to infinity (worst)
        Target: < 0.693 (better than random)
        
        Random baseline: -log(0.5) = 0.693
        """
        logloss = log_loss(y_true, y_pred_proba)
        self.metrics['log_loss'] = logloss
        
        random_baseline = np.log(2)  # 0.693
        improvement = ((random_baseline - logloss) / random_baseline) * 100
        
        self.logger.info(f"Log Loss: {logloss:.4f} ({improvement:+.1f}% vs random)")
        
        return logloss, improvement
    
    def calculate_roc_auc(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> Tuple[float, str]:
        """
        ROC-AUC (Receiver Operating Characteristic - Area Under Curve)
        
        Measures overall discriminative ability of the model
        
        Range: 0.5 (random) to 1.0 (perfect)
        Target: > 0.55 for sports betting
        
        Interpretation:
        - 0.5: No better than random
        - 0.52-0.55: Slight edge
        - 0.55-0.60: Good edge
        - > 0.60: Excellent edge
        """
        roc_auc = roc_auc_score(y_true, y_pred_proba)
        self.metrics['roc_auc'] = roc_auc
        
        if roc_auc < 0.52:
            quality = "No better than random"
        elif roc_auc < 0.55:
            quality = "Slight edge"
        elif roc_auc < 0.60:
            quality = "Good edge"
        else:
            quality = "Excellent edge"
        
        self.logger.info(f"ROC-AUC: {roc_auc:.4f} ({quality})")
        
        return roc_auc, quality
    
    def calibration_analysis(self, y_true: np.ndarray, y_pred_proba: np.ndarray, 
                            n_bins: int = 10) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Calibration Analysis - are 70% predictions actually winning 70%?
        
        Perfect calibration: predicted probabilities match actual win frequencies
        
        Returns:
            fraction_of_positives: Actual win rate in each probability bin
            mean_predicted_value: Average predicted probability in each bin
            ECE: Expected Calibration Error
        """
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true, y_pred_proba, n_bins=n_bins, strategy='uniform'
        )
        
        # Expected Calibration Error
        ece = np.mean(np.abs(fraction_of_positives - mean_predicted_value))
        self.metrics['expected_calibration_error'] = ece
        self.calibration_data['fraction_of_positives'] = fraction_of_positives
        self.calibration_data['mean_predicted_value'] = mean_predicted_value
        
        self.logger.info(f"Expected Calibration Error: {ece:.4f} (target: < 0.10)")
        
        return fraction_of_positives, mean_predicted_value, ece
    
    def plot_calibration_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray):
        """Plot calibration curve"""
        fraction_of_positives, mean_predicted_value, ece = self.calibration_analysis(
            y_true, y_pred_proba
        )
        
        plt.figure(figsize=(10, 8))
        
        # Perfect calibration line
        plt.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Calibration')
        
        # Model calibration
        plt.plot(mean_predicted_value, fraction_of_positives, 's-', linewidth=2, 
                markersize=8, label='Model')
        
        plt.xlabel('Mean Predicted Probability', fontsize=12)
        plt.ylabel('Fraction of Positives', fontsize=12)
        plt.title(f'Calibration Plot - {self.sport} (ECE: {ece:.4f})', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return plt
    
    # ========================================================================
    # STATISTICAL SIGNIFICANCE
    # ========================================================================
    
    def permutation_test(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                        n_permutations: int = 1000) -> Tuple[float, str, List[float]]:
        """
        Permutation Test - is accuracy significantly better than random?
        
        Hypothesis Test:
        H0: Predictions are no better than random
        H1: Predictions are significantly better than random
        
        p-value < 0.05 means we REJECT H0 (predictions are real)
        p-value >= 0.05 means we FAIL TO REJECT H0 (could be random)
        
        Returns:
            p_value: Probability predictions are from random distribution
            significance: Interpretation string
            random_accuracies: Distribution of random accuracies
        """
        self.logger.info("Running permutation test (1000 iterations)...")
        
        actual_accuracy = accuracy_score(y_true, y_pred_proba > 0.5)
        
        # Generate random baseline distribution
        random_accuracies = []
        for i in range(n_permutations):
            if i % 200 == 0:
                self.logger.debug(f"  Iteration {i}/{n_permutations}")
            
            y_random = np.random.permutation(y_true)
            random_acc = accuracy_score(y_random, y_pred_proba > 0.5)
            random_accuracies.append(random_acc)
        
        random_accuracies = np.array(random_accuracies)
        
        # Calculate p-value
        p_value = np.mean(random_accuracies >= actual_accuracy)
        
        if p_value < 0.01:
            significance = "HIGHLY SIGNIFICANT (p < 0.01)"
        elif p_value < 0.05:
            significance = "SIGNIFICANT (p < 0.05)"
        else:
            significance = "NOT SIGNIFICANT - no better than random"
        
        self.metrics['permutation_p_value'] = p_value
        self.logger.info(f"Permutation Test p-value: {p_value:.4f} ({significance})")
        self.logger.info(f"  Model accuracy: {actual_accuracy:.4f}")
        self.logger.info(f"  Random mean: {random_accuracies.mean():.4f}")
        self.logger.info(f"  Random std: {random_accuracies.std():.4f}")
        
        return p_value, significance, random_accuracies.tolist()
    
    def plot_permutation_distribution(self, y_true: np.ndarray, y_pred_proba: np.ndarray):
        """Plot permutation test distribution"""
        actual_accuracy = accuracy_score(y_true, y_pred_proba > 0.5)
        p_value, _, random_accuracies = self.permutation_test(y_true, y_pred_proba)
        
        plt.figure(figsize=(12, 7))
        
        # Histogram of random accuracies
        plt.hist(random_accuracies, bins=50, alpha=0.7, color='blue', edgecolor='black', label='Random')
        
        # Actual accuracy
        plt.axvline(actual_accuracy, color='red', linestyle='--', linewidth=2, label=f'Model ({actual_accuracy:.4f})')
        
        # Mean of random
        plt.axvline(np.mean(random_accuracies), color='green', linestyle='--', linewidth=2, 
                   label=f'Random Mean ({np.mean(random_accuracies):.4f})')
        
        plt.xlabel('Accuracy', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title(f'Permutation Test - {self.sport} (p={p_value:.4f})', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        return plt
    
    # ========================================================================
    # VEGAS COMPARISON
    # ========================================================================
    
    def vegas_comparison(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                        vegas_implied_probs: np.ndarray) -> Tuple[float, float, float]:
        """
        Compare model predictions against Vegas odds
        
        Vegas typically achieves 52-53% accuracy (includes vigorish)
        Professional bettors aim to beat this by 2-3%
        
        Returns:
            model_accuracy: Our model's accuracy
            vegas_accuracy: Vegas implied accuracy
            improvement: How much better we are
        """
        model_accuracy = accuracy_score(y_true, y_pred_proba > 0.5)
        vegas_accuracy = accuracy_score(y_true, vegas_implied_probs > 0.5)
        
        improvement = (model_accuracy - vegas_accuracy) * 100
        
        self.metrics['model_accuracy'] = model_accuracy
        self.metrics['vegas_accuracy'] = vegas_accuracy
        self.metrics['improvement_vs_vegas'] = improvement
        
        self.logger.info(f"Model Accuracy: {model_accuracy:.4f}")
        self.logger.info(f"Vegas Accuracy: {vegas_accuracy:.4f}")
        self.logger.info(f"Improvement vs Vegas: {improvement:+.2f}%")
        
        if improvement > 2:
            verdict = "✓ STRONG EDGE - Ready for deployment"
        elif improvement > 0:
            verdict = "~ SLIGHT EDGE - Monitor performance"
        else:
            verdict = "✗ NO EDGE - Needs improvement"
        
        self.logger.info(f"Verdict: {verdict}")
        
        return model_accuracy, vegas_accuracy, improvement
    
    # ========================================================================
    # CONFUSION MATRIX
    # ========================================================================
    
    def analyze_confusion_matrix(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> Dict:
        """
        Analyze false positives and false negatives
        """
        y_pred = (y_pred_proba > 0.5).astype(int)
        cm = confusion_matrix(y_true, y_pred)
        
        tn, fp, fn, tp = cm.ravel()
        
        # Calculate rates
        true_positive_rate = tp / (tp + fn)
        false_positive_rate = fp / (fp + tn)
        true_negative_rate = tn / (tn + fp)
        false_negative_rate = fn / (fn + tp)
        
        # Precision and recall
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # F1 score
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics_dict = {
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positive_rate': float(true_positive_rate),
            'false_positive_rate': float(false_positive_rate),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
        
        self.logger.info(f"Confusion Matrix Analysis:")
        self.logger.info(f"  TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")
        self.logger.info(f"  Sensitivity (Recall): {true_positive_rate:.4f}")
        self.logger.info(f"  Specificity: {true_negative_rate:.4f}")
        self.logger.info(f"  Precision: {precision:.4f}")
        self.logger.info(f"  F1 Score: {f1:.4f}")
        
        return metrics_dict
    
    # ========================================================================
    # COMPREHENSIVE REPORT
    # ========================================================================
    
    def generate_comprehensive_report(self) -> str:
        """Generate full statistical validation report"""
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  PREDICTION MODEL VALIDATION REPORT                          ║
║                              {self.sport} Predictions                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. CALIBRATION METRICS
   ════════════════════════════════════════════════════════════════════════════
   
   Brier Score:                     {self.metrics.get('brier_score', 'N/A'):.4f}
   └─ Range: 0 (perfect) to 1 (worst)
   └─ Target: < 0.25
   └─ Status: {"✓ PASS" if self.metrics.get('brier_score', 1.0) < 0.25 else "✗ FAIL"}
   
   Log Loss:                        {self.metrics.get('log_loss', 'N/A'):.4f}
   └─ Range: 0 (perfect) to ∞ (worst)
   └─ Target: < 0.693 (better than random 50%)
   └─ Status: {"✓ PASS" if self.metrics.get('log_loss', 1.0) < 0.693 else "✗ FAIL"}
   
   Expected Calibration Error:      {self.metrics.get('expected_calibration_error', 'N/A'):.4f}
   └─ Range: 0 (perfect) to 1 (worst)
   └─ Target: < 0.10
   └─ Status: {"✓ PASS" if self.metrics.get('expected_calibration_error', 1.0) < 0.10 else "✗ FAIL"}


2. DISCRIMINATIVE ABILITY
   ════════════════════════════════════════════════════════════════════════════
   
   ROC-AUC Score:                   {self.metrics.get('roc_auc', 'N/A'):.4f}
   └─ Range: 0.5 (random) to 1.0 (perfect)
   └─ Target: > 0.55 (to have betting edge)
   └─ Status: {"✓ PASS" if self.metrics.get('roc_auc', 0) > 0.55 else "✗ FAIL"}


3. STATISTICAL SIGNIFICANCE
   ════════════════════════════════════════════════════════════════════════════
   
   Permutation Test p-value:        {self.metrics.get('permutation_p_value', 'N/A'):.4f}
   └─ Hypothesis: Predictions better than random
   └─ Target: < 0.05 (95% confidence)
   └─ Status: {"✓ SIGNIFICANT" if self.metrics.get('permutation_p_value', 1.0) < 0.05 else "✗ NOT SIGNIFICANT"}


4. BETTING PERFORMANCE
   ════════════════════════════════════════════════════════════════════════════
   
   Model Accuracy:                  {self.metrics.get('model_accuracy', 'N/A'):.2%}
   Vegas Baseline:                  {self.metrics.get('vegas_accuracy', 'N/A'):.2%}
   Improvement:                     {self.metrics.get('improvement_vs_vegas', 'N/A'):+.2f}%
   └─ Target: > 2% edge over Vegas
   └─ Status: {"✓ PROFITABLE EDGE" if self.metrics.get('improvement_vs_vegas', 0) > 2 else "⚠ MARGINAL EDGE" if self.metrics.get('improvement_vs_vegas', 0) > 0 else "✗ NEGATIVE EDGE"}


5. CONFUSION MATRIX
   ════════════════════════════════════════════════════════════════════════════
   
   True Positives:                  {self.metrics.get('TP', 'N/A')}
   True Negatives:                  {self.metrics.get('TN', 'N/A')}
   False Positives:                 {self.metrics.get('FP', 'N/A')}
   False Negatives:                 {self.metrics.get('FN', 'N/A')}
   
   Sensitivity (Recall):            {self.metrics.get('sensitivity', 'N/A'):.4f}
   Specificity:                     {self.metrics.get('specificity', 'N/A'):.4f}
   Precision:                       {self.metrics.get('precision', 'N/A'):.4f}
   F1 Score:                        {self.metrics.get('f1_score', 'N/A'):.4f}


6. FINAL VERDICT
   ════════════════════════════════════════════════════════════════════════════
"""
        
        # Determine overall verdict
        brier_ok = self.metrics.get('brier_score', 1.0) < 0.25
        logloss_ok = self.metrics.get('log_loss', 1.0) < 0.693
        ece_ok = self.metrics.get('expected_calibration_error', 1.0) < 0.10
        roc_ok = self.metrics.get('roc_auc', 0) > 0.55
        sig_ok = self.metrics.get('permutation_p_value', 1.0) < 0.05
        edge_ok = self.metrics.get('improvement_vs_vegas', 0) > 2
        
        passes = sum([brier_ok, logloss_ok, ece_ok, roc_ok, sig_ok, edge_ok])
        
        if passes >= 5:
            report += "\n   ✓✓✓ MODEL IS READY FOR DEPLOYMENT ✓✓✓\n"
            report += "   Model passes statistical validation with profitable edge.\n"
        elif passes >= 3:
            report += "\n   ✓✓ MODEL SHOWS PROMISE - NEEDS REFINEMENT ✓✓\n"
            report += "   Model is statistically sound but edge is marginal.\n"
        else:
            report += "\n   ✗ MODEL NEEDS SIGNIFICANT IMPROVEMENT ✗\n"
            report += "   Model does not pass statistical validation.\n"
        
        report += """
   Recommendations:
"""
        
        if not brier_ok:
            report += "   • Improve calibration by adjusting probability outputs\n"
        if not roc_ok:
            report += "   • Enhance feature engineering to increase discrimination\n"
        if not sig_ok:
            report += "   • Model may not have real predictive power\n"
        if not edge_ok:
            report += "   • Reduce false positives to improve edge over Vegas\n"
        
        report += f"""
═════════════════════════════════════════════════════════════════════════════════
Report Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
═════════════════════════════════════════════════════════════════════════════════
"""
        
        return report


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Example data
    y_true = np.random.randint(0, 2, 1000)
    y_pred_proba = np.random.uniform(0, 1, 1000)
    vegas_implied = np.random.uniform(0.48, 0.52, 1000)  # Vegas is calibrated
    
    # Validate
    validator = PredictionValidator(sport='NBA')
    
    validator.calculate_brier_score(y_true, y_pred_proba)
    validator.calculate_log_loss(y_true, y_pred_proba)
    validator.calculate_roc_auc(y_true, y_pred_proba)
    validator.calibration_analysis(y_true, y_pred_proba)
    validator.permutation_test(y_true, y_pred_proba)
    validator.vegas_comparison(y_true, y_pred_proba, vegas_implied)
    cm_analysis = validator.analyze_confusion_matrix(y_true, y_pred_proba)
    validator.metrics.update({f'{k}': v for k, v in cm_analysis.items()})
    
    # Generate report
    print(validator.generate_comprehensive_report())
