(sec_deployment_view)=
# Deployment View

The deployment view describes:

1. the technical infrastructure used to execute your system, with infrastructure elements like geographical locations, environments, computers, processors, channels and net topologies as well as other infrastructure elements and
2. the mapping of (software) building blocks to that infrastructure elements.

Often systems are executed in different environments, e.g. development environment, test environment, production environment. In such cases you should document all relevant environments.

Especially document the deployment view when your software is executed as distributed system with more then one computer, processor, server or container or when you design and construct your own hardware processors and chips.

From a software perspective it is sufficient to capture those elements of the infrastructure that are needed to show the deployment of your building blocks. Hardware architects can go beyond that and describe the infrastructure to any level of detail they need to capture.

```{todo}
Add {ref}`sec_deployment_view`, see [arc42-guideline](https://docs.arc42.org/section-7/)
```

(sec_deployment_level_1)=
## Infrastructure Level  1

(fig_deployment_diagram)=
```{drawio-figure} _figures/deployment_diagram.drawio
Deployment-Diagramm
```

(sec_deployment_level_2)=
## Infrastructure Level 2
