import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, accuracy_score, roc_curve, auc
import sqlite3
import joblib
import pandas as pd
from ucimlrepo import fetch_ucirepo

# Model paths
MODEL_PATHS = {
    'logistic': os.path.join(os.path.dirname(__file__), '../logistic_regression_model_new.joblib'),
    'random_forest': os.path.join(os.path.dirname(__file__), '../random_forest_model.joblib'),
    'xgboost': os.path.join(os.path.dirname(__file__), '../xgboost_model.joblib'),
}
SCALER_PATH = os.path.join(os.path.dirname(__file__), '../../notebook/models/scaler.joblib')
SAMPLE_INPUT_PATH = os.path.join(os.path.dirname(__file__), '../../notebook/models/sample_input.json')

# Lazy load models
_models = {}
_scaler = None

# Load sample input template for column order
_sample_input_df = None
def _get_sample_input_df():
    global _sample_input_df
    if _sample_input_df is None:
        _sample_input_df = pd.read_json(SAMPLE_INPUT_PATH, typ='series').to_frame().T
    return _sample_input_df.copy()

def _load_model(model_name):
    global _models, _scaler
    if model_name not in _models:
        if model_name == 'logistic':
            print(f"DEBUG: Loading logistic model from {MODEL_PATHS['logistic']}")
            _models[model_name] = joblib.load(MODEL_PATHS['logistic'])
            if _scaler is None:
                print(f"DEBUG: Loading scaler from {SCALER_PATH}")
                _scaler = joblib.load(SCALER_PATH)
        elif model_name == 'random_forest':
            print(f"DEBUG: Loading random forest model from {MODEL_PATHS['random_forest']}")
            _models[model_name] = joblib.load(MODEL_PATHS['random_forest'])
        elif model_name == 'xgboost':
            print(f"DEBUG: Loading xgboost model from {MODEL_PATHS['xgboost']}")
            _models[model_name] = joblib.load(MODEL_PATHS['xgboost'])
        else:
            raise ValueError('Unknown model: ' + model_name)
    return _models[model_name]

def preprocess_features(features):
    """
    Preprocess features for heart disease prediction model
    features: list of 13 values in the expected order
    Returns a DataFrame with columns matching training (one-hot encoded, reindexed)
    """
    feature_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                     'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    
    print("DEBUG: Raw input features:", features)
    
    # Create DataFrame
    df = pd.DataFrame([dict(zip(feature_names, features))])
    
    # Get the template to understand expected column structure
    template = _get_sample_input_df()
    print("DEBUG: Template columns:", template.columns.tolist())
    
    # Initialize result with all zeros matching template structure
    result = pd.DataFrame(0, index=[0], columns=template.columns, dtype=float)
    
    # Set continuous features directly
    continuous_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
    for feat in continuous_features:
        if feat in result.columns:
            result[feat] = float(df[feat].iloc[0])
            print(f"DEBUG: Set continuous {feat} = {result[feat].iloc[0]}")
    
    # Handle categorical features based on what we see in template columns
    # Extract categorical column patterns from template
    categorical_columns = {}
    for col in template.columns:
        if '_' in col and col not in continuous_features:
            feature_name = col.split('_')[0]
            if feature_name not in categorical_columns:
                categorical_columns[feature_name] = []
            categorical_columns[feature_name].append(col)
    
    print("DEBUG: Found categorical column patterns:", categorical_columns)
    
    # Set categorical features based on input values
    categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
    
    for feat in categorical_features:
        if feat in categorical_columns:
            input_value = df[feat].iloc[0]
            
            # Convert to appropriate format based on what we see in template
            if feat in ['ca', 'thal']:
                # These appear to use float format in column names
                target_col = f"{feat}_{float(input_value)}"
            else:
                # These use integer format
                target_col = f"{feat}_{int(input_value)}"
            
            print(f"DEBUG: Looking for column '{target_col}' for {feat}={input_value}")
            
            if target_col in result.columns:
                result[target_col] = 1.0
                print(f"DEBUG: Set {target_col} = 1")
            else:
                print(f"DEBUG: Column '{target_col}' not found in template")
                print(f"DEBUG: Available columns for {feat}: {categorical_columns[feat]}")
    
    print("DEBUG: Final result shape:", result.shape)
    print("DEBUG: Non-zero values:")
    non_zero_cols = result.columns[result.iloc[0] != 0]
    for col in non_zero_cols:
        print(f"  {col}: {result[col].iloc[0]}")
    
    return result

def preprocess_features_robust(features):
    """
    More robust preprocessing that explicitly handles UCI Heart Disease encoding
    """
    feature_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                     'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    
    print("DEBUG: Raw input features:", features)
    
    # Create DataFrame
    df = pd.DataFrame([dict(zip(feature_names, features))])
    
    # Get template structure
    template = _get_sample_input_df()
    print("DEBUG: Template columns:", template.columns.tolist())
    
    # Start with continuous features only
    continuous_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
    result_df = df[continuous_features].copy()
    
    # Add categorical features with explicit control over encoding
    categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
    
    for cat_feature in categorical_features:
        # Create dummy variables but don't drop first automatically
        dummies = pd.get_dummies(df[cat_feature], prefix=cat_feature, drop_first=False)
        
        # Only keep the columns that exist in our template
        template_cols_for_feature = [col for col in template.columns if col.startswith(f"{cat_feature}_")]
        dummies_filtered = dummies.reindex(columns=template_cols_for_feature, fill_value=0)
        
        # Add to result
        result_df = pd.concat([result_df, dummies_filtered], axis=1)
        
        print(f"DEBUG: Processed {cat_feature} = {df[cat_feature].iloc[0]}")
        print(f"  Created columns: {dummies.columns.tolist()}")
        print(f"  Template expects: {template_cols_for_feature}")
        print(f"  Final columns: {dummies_filtered.columns.tolist()}")
        print(f"  Values: {dummies_filtered.iloc[0].tolist()}")
    
    # Final reindex to ensure exact match with template
    result_df = result_df.reindex(columns=template.columns, fill_value=0)
    
    print("DEBUG: Robust preprocessing result:")
    print("  Shape:", result_df.shape)
    print("  Non-zero columns:", result_df.columns[result_df.iloc[0] != 0].tolist())
    
    return result_df

