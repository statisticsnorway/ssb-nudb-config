## Datatypesetting på nye variabler - Er dette korrekt?
vg_antall_fag_elevkurs (unit vgs, dtype INTEGER)
vg_karakterpoeng (unit vgs, dtype FLOAT)
vg_ervedtak_saer_spraak (unit vgs, dtype BOOLEAN)
vg_prove_dato (unit tid, dtype DATETIME)
uh_campus_kommune (unit uh, dtype STRING, length [4], klass_codelist=131; renamed_from ['campus_kom'])
uh_erpermisjon (unit uh, dtype BOOLEAN; renamed_from ['permisjon'])
uh_undervisningsspraak (unit uh, dtype STRING; renamed_from ['undervisningssprak'])
utd_orgnr_navn_inn (unit skole, dtype STRING; renamed_from ['skolenavn'])
vg_ny_laerling (unit vgs, dtype BOOLEAN; renamed_from ['nylaerl'])


## snr_mrk -> snr_mrk
> med nytt regime "vi beholder alltid fnr, og snr", så er denne unødvendig.
> Den kan finnes med `df['snr'].notna()`, og vil slik være enklere å opprettholde.
> Denne tas derfor ikke med i configgen, da den skal fjernes der den spottes.
> Foreslår heller "fnr_mrk_freg" som en variabel som sier "om utfylt fnr kobler mot freg" el. Vi kan kanskje sitte i en situasjon hvor snr mangler, men fnr kobler mot freg? Eller er det umulig?


# Kolonner i config som ikke er i omdøpingene
- Se csv i reports - skal de som ikke er med ligge definert under "utdatert" med en kommentar?
- Hvilke skal med og mangler i tilfelle omdøpinger?


## Vanskelig å skille disse fra hverandre
[variables.utd_viderutd_nettbasert]
    klass_codelist = 794
    renamed_from = ["evufjern"]

[variables.utd_nett_eller_stedbasert]
    klass_codelist = 796
    renamed_from = ["organisering"]
