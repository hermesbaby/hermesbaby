(sec_architectural_decisions)=
# Architekturentscheidungen

```{todo}
Beschreiben des {ref}`sec_architectural_decisions` mithilfe der [arc42-guideline](https://docs.arc42.org/section-9/). Siehe dazu auch {cite:p}`aim42`.
```
<!--
.Inhalt
Wichtige, teure, große oder riskante Architektur- oder Entwurfsentscheidungen inklusive der jeweiligen Begründungen.
Mit "Entscheidungen" meinen wir hier die Auswahl einer von mehreren Alternativen unter vorgegebenen Kriterien.

Wägen Sie ab, inwiefern Sie Entscheidungen hier zentral beschreiben, oder wo eine lokale Beschreibung (z.B. in der Whitebox-Sicht von Bausteinen) sinnvoller ist.
Vermeiden Sie Redundanz.
Verweisen Sie evtl. auf Abschnitt 4, wo schon grundlegende strategische Entscheidungen beschrieben wurden.

.Motivation
Stakeholder des Systems sollten wichtige Entscheidungen verstehen und nachvollziehen können.

.Form
Verschiedene Möglichkeiten:

* ADR (https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) für jede wichtige Entscheidung
* Liste oder Tabelle, nach Wichtigkeit und Tragweite der Entscheidungen geordnet
* ausführlicher in Form einzelner Unterkapitel je Entscheidung
****
-->

Architekturentscheidungen können im gesamten Dokument definiert sein. Diese Tabelle führt sämtliche auf.

<!--
Für weitere Infos über `needtable` und `need`: https://sphinx-needs.readthedocs.io/en/latest/directives/needtable.html
-->

(tab_architectural_decisions)=
```{needtable} Architekturentscheidungen
:types: decision
:columns: id;title
```

(sec_central_architectural_decisions)=
## Zentrale Architekturentscheidungen


```{decision} Programmiersprache: Wir bevorzugen Python
:id: DECISION_01

Python bietet eine optimale Balance zwischen Lesbarkeit, Produktivität und Leistung, die für unser Projekt entscheidend ist. Die klare Syntax erleichtert die Zusammenarbeit im Team und reduziert die Einarbeitungszeit für neue Entwickler. Darüber hinaus verfügt Python über ein umfangreiches Ökosystem von Bibliotheken und Frameworks, die unsere Entwicklungsanforderungen abdecken, insbesondere in den Bereichen Datenverarbeitung, Machine Learning und Webentwicklung.


Die hohe Entwicklungsgeschwindigkeit mit Python ermöglicht schnellere Iterationen und kürzere Time-to-Market. Die große und aktive Community gewährleistet kontinuierliche Verbesserungen der Sprache sowie schnelle Unterstützung bei technischen Herausforderungen. Python's plattformübergreifende Kompatibilität und nahtlose Integration mit anderen Systemen entspricht zudem unseren Anforderungen an eine flexible, zukunftssichere Architektur.
```