def predict_heart_disease(features, model_name='logistic'):
    # Expected feature order:
    # ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    if not isinstance(features, (list, tuple)) or len(features) != 13:
        raise ValueError(f'Expected 13 features in the order: [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal], but got {len(features)}: {features}')
    
    model = _load_model(model_name)
    
    # Use the robust preprocessing function
    X_input = preprocess_features_robust(features)
    
    print("DEBUG: Raw features:", features)
    print("DEBUG: Preprocessed input columns:", list(X_input.columns))
    print("DEBUG: Preprocessed input values:", X_input.values)
    
    if model_name == 'logistic':
        arr_scaled = _scaler.transform(X_input)
        print("DEBUG: Scaled input:", arr_scaled)
        pred = model.predict_proba(arr_scaled)[0][1]
    else:
        pred = model.predict_proba(X_input)[0][1]
    
    print("DEBUG: Predicted probability:", pred)
    return float(pred)

def get_model_performance(model_name='logistic'):
    # Load UCI Heart Disease dataset using ucimlrepo
    heart_disease = fetch_ucirepo(id=45)
    X = heart_disease.data.features
    y_true = heart_disease.data.targets
    
    if isinstance(y_true, pd.DataFrame):
        y_true = y_true.iloc[:, 0]
    y_true = y_true.apply(lambda x: 1 if x > 0 else 0)
    
    # Preprocessing for categorical variables
    categorical = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal']
    X = pd.get_dummies(X, columns=[col for col in categorical if col in X.columns], drop_first=True)
    
    # Align columns for models
    template = _get_sample_input_df()
    X = X.reindex(columns=template.columns, fill_value=0)
    
    if model_name == 'logistic':
        scaler = _scaler if _scaler is not None else joblib.load(SCALER_PATH)
        X_proc = scaler.transform(X)
    else:
        X_proc = X.values
    
    model = _load_model(model_name)
    y_score = model.predict_proba(X_proc)[:,1]
    y_pred = (y_score >= 0.5).astype(int)
    
    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)
    
    # Confusion matrix
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.matshow(cm, cmap=plt.cm.Reds, alpha=0.7)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(x=j, y=i, s=cm[i, j], va='center', ha='center')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    cm_path = f'static/images/cm_{model_name}.png'
    plt.savefig(os.path.join(os.path.dirname(__file__), '../../web/' + cm_path), bbox_inches='tight')
    plt.close(fig)
    
    # Accuracy bar
    fig2, ax2 = plt.subplots(figsize=(3, 3))
    ax2.bar(['Accuracy'], [acc], color='#27ae60')
    ax2.set_ylim(0, 1)
    ax2.set_title('Model Accuracy')
    acc_path = f'static/images/accuracy_{model_name}.png'
    plt.savefig(os.path.join(os.path.dirname(__file__), '../../web/' + acc_path), bbox_inches='tight')
    plt.close(fig2)
    
    # ROC curve
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    fig3, ax3 = plt.subplots(figsize=(4, 4))
    ax3.plot(fpr, tpr, color='#c0392b', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    ax3.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--')
    ax3.set_xlim([0.0, 1.0])
    ax3.set_ylim([0.0, 1.05])
    ax3.set_xlabel('False Positive Rate')
    ax3.set_ylabel('True Positive Rate')
    ax3.set_title('Receiver Operating Characteristic')
    ax3.legend(loc='lower right')
    roc_path = f'static/images/roc_{model_name}.png'
    plt.savefig(os.path.join(os.path.dirname(__file__), '../../web/' + roc_path), bbox_inches='tight')
    plt.close(fig3)
    
    # Loss curve (dummy for all models)
    loss = [0.7, 0.6, 0.5, 0.45, 0.4, 0.38, 0.36, 0.35, 0.34, 0.33]
    fig4, ax4 = plt.subplots(figsize=(4, 3))
    ax4.plot(range(1, len(loss)+1), loss, marker='o', color='#2980b9')
    ax4.set_xlabel('Epoch')
    ax4.set_ylabel('Loss')
    ax4.set_title('Training Loss Curve')
    loss_path = f'static/images/loss_{model_name}.png'
    plt.savefig(os.path.join(os.path.dirname(__file__), '../../web/' + loss_path), bbox_inches='tight')
    plt.close(fig4)
    
    return {
        'accuracy': acc,
        'confusion_matrix': cm.tolist(),
        'cm_image': cm_path,
        'accuracy_image': acc_path,
        'roc_image': roc_path,
        'loss_image': loss_path
    }

def get_total_reports():
    DB_PATH = os.path.join(os.path.dirname(__file__), '../../web/users.db')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM records')
    count = c.fetchone()[0]
    conn.close()
    return count