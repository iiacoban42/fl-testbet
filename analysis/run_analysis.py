
from get_stats import get_event_timing
from plot_results import parse_log, plot_mean_time_diff, plot_cumulative_time_diff, plot_number_of_requests, plot_channel_time, plot_stacked_bar
from t_test import run_test_for_event, get_event_avg_per_round

# parse log files
get_event_timing("logs/logs_fl/", "analysis/results/results_FL.txt")
get_event_timing("logs/logs_statefl/", "analysis/results/results_StateFL.txt")
get_event_timing("logs/logs_bcfl/", "analysis/results/results_BCFL.txt")


# plot results
log_data_FL = parse_log("analysis/results/results_FL.txt")
log_data_StateFL = parse_log("analysis/results/results_StateFL.txt")
log_data_BCFL = parse_log("analysis/results/results_BCFL.txt")

plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Training", 'Mean Client Training Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Aggregating", 'Mean Aggregation Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Round", 'Mean Round Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "FL", 'Federated Learning Time: FL vs BCFL vs StateFL')
plot_mean_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Experiment", 'E2E Time: FL vs BCFL vs StateFL')

plot_cumulative_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Round", 'Cumulative Round Time: FL vs BCFL vs StateFL')
plot_cumulative_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Aggregating", 'Cumulative Aggregation Time: FL vs BCFL vs StateFL')
plot_cumulative_time_diff(log_data_FL, log_data_BCFL, log_data_StateFL, "Training", 'Cumulative training Time: FL vs BCFL vs StateFL')


plot_number_of_requests(log_data_StateFL, "ipfs", 'IPFS Requests')
plot_number_of_requests(log_data_StateFL, "perun", 'Perun Requests')


plot_channel_time(log_data_StateFL, 'Time to Handle Channel Opening and Closing')

plot_stacked_bar(log_data_StateFL, 'StateFL Events', channel=True)
plot_stacked_bar(log_data_FL, 'FL Events', channel=False)
plot_stacked_bar(log_data_BCFL, 'BCFL Events', channel=False)

# run t-tests

log_data_StateFL = get_event_timing("logs/logs_statefl/")
log_data_BCFL = get_event_timing("logs/logs_bcfl/")

log_data_StateFL = get_event_avg_per_round(log_data_StateFL)
log_data_BCFL = get_event_avg_per_round(log_data_BCFL)

run_test_for_event(log_data_StateFL, log_data_BCFL, "Training", "T-test on Training Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "Aggregating", "T-test on Aggregation Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "Round", "T-test on Round Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "FL", "T-test on FL Time")

run_test_for_event(log_data_StateFL, log_data_BCFL, "Experiment", "T-test on E2E Time")
