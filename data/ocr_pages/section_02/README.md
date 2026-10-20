# Pracovní přepisy skenů 32–41

Deset prvních skenů sekce **Rok 1920–1929**, číslované strany kroniky
27–36 (zápisy z let 1920–1924). Přepsáno přímo z obrazů dne 20. 10. 2026,
bez volání Anthropic API a bez následného jazykového uhlazení. Všech deset
stránek bylo následně znovu porovnáno po řádcích se skeny; sporné pasáže,
jména a čísla byly kontrolovány na samostatných zvětšených výřezech.

Zdroj každé stránky: `https://www.vranov.cz/evt_image.php?img=ID`.
Stažené obrazy jsou v ignorovaném adresáři `data/images/section_02/`.
Poskytnuté skeny mají výšku 1024 pixelů; zvětšené výřezy byly použity pro čtení.

**Jde o pracovní, neověřené přepisy.** Obsahují mnoho nejistých čtení,
zejména na straně 27 (sken 32). Pro spolehlivé citování je nutná kontrola
podle originálu nebo kvalitnějšího skenu. Nejasná slova a delší pasáže jsou
označeny `[?odhad?]`, nerozpoznané úseky `[nečitelné]`. Poznámky přepisujícího
a okrajové poznámky jsou v hranatých závorkách. Zlomky a některé číselné údaje
rovněž vyžadují kontrolu. Řádky odpovídají skenům; slova rozdělená na konci
řádku se při sestavení HTML spojují. Text pokračující mezi stránkami zůstává
rozdělen. Nejisté úseky označené `[?…?]` nejsou potvrzeným čtením ani po revizi.

Na straně 36 byly rozpočtové částky ponechány podle čtení skenu, přestože
zmínka o schodku s uvedenými příjmy a výdaji početně nesouhlasí. Text nebyl
opravován dopočítáváním ani podle očekávaného historického vývoje.

Jednotlivé soubory používají formát `page_NNN_idID.txt` podporovaný skriptem
`06_merge_page_texts.py`; stejné texty jsou přidané v `data/transcriptions.json`.
Při této aktualizaci bylo přidáno pouze těchto deset záznamů, původní záznamy
zůstaly zachovány. Pro zobrazení použijte `python 04_build_html.py`;
samostatný ukázkový web v `vranov-kronika-ocr-web/` obsahuje původních pět stran.
