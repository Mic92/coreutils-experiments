#!/usr/bin/env python
import sys

from plot import sns, plt
import pandas as pd

import matplotlib.ticker as ticker

from collections import defaultdict


def assign_time_stats(df, prefix):
    user_time = df[f"{prefix}_utime_seconds"] + (df[f"{prefix}_utime_microseconds"] / 1e6)
    sys_time = df[f"{prefix}_stime_seconds"] + (df[f"{prefix}_stime_microseconds"] / 1e6)
    time = sys_time + user_time

    wall_time = df[f"{prefix}_wall_time_seconds"] + (df[f"{prefix}_wall_time_nanoseconds"] / 1e9)

    fields = {
        f"{prefix}_user_time": user_time,
        f"{prefix}_sys_time": sys_time,
        f"{prefix}_cpu_time": time,
        f"{prefix}_wall_time": wall_time,
    }
    return df.assign(**fields)


def align_fields(*fields):
    def apply(group):
        for f in fields:
            group[f] = group[f] - group[f].iloc[0]
        return group
    return apply


def draw_speedup(df):
    data = defaultdict(list)
    X = "Resource usage"
    Y = "Speedup"
    HUE = "Simulation time [min]"
    periods = [1, 10, 20, 30, 60]

    for period in periods:
        df2 = df[df.original_wall_time < (period * 60)]
        data[X].extend(["CPU time"] * len(df2))
        data[HUE].extend([period] * len(df2))
        data[Y].extend(df2.original_cpu_time / df2.replay_cpu_time)

        data[X].extend(["Maximum resident memory time"] * len(df2))
        data[HUE].extend([period] * len(df2))
        data[Y].extend(df2.original_maxrss / df2.replay_maxrss)

    df3 = pd.DataFrame(data)
    writer = pd.ExcelWriter('cpu_speedup.xlsx')
    df3[df3[X] == "CPU time"].to_excel(writer, "Sheet1")
    writer.save()
    sns.barplot(x=X, y=Y, hue=HUE, data=df3[df3[X] == "CPU time"])
    plt.savefig("cpu-speedup.png")
    plt.close()

    df3 = pd.DataFrame(data)
    sns.barplot(x=X, y=Y, hue=HUE, data=df3[df3[X] == "Maximum resident memory time"])
    plt.savefig("memory-speedup.pdf")
    plt.close()


def aggregate_replay_cpu_time(v):
    v['replay_cpu_time'] = v.replay_cpu_time.cumsum()
    return v


def draw_bugs_found(df):
    data = defaultdict(list)
    df = df.groupby(df.application).apply(aggregate_replay_cpu_time).reset_index()
    X = "Method"
    Y = "Number of found bugs"
    HUE = "CPU time budget [min]"
    periods = [1, 10, 20, 30, 60]

    for period in periods:
        df2 = df[df.original_cpu_time < (period * 60)]
        data[X].append("Klee")
        data[Y].append(len(df2))
        data[HUE].append(period)

        df3 = df[df.replay_cpu_time < (period * 60)]
        data[X].append("Replay Klee")
        data[Y].append(len(df3))
        data[HUE].append(period)

    df4 = pd.DataFrame(data)
    sns.barplot(x=HUE, y=Y, hue=X, data=df4)
    plt.savefig("found-bugs-after-time.pdf")
    plt.close()


def draw_path_length(df):
    df.replay_solver_time = df.replay_solver_time / 1000000
    sns.regplot(x="replay_path_length",
                y="replay_solver_time",
                data=df)
    plt.savefig("replay-path-length-1.pdf")
    plt.close()

    sns.regplot(x="replay_path_length",
                y="replay_cpu_time",
                data=df)
    plt.savefig("replay-path-length-2.pdf")
    plt.close()


def draw_pairplot(df):
    df.replay_solver_time = df.replay_solver_time / 1000000
    sns.pairplot(df, vars=["replay_allocations",
                           "replay_solver_time",
                           "replay_constraint_size",
                           "replay_path_length"])
    plt.savefig("pairplot.pdf")
    plt.close()

    #sns.regplot(x="replay_path_length",
    #            y="replay_cpu_time",
    #            data=df)
    #plt.savefig("replay-path-length-2.pdf")
    #plt.close()
    #df.replay_solver_time = df.replay_solver_time / 1000000
    #sns.regplot(x="replay_path_length",
    #            y="replay_solver_time",
    #            data=df)
    #plt.savefig("replay-path-length-1.pdf")
    #plt.close()

    #sns.regplot(x="replay_path_length",
    #            y="replay_cpu_time",
    #            data=df)
    #plt.savefig("replay-path-length-2.pdf")
    #plt.close()


def main(args):
    if len(args) < 2:
        print(f"USAGE {args[0]} FILE", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(args[1], sep="\t")
    df = df[~df.original_error_message.str.contains("Execution halting")]

    df = assign_time_stats(df, "original")
    df = assign_time_stats(df, "replay")

    df = df.groupby(df.application).apply(align_fields("original_wall_time")).reset_index()

    draw_pairplot(df)
    draw_path_length(df)
    draw_bugs_found(df)
    draw_speedup(df)

if __name__ == "__main__":
    main(sys.argv)
