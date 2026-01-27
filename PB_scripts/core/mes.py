"""
Method of Equal Shares (MES/Waterflow) helpers.

This module wraps pabutools MES functionality with common patterns
used in the experiment scripts.
"""

from pabutools.rules import method_of_equal_shares
from pabutools.election import Cardinality_Sat, Cost_Sat
import pandas as pd


def run_mes_approval(instance, profile):
    """
    Run MES with cardinality/approval satisfaction.
    
    Args:
        instance: Pabulib instance
        profile: Pabulib profile
        
    Returns:
        Set of selected projects
    """
    return method_of_equal_shares(
        instance=instance,
        profile=profile,
        sat_class=Cardinality_Sat,
    )


def run_mes_cost(instance, profile):
    """
    Run MES with cost satisfaction.
    
    Args:
        instance: Pabulib instance
        profile: Pabulib profile
        
    Returns:
        Set of selected projects
    """
    return method_of_equal_shares(
        instance=instance,
        profile=profile,
        sat_class=Cost_Sat,
    )


def calculate_efficiency(result, initial_budget: float) -> float:
    """
    Calculate budget efficiency of a selection.
    
    Args:
        result: Set of selected projects
        initial_budget: Original budget
        
    Returns:
        Efficiency ratio (0.0 to 1.0)
    """
    total_cost = sum(p.cost for p in result)
    return total_cost / initial_budget if initial_budget > 0 else 0.0


def mes_with_budget_increase_exhaustion(
    instance,
    profile,
    sat_class=Cardinality_Sat,
    stop_on_overspend: bool = True,
):
    """
    Run MES with incremental budget increases until exhaustion.
    
    Args:
        instance: Pabulib instance
        profile: Pabulib profile
        sat_class: Satisfaction class (Cardinality_Sat or Cost_Sat)
        stop_on_overspend: If True, stop when cost exceeds initial budget
        
    Returns:
        Tuple of (result, efficiency, increase_count)
    """
    initial_budget = int(instance.budget_limit)
    increase_counter = 0
    
    while True:
        result = method_of_equal_shares(
            instance=instance,
            profile=profile,
            sat_class=sat_class,
        )
        
        total_cost = sum(p.cost for p in result)
        
        if stop_on_overspend and total_cost > initial_budget:
            break
            
        if len(result) == len(instance):  # All projects selected
            break
            
        increase_counter += 1
        instance.budget_limit = instance.budget_limit + 1

    efficiency = total_cost / initial_budget if initial_budget > 0 else 0.0
    return result, efficiency, increase_counter


def create_mes_results_df(
    result,
    efficiency: float,
    budget_increase_count: int,
    max_increase: float = 0,
    min_increase: float = 0,
    avg_increase: float = 0,
) -> pd.DataFrame:
    """
    Create a standardized results DataFrame for MES experiments.
    """
    data = {
        'selected_projects': [list(result)],
        'efficiency': [efficiency],
        'budget_increase_count': [budget_increase_count],
        'max_budget_increase': [max_increase],
        'min_budget_increase': [min_increase],
        'avg_budget_increase': [avg_increase],
    }
    return pd.DataFrame(data)

