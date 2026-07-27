from data_loader import load_all_results
import pandas as pd
from plot_functions import comparison_scatter_plot
import matplotlib.pyplot as plt
import math

# Add src to path for scalable_proportional_pb
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from scalable_proportional_pb.pabulib_io import parse_pabulib_file

def intersect_on_election(*result_dataframes):
  '''
  Return the given dataframes with only the rows remaining that were present in each dataframe
  acording to the `election_name` value.
  
  :param result_dataframes: List of dataframes to be intersected
  '''
  common_elections = set(result_dataframes[0]['election_name'])
  for df in result_dataframes[1:]:
    common_elections = common_elections.intersection(set(df['election_name']))

  return tuple(df[df['election_name'].isin(common_elections)].reset_index(drop=True) for df in result_dataframes)

def merge(column, *dataframes):
  """Merge multiple result DataFrames on the common `election_name` values.
  dataframes should be ("name", dataframe) where name will be the name of the column in the merged dataframe

  Returns a DataFrame with one row per common filename and one column per
  input DataFrame (named according the given name for each dataframe), containing the value
  of `column` for that filename from each DataFrame.
  """
  if not dataframes:
    return pd.DataFrame()

  # Build a list of Series (indexed by filename) containing the requested column
  series_list = []
  for (name,df) in dataframes:
    # Select election_name and column, drop NA filenames and duplicate filenames
    sel = df.loc[:, ['election_name', column]].dropna(subset=['election_name']).drop_duplicates(subset=['election_name']).copy()
    sel = sel.set_index('election_name')
    sel = sel.rename(columns={column: name})
    series_list.append(sel)

  # Inner join all selections on filename to keep only common filenames
  merged = pd.concat(series_list, axis=1, join='inner')
  merged = merged.reset_index()
  return merged

def size_of_outcome_set(result_df):
  """
  Adds a column that contains the size of the outcome set
  
  :param result_df: Dataframe containing results as loaded by the data_loader file
  """
  result_df['size_of_outcome'] = result_df['most_efficient_project_set'].apply(len)
  return result_df

def election_information(result_df):
  """
  Adds a column that contains the corresponding election for that file
  
  :param result_df: Dataframe containing results as loaded by the data_loader file
  """
  def load_election_from_name(election_name):
    election = parse_pabulib_file(f"../Data/{election_name}.pb")
    return election
  
  result_df['election'] = result_df['election_name'].apply(load_election_from_name)
  return result_df

def median_cost_of_projects(result_df):
  """
  Adds a column that contains the median cost of the projects in the outcome
  
  :param result_df: Dataframe containing results as loaded by the data_loader file, and containing column 'election' from the election_information function
  """
  def get_median_cost(row):
    election = row['election']
    project_set = row['most_efficient_project_set']
    costs = [election.projects[p].cost for p in project_set]
    return pd.Series(costs).median()

  result_df['median_cost_of_projects'] = result_df.apply(get_median_cost, axis=1)
  return result_df

def voter_utilities(result_df, utility):
  """
  Adds a column that contains the utilities (cardinal or cost) of each voter for the highest efficiency outcome
  
  :param result_df: Dataframe containing results as loaded by the data_loader file, and containing column 'election' from the election_information function
  :param utility: Either 'cardinal' or 'cost'
  """
  def get_voter_utilities(row):
    election = row['election']
    project_set = row['most_efficient_project_set']
    utilities = []
    for voter in election.voters:
      voter_utility = 0
      for project_id in project_set:
        if project_id in election.approvals[voter]:
          if utility == 'cardinal':
            voter_utility += 1
          elif utility == 'cost':
            voter_utility += election.projects[project_id].cost
      utilities.append(voter_utility)
    return utilities

  col_name = f'voter_utilities_{utility}'
  result_df[col_name] = result_df.apply(get_voter_utilities, axis=1)
  return result_df

def gini_index(result_df, utility):
  """
  Adds a column that contains the gini index for the voters based on their utility (cardinal or cost) for the highest efficiency outcome.
  
  :param result_df: Dataframe containing results as loaded by the data_loader file, and containing column 
  'voter_utilities_{utility}' from the voter_utilities function
  :param utility: Utility to use for calculating gini index. Either 'cost' or 'cardinal'
  """
  def compute_gini(utilities_list):
    """Compute the Gini index for a list of utilities."""
    n = len(utilities_list)
    mean_utility = sum(utilities_list) / n

    # Calculate gini as (average variance) / (2*mean)
    abs_diffs = sum(abs(u_i - u_j) for u_i in utilities_list for u_j in utilities_list)
    gini = abs_diffs / (2 * n * n * mean_utility)
    return gini

  col_name = f'voter_utilities_{utility}'
  gini_col_name = f'gini_index_{utility}'
  result_df[gini_col_name] = result_df[col_name].apply(compute_gini)
  return result_df

