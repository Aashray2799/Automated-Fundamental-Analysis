def plot_dist(df, ticker, sector, _filter, metric, metric_val, fig_size=(20, 10), show_ticker=True, show_subheader=True):
    """
    sector = True: Query by the stock's sector
    sector = False: Query by the stock's industry
    _filter: The sector or industry of the stock entered
    metric: The metric that the user selected
    """

    # Grade to numeric conversion
    grade_map = {
        'A+': 10, 'A': 9, 'A-': 8,
        'B+': 7, 'B': 6, 'B-': 5,
        'C+': 4, 'C': 3, 'C-': 2,
        'D+': 1, 'D': 0
    }

    # Convert metric value and column to numeric if it's a grade
    if isinstance(metric_val, str) and metric_val in grade_map:
        metric_val = grade_map[metric_val]
        df[metric] = df[metric].map(grade_map)
    else:
        metric_val = float(str(metric_val).replace('%', ''))
        df = convert_col_to_float(df, metric)

    # Filter dataset by sector or industry
    stock_sector_df = df[df['Sector'] == _filter] if sector else df[df['Industry'] == _filter]
    stock_sector_data = remove_outliers(stock_sector_df, metric, 3.5 if sector else 10)

    # Plot
    fig = plt.figure(figsize=fig_size)
    matplotlib.rcParams['axes.grid'] = True
    matplotlib.rcParams['savefig.transparent'] = True

    custom_style = {'axes.labelcolor': 'white',
                    'xtick.color': 'white',
                    'ytick.color': 'white'}

    sns.set_style({'axes.grid': False})
    sns.set_style(rc=custom_style)

    ax = sns.histplot(stock_sector_data, bins=10, kde=True)

    # Format plot info
    display_metric = metric if metric != 'Operating Margin' else 'Op. Margin'
    if display_metric == 'Volatility (Month)':
        display_metric = 'Volatility'

    subheader = f"{ticker if show_ticker else ''} {display_metric}: {str(metric_val)[:str(metric_val).find('.') + 2]}"
    md = f"Distribution of {metric} values in the {_filter} {'Sector' if sector else 'Industry'}" if show_subheader else ''

    # Highlight bin
    x_vals = [p.get_x() for p in ax.patches]
    x_vals = np.array(x_vals)
    if len(x_vals) > 1:
        diff = np.average(np.diff(x_vals))
        bin_to_color = float(metric_val)
        for p in ax.patches:
            if int(p.get_x()) in range(int(bin_to_color - diff), int(bin_to_color + diff)):
                p.set_color('crimson')

    return fig, subheader, md
