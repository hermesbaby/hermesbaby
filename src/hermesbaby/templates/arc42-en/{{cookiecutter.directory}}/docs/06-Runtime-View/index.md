(sec_runtime_view)=
# Runtime View

The runtime view describes concrete behavior and interactions of the system’s building blocks in form of scenarios from the following areas:

- important use cases or features: how do building blocks execute them?
- interactions at critical external interfaces: how do building blocks cooperate with users and neighbouring systems?
- operation and administration: launch, start-up, stop
- error and exception scenarios

Remark: The main criterion for the choice of possible scenarios (sequences, workflows) is their *architectural relevancy*. It is *not* important to describe a large number of scenarios. You should rather document a representative selection.

```{todo}
Add {ref}`sec_runtime_view`, see [arc42-guideline](https://docs.arc42.org/section-6/)
```

## Runtime Scenario 1

```{uml} _figures/runtime_scenario_01.puml
:caption: Sequence Diagram
```
