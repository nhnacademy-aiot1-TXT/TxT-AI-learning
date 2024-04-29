from config import load_environment_variables
from object_service import ObjectService
from model_manager import ModelManager
from data_manager import DataManager
from issue_token import get_token
import pandas as pd
import joblib

def prepare_data(data_manager, topics):
    """
    지정된 토픽에 따라 데이터베이스에서 데이터를 쿼리하고, 필요한 처리를 수행한 후 데이터 프레임을 생성합니다.

    Args:
        data_manager (DataManager): 데이터베이스 쿼리를 관리하는 DataManager 인스턴스.
        topics (list of tuple): 데이터를 쿼리할 토픽 목록. 각 튜플은 (측정 항목, 위치, 시간 간격, 집계 방식)을 포함합니다.

    Returns:
        DataFrame: 처리된 데이터가 포함된 판다스 데이터프레임.
    """
    results = {}
    for topic, place , time, calc in topics:
        df = data_manager.query_influx(topic, place)
        df = DataManager.drop_and_time_convert_data(df)
        series = DataManager.resample_data(df, 'value', time, calc)
        results[place+'_'+topic] = series
    return pd.DataFrame({
        'outdoor_temperature': results['outdoor_temperature'],
        'outdoor_humidity': results['outdoor_humidity'],
        'temperature': results['class_a_temperature'],
        'humidity': results['class_a_humidity'],
        'people_count': results['class_a_total_people_count'],
        'air_conditional': results['class_a_magnet_status']
    })

def handle_missing_values(data_df):
    """
    데이터 프레임에서 결측치를 확인하고, 처리합니다.

    Args:
        data_df (DataFrame): 결측치를 확인하고 처리할 데이터 프레임.

    Returns:
        DataFrame: 결측치가 처리된 데이터 프레임.
    """
    null_values = data_df.isnull().sum()
    print('Initial null value:\n', null_values)
    return DataManager.fill_missing_values(data_df)

def train_and_evaluate_models(data_df_filled):
    """
    데이터 프레임을 사용하여 여러 머신러닝 모델을 훈련시키고 평가합니다.

    Args:
        data_df_filled (DataFrame): 훈련에 사용될 데이터 프레임.

    Returns:
        dict: 훈련된 모델 객체를 포함하는 딕셔너리.
    """
    model_manager = ModelManager(data_df_filled)
    model_manager.train_test_split()
    model_manager.train_logistic_regression()
    model_manager.train_random_forest()
    model_manager.train_xgboost()
    accuracies = model_manager.evaluate_models()
    for model_name, accuracy in accuracies.items():
        print(f"{model_name} Accuracy: {accuracy}")
    return model_manager.models['RandomForest']

def save_and_upload_model(model, env_vars):
    """
    훈련된 모델을 파일로 저장하고, NHN Object Storage에 업로드합니다.

    Args:
        model (Model): 저장하고 업로드할 모델 객체.
        env_vars (dict): 환경 변수들을 포함한 딕셔너리.

    Returns:
        None
    """
    model_path, model_name = './', 'air_conditional_ai_model.joblib'
    joblib.dump(model, model_path + model_name)
    token = get_token(env_vars['auth_url'], env_vars['tenant_id'], env_vars['user_email'], env_vars['password'])
    access_token_id = token.get('access').get('token').get('id')
    obj_service = ObjectService(env_vars['storage_url'], access_token_id)
    obj_service.upload(env_vars['container_name'], model_name, '.')


def main():
    """
    데이터 전처리, 모델 훈련, 모델 저장 및 업로드 작업을 수행하는 메인 함수.
    """
    env_vars = load_environment_variables()
    data_manager = DataManager(env_vars['db_url'], env_vars['token'], env_vars['org'], env_vars['bucket'])
    topics = [
        ('temperature', 'outdoor', 'T', 'mean'),
        ('humidity', 'outdoor', 'T', 'mean'),
        ('temperature', 'class_a', 'T', 'mean'),
        ('humidity', 'class_a', 'T', 'mean'),
        ('total_people_count', 'class_a', 'T', 'last'),
        ('magnet_status', 'class_a', 'T', 'last'),
    ]
    data_df = prepare_data(data_manager, topics)
    data_manager.close_connection()
    print('데이터 프레임 : \n', data_df)

    data_df = DataManager.process_time_column(data_df)
    print('process_time_column 결과', data_df)

    data_df_filled = handle_missing_values(data_df)
    print('After processing null value: \n', data_df_filled.isnull().sum())
    
    model = train_and_evaluate_models(data_df_filled)
    save_and_upload_model(model, env_vars)

if __name__ == '__main__':
    main()
