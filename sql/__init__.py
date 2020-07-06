import pandas as pd
import numpy as np

df_raw = pd.read_csv('esp8266_readings - Sheet1.csv')
_ = df_raw.drop(axis = 0, index = [0,1,2,3,4,5,6,7,8,9], inplace=True)
df_raw.index = np.arange(0, len(df_raw))


temperature_humidity_df = df_raw.Value3.str.split(';', expand = True)
df_raw[["Temperature", "Humidity"]] = temperature_humidity_df

df_clean = df_raw.drop(axis = 1, columns = ["Value3"])
df_clean.columns = ['date', 'event_name', 'digital_button', 'photoresistor', 'temperature', 'humidity']

df_clean.to_csv("./esp8266readings1.csv")

if __name__ == '__main__':
    print(df_clean)
    