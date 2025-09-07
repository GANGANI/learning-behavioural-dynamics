import papermill as pm
from datetime import datetime

# Generate timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

pm.execute_notebook(
    'lstm.ipynb',  # Path to the input notebook
    f'lstm_{timestamp}.ipynb'        # Path to the output notebook
)