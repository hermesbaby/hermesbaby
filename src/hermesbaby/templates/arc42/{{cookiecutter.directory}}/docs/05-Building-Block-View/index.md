(sec_building_block_view)=
# Bausteinsicht

```{todo}
Beschreiben des {ref}`sec_building_block_view` mithilfe der [arc42-guideline](https://docs.arc42.org/section-5/)
```

<!--
.Inhalt
Die Bausteinsicht zeigt die statische Zerlegung des Systems in Bausteine (Module, Komponenten, Subsysteme, Klassen, Schnittstellen, Pakete, Bibliotheken, Frameworks, Schichten, Partitionen, Tiers, Funktionen, Makros, Operationen, Datenstrukturen, ...) sowie deren Abhängigkeiten (Beziehungen, Assoziationen, ...)


Diese Sicht sollte in jeder Architekturdokumentation vorhanden sein.
In der Analogie zum Hausbau bildet die Bausteinsicht den _Grundrissplan_.

.Motivation
Behalten Sie den Überblick über den Quellcode, indem Sie die statische Struktur des Systems durch Abstraktion verständlich machen.

Damit ermöglichen Sie Kommunikation auf abstrakterer Ebene, ohne zu viele Implementierungsdetails offenlegen zu müssen.

.Form
Die Bausteinsicht ist eine hierarchische Sammlung von Blackboxen und Whiteboxen (siehe Abbildung unten) und deren Beschreibungen.

image::05_building_blocks-DE.png["Hierarchie in der Bausteinsicht"]

*Ebene 1* ist die Whitebox-Beschreibung des Gesamtsystems, zusammen mit Blackbox-Beschreibungen der darin enthaltenen Bausteine.

*Ebene 2* zoomt in einige Bausteine der Ebene 1 hinein.
Sie enthält somit die Whitebox-Beschreibungen ausgewählter Bausteine der Ebene 1, jeweils zusammen mit Blackbox-Beschreibungen darin enthaltener Bausteine.

*Ebene 3* zoomt in einige Bausteine der Ebene 2 hinein, usw.
-->


(sec_whitebox_system)=
## Whitebox Gesamtsystem

<!--
An dieser Stelle beschreiben Sie die Zerlegung des Gesamtsystems anhand des nachfolgenden Whitebox-Templates.
Dieses enthält:

* Ein Übersichtsdiagramm
* die Begründung dieser Zerlegung
* Blackbox-Beschreibungen der hier enthaltenen Bausteine.
Dafür haben Sie verschiedene Optionen:

** in _einer_ Tabelle, gibt einen kurzen und pragmatischen Überblick über die enthaltenen Bausteine sowie deren Schnittstellen.
** als Liste von Blackbox-Beschreibungen der Bausteine, gemäß dem Blackbox-Template (siehe unten).
Diese Liste können Sie, je nach Werkzeug, etwa in Form von Unterkapiteln (Text), Unter-Seiten (Wiki) oder geschachtelten Elementen (Modellierungswerkzeug) darstellen.

* (optional:) wichtige Schnittstellen, die nicht bereits im Blackbox-Template eines der Bausteine erläutert werden, aber für das Verständnis der Whitebox von zentraler Bedeutung sind.
Aufgrund der vielfältigen Möglichkeiten oder Ausprägungen von Schnittstellen geben wir hierzu kein weiteres Template vor.
Im schlimmsten Fall müssen Sie Syntax, Semantik, Protokolle, Fehlerverhalten, Restriktionen, Versionen, Qualitätseigenschaften, notwendige Kompatibilitäten und vieles mehr spezifizieren oder beschreiben.
Im besten Fall kommen Sie mit Beispielen oder einfachen Signaturen zurecht.
-->


{numref}`fig_overview_diagram` zeigt ...

(fig_overview_diagram)=
```{drawio-figure} _figures/overview_diagram.drawio
Übersichts-Diagramm
```


### Bausteine

`User`
: Erläuterung

`box_1`
: Erläuterung

`box_2`
: Erläuterung

`box_3`
: Erläuterung

`box_4`
: Erläuterung

`box_5`
: Erläuterung

`Neighbor`
: Erläuterung


### Schnittstellen

`IF_USER_SYS`
: Erläuterung

`IF_SYS_USER`
: Erläuterung

`IF_1_2`
: Erläuterung

`IF_1_5`
: Erläuterung

`IF_2_3`
: Erläuterung

`IF_4_2`
: Erläuterung

`IF_4_5`
: Erläuterung

`IF_SYS_NB`
: Erläuterung

`IF_NB_SYS`
: Erläuterung


<!--
Hier folgen jetzt Erläuterungen zu Blackboxen der Ebene 1.

Falls Sie die tabellarische Beschreibung wählen, so werden Blackboxen darin nur mit Name und Verantwortung nach folgendem Muster beschrieben:


| Name | Verantwortung |
|------|---------------|
| _<Blackbox 1>_ | _<Text>_
| _<Blackbox 2>_ | _<Text>_


Falls Sie die ausführliche Liste von Blackbox-Beschreibungen wählen, beschreiben Sie jede wichtige Blackbox in einem eigenen Blackbox-Template.
Dessen Überschrift ist jeweils der Namen dieser Blackbox.
-->

### Bausteine

#### box_1

<!--
Beschreiben Sie die <Blackbox 1> anhand des folgenden Blackbox-Templates:

* Zweck/Verantwortung
* Schnittstelle(n), sofern diese nicht als eigenständige Beschreibungen herausgezogen sind.
Hierzu gehören eventuell auch Qualitäts- und Leistungsmerkmale dieser Schnittstelle.
* (Optional) Qualitäts-/Leistungsmerkmale der Blackbox, beispielsweise Verfügbarkeit, Laufzeitverhalten o. Ä.
* (Optional) Ablageort/Datei(en)
* (Optional) Erfüllte Anforderungen, falls Sie Traceability zu Anforderungen benötigen.
* (Optional) Offene Punkte/Probleme/Risiken
-->


#### box_i

<!--
_<Blackbox-Template>_
-->


#### box_n

<!--
_<Blackbox-Template>_
-->


## Ebene 2

<!--
Beschreiben Sie den inneren Aufbau (einiger) Bausteine aus Ebene 1 als Whitebox.

Welche Bausteine Ihres Systems Sie hier beschreiben, müssen Sie selbst entscheiden.
Bitte stellen Sie dabei Relevanz vor Vollständigkeit.
Skizzieren Sie wichtige, überraschende, riskante, komplexe oder besonders volatile Bausteine.
Normale, einfache oder standardisierte Teile sollten Sie weglassen.
-->


### Whitebox _<Baustein 1>_

<!--
...zeigt das Innenleben von _Baustein 1_.
-->


### Whitebox _<Baustein 2>_



### Whitebox _<Baustein m>_



## Ebene 3

<!--
Beschreiben Sie den inneren Aufbau (einiger) Bausteine aus Ebene 2 als Whitebox.

Bei tieferen Gliederungen der Architektur kopieren Sie diesen Teil von arc42 für die weiteren Ebenen.
-->


### Whitebox <_Baustein x.1_>



### Whitebox <_Baustein x.2_>



### Whitebox <_Baustein y.1_>
