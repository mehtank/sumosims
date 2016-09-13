# sumosims
SUMO simulations

## Setup
- Install SUMO
- Install python requirements
```
pip install -r requirements.txt
```
- Install [gurobi](https://www.gurobi.com/academia/for-universities)
- Configure `gurobipy`. The following test script should run without errors.
```
pushd <GUROBI_INSTALL_DIR>
python setup.py install
popd
python python/milp.py
```

## Usage
To use: 
```
% make PROJ=circular
```

To create a plot of the resulting data:
```
% python python/spatiotemporal.py
```

The plot will be in ./labeled.png

---

For a gui use: 
```
% make gui PROJ=hello
```
