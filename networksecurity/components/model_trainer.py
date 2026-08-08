import os
import sys

from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig



from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object,load_object
from networksecurity.utils.main_utils.utils import load_numpy_array_data
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.ensemble import (
    RandomForestClassifier,
)
import mlflow
import dagshub
dagshub.init(repo_owner='harshahs2004', repo_name='NETWORK_SECURITY', mlflow=True)

# os.environ["MLFLOW_TRACKING_URI"]="https://dagshub.com/harshahs2004/NETWORK_SECURITY.mlflow"
# os.environ["MLFLOW_TRACKING_USERNAME"]="harshahs2004"
# os.environ["MLFLOW_TRACKING_PASSWORD"]="02403c142bbd2a0417be6a08771cd7100256a58e"





class ModelTrainer:
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact:DataTransformationArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_transformation_artifact=data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)

        
    def track_mlflow(self,best_model,classificationmetric):
            with mlflow.start_run():
                f1_score = classificationmetric.f1_score
                precision_score = classificationmetric.precision_score
                recall_score = classificationmetric.recall_score

                mlflow.log_metric("f1_score", f1_score)
                mlflow.log_metric("precision", precision_score)
                mlflow.log_metric("recall_score", recall_score)

                mlflow.sklearn.log_model(
                    best_model,
                    "model",
                    registered_model_name="phisingdetectionmodel"
                )
        

    


        
    def train_model(self,X_train,y_train,x_test,y_test):
        models = {
        "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_features="log2",
        min_samples_leaf=2,
        verbose=1,
        class_weight='balanced'
    )
}
        best_model_name = "Random Forest"
        best_model = models[best_model_name]
        best_model.fit(X_train, y_train)

        logging.info(f"best model {best_model}")
        
        y_train_pred=best_model.predict(X_train)

        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)
        
        ## Track the experiements with mlflow
        self.track_mlflow(best_model,classification_train_metric)


        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)

        self.track_mlflow(best_model,classification_test_metric)

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj=NetworkModel)
        #model pusher
        save_object("final_model/model.pkl",best_model)
        

        ## Model Trainer Artifact
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric
                             )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact


        

        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            #loading training array and testing array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model_trainer_artifact=self.train_model(x_train,y_train,x_test,y_test)
            return model_trainer_artifact

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)