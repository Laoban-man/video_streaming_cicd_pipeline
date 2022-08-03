import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_predict
from sklearn.preprocessing import StandardScaler, Normalizer
import skimage
from sklearn.pipeline import Pipeline
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
import cv2
import mlflow
import mlflow.sklearn
from skimage import color
from skimage.feature import hog
from urllib.parse import urlparse




class RGB2GrayTransformer(BaseEstimator, TransformerMixin):
    """
    Convert an array of RGB images to grayscale
    """
 
    def __init__(self):
        pass
 
    def fit(self, X, y=None):
        """returns itself"""
        return self
 
    def transform(self, X, y=None):
        """perform the transformation and return an array"""
        #print(type(X))
        if type(X)!= list and type(X)!=np.ndarray:
            img=np.asarray(X.inputs[0].data).reshape(224,224,3)
            print(img.shape)
            return np.array(color.rgb2gray(img))
        return np.array([color.rgb2gray(img) for img in X])
     

class HogTransformer(BaseEstimator, TransformerMixin):
    """
    Expects an array of 2d arrays (1 channel images)
    Calculates hog features for each img
    """
 
    def __init__(self, y=None, orientations=9,
                 pixels_per_cell=(8, 8),
                 cells_per_block=(3, 3), block_norm='L2-Hys'):
        self.y = y
        self.orientations = orientations
        self.pixels_per_cell = pixels_per_cell
        self.cells_per_block = cells_per_block
        self.block_norm = block_norm
 
    def fit(self, X, y=None):
        return self
 
    def transform(self, X, y=None):
 
        def local_hog(X):
            return hog(X,
                       orientations=self.orientations,
                       pixels_per_cell=self.pixels_per_cell,
                       cells_per_block=self.cells_per_block,
                       block_norm=self.block_norm)
        
        if X.shape==(224,224):
            X=X.reshape(224,224)
            return np.array(local_hog(X)).reshape(1,23328)
        else:
            try: # parallel
                print(np.array([local_hog(img) for img in X]).shape)
                return np.array([local_hog(img) for img in X])
            except:
                return np.array([local_hog(img) for img in X])
        
        

class model_training:
    def __init__(self,db_ip_str):
        self.data=self.get_data(db_ip_str)
        self.X_train,self.X_test,self.y_train,self.y_test=train_test_split(
            np.array(self.data['data']), 
            np.array(self.data['label']), 
            test_size=0.8,
            shuffle=True,
            random_state=42,
        )
        
    def get_data(self,db_ip_str):
        client = MongoClient("mongodb://"+db_ip_str+":27017")
        db=client["video-stream-records"]
        data=dict()
        data['data'] = []
        data['label'] = []
        for collection in db.list_collection_names():
            coll=db[collection]
            for document in db[collection].find():
                nparr = np.frombuffer(document["image"], np.uint8)
                # decode image
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                img = cv2.resize(img, (224, 224))
                if collection == "sixtine":
                    y="sixtine"
                elif collection == "nicolas":
                    y="nicolas"
                else:
                    y="dagobert"
                data["data"].append(img)
                data["label"].append(y)
        return data

    
if __name__ == "__main__":
    
    print("step 1")
    model=model_training("35.238.232.235")
    with mlflow.start_run():
        print("step 2")
        HOG_pipeline = Pipeline([
            ('grayify', RGB2GrayTransformer()),
            ('hogify', HogTransformer(
                pixels_per_cell=(14, 14), 
                cells_per_block=(2, 2), 
                orientations=9, 
                block_norm='L2-Hys')
            ),
            ('scalify', StandardScaler()),
            ('classify', SGDClassifier(random_state=42, max_iter=1000, tol=1e-3))
        ])
        
        param_grid = {
                'hogify__orientations': [8],
                'hogify__cells_per_block': [(2, 2)],
                'hogify__pixels_per_cell': [(8, 8)],
                'classify': [
                     SGDClassifier(random_state=42, max_iter=1000, tol=1e-3),
                     svm.SVC(kernel='linear')
                 ]
            }
        print("step 3")
        grid_search = GridSearchCV(HOG_pipeline, 
                           param_grid, 
                           cv=2,
                           n_jobs=-1,
                           scoring='accuracy',
                           verbose=1,
                           return_train_score=True)
        grid_res= grid_search.fit(model.X_train, model.y_train)
        
        best_pred = grid_res.predict(model.X_test)
        accuracy=100*np.sum(best_pred == model.y_test)/len(model.y_test)
        
        mlflow.log_param("orientations", grid_search.best_params_["hogify__orientations"])
        mlflow.log_param("cell_per_block", grid_search.best_params_["hogify__cells_per_block"])
        mlflow.log_param("pixels_per_cell", grid_search.best_params_["hogify__pixels_per_cell"])
        mlflow.log_param("classifier", grid_search.best_params_["classify"])
        mlflow.log_metric("accuracy", accuracy)

        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        # Model registry does not work with file store
        if tracking_url_type_store != "file":

            # Register the model
            # There are other ways to use the Model Registry, which depends on the use case,
            # please refer to the doc for more information:
            # https://mlflow.org/docs/latest/model-registry.html#api-workflow
            mlflow.sklearn.log_model(grid_search, "model", registered_model_name="Video_classifier")
        else:
            mlflow.sklearn.log_model(grid_search, "model")
            

