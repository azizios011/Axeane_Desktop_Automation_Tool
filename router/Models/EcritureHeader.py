# Models/EcritureHeader.py
from Function.JS_Elements import AxeaneJS
from Debug.Logger import ColorLogger as log


class EcritureHeader:
    """Fills the top info zone of the Saisie des écritures form."""

    # Selectors from the DOM (works for both Modele2 and ModeleWithPiece)
    SEL_DATE = "#ec-date-creation"
    SEL_JOURNAL = "jo-eav"
    SEL_MOIS = "inputMoisIdEcriture"
    SEL_DEVISE = "devise"
    SEL_JOUR = "#inputJourIdEcritureAv, #inputJourIdEcriturePiece"
    SEL_REF = "#idDocumentInputMD2, #idDocumentInputTD"
    SEL_LIBELLE = "#inputLibelleIdMD2, #inputLibelleIdTD"

    def __init__(self, page):
        self.page = page
        self.js = AxeaneJS(page)

    async def set_date(self, date_str: str):
        """Set the operation date (dd/mm/yyyy format)."""
        await self.js.fill_ng_input(self.SEL_DATE, date_str)
        log.debug(f"Header: Date set to {date_str}")

    async def set_journal(self, journal_code: str):
        """Select the journal (VT, CA, BQ, etc.)."""
        await self.js.select_nya_bs_select(self.SEL_JOURNAL, journal_code)
        log.debug(f"Header: Journal set to {journal_code}")

    async def set_mois(self, mois_text: str):
        """Select the month (e.g., 'Mars 2026')."""
        await self.js.select_nya_bs_select(self.SEL_MOIS, mois_text)
        log.debug(f"Header: Mois set to {mois_text}")

    async def set_ref(self, ref: str):
        """Set the piece/reference number."""
        await self.js.fill_ng_input(self.SEL_REF, ref)
        log.debug(f"Header: Ref set to {ref}")

    async def set_libelle(self, libelle: str):
        """Set the libellé (label)."""
        await self.js.fill_ng_input(self.SEL_LIBELLE, libelle)
        log.debug(f"Header: Libellé set to {libelle}")

    async def fill_all(self, date_str: str, journal: str, mois: str, ref: str, libelle: str):
        """Fill all header fields in sequence."""
        await self.set_journal(journal)
        await self.set_mois(mois)
        await self.set_date(date_str)
        await self.set_ref(ref)
        await self.set_libelle(libelle)
        