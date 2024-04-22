from config import load_environment_variables
from object_service import ObjectService
from model_manager import ModelManager
from data_manager import DataManager
from issue_token import get_token
import pandas as pd
import joblib

# 데이터 로드 및 데이터프레임으로 변환
def prepare_data(data_manager, topics):
    results = {}
    for topic, time, calc in topics:
        df = data_manager.query_influx(topic) # DB에서 데이터 불러오기
        df = DataManager.preprocess_data(df, 'class_a') # class_a 데이터만 가져오기
        series = DataManager.resample_data(df, 'value', time, calc) # 데이터 리샘플링
        results[topic] = series
    return pd.DataFrame({
        'temperature': results['temperature'],
        'humidity': results['humidity'],
        'people_count': results['total_people_count'],
        'air_conditional': results['magnet_status']
    })

# 결측치 확인 및 제거
def handle_missing_values(data_df):
    null_values = data_df.isnull().sum()
    print('Initial null value:\n', null_values)
    return DataManager.fill_missing_values(data_df)

# 모델 관리 인스턴스 생성 및 모델 훈련, 평가
def train_and_evaluate_models(data_df_filled):
    model_manager = ModelManager(data_df_filled)
    model_manager.train_test_split()
    model_manager.train_logistic_regression()
    model_manager.train_random_forest()
    model_manager.train_xgboost()
    accuracies = model_manager.evaluate_models()
    for model_name, accuracy in accuracies.items():
        print(f"{model_name} Accuracy: {accuracy}")
    return model_manager.models['RandomForest']

# Storage Access 토큰 발급 및 모델 업로드
def save_and_upload_model(model, env_vars):
    model_path, model_name = './', 'air_conditional_ai_model.joblib'
    joblib.dump(model, model_path + model_name)
    token = get_token(env_vars['auth_url'], env_vars['tenant_id'], env_vars['user_email'], env_vars['password'])
    access_token_id = token.get('access').get('token').get('id')
    obj_service = ObjectService(env_vars['storage_url'], access_token_id)
    obj_service.upload(env_vars['container_name'], model_name, '.')


def main():
    env_vars = load_environment_variables()
    data_manager = DataManager(env_vars['db_url'], env_vars['token'], env_vars['org'], env_vars['bucket'])
    topics = [
        ('temperature', 'T', 'mean'),
        ('humidity', 'T', 'mean'),
        ('total_people_count', 'T', 'last'),
        ('magnet_status', 'T', 'last'),
    ]
    data_df = prepare_data(data_manager, topics)
    data_manager.close_connection()
    print('데이터 프레임 : \n', data_df)

    data_df_filled = handle_missing_values(data_df)
    print('After processing null value: \n', data_df_filled.isnull().sum())
    
    model = train_and_evaluate_models(data_df_filled)
    save_and_upload_model(model, env_vars)


if __name__ == '__main__':
    main()