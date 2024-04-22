from IssueToken import IssueToken
from ObjectService import ObjectService
from ModelManager import ModelManager
from DataManager import DataManager
from dotenv import load_dotenv
import pandas as pd
import joblib
import os

if __name__ == '__main__':
    load_dotenv('secret.env')
    db_url = os.getenv('DB_URL')
    token = os.getenv('DB_TOKEN')
    org = os.getenv('DB_ORG')
    bucket = os.getenv('DB_BUCKET')

    # location, dittionary(topic, time, calc)

    # 데이터 관리 인스턴스 생성 및 데이터 로드
    data_manager = DataManager(db_url, token, org, bucket)
    temperature_df = data_manager.query_influx("temperature")
    humidity_df = data_manager.query_influx("humidity")
    people_count_df = data_manager.query_influx("total_people_count")
    magnet_status_df = data_manager.query_influx("magnet_status")
    # 데이터 전처리
    temperature_df = DataManager.preprocess_data(temperature_df, 'class_a')
    humidity_df = DataManager.preprocess_data(humidity_df, 'class_a')
    people_count_df = DataManager.preprocess_data(people_count_df, 'class_a')
    magnet_status_df = DataManager.preprocess_data(magnet_status_df, 'class_a')
    # 데이터 리샘플링
    temperature_series = DataManager.resample_data(temperature_df, 'value', 'T', 'mean')
    humidity_series = DataManager.resample_data(humidity_df, 'value', 'T', 'mean')
    people_count_series = DataManager.resample_data(people_count_df, 'value', 'T', 'last')
    magnet_status_series = DataManager.resample_data(magnet_status_df, 'value', 'T', 'last')

    print(humidity_series.head(),'\n', humidity_series.head(),'\n', people_count_series.head(),'\n',magnet_status_series.head(),'\n')

    data_df = pd.DataFrame({
        'temperature': temperature_series,
        'humidity': humidity_series,
        'people_count': people_count_series,
        'air_conditional': magnet_status_series
    })
    print('데이터 관리 결과 : \n', data_df)

    # 결측치 제거
    null_values = data_df.isnull().sum()
    print('Initial null value:\n', null_values)

    data_df_filled = DataManager.fill_missing_values(data_df)
    print('After processing null value: \n', data_df_filled.isnull().sum())


    # 모델 관리 인스턴스 생성 및 모델 훈련
    model_manager = ModelManager(data_df_filled)
    model_manager.train_test_split()
    model_manager.train_logistic_regression()
    model_manager.train_random_forest()
    model_manager.train_xgboost()

    # 모델 평가 및 결과 출력
    accuracies = model_manager.evaluate_models()
    for model_name, accuracy in accuracies.items():
        print(f"{model_name} Accuracy: {accuracy}")

    # 모델 저장
    MODEL_PATH = './'
    MODEL_NAME = 'air_conditional_ai_model.joblib'
    joblib.dump(model_manager.models['RandomForest'], MODEL_PATH+MODEL_NAME)

    data_manager.close_connection()

    # 모델 업로드를 위한 토큰 발급
    AUTH_URL = os.getenv('AUTH_URL')
    TENANT_ID = os.getenv('TENANT_ID')
    USER_EMAIL = os.getenv('USER_EMAIL')
    PASSWORD = os.getenv('PASSWORD')

    issue_token = IssueToken()
    token = issue_token.get_token(AUTH_URL, TENANT_ID, USER_EMAIL, PASSWORD)
    ACCESS_TOKEN_ID = token.get('access').get('token').get('id')

    # 모델 업로드
    STORAGE_URL = os.getenv('STORAGE_URL')
    CONTAINER_NAME = os.getenv('CONTAINER_NAME')
    OBJECT_PATH = '.' 
    
    obj_service = ObjectService(STORAGE_URL, ACCESS_TOKEN_ID)

    obj_service.upload(CONTAINER_NAME, MODEL_NAME, OBJECT_PATH)
