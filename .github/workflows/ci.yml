name: Python CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout del codice
      uses: actions/checkout@v3

    - name: Setup di Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Installazione dipendenze
      run: |
        pip install -r requirements.txt
        pip install black isort pytest

    - name: Verifica formattazione con Black e isort
      run: |
        black --check .
        isort --check-only .

    - name: Esecuzione dei test
      run: pytest