# Intelliplane
AI powered autopilot 

## usage
### simulator
execute ./simulator/main.py
parameters can be configured in ./simulator/helper/tools/constants.py

### autopilot
execute -/autopilot/rnn/main.py

## Erklärung
Da wir den Autopiloten nicht in Echtzeit auf dem Flugzeug testen können, mussten wir zwei neuronale Netze entwickeln: Bei dem einen handelt
es sich um einen Flugsimulator, welcher aus vorangegangenen Mess- und Steuerdaten die nächsten Daten vorhersagt. Dieses kann mit herkömmlichen supervised learning trainiert werden.
Mit Hilfe dieses Netzes kann dann der eigentiche Autopilot trainiert werden. Der Autopilot wird darauf trainiert, aus bestimmten Startsituationen heraus in einigen Zeitschritten einige Parameter wie den Anstellwinkel auf einen bestimmten Wert zu steuern.
Da beide Aufgaben das Arbeiten mit Zeitreihen beinhalten, sind beide neuronalen Netze als rekurrente Netzwerke ausgelegt. Der Simulator sagt aus den aktuellen Parametern und Steuerungssignalen sowie seinem internen Speicher (auch "state" genannt) die Parameter im nächsten Zeitpunkt voraus und darf seinen Speicher beschreiben.
Ganz ähnlich funkioniert der Autopilot: Er bestimmt aus den aktuellen Parametern und Steuerungssignalen die Steuerungssignale zum nächsten Zeitpunkt.
Im Training des Simulators wird der Simulator mithilfe der RNN-Klasse von Tensorflow nach und nach auf alle Zeitpunkte einer Zeitreihe aufgerufen. Dabei wird der interne Speicher von einem Zeitpunkt zum nächsten weitergegeben.So haben Daten aus mehreren Zeitpunkten Einfluss auf das Ergebnis.
Am Ende wird nur die Ähnlichkeit des letzten Aufrufs des Simulators mit den tatsächlichen nächsten Parameterwerten von der Fehlerfunktion bewertet.

Das Training des Autopilots basiert auf einem weitern Netzwerk. Dieses hat als Eingabe die Ausgangssituation und als Ausgabe (Eine Zeitreihe von Parameter- und Steuerungswerten) und als Ausgabe das Verhalten des Flugzeugs in den nächsten Zeitschritten. Dafür benutzt es den Autopiloten und den Simulator.
Dabei sind die Parameter des Autopiloten im Gegensatz zu denen des Simulators trainierbar (dieser ist vortrainiert). Der Fehler des Netzwerks wird dann aus der Abweichung dieser vorausgesagten Parameter von vorbestimmten Zielwerten (Horizontalflug, keine Schräglage...) berechnet.
So wird der Autopilot darauf trainiert, diese Zielwerte zu erreichen.
Nun stellt sich natürlich die Frage, was man mit einem Autopiloten anfangen soll, der nur horizontal in eine Richtung fliegen kann. Unser Verfahren, dem Autopiloten Steuereingaben zu machen, ist, dem Autopiloten keine absoluten Daten, sondern Daten relativ zum Zielwert zu übergeben.
Beispielsweise wird die Höhe immer auf 0m gesteuert. Wenn sich das Flugzeug dann 20m unter der Zielhöhe befindet, wird dem Autopiloten eine Höhe von -20m gemeldet. So lässt sich das Training sehr vereinfachen.
Es spricht aber nichts dagegen, dem Autopiloten in einer späteren Version auch eine Zielgeschwindigkeit zu übergeben.

Das Autopilottrainingsnetzwerk funktioniert folgendermaßen: Autopilot und Simulator initialisieren ihren internen Speicher durch das Verarbeiten der Startsituation. Dann bestimmen Autopilot und Simulator die nächsten Steuerungssignale, Parameter und Speicherstatus. Nach diesem Prinzip werden die Netzwerke einige Male mit ihren eigenen Ausgaben als Eingaben aufgerufen.
So steuert der Autopilot die nächsten paar Zeitschritte und wird dafür von der Fehlerfunktion bewertet.