def log_nash_welfare(result_df, utility):
  """
  Adds a column that contains the log of the nash welfare of the voters based on their utility (cardinal or cost) for the highest efficiency outcome.
  
  :param result_df: Dataframe containing results as loaded by the data_loader file, and containing column 
  'voter_utilities_{utility}' from the voter_utilities function
  :param utility: Utility to use for calculating nash welfare. Either 'cost' or 'cardinal'
  """
  def compute_log_nash_welfare(utilities_list):
    """Compute the log Nash welfare for a list of utilities."""
    n = len(utilities_list)
    # Use sum of logs to avoid overflow, treating zero utilities carefully
    log_sum = sum(math.log(u) if u > 0 else float('-inf') for u in utilities_list)
    if log_sum == float('-inf'):
      return 0.0
    return log_sum

  col_name = f'voter_utilities_{utility}'
  nash_col_name = f'log_nash_welfare_{utility}'
  result_df[nash_col_name] = result_df[col_name].apply(compute_log_nash_welfare)
  return result_df

def runtime(result_df):
  """
  Adds a column that contains the runtime (elapsed time) from sacct outputs.

  :param result_df: Dataframe containing results as loaded by the data_loader file
  """
  index_file = Path(__file__).parent.parent / "index_to_filename.csv"

  def build_index_map():
    if not index_file.exists():
      return {}
    with open(index_file, "r", encoding="utf-8") as f:
      # index_to_filename.csv is a single row of comma-separated paths
      lines = [line.strip() for line in f if line.strip()]
    if not lines:
      return {}
    # Support multi-line CSV by splitting all lines on commas
    raw_items = []
    for line in lines:
      raw_items.extend([item.strip() for item in line.split(",") if item.strip()])

    mapping = {}
    for idx, item in enumerate(raw_items):
      name = Path(item).stem
      mapping[name] = idx
    return mapping

  index_map = build_index_map()

  def parse_run_info(filepath: str):
    if not filepath:
      return None, None, None
    path = Path(filepath)
    parts = list(path.parts)
    if "results" in parts:
      i = parts.index("results")
      if len(parts) > i + 3:
        return parts[i + 1], parts[i + 2], parts[i + 3]
    for i, part in enumerate(parts):
      if part in {"ees", "mes"} and len(parts) > i + 2:
        return parts[i], parts[i + 1], parts[i + 2]
    return None, None, None

  def read_elapsed(sacct_csv: Path):
    if not sacct_csv.exists():
      return None
    try:
      with open(sacct_csv, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
      if len(lines) < 2:
        return None

      header_line = lines[0]
      data_line = lines[1]

      header = header_line.split(",") if "," in header_line else header_line.split("|")
      data = data_line.split("|") if "|" in data_line else data_line.split(",")

      elapsed_idx = None
      for i, col in enumerate(header):
        if col.strip().lower() == "elapsed":
          elapsed_idx = i
          break

      if elapsed_idx is None or elapsed_idx >= len(data):
        return None
      return data[elapsed_idx].strip()
    except Exception:
      return None
    
  def elapsed_to_seconds(value):
    raw = str(value)
    days = 0
    time_part = raw
    if "-" in raw:
      day_part, time_part = raw.split("-", 1)
      days = int(day_part)

    parts = time_part.split(":")
    if len(parts) == 3:
      h, m, s = parts
    elif len(parts) == 2:
      h, m, s = "0", parts[0], parts[1]
    return days * 86400 + int(h) * 3600 + int(m) * 60 + float(s)

  def get_runtime(row):
    election_name = row["election_name"]

    index = index_map.get(election_name)

    filepath = row["filepath"]

    method, utility, completion = parse_run_info(filepath)

    completion_folder = completion.replace("-", "_")
    sacct_dir = Path(__file__).parent.parent / "sacct_outputs" / f"{method}_{utility}_{completion_folder}"
    sacct_file = sacct_dir / f"{index}.csv"
    elapsed_string = read_elapsed(sacct_file)
    return elapsed_to_seconds(elapsed_string)

  result_df["runtime"] = result_df.apply(get_runtime, axis=1)
  return result_df

def unique_efficiencies(result_df):
  """
  Adds a column that contains the number of unique efficiency values found during the search.
  
  :param result_df: Dataframe containing results as loaded by the data_loader file
  """
  def count_unique(efficiency_list):
    return len(set(efficiency_list))

  result_df['unique_efficiencies'] = result_df['efficiency_list'].apply(count_unique)
  return result_df

def count_thresholds(vals_a, vals_b, label_a="A", label_b="B", context=""):
    ratio = (vals_a / vals_b)
    ratio = ratio[ratio>1.0001]
    counts = {
        ">1.0 times": (ratio > 1.0001).sum(),
        "1.1 times": (ratio >= 1.10).sum(),
        "1.25 times": (ratio >= 1.25).sum(),
        "1.5 times": (ratio >= 1.50).sum(),
        "2.0 times": (ratio >= 2.00).sum(),
    }
    total = len(vals_a)
    prefix = f"{context} " if context else ""
    print(
        f"{prefix}{label_a} vs {label_b} (n={total}):\n"
        f" >1.0 times={counts['>1.0 times']}\n"
        f" 1.1 times={counts['1.1 times']}\n"
        f" 1.25 times={counts['1.25 times']}\n"
        f" 1.5 times={counts['1.5 times']}\n"
        f" 2.0 times={counts['2.0 times']}\n"
        f" max={ratio.max():.2f}\n"
        f" median={ratio.median():.2f}\n"
        f" mean={ratio.mean():.2f}"
    )