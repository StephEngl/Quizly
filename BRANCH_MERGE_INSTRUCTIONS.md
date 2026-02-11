# Anleitung: Copilot Branch in Main Branch zusammenführen

## Aktueller Status ✅

Die LICENSE-Datei (MIT License) wurde erfolgreich zum Repository hinzugefügt!

## Was wurde gemacht?

- ✅ LICENSE-Datei hinzugefügt (MIT License wie im README erwähnt)
- ✅ Änderungen sind im Branch `copilot/add-license-to-main`

## Wie bekomme ich nur den Main Branch?

Sie haben **3 einfache Optionen**:

### Option 1: Branch umbenennen (Einfachste Lösung) ⭐

Da Sie nur diesen einen Branch haben, können Sie ihn einfach auf GitHub umbenennen:

1. Gehen Sie zu: https://github.com/StephEngl/Quizly
2. Klicken Sie auf den Branch-Selector (wo "copilot/add-license-to-main" steht)
3. Klicken Sie auf "View all branches"
4. Bei `copilot/add-license-to-main` klicken Sie auf das Stift-Symbol
5. Benennen Sie um zu `main`
6. Fertig! ✅

### Option 2: Branch über GitHub Settings umbenennen

1. Gehen Sie zu: https://github.com/StephEngl/Quizly/settings
2. Navigieren Sie zu "Branches"
3. Klicken Sie bei "Default branch" auf das Stift-Symbol
4. Wenn `main` nicht existiert, erstellen Sie ihn:
   - Gehen Sie zurück zu Code
   - Klicken Sie auf den Branch-Selector
   - Tippen Sie "main" ein und klicken Sie "Create branch: main"
5. Dann setzen Sie `main` als Default

### Option 3: Lokaler Git Command

Wenn Sie das Repository lokal geklont haben:

```bash
# Branch umbenennen
git branch -m copilot/add-license-to-main main

# Neuen Branch hochladen
git push -u origin main

# Alten Branch löschen
git push origin --delete copilot/add-license-to-main
```

## Zusammenfassung

Der schnellste Weg: **Option 1** - Einfach den Branch auf GitHub umbenennen!

Danach haben Sie nur noch einen `main` Branch mit der LICENSE-Datei. 🎉

---

Diese Datei können Sie nach dem Umbenennen löschen, sie dient nur als Anleitung.
