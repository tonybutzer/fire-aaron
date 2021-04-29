import pandas as pd

def df_prune_just_growing_season(in_df):
	df=(in_df)
	#Add Date/Time Constructor to Date Column of DF
	df['datetime'] = pd.to_datetime(df['datetime'])

	#Make a seasonality List to show only products where month acquired is May to September
	df = df[df['datetime'].dt.month.between(5, 9)]
	df = df.reset_index(drop=True)
	return df
