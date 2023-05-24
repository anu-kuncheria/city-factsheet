# cityfactsheet-mobiliti



```mermaid
graph LR;
    etl.py-->system_metrics.py-->visualisation.py-->truck.py-->highadt.py-->legs_dest.py-->text.py-->report.py;
```

After executing the aforementioned pipeline, a fully processed California network is generated, which can subsequently be clipped according to the specified region of interest.