### Datenbeschaffung
Alles zum Beschaffen der Trainingsdaten befindet sich im Ordner ./dataCollection. Im Unterordner arduino befindet sich der Code, der die Sensordaten im Flugzeug verarbeitet, codiert und sendet.
in telemetryServer befindet sich das NodeJS-Programm, das die Daten empfängt sowie an die Website im Ordner weiterleitet. Diese visualisiert die Daten und bietet die Möglichkeit, eine Aufzeichnung herunterzuladen. Aus dieser lassen sich Trainingsbeispiele auslesen. Unsere Testflüge befinden sich im Ordner logs.
### Simulator
Der Simulator befindet sich im Unterordner simulator. Der Einstiegspunkt ist main.py . trainModel.py biete die Methode, ein fertig traninertes Simulatormodell zu laden.
helper ist ein Modul, das einige wiederverwendbare Codestücke enthält: In helper.models befinden sich alle getesteten Simulator-Netzwerke, in helper.tools sind Werkzeuge wie eine Datensatzklasse und ein Test-Script für den Simulator. In der Datei helper.tools.constants lassen sich zentral die wichtigsten globalen Einstellungen vornehmen.
Zu beachten ist, dass nur das Netzwerk rnnSimV2 stabil funktioniert.
Im Ordner javascript ist ein noch nicht funktionsfähiger Ansatz, von python auf Javascript umzusteigen.
Die Datenformate (Reihenfolge und Bedeutung der Prameter) sind in helper.tools.readLog.py erklärt.
### Autopilot
Der relevante, benutzte Autopilot liegt in autopilot/rnn. Er wird mit main.py gestartet. Das Projekt ist so ausgelegt, dass ein Autopilot- und ein Simulatornetzwerk geladen werden. Beide müssen aus einem einzigen rekurrenten Netz bestehen, damit das Training funktioniert (die rekurrente Zelle darf aber beliebig kompliziert sein).

Das Trainingsnetzwerk für den Autopiloten (der "apTrainer") bestimmt mit AUtopilot und Simulator das Verhalten des FLugzeugs aus einer AUsgangssituation heraus. Dazu initialisert er zunächst die states von Simulator und Autopilot mithilfe der Startsituation. Simulator und Autopilot bestimmen dann aus ihrem Speicher und dem letzten Datensatz ihren Teil des Datensatzes einen Zeitpunkt später. Dieser wird dann wieder zurüchgeführt, sodass die nächsten paar (20) Flugzustände bei Steuerung durch den Autopiloten vorausgesagt werden.
Diese Voraussage wird dann durch eine Fehlerfunktion bewertet, sodass der Autopilot auf eine sinnvolle Steuerung hin trainiert werden kann.

## Ergebnis
Wenn nur Anstellwinkel und Schräglage betrachtet werden, lässt sich das Ergebnis durchaus sehen: Der Simulator reagiert plausibel auf Steuerausschläge mit Höhen- und Querruder.  Auch der Autopilot steuert die beiden Größen aus beliebigen Ausgangssituationen präzise auf null (siehe autopilot_behavior.pdf) . Nach den ersten 2.5s übernimmt der Autopilot das Steuer. Er stabilisiert das Flugzeug schnell und präzise, pitch und bank werden auf null gesteuert).

## Ausblick
Bei Hinzunahme von Geschwindigkeit und Höhe findet das Netzwerk beim Training leider noch keine sinnvolle Lösung, der Simulator reagiert nicht richtig auf Höhenruder- und Querruderinputs. Der entsprechende ist im folgenden branch verfügbar: https://github.com/fynsta/Intelliplane/tree/Ole
Unser Ansatz ist hier, den Simulator Höhendifferenzen voraussagen zu lassen, dem Autopiloten aber die absolute Höhe zu übergeben. So muss lediglich der "apTrainer" signifikant angepasst werden. Mit etwas fine-tuning kann hierfür aber sicherlich auch ein zufriedenstellendes Ergebnis erzielt werden. Analog kann das Steuern auf einen bestimmten Kurs implementiert werden. Allerdings halten wir es für möglich, dass hierfür noch sauberere Messdaten notwendig sind.
Ein Ansatz, um den Simulator noch realistischer zu machen, ist nicht mehr mit absoluten Werten, sondern mit Wahrscheinlichkeitsverteilungen zu arbeiten. Der Simulator sagt dann aus einer Wahrscheinlichkeitsverteilung von Ausgangssituationen eine Wahrscheinlichkeitsverteilung von nächsten Flugzuständen voraus bei (festen) Steuerinputs. Der Autopilot bestimmt aus einer Wahrscheinlichkeitsverteilung von FLugzeuständen Steuerinputs. Die Wahrscheinlichkeitsverteilungen werden dabei parametrisiert (z.B. als Normalverteilung) und die Parameter übergeben. So lässt sich potenziell modellieren, dass z.B. durch Böen der Effekt von Steuerinputs nicht im Voraus klar ist. Sonst ist ein mögliches Problem, dass der SImulator ein "Durchschnittsverhalten" simuliert, das stabiler als in der Realität ist.

## Video
https://youtu.be/X3z1Nj0Oe-Q