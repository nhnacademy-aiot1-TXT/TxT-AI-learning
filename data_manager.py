from influxdb_client import InfluxDBClient
import pandas as pd

class DataManager:
    def __init__(self, db_url, token, org, bucket):
        self.client = InfluxDBClient(url=db_url, token=token, org=org, timeout=30_000)
        self.bucket = bucket

    def query_influx(self, measurement, place):
        query_api = self.client.query_api()

        query = f'''
        import "date"
        import "experimental/query"
        from(bucket: "{self.bucket}")
        |> range(start: date.sub(d: 7d, from: date.truncate(t: now(), unit: 1d)), stop: now())
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> filter(fn: (r) => r.place == "{place}")
        '''
        result_df = query_api.query_data_frame(query=query)
        print(f"{place} {measurement} shape: ", result_df.shape)
        return result_df

    def close_connection(self):
        self.client.close()

    @staticmethod
    def drop_and_time_convert_data(df):
        df = df.drop(columns=['_start', '_stop', 'result', 'table', 'topic', 'device'])
        df['_time'] = pd.to_datetime(df['_time']).dt.tz_convert('Asia/Seoul').dt.tz_localize(None)
        return df

    @staticmethod
    def resample_data(df, column, freq, method):
        df = df.set_index('_time')
        if method == 'mean':
            return df[column].resample(freq).mean()
        elif method == 'last':
            return df[column].resample(freq).last()
    
    @staticmethod
    def process_time_column(df):
        # 날짜값 제거
        df.index = df.index.time
        # time coulumn 생성
        df['time'] = df.index
        df['time_in_minutes'] = df['time'].apply(DataManager.time_to_minutes)
        df.drop(columns=['time'], inplace=True)
        return df

    @staticmethod
    def time_to_minutes(t):
        # 컬럼의 datetime.time을 분으로 변환
        return t.hour * 60 + t.minute
    
    @staticmethod
    def fill_missing_values(df):
        # 'outdoor_temperature'와 'outdoor_humidity' 컬럼의 첫 번째 값이 결측치인 경우 전체 평균값으로 채우기
        if pd.isna(df['outdoor_temperature'].iloc[0]):
            avg_temperature = df['outdoor_temperature'].mean()
            df.at[df.index[0], 'outdoor_temperature'] = avg_temperature
        if pd.isna(df['outdoor_humidity'].iloc[0]):
            avg_humidity = df['outdoor_humidity'].mean()
            df.at[df.index[0], 'outdoor_humidity'] = avg_humidity

        # 'air_conditional' 컬럼의 첫 번째 값이 결측치인 경우 'close'로 설정
        if pd.isna(df['air_conditional'].iloc[0]):
            df.at[df.index[0], 'air_conditional'] = 'close'

        # 'people_count' 컬럼에서 첫 번째 값이 결측치인 경우, 최근 유효 값으로 채우기
        if pd.isna(df['people_count'].iloc[0]):
            notnull_peoplecount = df[df['people_count'].notnull()].iloc[0]['people_count']
            df.at[df.index[0], 'people_count'] = notnull_peoplecount

        # 나머지 결측치 전방 채우기
        df = df.fillna(method='ffill', axis=0)
        return df
