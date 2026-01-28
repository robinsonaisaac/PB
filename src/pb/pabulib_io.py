"""
Pabulib I/O utilities.

Parse Pabulib .pb files into our internal Election representation.
"""

import csv
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

from .types import Election, Project


def parse_pabulib_file(filepath: str) -> Election:
    """
    Parse a Pabulib .pb file into an Election.
    
    Args:
        filepath: Path to the .pb file
        
    Returns:
        Election object with projects, voters, approvals, and budget.
    """
    path = Path(filepath)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into sections
    sections = content.split('\n')
    
    # Parse metadata
    meta = {}
    projects_data = []
    votes_data = []
    
    current_section = None
    header = None
    
    for line in sections:
        line = line.strip()
        if not line:
            continue
        
        if line == 'META':
            current_section = 'META'
            continue
        elif line == 'PROJECTS':
            current_section = 'PROJECTS'
            header = None
            continue
        elif line == 'VOTES':
            current_section = 'VOTES'
            header = None
            continue
        
        if current_section == 'META':
            if ';' in line:
                parts = line.split(';', 1)
                if len(parts) == 2:
                    meta[parts[0]] = parts[1]
        
        elif current_section == 'PROJECTS':
            if header is None:
                header = line.split(';')
            else:
                values = line.split(';')
                if len(values) >= len(header):
                    row = dict(zip(header, values))
                    projects_data.append(row)
        
        elif current_section == 'VOTES':
            if header is None:
                header = line.split(';')
            else:
                values = line.split(';')
                if len(values) >= len(header):
                    row = dict(zip(header, values))
                    votes_data.append(row)
    
    # Extract budget
    budget = Fraction(meta.get('budget', '0'))
    
    # Build projects dict
    projects: Dict[str, Project] = {}
    for row in projects_data:
        pid = row.get('project_id', '')
        cost_str = row.get('cost', '0')
        cost = Fraction(cost_str)
        projects[pid] = Project(id=pid, cost=cost)
    
    # Build voters and approvals
    voters: List[int] = []
    approvals: Dict[int, Set[str]] = {}
    
    # Find the vote column (might be 'vote' or different)
    vote_col = 'vote'
    if votes_data and 'vote' not in votes_data[0]:
        # Try to find it
        for key in votes_data[0].keys():
            if 'vote' in key.lower():
                vote_col = key
                break
    
    for i, row in enumerate(votes_data):
        voter_id = i  # Use 0-indexed integers
        voters.append(voter_id)
        
        vote_str = row.get(vote_col, '')
        if vote_str:
            approved = set(vote_str.split(','))
            # Filter to only valid project ids
            approved = {p for p in approved if p in projects}
        else:
            approved = set()
        
        approvals[voter_id] = approved
    
    return Election(
        projects=projects,
        voters=voters,
        approvals=approvals,
        budget=budget,
    )


def write_results_csv(
    filepath: str,
    selected_projects: Set[str],
    efficiency: Fraction,
    budget_increase_count: int,
    additional_data: Optional[Dict] = None,
):
    """
    Write results to a CSV file.
    
    Args:
        filepath: Output path
        selected_projects: Set of selected project ids
        efficiency: Spending efficiency (fraction of budget used)
        budget_increase_count: Number of budget increases performed
        additional_data: Optional dict of additional columns
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        'selected_projects': [list(selected_projects)],
        'efficiency': [float(efficiency)],
        'budget_increase_count': [budget_increase_count],
    }
    
    if additional_data:
        for key, val in additional_data.items():
            data[key] = [val]
    
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(data.keys()))
        writer.writeheader()
        row = {k: v[0] for k, v in data.items()}
        writer.writerow(row)

