import numpy as np
import pandas as pd
from scipy import stats
from plot_results import parse_log, get_mean_time

def independent_t_test(mean1, mean2, std1, std2, n=10):
    # Compute mean and standard deviation for each sample
    # mean1, mean2 = np.mean(sample1), np.mean(sample2)
    # std1, std2 = np.std(sample1, ddof=1), np.std(sample2, ddof=1)

    # # Compute the standard error of the difference between means
    # n1, n2 = len(sample1), len(sample2)
    n1 = n
    n2 = n
    sed = np.sqrt((std1**2 / n1) + (std2**2 / n2))

    # Compute the t statistic
    t_stat = (mean1 - mean2) / sed

    # Degrees of freedom
    df = n1 + n2 - 2

    # Compute critical value (two-tailed test)
    alpha = 0.05
    critical_value = stats.t.ppf(1 - alpha / 2, df)

    # Compute p-value
    p = (1 - stats.t.cdf(abs(t_stat), df)) * 2

    return t_stat, p, critical_value


def run_test_for_event(sampleStateFL, sampleBCFL, event, caption=""):

    labels, times_FL_training = get_mean_time(sampleBCFL, event)
    labels, times_StateFL_training = get_mean_time(sampleStateFL, event)
    p_values = []
    critical_values = []
    t_stats = []
    sig = []
    for i, _ in enumerate(labels):
        t_stat, p, critical_value = independent_t_test(times_FL_training[i], times_StateFL_training[i], 10, 10, 10)
        # round up to 3 decimal places
        p = round(p, 3)
        critical_value = round(critical_value, 3)
        t_stat = round(t_stat, 3)

        p_values.append(p)
        critical_values.append(critical_value)
        t_stats.append(t_stat)

        if np.abs(t_stat) > critical_value:
            sig.append(True)
        else:
            sig.append(False)

    d = {'(#C, #R)': labels, 'p-value': p_values, 't-value': t_stats, 'significant': sig}
    df = pd.DataFrame(data=d)
    print(df)

    # Convert DataFrame to LaTeX table
    latex_table = df.to_latex(index=False, caption=caption, label=f'tab:t-test{event}', column_format='|c|c|c|c|', position='h')


    # Write LaTeX code to a file
    with open(f'analysis/stats_table/{event}.tex', 'w') as f:
        f.write(latex_table)

    return df


log_data_FL = parse_log("analysis/results/results_FL.txt")
log_data_StateFL = parse_log("analysis/results/results_StateFL.txt")
log_data_BCFL = parse_log("analysis/results/results_BCFL.txt")


labels, times_FL_training = get_mean_time(log_data_FL, "Training")
labels, times_StateFL_training = get_mean_time(log_data_StateFL, "Training")


run_test_for_event(log_data_StateFL, log_data_BCFL, "Training", "T-test on Training Time")
run_test_for_event(log_data_StateFL, log_data_BCFL, "Aggregating", "T-test on Aggregation Time")
run_test_for_event(log_data_StateFL, log_data_BCFL, "Round", "T-test on Round Time")
run_test_for_event(log_data_StateFL, log_data_BCFL, "FL", "T-test on FL Time")
run_test_for_event(log_data_StateFL, log_data_BCFL, "Experiment", "T-test on E2E Time")
