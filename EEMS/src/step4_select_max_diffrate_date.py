import numpy as np
import pandas as pd
from pathlib import Path
from itertools import combinations
from sklearn.preprocessing import MinMaxScaler

# pd.set_option('display.max_rows', None)

def select_max_diffrate_date(df: pd.DataFrame, motor1_name: str, motor2_name: str, base_dir: Path) -> pd.DataFrame:
    """
    Select and analyze daily motor data:
    - Select dates where both given motors (motor1_name, motor2_name) exist
    - Normalize diff and diff_rate using MinMax scaling
    - Compute scores for each pairwise date combination
    - Return results save to file

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the columns 'date', 'motor', 'diff', 'diff_rate'
    motor1_name : str
        Example: 'P1730A', 'P7412A_EXT'
    motor2_name : str
        Example: 'P1730B', 'P7412B_EXT'

    Returns
    -------
    pd.DataFrame
        A DataFrame with the columns ['date_compare', 'score']
    """
    date_box = []
    combined_date_box = []
    for date, group in df.groupby('date'):
        if len(group) == 2:
            row = {
                'date': date,
                f"{motor1_name}_diff" : group[group['motor'] == f'TORAY_{motor1_name}']['diff'].values[0],
                f"{motor1_name}_diff_rate": group[group['motor'] == f'TORAY_{motor1_name}']['diff_rate'].values[0],
                f"{motor2_name}_diff": group[group['motor'] == f'TORAY_{motor2_name}']['diff'].values[0],
                f"{motor2_name}_diff_rate": group[group['motor'] == f'TORAY_{motor2_name}']['diff_rate'].values[0]
            }
            date_box.append(date)
            combined_date_box.append(row)

    combined_df = pd.DataFrame(combined_date_box).set_index('date')
    scaled = MinMaxScaler().fit_transform(combined_df)
    scaled_df = pd.DataFrame(scaled, columns=combined_df.columns, index=combined_df.index)

    combi = list(combinations(date_box, 2))

    combi_data = []
    for c in combi:
        rows_c = {
                'date_compare': f'{c[0]} - {c[1]}',
                'score': np.sum(np.abs(scaled_df.loc[c[1]] - scaled_df.loc[c[0]])),
        }
        combi_data.append(rows_c)

    combi_final_df = pd.DataFrame(combi_data)

    save_result_csv = base_dir / f'max_diff_rate_dates_{motor1_name}_{motor2_name}.csv'
    #combi_final_df.to_csv(save_result_csv)

    print(f'BEST max_diffrate_date {motor1_name}, {motor2_name} score idx: ', combi_final_df.loc[np.argmax(combi_final_df['score'])])

    return combi_final_df


def main():


    base_dir = Path.cwd().parents[0] / "src" / "preprocessing_results" / "active_power"


    save_df_result = [f for f in base_dir.glob("*.csv") if 'saved' in f.stem][0]

    save_df = pd.read_csv(save_df_result)
    print(save_df.head())


    unique_motor_name = save_df['motor'].unique()

    inner_df = pd.concat([save_df[save_df['motor'] == 'TORAY_P1730A'],
                           save_df[save_df['motor'] == 'TORAY_P1730B']], axis=0)

    outer_df = pd.concat([save_df[save_df['motor'] == 'TORAY_P7412A_EXT'],
                           save_df[save_df['motor'] == 'TORAY_P7412B_EXT'],
                           save_df[save_df['motor'] == 'TORAY_P7412A_MCC'],
                           save_df[save_df['motor'] == 'TORAY_P7412B_MCC']], axis=0)

    outer_EXT_df = pd.concat([save_df[save_df['motor'] == 'TORAY_P7412A_EXT'],
                           save_df[save_df['motor'] == 'TORAY_P7412B_EXT']], axis=0)

    outer_MCC_df = pd.concat([save_df[save_df['motor'] == 'TORAY_P7412A_MCC'],
                             save_df[save_df['motor'] == 'TORAY_P7412B_MCC']], axis=0)


    inner_result_df = select_max_diffrate_date(inner_df, 'P1730A', 'P1730B', base_dir)
    outer_EXT_result_df = select_max_diffrate_date(outer_EXT_df, 'P7412A_EXT', 'P7412B_EXT', base_dir)
    outer_MCC_result_df = select_max_diffrate_date(outer_MCC_df, 'P7412A_MCC', 'P7412B_MCC', base_dir)


if __name__ == '__main__':
    main()
