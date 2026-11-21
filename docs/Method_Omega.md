# Method Omega SPARQL and Gruff Examples

### Query For Model Hierarchy
This is for *Method Omega*, the methodology for the consulting firm. 

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

### Gruff Visualization of Model Hierarchy
<img width="993" height="843" alt="image" src="https://github.com/user-attachments/assets/74195dd6-9b51-44fb-9724-e147a815f12a" />

### Query For Plan Hierarchy
This is for *Method Omega* applied to a client for a project to build a `Customer Portal`. This and the following queries and graphs are for a planed project that hasn't started to execute yet. 

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

### Query for Develop Wireframes, Write Use Cases, and Review Requirements, with inputs, outputs, people, and roles:
| Person | Assigned role | Examples of assigned work |
|---|---|---|
| Alex Morgan | Project Manager | Kickoff Meeting; Review Requirements |
| Priya Shah | Business Analyst | Requirements Acquisition; Write Use Cases |
| Jordan Lee | User Experience Designer | Wireframe Interviews; Develop Wireframes |
| Sam Rivera | Developer | Technical Design; Implementation; Rollout |
| Taylor Chen | Quality Engineer | Testing |
```
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>

SELECT DISTINCT ?subject ?predicate ?object
WHERE {
  VALUES ?step {
    pm:Portal_Develop_Wireframes
    pm:Portal_Write_Use_Cases
    pm:Portal_Review_Requirements
  }

  {
    VALUES ?predicate {
      pp:hasInputVar
      pp:hasOutputVar
    }
    ?step ?predicate ?object .
    BIND(?step AS ?subject)
  }
  UNION
  {
    ?subject pm:has_assigned_step ?step .
    VALUES ?predicate {
      pm:has_assigned_step
      pm:has_assigned_agent
      pm:has_assigned_role
    }
    ?subject ?predicate ?object .
  }
}
ORDER BY ?subject ?predicate ?object
```
<img width="1119" height="656" alt="image" src="https://github.com/user-attachments/assets/c37d5026-b882-4b0d-9aa2-0177d689064b" />

### Query for Sequential Flows in the Methodology

| Level | Sequential flow |
|---|---|
| Method Omega | Requirements Acquisition → Technical Design → Implementation → Testing → Rollout |
| Requirements Acquisition | Kickoff Meeting → Create Project Narrative → Create Detailed Requirements → Review Requirements |
| Create Detailed Requirements | Create Wireframes → Create Use Cases |
| Create Wireframes | User Wireframe Interviews → Develop Wireframes |
| Create Use Cases | Use Case Interviews → Write Use Cases |

```
PREFIX pm: <https://in2use.com/process_model/>

CONSTRUCT {
  ?source pm:is_source_step_of ?transition .
  ?transition pm:has_target_step ?target .
  ?transition pm:has_condition ?condition .
}
WHERE {
  VALUES ?plan {
    pm:Method_Omega
    pm:Requirements_Acquisition_Plan
    pm:Create_Detailed_Requirements_Plan
    pm:Create_Wireframes_Plan
    pm:Create_Use_Cases_Plan
  }

  ?plan pm:has_step ?source .
  ?source pm:is_source_step_of ?transition .
  ?transition pm:has_target_step ?target .

  OPTIONAL {
    ?transition pm:has_condition ?condition .
  }
}
```
<img width="1556" height="905" alt="image" src="https://github.com/user-attachments/assets/e754494c-e10b-42d6-9fd4-0c6e870e3c56" />
