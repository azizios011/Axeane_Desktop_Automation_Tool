# Models/EcritureHeader.py
from Function.JS_Elements import AxeaneJS

class EcritureHeader:
    def __init__(self, page):
        self.page = page
        self.js = AxeaneJS(page)

    async def set_journal(self, journal_code: str):
        # Selector from DOM: ol#jo-eav (nya-bs-select)
        await self.js.select_nya_bs_select("ecritureGrouping.journal", journal_code)

    async def set_mois(self, mois_text: str):
        # Selector from DOM: ol#inputMoisIdEcriture (nya-bs-select)
        await self.js.select_nya_bs_select("items.selectedMoisDocComptable", mois_text)

    async def set_ref(self, ref: str):
        # Selector from DOM: input#idDocumentInputTD
        await self.js.fill_ng_input("#idDocumentInputTD", ref)

    async def set_libelle(self, libelle: str):
        # Selector from DOM: input#inputLibelleIdTD
        await self.js.fill_ng_input("#inputLibelleIdTD", libelle)
        