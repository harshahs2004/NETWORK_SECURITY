from dataclasses import dataclass
@dataclass
class DataIngestionArtifact:
    trained_file_path:str
    test_file_path:str

@dataclass 
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: bool 
    valid_test_file_path: bool
    invalid_train_file_path: bool 
    invalid_test_file_path: bool
    drift_report_file_path: str
    
    
   

