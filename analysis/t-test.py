import numpy as np
import pandas as pd
from scipy import stats
from plot_results import parse_log, get_mean_time
from get_stats import get_event_timing


def independent_t_test(mean1, mean2, std1, std2, n1, n2):
    # Compute mean and standard deviation for each sample
    # mean1, mean2 = np.mean(sample1), np.mean(sample2)
    # std1, std2 = np.std(sample1, ddof=1), np.std(sample2, ddof=1)

    # # Compute the standard error of the difference between means
    # n1, n2 = len(sample1), len(sample2)
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


def get_event_avg_per_round(logs_per_config):
    round_times = {}
    training_times = {}
    aggregation_times = {}

    for config, events in logs_per_config.items():
        for event, timings in events.items():
            if "Round=" in event:
                if config not in round_times:
                    round_times[config] = []
                round_times[config].append(timings)

            elif "Training client=" in event:
                if config not in training_times:
                    training_times[config] = []
                training_times[config].append(timings)

            elif "Aggregating round=" in event:
                if config not in aggregation_times:
                    aggregation_times[config] = []
                aggregation_times[config].append(timings)


    # col_means = [sum(i)/len(i) for i in zip(*arr)] #column wise means
    # row_means = [sum(i)/len(i) for i in arr] #row wise means

    for config, rounds in round_times.items():
        means = [sum(i)/len(i) for i in zip(*rounds)]
        logs_per_config[config]['Round'] = means

    for config, aggr in aggregation_times.items():
        means = [sum(i)/len(i) for i in zip(*aggr)]
        logs_per_config[config]['Aggregating'] = means

    for config, training in training_times.items():
        means = [sum(i)/len(i) for i in zip(*training)]
        logs_per_config[config]['Training'] = means

    return logs_per_config


def get_event_times(logs_per_config, event):
    res = {}

    for config, events in logs_per_config.items():
        rounds_clients = tuple(map(int, [s.split('=')[1] for s in config.split(',') if 'ROUNDS' in s or 'NUM_CLIENTS' in s]))
        res[rounds_clients] = events[event]

    return res


def run_test_for_event(sampleStateFL, sampleBCFL, event, caption=""):

    if event == "Experiment":
        opening_times = get_event_times(sampleStateFL, "opening channels")
        settling_times = get_event_times(sampleStateFL, "settling channels")
        sampleBCFL = get_event_times(sampleBCFL, "FL")
        sampleStateFL = get_event_times(sampleStateFL, "FL")

        for config, events in sampleStateFL.items():
            channel_time = np.add(opening_times[config], settling_times[config]).tolist()
            sampleStateFL[config] = np.add(events, channel_time).tolist()
    else:
        sampleStateFL = get_event_times(sampleStateFL, event)
        sampleBCFL = get_event_times(sampleBCFL, event)

    p_values = []
    critical_values = []
    t_stats = []
    sig = []

    for config, _ in sampleBCFL.items():
        BCFL_std = np.std(sampleBCFL[config], ddof=1)
        StateFL_std = np.std(sampleStateFL[config], ddof=1)
        BCFL_mean = np.mean(sampleBCFL[config])
        StateFL_mean = np.mean(sampleStateFL[config])

        t_stat, p, critical_value = independent_t_test(BCFL_mean, StateFL_mean, BCFL_std, StateFL_std, len(sampleBCFL[config]), len(sampleStateFL[config]))
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

    labels = [f'{config}' for config in sampleBCFL.keys()]

    d = {'(#C, #R)': labels, 'p-value': p_values, 't-value': t_stats, 'significant': sig}
    df = pd.DataFrame(data=d)
    print(df)

    # Convert DataFrame to LaTeX table
    latex_table = df.to_latex(index=False, caption=caption, label=f'tab:t-test{event}', column_format='|c|c|c|c|', position='h')


    # Write LaTeX code to a file
    with open(f'analysis/stats_table/{event}.tex', 'w') as f:
        f.write(latex_table)

    return df



# log_data_StateFL = parse_log("analysis/results/results_StateFL.txt")
# log_data_BCFL = parse_log("analysis/results/results_BCFL.txt")

log_data_StateFL = get_event_timing("logs/logs_statefl/")
log_data_BCFL = get_event_timing("logs/logs_bcfl/")

log_data_StateFL = get_event_avg_per_round(log_data_StateFL)
log_data_BCFL = get_event_avg_per_round(log_data_BCFL)

run_test_for_event(log_data_StateFL, log_data_BCFL, "Training", "T-test on Training Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "Aggregating", "T-test on Aggregation Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "Round", "T-test on Round Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "FL", "T-test on FL Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "Experiment", "T-test on E2E Time")
