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


def merge(column, *dataframes) -> pd.DataFrame:
  """Merge multiple result DataFrames on the common `filename` values.
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

def representativeness(result_df, utility):
  """
  Adds a column that contains the representativness of the voters based on their utility (cardinal or cost) for the highest efficiency outcome.
  
  :param result_df: Dataframe containing results as loaded by the data_loader file, and containing column 
  'voter_utilities_{utility}' from the voter_utilities function
  :param utility: Utility to use for calculating representativeness. Either 'cost' or 'cardinal'
  """


def main():
  data = load_all_results("../results")
  ees_cardinal_add_one = data['ees']['cardinal']['add-one']
  mes_cardinal_add_one = data['mes']['cardinal']['add-one']
  cardinal_add_one_merged = merge('highest_efficiency_attained', ("ees_add_one", ees_cardinal_add_one), ("mes_add_one", mes_cardinal_add_one))
  effiency_scatter_plot_1 = comparison_scatter_plot(x=cardinal_add_one_merged['ees_add_one'],
                          y =cardinal_add_one_merged['mes_add_one'],
                          x_label="Spending Efficiency of EES (Add-One)",
                          y_label="Spending Efficiency of MES (Add-One)",
                          title="Comparing EES/MES Add-One Efficiency for Cardinal Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  
  ees_cost_add_one = data['ees']['cost']['add-one']
  mes_cost_add_one = data['mes']['cost']['add-one']
  cost_add_one_merged = merge('highest_efficiency_attained', ("ees_add_one", ees_cost_add_one), ("mes_add_one", mes_cost_add_one))
  effiency_scatter_plot_2 = comparison_scatter_plot(x=cost_add_one_merged['ees_add_one'],
                          y =cost_add_one_merged['mes_add_one'],
                          x_label="Spending Efficiency of EES (Add-One)",
                          y_label="Spending Efficiency of MES (Add-One)",
                          title="Comparing EES/MES Add-One Efficiency for cost Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  
  ees_cardinal_add_one = data['ees']['cardinal']['add-one']
  ees_cardinal_add_opt = data['ees']['cardinal']['add-opt']
  cardinal_add_one_merged = merge('highest_efficiency_attained', ("ees_add_one", ees_cardinal_add_one), ("ees_add_opt", ees_cardinal_add_opt))
  effiency_scatter_plot_3 = comparison_scatter_plot(x=cardinal_add_one_merged['ees_add_one'],
                          y =cardinal_add_one_merged['ees_add_opt'],
                          x_label="Spending Efficiency of EES (Add-One)",
                          y_label="Spending Efficiency of EES (Add-Opt)",
                          title="Comparing EES Add-One/Add-Opt Efficiency for cardinal Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'Add-One', 'equal': 'Equal', 'second': 'Add-Opt'},
                          )
  
  ees_cost_add_one = data['ees']['cost']['add-one']
  ees_cost_add_opt = data['ees']['cost']['add-opt']
  cost_add_one_merged = merge('highest_efficiency_attained', ("ees_add_one", ees_cost_add_one), ("ees_add_opt", ees_cost_add_opt))
  effiency_scatter_plot_4 = comparison_scatter_plot(x=cost_add_one_merged['ees_add_one'],
                          y =cost_add_one_merged['ees_add_opt'],
                          x_label="Spending Efficiency of EES (Add-One)",
                          y_label="Spending Efficiency of EES (Add-Opt)",
                          title="Comparing EES Add-One/Add-Opt Efficiency for cost Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'Add-One', 'equal': 'Equal', 'second': 'Add-Opt'},
                          )
  
  ees_cardinal_add_opt = data['ees']['cardinal']['add-opt']
  mes_cardinal_add_one = data['mes']['cardinal']['add-one']
  cardinal_add_one_merged = merge('highest_efficiency_attained', ("ees_add_opt", ees_cardinal_add_opt), ("mes_add_one", mes_cardinal_add_one))
  effiency_scatter_plot_5 = comparison_scatter_plot(x=cardinal_add_one_merged['ees_add_opt'],
                          y=cardinal_add_one_merged['mes_add_one'],
                          x_label="Spending Efficiency of EES (Add-Opt)",
                          y_label="Spending Efficiency of MES (Add-One)",
                          title="Comparing EES Add-Opt / MES Add-One Efficiency for cardinal Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  
  ees_cost_add_opt = data['ees']['cost']['add-opt']
  mes_cost_add_one = data['mes']['cost']['add-one']
  cost_add_one_merged = merge('highest_efficiency_attained', ("ees_add_opt", ees_cost_add_opt), ("mes_add_one", mes_cost_add_one))
  effiency_scatter_plot_6 = comparison_scatter_plot(x=cost_add_one_merged['ees_add_opt'],
                          y=cost_add_one_merged['mes_add_one'],
                          x_label="Spending Efficiency of EES (Add-Opt)",
                          y_label="Spending Efficiency of MES (Add-One)",
                          title="Comparing EES Add-Opt / MES Add-One Efficiency for cost Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  
  ees_cardinal_add_opt = data['ees']['cardinal']['add-opt']
  ees_cardinal_add_one = data['ees']['cardinal']['add-one']
  # Merge to get best of both worlds
  ees_merged = merge('highest_efficiency_attained', ("ees_add_opt", ees_cardinal_add_opt), ("ees_add_one", ees_cardinal_add_one))
  ees_merged['highest_efficiency_attained'] = ees_merged[['ees_add_opt', 'ees_add_one']].max(axis=1)

  mes_cardinal_add_one = data['mes']['cardinal']['add-one']
  cardinal_merged = merge('highest_efficiency_attained', ("ees", ees_merged), ("mes_add_one", mes_cardinal_add_one))
  effiency_scatter_plot_7 = comparison_scatter_plot(x=cardinal_merged['ees'],
                          y=cardinal_merged['mes_add_one'],
                          x_label="Spending Efficiency of EES (Merged)",
                          y_label="Spending Efficiency of MES (Add-One)",
                          title="Comparing EES Merged / MES Add-One Efficiency for cardinal Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  
  ees_cost_add_opt = data['ees']['cost']['add-opt']
  ees_cost_add_one = data['ees']['cost']['add-one']
  # Merge to get best of both worlds
  ees_merged = merge('highest_efficiency_attained', ("ees_add_opt", ees_cost_add_opt), ("ees_add_one", ees_cost_add_one))
  ees_merged['highest_efficiency_attained'] = ees_merged[['ees_add_opt', 'ees_add_one']].max(axis=1)

  mes_cost_add_one = data['mes']['cost']['add-one']
  cost_merged = merge('highest_efficiency_attained', ("ees", ees_merged), ("mes_add_one", mes_cost_add_one))
  effiency_scatter_plot_8 = comparison_scatter_plot(x=cost_merged['ees'],
                          y=cost_merged['mes_add_one'],
                          x_label="Spending Efficiency of EES (Merged)",
                          y_label="Spending Efficiency of MES (Add-One)",
                          title="Comparing EES Merged / MES Add-One Efficiency for cost Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  

  ees_cardinal_add_one_exhaustive = data['ees']['cardinal']['add-one_exhaustive']
  ees_cardinal_add_opt_exhaustive = data['ees']['cardinal']['add-opt_exhaustive']
  cardinal_add_one_exhaustive_merged = merge('highest_efficiency_attained', ("ees_add_one_exhaustive", ees_cardinal_add_one_exhaustive), ("ees_add_opt_exhaustive", ees_cardinal_add_opt_exhaustive))
  effiency_scatter_plot_9 = comparison_scatter_plot(x=cardinal_add_one_exhaustive_merged['ees_add_one_exhaustive'],
                          y =cardinal_add_one_exhaustive_merged['ees_add_opt_exhaustive'],
                          x_label="Spending Efficiency of EES (Add-One_exhaustive)",
                          y_label="Spending Efficiency of EES (Add-Opt_exhaustive)",
                          title="Comparing EES Add-One/Add-Opt Exhaustive Efficiency for cardinal Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'Add-One', 'equal': 'Equal', 'second': 'Add-Opt'},
                          )
  
  ees_cost_add_one_exhaustive = data['ees']['cost']['add-one_exhaustive']
  ees_cost_add_opt_exhaustive = data['ees']['cost']['add-opt_exhaustive']
  cost_add_one_exhaustive_merged = merge('highest_efficiency_attained', ("ees_add_one_exhaustive", ees_cost_add_one_exhaustive), ("ees_add_opt_exhaustive", ees_cost_add_opt_exhaustive))
  effiency_scatter_plot_10 = comparison_scatter_plot(x=cost_add_one_exhaustive_merged['ees_add_one_exhaustive'],
                          y =cost_add_one_exhaustive_merged['ees_add_opt_exhaustive'],
                          x_label="Spending Efficiency of EES (Add-One_exhaustive)",
                          y_label="Spending Efficiency of EES (Add-Opt_exhaustive)",
                          title="Comparing EES Add-One/Add-Opt Exhaustive Efficiency for cost Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'Add-One', 'equal': 'Equal', 'second': 'Add-Opt'},
                          )
  
  ees_cardinal_add_opt_exhaustive = data['ees']['cardinal']['add-opt_exhaustive']
  mes_cardinal_add_one_exhaustive = data['mes']['cardinal']['add-one_exhaustive']
  cardinal_add_one_exhaustive_merged = merge('highest_efficiency_attained', ("ees_add_opt_exhaustive", ees_cardinal_add_opt_exhaustive), ("mes_add_one_exhaustive", mes_cardinal_add_one_exhaustive))
  effiency_scatter_plot_11 = comparison_scatter_plot(x=cardinal_add_one_exhaustive_merged['ees_add_opt_exhaustive'],
                          y=cardinal_add_one_exhaustive_merged['mes_add_one_exhaustive'],
                          x_label="Spending Efficiency of EES (Add-Opt_exhaustive)",
                          y_label="Spending Efficiency of MES (Add-One_exhaustive)",
                          title="Comparing EES Add-Opt / MES Add-One Exhaustive Efficiency for cardinal Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  
  ees_cost_add_opt_exhaustive = data['ees']['cost']['add-opt_exhaustive']
  mes_cost_add_one_exhaustive = data['mes']['cost']['add-one_exhaustive']
  cost_add_one_exhaustive_merged = merge('highest_efficiency_attained', ("ees_add_opt_exhaustive", ees_cost_add_opt_exhaustive), ("mes_add_one_exhaustive", mes_cost_add_one_exhaustive))
  effiency_scatter_plot_11 = comparison_scatter_plot(x=cost_add_one_exhaustive_merged['ees_add_opt_exhaustive'],
                          y=cost_add_one_exhaustive_merged['mes_add_one_exhaustive'],
                          x_label="Spending Efficiency of EES (Add-Opt_exhaustive)",
                          y_label="Spending Efficiency of MES (Add-One_exhaustive)",
                          title="Comparing EES Add-Opt / MES Add-One Exhaustive Efficiency for cost Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'EES', 'equal': 'Equal', 'second': 'MES'},
                          )
  
  ees_cost_add_opt = data['ees']['cost']['add-opt']
  ees_cost_add_opt_skip = data['ees']['cost']['add-opt-skip']
  opt_merged = merge('highest_efficiency_attained', ("ees_add_opt", ees_cost_add_opt), ("ees_add_opt_skip", ees_cost_add_opt_skip))
  effiency_scatter_plot_13 = comparison_scatter_plot(x=opt_merged['ees_add_opt'],
                          y=opt_merged['ees_add_opt_skip'],
                          x_label="Spending Efficiency of EES (Add-Opt)",
                          y_label="Spending Efficiency of EES (Add-Opt-Skip)",
                          title="Comparing EES Add-Opt / EES Add-Opt-Skip Efficiency for cost Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'Add-Opt', 'equal': 'Equal', 'second': 'Add-Opt-Skip'},
                          )
  
  ees_cardinal_add_opt = data['ees']['cardinal']['add-opt']
  ees_cardinal_add_opt_skip = data['ees']['cardinal']['add-opt-skip']
  opt_merged = merge('highest_efficiency_attained', ("ees_add_opt", ees_cardinal_add_opt), ("ees_add_opt_skip", ees_cardinal_add_opt_skip))
  effiency_scatter_plot_14 = comparison_scatter_plot(x=opt_merged['ees_add_opt'],
                          y=opt_merged['ees_add_opt_skip'],
                          x_label="Spending Efficiency of EES (Add-Opt)",
                          y_label="Spending Efficiency of EES (Add-Opt-Skip)",
                          title="Comparing EES Add-Opt / EES Add-Opt-Skip Efficiency for cardinal Utilities",
                          show_percentages=True,
                          percentage_labels={'first': 'Add-Opt', 'equal': 'Equal', 'second': 'Add-Opt-Skip'},
                          )

  plt.show()

if __name__ == "__main__":
  main()