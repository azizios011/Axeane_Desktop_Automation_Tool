# Function/FormFiller.py
from Function.JS_Elements import AxeaneJS
from Debug.Logger import ColorLogger as log


class AxeaneFormFiller:
    """
    High-level form filler for Axeane Kompta.
    Uses AxeaneJS for low-level AngularJS interactions.
    """

    # Axeane page URLs
    URL_SAISIE = "https://kompta.axeane.com/views/comptageneral/traitement/ecritures/ecranEcritureMainModele2.html"
    URL_HOME = "https://kompta.axeane.com"

    def __init__(self, page):
        self.page = page
        self.js = AxeaneJS(page)

    # ──────────────────────────────────────────────
    # NAVIGATION
    # ──────────────────────────────────────────────
    async def navigate_to_saisie(self):
        """Navigate to the 'Saisie des écritures' page."""
        log.info("Navigating to Saisie des écritures...")
        await self.page.goto(self.URL_SAISIE)
        await self.page.wait_for_load_state("networkidle")
        await self.page.wait_for_timeout(1500)
        log.success("Navigated to Saisie des écritures")

    async def get_current_url(self):
        """Get the current page URL."""
        return self.page.url

    async def test_connection(self):
        """Test if we're connected to Axeane Kompta."""
        try:
            url = await self.get_current_url()
            if "axeane.com" in url:
                log.success(f"Connected to Axeane: {url}")
                return True, url
            else:
                log.warn(f"Not on Axeane: {url}")
                return False, url
        except Exception as e:
            log.error(f"Connection test failed: {e}")
            return False, str(e)

    # ──────────────────────────────────────────────
    # FORM FILLING
    # ──────────────────────────────────────────────
    async def fill_header(self, journal, mois, ref, libelle, date=None):
        """
        Fill the header section of the Saisie form.
        
        Args:
            journal: Journal code (e.g., "VT", "CA", "BQ")
            mois: Month text (e.g., "Mars 2026")
            ref: Reference/piece number (e.g., "FC000761")
            libelle: Label (e.g., client name)
            date: Optional date (dd/mm/yyyy). If None, uses current date.
        """
        log.info(f"Filling header: journal={journal}, mois={mois}, ref={ref}")

        # Select journal
        await self.js.select_nya_bs_select("jo-eav", journal)
        await self.page.wait_for_timeout(300)

        # Select month
        await self.js.select_nya_bs_select("inputMoisIdEcriture", mois)
        await self.page.wait_for_timeout(300)

        # Fill reference
        await self.js.fill_ng_input("#idDocumentInputMD2, #idDocumentInputTD", ref)

        # Fill libellé
        await self.js.fill_ng_input("#inputLibelleIdMD2, #inputLibelleIdTD", libelle)

        # Fill date if provided
        if date:
            await self.js.fill_ng_input("#ec-date-creation", date)

        log.success(f"Header filled: {ref} - {libelle}")

    async def add_row(self):
        """Add a new row to the ecriture table."""
        await self.js.click_ng_button("ajouterEcriture()")
        await self.page.wait_for_timeout(400)

    async def fill_row(self, row_index, account, libelle, debit=0, credit=0):
        """
        Fill a single row in the ecriture table.
        
        Args:
            row_index: Row index (0-based)
            account: Account code (e.g., "411000")
            libelle: Row label
            debit: Debit amount (0 if credit)
            credit: Credit amount (0 if debit)
        """
        log.debug(f"Filling row {row_index}: {account} | D:{debit} C:{credit}")

        # Fill account (typeahead)
        account_selector = f"#cc_{row_index}_3"
        try:
            await self.page.locator(account_selector).wait_for(state="visible", timeout=2000)
        except Exception:
            account_selector = f"#cc_{row_index}_2"
        await self.js.select_typeahead(account_selector, account)

        # Fill libellé
        libelle_selector = f"#exlibelle{row_index}"
        await self.js.fill_ng_input(libelle_selector, libelle)

        # Fill debit or credit
        if debit and debit > 0:
            debit_selector = f"#debit-eav-{row_index}"
            try:
                await self.page.locator(debit_selector).wait_for(state="visible", timeout=2000)
            except Exception:
                debit_selector = f"#debit-eavp-{row_index}"
            await self.js.fill_ng_input(debit_selector, f"{debit:.3f}")

        if credit and credit > 0:
            credit_selector = f"#credit-eav-{row_index}"
            try:
                await self.page.locator(credit_selector).wait_for(state="visible", timeout=2000)
            except Exception:
                credit_selector = f"#credit-eavp-{row_index}"
            await self.js.fill_ng_input(credit_selector, f"{credit:.3f}")

    async def fill_invoice(self, header_data, formula_lines):
        """
        Fill a complete invoice (header + all rows).
        
        Args:
            header_data: Dict with journal, mois, ref, libelle, date
            formula_lines: List of dicts with account, label, debit, credit
        """
        log.info(f"Filling invoice: {header_data.get('ref')}")

        # Fill header
        await self.fill_header(
            journal=header_data.get("journal", "VT"),
            mois=header_data.get("mois", "Mars 2026"),
            ref=header_data.get("ref", ""),
            libelle=header_data.get("libelle", ""),
            date=header_data.get("date"),
        )

        # Fill rows
        for i, line in enumerate(formula_lines):
            if i > 0:
                await self.add_row()
            await self.fill_row(
                row_index=i,
                account=line.get("account", ""),
                libelle=line.get("label", ""),
                debit=line.get("debit", 0),
                credit=line.get("credit", 0),
            )

        log.success(f"Invoice {header_data.get('ref')} filled ({len(formula_lines)} rows)")

    async def save(self):
        """Click the Save button and wait for completion."""
        log.info("Saving entry...")
        await self.js.click_button_id("ec-save")
        await self.page.wait_for_load_state("networkidle")
        await self.page.wait_for_timeout(1000)
        log.success("Entry saved")

    async def balance(self):
        """Click the Balance (Équilibrer) button."""
        log.info("Balancing entry...")
        await self.js.click_ng_button("equilibrerEcriture()")
        await self.page.wait_for_timeout(500)

    async def reset_form(self):
        """Reset/clear the current form."""
        log.info("Resetting form...")
        await self.js.click_ng_button("resetEcritures()")
        await self.page.wait_for_timeout(500)

    async def wait_for_form_ready(self, timeout=10000):
        """Wait for the form to be ready for a new entry."""
        try:
            await self.page.locator("#idDocumentInputMD2, #idDocumentInputTD").wait_for(
                state="visible", timeout=timeout
            )
            await self.page.wait_for_timeout(300)
            return True
        except Exception as e:
            log.warn(f"Form not ready: {e}")
            return False

    # ──────────────────────────────────────────────
    # BATCH PROCESSING
    # ──────────────────────────────────────────────
    async def process_batch(self, invoices, progress_callback=None):
        """
        Process a batch of invoices.
        
        Args:
            invoices: List of dicts with header_data and formula_lines
            progress_callback: Optional callback(current, total, success, failed)
        """
        total = len(invoices)
        success = 0
        failed = 0

        log.info(f"Starting batch processing: {total} invoices")

        for i, invoice in enumerate(invoices):
            try:
                await self.fill_invoice(
                    header_data=invoice.get("header", {}),
                    formula_lines=invoice.get("lines", []),
                )
                await self.save()
                await self.wait_for_form_ready()
                success += 1
                log.success(f"[{i+1}/{total}] Saved: {invoice.get('header', {}).get('ref')}")
            except Exception as e:
                failed += 1
                log.error(f"[{i+1}/{total}] Failed: {e}")
                # Try to recover
                try:
                    await self.reset_form()
                    await self.wait_for_form_ready()
                except Exception:
                    pass

            if progress_callback:
                progress_callback(i + 1, total, success, failed)

        log.success(f"Batch complete: {success} succeeded, {failed} failed")
        return success, failed
        