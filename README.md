# GiIXEA
Gesetze-im-Internet XML Extraction Algorithm

## Motivation
Gesetze-im-Internet(GiL) ist ein toller Service, da alle Gesetzestexte auch im XML-Format verfügbar sind. Im Zusammenhang mit einer möglichen Weiterverarbeitung in LLM wollte ich die Möglichkeit haben, einzelne Paragraphen abfragen.

## Realisierung
XML-Datei wird von GiI heruntergeladen, in Python in JSON-Format umgewandelt, in RedisJSON gespeichert und mit dem Algorithmus, der hier präsentiert wird, verarbeitet. 
### Fähigkeit
Momentan ist es möglich, mit dem Algorithmus den Gesetzestext komplett in Strings wiederzugeben. Getestet wurde in BGB und StGB
### Einschränkung
Es gibt an manchen Stellen das Problem, dass Aufzählungen innerhalb eines Absatzes auftaucht, der Absatz wird als ganzes Element aufgelistet, die Aufzählungen tauchen zwar als Kindeselemente, aber es gibt keine Möglichkeit, die Aufzählungen an den richtigen Stellen zu versetzen.

z.B. §357b Abs.2 Nr.1 und Nr.2 https://www.gesetze-im-internet.de/bgb/__357b.html

Abs.2 wird in der XML-Datei so dargestellt:

"(2) Im Falle des Widerrufs von außerhalb von Geschäftsräumen geschlossenen Verträgen oder Fernabsatzverträgen über Finanzdienstleistungen ist der Verbraucher zur Zahlung von Wertersatz für die vom Unternehmer bis zum Widerruf erbrachte Dienstleistung verpflichtet, wenn er Im Falle des Widerrufs von Verträgen über eine entgeltliche Finanzierungshilfe, die von der Ausnahme des § 506 Absatz 4 erfasst sind, gelten auch § 357 Absatz 5 bis 7 und § 357a Absatz 1 und 2 entsprechend. Ist Gegenstand des Vertrags über die entgeltliche Finanzierungshilfe die Lieferung von nicht auf einem körperlichen Datenträger befindlichen digitalen Inhalten, hat der Verbraucher Wertersatz für die bis zum Widerruf gelieferten digitalen Inhalte zu leisten, wenn er Ist im Vertrag eine Gegenleistung bestimmt, ist sie bei der Berechnung des Wertersatzes zu Grunde zu legen. Ist der vereinbarte Gesamtpreis unverhältnismäßig hoch, ist der Wertersatz auf der Grundlage des Marktwerts der erbrachten Leistung zu berechnen."

Die Kindeselemente sehen so aus:

"vor Abgabe seiner Vertragserklärung auf diese Rechtsfolge hingewiesen worden ist und"

"ausdrücklich zugestimmt hat, dass der Unternehmer vor Ende der Widerrufsfrist mit der Ausführung der Dienstleistung beginnt."

Es gibt keine Information darüber, an welchen Stellen diese Aufzählungen in den Absatz hinzugefügt werden. Ein Work-Around momentan ist die XML-Datein manuell zu bearbeiten.
