(sec_quality_requirements)=
# Qualitätsanforderungen

```{todo}
Beschreiben des {ref}`sec_quality_requirements` mithilfe der [arc42-guideline](https://docs.arc42.org/section-10/). Siehe dazu auch {cite:p}`aim42`.
```

<!--
.Inhalt
Dieser Abschnitt enthält möglichst alle Qualitätsanforderungen als Qualitätsbaum mit Szenarien.
Die wichtigsten davon haben Sie bereits in Abschnitt 1.2 (Qualitätsziele) hervorgehoben.

Nehmen Sie hier auch Qualitätsanforderungen geringerer Priorität auf, deren Nichteinhaltung oder -erreichung geringe Risiken birgt.

.Motivation
Weil Qualitätsanforderungen die Architekturentscheidungen oft maßgeblich beeinflussen, sollten Sie die für Ihre Stakeholder relevanten Qualitätsanforderungen kennen, möglichst konkret und operationalisiert.
-->


(sec_quality_tree)=
## Qualitätsbaum

<!--
.Inhalt
Der Qualitätsbaum (á la ATAM) mit Qualitätsszenarien an den Blättern.

.Motivation
Die mit Prioritäten versehene Baumstruktur gibt Überblick über die -- oftmals zahlreichen -- Qualitätsanforderungen.

.Form
* Baumartige Verfeinerung des Begriffes „Qualität“, mit „Qualität“ oder „Nützlichkeit“ als Wurzel.
* Mindmap mit Qualitätsoberbegriffen als Hauptzweige

In jedem Fall sollten Sie hier Verweise auf die Qualitätsszenarien des folgenden Abschnittes aufnehmen.
-->




(sec_quality_scenarios)=
## Qualitätsszenarien

<!--
.Inhalt
Konkretisierung der (in der Praxis oftmals vagen oder impliziten) Qualitätsanforderungen durch (Qualitäts-)Szenarien.

Diese Szenarien beschreiben, was beim Eintreffen eines Stimulus auf ein System in bestimmten Situationen geschieht.

Wesentlich sind zwei Arten von Szenarien:

* Nutzungsszenarien (auch bekannt als Anwendungs- oder Anwendungsfallszenarien) beschreiben, wie das System zur Laufzeit auf einen bestimmten Auslöser reagieren soll.
Hierunter fallen auch Szenarien zur Beschreibung von Effizienz oder Performance.
Beispiel: Das System beantwortet eine Benutzeranfrage innerhalb einer Sekunde.
* Änderungsszenarien beschreiben eine Modifikation des Systems oder seiner unmittelbaren Umgebung.
Beispiel: Eine zusätzliche Funktionalität wird implementiert oder die Anforderung an ein Qualitätsmerkmal ändert sich.


.Motivation
Szenarien operationalisieren Qualitätsanforderungen und machen deren Erfüllung mess- oder entscheidbar.

Insbesondere wenn Sie die Qualität Ihrer Architektur mit Methoden wie ATAM überprüfen wollen, bedürfen die in Abschnitt 1.2 genannten Qualitätsziele einer weiteren Präzisierung bis auf die Ebene von diskutierbaren und nachprüfbaren Szenarien.

.Form
Entweder tabellarisch oder als Freitext.
-->


(fig_quality_tree)=
```{uml} _figures/quality_tree.puml
:caption: Die im Qualitätsbaum verorteten Qualitätsszenarien
```

{numref}`fig_quality_tree` zeigt ...

```{todo}
- Markieren der im Kapitel {ref}`sec_quality_goals` ausgesuchten Qualitäten.
- Erarbeiten der Qualitätsszenarien mit dem Fokus der ausgesuchten Qualitäten.
- Einsortieren der Qualitätsscenarien im {numref}`fig_quality_tree`.
```


### Qualitätsscenario 1

(fig_quality_scenario_01)=
```{uml} _figures/quality_scenario_01.puml
:caption: Sequenz des Qualitätsscenario 1
```

{numref}`fig_quality_scenario_01` zeigt ...
