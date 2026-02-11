# Anleitung: Copilot Branch in Main Branch zusammenführen

## Aktueller Status ✅

Die LICENSE-Datei wurde erfolgreich zum Repository hinzugefügt. Beide Branches (`copilot/add-license-to-main` und `main`) enthalten jetzt die gleichen Änderungen.

## Nächste Schritte

Um nur noch den `main` Branch zu haben, folgen Sie diesen Schritten:

### Option 1: Main Branch als Standard festlegen (Empfohlen)

1. **Gehen Sie zu Ihrem GitHub Repository**: https://github.com/StephEngl/Quizly

2. **Öffnen Sie die Einstellungen**:
   - Klicken Sie auf "Settings" (Einstellungen)
   - Navigieren Sie zu "Branches" im linken Menü

3. **Ändern Sie den Default Branch**:
   - Bei "Default branch" klicken Sie auf das Stift-Symbol
   - Wählen Sie `main` aus dem Dropdown
   - Klicken Sie auf "Update"
   - Bestätigen Sie die Änderung

4. **Löschen Sie den Copilot Branch** (optional):
   ```bash
   git branch -d copilot/add-license-to-main
   git push origin --delete copilot/add-license-to-main
   ```

### Option 2: Pull Request erstellen

1. Erstellen Sie einen Pull Request von `copilot/add-license-to-main` nach `main`
2. Mergen Sie den Pull Request
3. Löschen Sie den `copilot/add-license-to-main` Branch nach dem Merge

### Was wurde geändert?

- ✅ LICENSE-Datei (MIT License) hinzugefügt
- ✅ Main Branch erstellt mit allen Änderungen vom Copilot Branch
- ✅ Beide Branches sind auf dem gleichen Stand

### Wichtiger Hinweis

Da der `main` Branch lokal erstellt wurde, müssen Sie ihn noch auf GitHub pushen. Sie können dies auf zwei Arten tun:

**Lokaler Push (wenn Sie das Repository lokal geklont haben)**:
```bash
git checkout main
git push -u origin main
```

**Oder über die GitHub Weboberfläche**:
Der `main` Branch wird beim Merge des Pull Requests automatisch auf GitHub erstellt.

---

Falls Sie Fragen haben oder Hilfe benötigen, lassen Sie es mich wissen!
