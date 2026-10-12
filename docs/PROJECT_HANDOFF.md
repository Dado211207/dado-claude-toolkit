# dado-claude-toolkit — handoff za nastavak rada

> Presjek: 12. oktobar 2026, grana `main` na `da8276e0` prije ove dokumentacione izmjene. Opis koda je provjeren u repozitorijumu; stanje hostinga koje nije izričito potvrđeno označeno je kao neprovjereno. Ovaj dokument nije zamjena za aktuelni kod, CI ili odluke vlasnika.

## Svrha i stanje

Javni marketplace `dado-tools` za opcione Claude Code plugine: discipline rada u repozitorijumu, UI dizajn, web kvalitet, Python/Windows release, dvojezični sadržaj i bezbjednost izdanja. `main` je 28. avgusta 2026. spojio UI/UX paket (#2). `README.md` navodi verziju 0.1.0 i upute za instalaciju; nema aktivnih PR-ova u ovom presjeku. Toolkit nije automatska dozvola za pristup nalozima, deployment ili promjenu tuđeg projekta.

## Izvori, provjera i održavanje

Manifest marketplacea je u `.claude-plugin/`, definicije pod `plugins/`, profili usvajanja pod `profiles/`, provjere u `tests/` i `.github/workflows/validate.yml`. `docs/INSTALL.md`, `LOCAL-USAGE.md`, `CLOUD-USAGE.md`, `SECURITY.md`, `THREAT-MODEL.md`, `TRUST-AND-PERMISSIONS.md` i `MAINTENANCE.md` objašnjavaju granice. Za novu vještinu ili promjenu manifesta uskladi verziju, primjere, kompatibilnost, pravila dozvola i sve testove/workflow. Ako se mijenja skill, prati njegovu proceduru i verzionisanje, ne samo opis u README-u. `dado-claude-toolkit-sandbox` je odvojeno mjesto za probu i ne smije se tretirati kao korisnički projekat ili release.

## Kako nastaviti u novom chatu

1. Otvori ovaj dokument, `README.md`, najnoviji commit na `main` i otvorene PR-ove. Stariji planovi i nacrti ne nadjačavaju noviji kod.
2. Za konkretan zadatak pročitaj navedene izvorne fajlove i provjeri odgovarajuće podatke sa vlasnikom; ne dopunjavaj činjenice nagađanjem.
3. Pokreni relevantne provjere, pregledaj promjenu na telefonu i računaru kada dira UI, pa dokumentuj šta je stvarno objavljeno. Nikad ne upisuj lozinke, tokene, lične podatke ili sadržaj privatnih razgovora u Git.

