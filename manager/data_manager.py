from sklearn.ensemble import IsolationForest
from influxdb_client import InfluxDBClient
import pandas as pd

class DataManager:
    """
    InfluxDB에 데이터를 요청하고 받은 데이터를 처리하는 클래스 입니다.
    """

    def __init__(self, db_url, token, org, bucket):
        """
        InfluxDB에 접속하기 위한 클라이언트를 초기화 합니다.

        Args:
            db_url (str): 데이터베이스 서버의 URL.
            token (str): 접근 토큰.
            org (str): 조직 이름.
            bucket (str): 데이터를 쿼리할 버킷의 이름.
        """
        self.client = InfluxDBClient(url=db_url, token=token, org=org, timeout=30_000)
        self.bucket = bucket

    def query_influx(self, measurement, place):
        """
        지정된 장소와 측정값에 대한 데이터를 요청합니다.
        쿼리문 : 현재시간에서 날짜만 추출한 뒤 보고싶은 기간만큼의 날짜를 뺍니다. 이후 해당 날짜 0시부터 현재까지의 데이터를 조회합니다.

        Args:
            measurement (str): 필요한 센서 정보.
            place (str): 센서가 설치된 위치.

        Returns:
            DataFrame: 쿼리 결과를 데이터프레임으로 반환.
        """
        query_api = self.client.query_api()

        query = f'''
        import "date"
        import "experimental/query"
        from(bucket: "{self.bucket}")
        |> range(
        start: date.add(d: -9h, to: date.sub(d: 14d, from: date.truncate(t: now(), unit: 1d))),
        stop: now()
        )
        |> filter(fn: (r) => r["_measurement"] == "{measurement}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> filter(fn: (r) => r.place == "{place}")
        '''
        result_df = query_api.query_data_frame(query=query)
        print(f"{place} {measurement} shape: ", result_df.shape)
        return result_df

    def close_connection(self):
        """
        데이터베이스 클라이언트의 연결을 안전하게 종료합니다.
        """
        self.client.close()

    @staticmethod
    def drop_and_time_convert_data(df):
        """
        데이터프레임에서 필요없는 컬럼을 제거하고, 시간 컬럼을 한국 시간으로 변환합니다.
        이후 주말데이터를 제거합니다.

        Args:
            df (DataFrame): 원본 데이터프레임.

        Returns:
            DataFrame: 처리된 데이터프레임.
        """
        df = df.drop(columns=['_start', '_stop', 'result', 'table', 'topic', 'device'])
        df['_time'] = pd.to_datetime(df['_time']).dt.tz_convert('Asia/Seoul').dt.tz_localize(None)
        df = df[df['_time'].dt.dayofweek < 5]
        return df

    @staticmethod
    def resample_data(df, column, freq, method):
        """
        지정된 빈도와 방법으로 데이터를 리샘플링합니다.

        Args:
            df (DataFrame): 리샘플링할 데이터프레임.
            column (str): 리샘플링할 컬럼 이름.
            freq (str): 리샘플링 빈도.
            method (str): 리샘플링 방법 ('mean' 또는 'last').

        Returns:
            DataFrame: 리샘플링된 데이터.
        """
        df = df.set_index('_time')
        if method == 'mean':
            return df[column].resample(freq).mean()
        elif method == 'last':
            return df[column].resample(freq).last()
    
    @staticmethod
    def process_time_column(df):
        """
        데이터프레임의 시간 인덱스를 사용해 'time_in_minutes' 컬럼을 생성합니다.

        Args:
            df (DataFrame): 처리할 데이터프레임.

        Returns:
            DataFrame: 시간 컬럼이 처리된 데이터프레임.
        """
        # 날짜값 제거
        df.index = df.index.time
        # time coulumn 생성
        df['time'] = df.index
        df['time_in_minutes'] = df['time'].apply(DataManager.time_to_minutes)
        df.drop(columns=['time'], inplace=True)
        return df

    @staticmethod
    def time_to_minutes(t):
        """
        자정으로부터 경과한 분을 계산합니다.

        Args:
            t (datetime.time): 자정부터 경과한 분을 계산할 시간 객체.

        Returns:
            int: 자정으로부터 경과한 분.
        """
        return t.hour * 60 + t.minute
    
    @staticmethod
    def fill_missing_values(df):
        """
        데이터프레임의 결측치를 처리합니다. 특정 컬럼의 첫 번째 값이 결측치인 경우 최근 유효 값으로 채웁니다.
        이후 나머지 결측치들은 결측치 전방 채우기로 채웁니다.

        Args:
            df (DataFrame): 처리할 데이터프레임.

        Returns:
            DataFrame: 결측치가 처리된 데이터프레임.
        """
        columns_to_fill = ['outdoor_temperature', 'outdoor_humidity', 'temperature', 'humidity', 'people_count', 'air_conditional']

        for column in columns_to_fill:
            if pd.isna(df[column].iloc[0]):
                notnull_value = df[df[column].notnull()].iloc[0][column]
                df.at[df.index[0], column] = notnull_value

        df = df.fillna(method='ffill', axis=0)
        return df

    @staticmethod
    def convert_air_conditional(df):
        """
        'air_conditional' 컬럼의 값을 'close'에서 0으로, 'open'에서 1로 변환합니다.

        Args:
            data_df (DataFrame): 변환할 데이터 프레임.

        Returns:
            DataFrame: 변환된 데이터 프레임.
        """
        df['air_conditional'] = df['air_conditional'].map({'close': 0, 'open': 1})
        return df

    @staticmethod
    def remove_outliers(data_df):
        """
        IsolationForest를 사용하여 데이터프레임의 이상치를 제거합니다.
        이상치의 비율은 고정된 값으로 설정됩니다.

        Args:
            data_df (pd.DataFrame): 이상치를 제거할 데이터프레임.

        Returns:
            pd.DataFrame: 이상치가 제거된 데이터프레임.
        """
        contamination_rate = 0.01  # 고정된 이상치 비율
        iso_forest = IsolationForest(contamination=contamination_rate, random_state=42)
        y_pred = iso_forest.fit_predict(data_df)
        mask = y_pred != -1
        return data_df[mask]