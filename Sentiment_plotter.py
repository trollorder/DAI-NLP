import pandas as pd
import datetime
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


def get_sentiment_analysis_graph(report_path,product):
    product = "apple watch"

    # load CSV file into DataFrame
    df = pd.read_csv(f'{report_path}/amazon_review Sentiment Analysis.csv')
    # convert date column to int

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].apply(lambda x: int(x.timestamp()))
    df['Sentiment'] = df['Sentiment'].map({'POSITIVE': 1, 'NEGATIVE': -1})


    sorted_df = df.sort_values(by=['timestamp'])

    # group the data by the x-axis values and sum up the y-axis values
    grouped = sorted_df.groupby('timestamp')['Sentiment'].mean().reset_index()

    # plot a scatter graph with the grouped data
    plt.scatter(grouped['timestamp'], grouped['Sentiment'])

    new_df = pd.DataFrame({'x_axis': grouped['timestamp'], 'y_axis': grouped['Sentiment']})
    print(new_df)

    # Fit a linear regression model to the data
    model = LinearRegression().fit(grouped[['timestamp']], grouped['Sentiment'])

    # Predict the y values using the linear regression model
    y_pred = model.predict(grouped[['timestamp']])

    # Plot the linear regression line
    plt.plot(grouped['timestamp'], y_pred, color='red')

    intercept = model.intercept_
    slope = model.coef_[0]

    # Print the coefficients
    print("\nLinear Regression Coefficients")
    print('Intercept:', intercept)
    print('Slope:', slope) # gradient of the linear regression; to be used to determine how pressing the issue is

    # set the title and labels for the plot
    plt.title(f'Sentiment over Time for {product} ')
    plt.xlabel('Time Stamp')
    plt.ylabel('Sentiment')
    plt.savefig(f'{report_path}/img/{product} Sentiment Analysis Overtime.png')
    # show the plot


