import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def plot_history_and_forecast(historical_data, forecast_data, target_name, 
                               forecast_dates, confidence_intervals=None,
                               model_name="Model", horizon_days=7,
                               save_path=None, show_plot=True):
    """
    Plot historical data and forecast with confidence intervals
    
    Parameters:
    - historical_data: Series or array of historical values
    - forecast_data: Array of forecast values
    - target_name: Name of the target variable
    - forecast_dates: List of dates for forecast
    - confidence_intervals: Optional tuple of (lower, upper) confidence bounds
    - model_name: Name of the forecasting model
    - horizon_days: Forecast horizon in days
    - save_path: Path to save the plot (optional)
    - show_plot: Whether to display the plot
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot historical data (last 60 days)
    hist_to_plot = historical_data.tail(60) if len(historical_data) > 60 else historical_data
    ax.plot(hist_to_plot.index, hist_to_plot.values, 
           label='Historical', color='#2E86AB', linewidth=2.5, marker='o', markersize=3)
    
    # Plot forecast
    ax.plot(forecast_dates, forecast_data, 
           label=f'Forecast ({horizon_days}-day)', color='#E63946', 
           linewidth=2.5, linestyle='--', marker='s', markersize=4)
    
    # Plot confidence interval if provided
    if confidence_intervals is not None:
        lower_ci, upper_ci = confidence_intervals
        ax.fill_between(forecast_dates, lower_ci, upper_ci, 
                        alpha=0.25, color='#E63946', label='95% Confidence Interval')
    
    # Formatting
    ax.set_title(f'{model_name}: {target_name.replace("_", " ").title()} Forecast\n'
                f'History + {horizon_days}-Day Forecast', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel(target_name.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Add vertical line to separate history and forecast
    if len(hist_to_plot) > 0:
        ax.axvline(x=hist_to_plot.index[-1], color='gray', 
                  linestyle=':', linewidth=2, alpha=0.7, label='Forecast Start')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved plot to: {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return fig, ax


def plot_actual_vs_predicted(y_true, y_pred, target_name, model_name="Model",
                             save_path=None, show_plot=True):
    """
    Plot actual vs predicted values
    
    Parameters:
    - y_true: Actual values
    - y_pred: Predicted values
    - target_name: Name of the target variable
    - model_name: Name of the model
    - save_path: Path to save the plot
    - show_plot: Whether to display the plot
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter plot
    ax.scatter(y_true, y_pred, alpha=0.6, s=50, color='#06A77D', edgecolors='black', linewidth=0.5)
    
    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 
           'r--', linewidth=2, label='Perfect Prediction', alpha=0.8)
    
    # Formatting
    ax.set_title(f'{model_name}: Actual vs Predicted\n{target_name.replace("_", " ").title()}', 
                fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Actual Values', fontsize=12, fontweight='bold')
    ax.set_ylabel('Predicted Values', fontsize=12, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Add R² text
    from sklearn.metrics import r2_score
    r2 = r2_score(y_true, y_pred)
    ax.text(0.05, 0.95, f'R² = {r2:.4f}', 
           transform=ax.transAxes, fontsize=12, 
           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved plot to: {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return fig, ax


def plot_feature_importance(feature_names, importances, top_n=15, 
                            model_name="Model", save_path=None, show_plot=True):
    """
    Plot feature importance
    
    Parameters:
    - feature_names: List of feature names
    - importances: Array of feature importance values
    - top_n: Number of top features to display
    - model_name: Name of the model
    - save_path: Path to save the plot
    - show_plot: Whether to display the plot
    """
    # Create DataFrame and sort
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False).head(top_n)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Horizontal bar plot
    colors = plt.cm.viridis(np.linspace(0, 1, len(importance_df)))
    ax.barh(range(len(importance_df)), importance_df['importance'], color=colors)
    ax.set_yticks(range(len(importance_df)))
    ax.set_yticklabels(importance_df['feature'], fontsize=10)
    ax.invert_yaxis()
    
    # Formatting
    ax.set_title(f'{model_name}: Top {top_n} Feature Importance', 
                fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Importance Score', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved plot to: {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return fig, ax


def plot_residuals(y_true, y_pred, target_name, model_name="Model",
                  save_path=None, show_plot=True):
    """
    Plot residuals (prediction errors)
    
    Parameters:
    - y_true: Actual values
    - y_pred: Predicted values
    - target_name: Name of the target variable
    - model_name: Name of the model
    - save_path: Path to save the plot
    - show_plot: Whether to display the plot
    """
    residuals = y_true - y_pred
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Residuals vs Predicted
    axes[0].scatter(y_pred, residuals, alpha=0.6, s=50, color='#F77F00', edgecolors='black', linewidth=0.5)
    axes[0].axhline(y=0, color='r', linestyle='--', linewidth=2)
    axes[0].set_title(f'Residuals vs Predicted\n{model_name}', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Predicted Values', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Residuals', fontsize=11, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # Residuals distribution
    axes[1].hist(residuals, bins=30, color='#06A77D', alpha=0.7, edgecolor='black')
    axes[1].axvline(x=0, color='r', linestyle='--', linewidth=2)
    axes[1].set_title(f'Residuals Distribution\n{model_name}', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Residuals', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved plot to: {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return fig, axes


def plot_multiple_forecasts(historical_data, forecasts_dict, target_name,
                            save_path=None, show_plot=True):
    """
    Plot multiple model forecasts on the same graph
    
    Parameters:
    - historical_data: Series of historical values
    - forecasts_dict: Dict with model names as keys and (dates, values, ci) as values
    - target_name: Name of the target variable
    - save_path: Path to save the plot
    - show_plot: Whether to display the plot
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot historical data
    hist_to_plot = historical_data.tail(60) if len(historical_data) > 60 else historical_data
    ax.plot(hist_to_plot.index, hist_to_plot.values, 
           label='Historical', color='#2E86AB', linewidth=2.5, marker='o', markersize=3)
    
    # Plot forecasts from different models
    colors = ['#E63946', '#F77F00', '#06A77D', '#9D4EDD']
    for idx, (model_name, (dates, values, ci)) in enumerate(forecasts_dict.items()):
        color = colors[idx % len(colors)]
        ax.plot(dates, values, label=f'{model_name} Forecast', 
               color=color, linewidth=2, linestyle='--', marker='s', markersize=3)
        
        if ci is not None:
            lower_ci, upper_ci = ci
            ax.fill_between(dates, lower_ci, upper_ci, alpha=0.15, color=color)
    
    # Formatting
    ax.set_title(f'Model Comparison: {target_name.replace("_", " ").title()} Forecast', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel(target_name.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.xticks(rotation=45, ha='right')
    
    # Add vertical line
    if len(hist_to_plot) > 0:
        ax.axvline(x=hist_to_plot.index[-1], color='gray', 
                  linestyle=':', linewidth=2, alpha=0.7)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved plot to: {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return fig, ax


def plot_correlation_heatmap(data, columns=None, save_path=None, show_plot=True):
    """
    Plot correlation heatmap
    
    Parameters:
    - data: DataFrame with data
    - columns: List of columns to include (optional)
    - save_path: Path to save the plot
    - show_plot: Whether to display the plot
    """
    if columns is None:
        # Select numeric columns
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    
    corr_data = data[columns].corr()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create mask for upper triangle
    mask = np.triu(np.ones_like(corr_data, dtype=bool))
    
    # Plot heatmap
    sns.heatmap(corr_data, mask=mask, annot=True, fmt='.2f', 
               cmap='RdBu_r', center=0, ax=ax, 
               cbar_kws={'shrink': 0.8}, linewidths=0.5)
    
    ax.set_title('Correlation Heatmap', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved plot to: {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return fig, ax


if __name__ == "__main__":
    # Test visualization functions
    print("=" * 60)
    print("VISUALIZATION UTILITIES TEST")
    print("=" * 60)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    historical = pd.Series(
        100 + np.cumsum(np.random.randn(90) * 5),
        index=dates
    )
    
    forecast_dates = pd.date_range(start=dates[-1] + pd.Timedelta(days=1), periods=7, freq='D')
    forecast_values = historical.iloc[-1] + np.cumsum(np.random.randn(7) * 3)
    lower_ci = forecast_values - 10
    upper_ci = forecast_values + 10
    
    print("\n1. Testing History + Forecast plot...")
    plot_history_and_forecast(
        historical, forecast_values, 'total_patients',
        forecast_dates, (lower_ci, upper_ci),
        model_name="Test Model", horizon_days=7,
        save_path='test_forecast.png', show_plot=False
    )
    
    print("\n2. Testing Actual vs Predicted plot...")
    y_true = historical.iloc[-30:]
    y_pred = y_true + np.random.randn(30) * 5
    plot_actual_vs_predicted(
        y_true, y_pred, 'total_patients',
        model_name="Test Model",
        save_path='test_actual_vs_pred.png', show_plot=False
    )
    
    print("\n3. Testing Feature Importance plot...")
    features = [f'feature_{i}' for i in range(20)]
    importances = np.random.rand(20) * 100
    plot_feature_importance(
        features, importances, top_n=10,
        model_name="Test Model",
        save_path='test_feature_importance.png', show_plot=False
    )
    
    print("\n✓ Visualization utilities test completed!")
    print("  Check the generated PNG files in the current directory.")
