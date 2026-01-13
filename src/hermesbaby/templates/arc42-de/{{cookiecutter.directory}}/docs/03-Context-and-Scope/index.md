(sec_context_and_scope)=
# Kontextabgrenzung

<!--
.Inhalt
Die Kontextabgrenzung grenzt das System gegen alle Kommunikationspartner (Nachbarsysteme und Benutzerrollen) ab.
Sie legt damit die externen Schnittstellen fest und zeigt damit auch die Verantwortlichkeit (scope) Ihres Systems: Welche Verantwortung trägt das System und welche Verantwortung übernehmen die Nachbarsysteme?

Differenzieren Sie fachlichen (Ein- und Ausgaben) und technischen Kontext (Kanäle, Protokolle, Hardware), falls nötig.


.Motivation
Die fachlichen und technischen Schnittstellen zur Kommunikation gehören zu den kritischsten Aspekten eines Systems.
Stellen Sie sicher, dass Sie diese komplett verstanden haben.

.Form
Verschiedene Optionen:

* Diverse Kontextdiagramme
-->


(sec_business_context)=
## Fachlicher Kontext

<!--
.Inhalt
Festlegung *aller* Kommunikationsbeziehungen (Nutzer, IT-Systeme, ...) mit Erklärung der fachlichen Ein- und Ausgabedaten oder Schnittstellen.
Zusätzlich (bei Bedarf) fachliche Datenformate oder Protokolle der Kommunikation mit den Nachbarsystemen.

.Motivation
Alle Beteiligten müssen verstehen, welche fachlichen Informationen mit der Umwelt ausgetauscht werden.

.Form
Alle Diagrammarten, die das System als Blackbox darstellen und die fachlichen Schnittstellen zu den Nachbarsystemen beschreiben.

Alternativ oder ergänzend können Sie eine Tabelle verwenden.
Der Titel gibt den Namen Ihres Systems wieder; die drei Spalten sind: Kommunikationsbeziehung, Eingabe, Ausgabe.

.Kapitelinhalte
- Diagramm und/oder Tabelle
- Optional: Erläuterung der externen fachlichen Schnittstellen.
-->

```{todo}
Beschreiben des {ref}`sec_business_context` mithilfe der [arc42-guideline](https://docs.arc42.org/section-3/)
```

{numref}`fig_business_context` sowie {numref}`tab_business_context` zeigen ...

(fig_business_context)=
```{drawio-figure} _figures/business_context.drawio
Technischer Kontext
```


(tab_business_context)=
```{table} Technischer Kontext
| Fachliche Schnittstelle | Beschreibung | Verbundenes System |
|-------------------------|--------------|--------------------|
|                         |              |                    |
```


(sec_technical_context)=
## Technischer Kontext

<!--
.Inhalt
Technische Schnittstellen (Kanäle, Übertragungsmedien) zwischen dem System und seiner Umwelt.
Zusätzlich eine Erklärung (_mapping_), welche fachlichen Ein- und Ausgaben über welche technischen Kanäle fließen.

.Motivation
Viele Stakeholder treffen Architekturentscheidungen auf Basis der technischen Schnittstellen des Systems zu seinem Kontext.

Insbesondere bei der Entwicklung von Infrastruktur oder Hardware sind diese technischen Schnittstellen durchaus entscheidend.

.Form
Beispielsweise UML Deployment-Diagramme mit den Kanälen zu Nachbarsystemen, begleitet von einer Tabelle, die Kanäle auf Ein-/Ausgaben abbildet.

.Kapitelinhalte
- Diagramm und/oder Tabelle
- Optional: Erläuterung der externen technischen Schnittstellen
- Mapping fachliche auf technische Schnittstellen
-->

```{todo}
Beschreiben des {ref}`sec_technical_context` mithilfe der [arc42-guideline](https://docs.arc42.org/section-3/)
```


{numref}`fig_technical_context` sowie {numref}`tab_technical_context` zeigen ...

(fig_technical_context)=
```{drawio-figure} _figures/technical_context.drawio
Technischer Kontext
```


(tab_technical_context)=
```{table} Technischer Kontext
| Technische Schnittstelle | Beschreibung | Protokoll/Technologie | Verbundenes System | Fachliche Schnittstelle |
|--------------------------|--------------|-----------------------|--------------------|-------------------------|
|                          |              |                       |                    |                         |
```

