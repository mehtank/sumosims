# sumosims
SUMO simulations

## Setup
- Install SUMO
- Install python requirements
```
pip install -r requirements.txt
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
