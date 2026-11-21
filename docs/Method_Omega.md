# Method Omega SPARQL and Gruff Examples

### Query For Model Hierarchy

```
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>

CONSTRUCT {
  ?plan pm:has_step ?step .
  ?step pp:isDecomposedAsPlan ?subplan .
}
WHERE {
  VALUES ?plan {
    pm:Method_Omega
    pm:Requirements_Acquisition_Plan
    pm:Create_Detailed_Requirements_Plan
    pm:Create_Wireframes_Plan
    pm:Create_Use_Cases_Plan
  }
  ?plan pm:has_step ?step .
  OPTIONAL {?step pp:isDecomposedAsPlan ?subplan .}}
```

### Query For Task Hierarchy

```
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>

SELECT DISTINCT ?subject ?predicate ?object
WHERE {
  VALUES ?plan {
    pm:Customer_Portal_Plan
    pm:Portal_Requirements_Acquisition_Plan
    pm:Portal_Create_Detailed_Requirements_Plan
    pm:Portal_Create_Wireframes_Plan
    pm:Portal_Create_Use_Cases_Plan
  }

  {
    ?plan pm:has_step ?object .
    BIND(?plan AS ?subject)
    BIND(pm:has_step AS ?predicate)
  }
  UNION
  {
    ?subject pp:isDecomposedAsPlan ?plan .
    BIND(pp:isDecomposedAsPlan AS ?predicate)
    BIND(?plan AS ?object)
  }
}
ORDER BY ?subject ?predicate ?object
```

### Gruff Visualization of Task Hierarchy

<img width="1067" height="858" alt="image" src="https://github.com/user-attachments/assets/ad065e56-bcfc-4bb9-9a23-6a25b169b705" />
